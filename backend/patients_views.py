"""
MedFind - Hospitals Module (Enhanced Views)
Production-ready API with nearby search, full detail, Bangladesh-wide
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Avg, Count, F
from django.utils import timezone
import math
import logging

logger = logging.getLogger(__name__)


def get_user_from_token(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, None
    token = auth.replace("Bearer ", "")
    try:
        from apps.accounts.models import User
        user_id = int(token.split("_")[2])
        return User.objects.get(id=user_id, is_active=True), None
    except Exception:
        return None, None


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance in km between two lat/lon points."""
    R = 6371
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(float(lat1))) *
         math.cos(math.radians(float(lat2))) *
         math.sin(dlon/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


class HospitalListView(APIView):
    """
    GET /api/v1/hospitals/
    Query params:
      q, division, district, type, has_emergency, has_icu, has_lab,
      min_rating, min_beds, specialty, page, limit, sort_by
    """

    def get(self, request):
        from apps.hospitals.models import Hospital
        from apps.hospitals.serializers import HospitalListSerializer

        qs = Hospital.objects.all()

        # Search
        q = request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(address__icontains=q) |
                Q(district__icontains=q) |
                Q(specialties__icontains=q)
            )

        # Filters
        division = request.query_params.get("division")
        if division:
            qs = qs.filter(division__iexact=division)

        district = request.query_params.get("district")
        if district:
            qs = qs.filter(district__icontains=district)

        h_type = request.query_params.get("type")
        if h_type:
            qs = qs.filter(hospital_type=h_type)

        if request.query_params.get("has_emergency") == "true":
            qs = qs.filter(emergency_open=True)

        if request.query_params.get("has_icu") == "true":
            qs = qs.filter(has_icu=True)

        if request.query_params.get("has_lab") == "true":
            qs = qs.filter(has_lab=True)

        if request.query_params.get("has_pharmacy") == "true":
            qs = qs.filter(has_pharmacy=True)

        min_rating = request.query_params.get("min_rating")
        if min_rating:
            qs = qs.filter(rating__gte=float(min_rating))

        min_beds = request.query_params.get("min_beds")
        if min_beds:
            qs = qs.filter(total_beds__gte=int(min_beds))

        # Sorting
        sort_by = request.query_params.get("sort_by", "rating")
        sort_map = {
            "rating": "-rating",
            "beds": "-total_beds",
            "name": "name",
            "newest": "-created_at",
        }
        qs = qs.order_by(sort_map.get(sort_by, "-rating"))

        # Pagination
        page = max(1, int(request.query_params.get("page", 1)))
        limit = min(50, max(1, int(request.query_params.get("limit", 20))))
        total = qs.count()
        qs = qs[(page - 1) * limit: page * limit]

        return Response({
            "success": True,
            "data": HospitalListSerializer(qs, many=True).data,
            "total": total,
            "page": page,
            "pages": math.ceil(total / limit),
            "limit": limit,
        })


class HospitalDetailView(APIView):
    """
    GET   /api/v1/hospitals/{id}/
    PATCH /api/v1/hospitals/{id}/  (admin only)
    """

    def get(self, request, pk):
        from apps.hospitals.models import Hospital
        from apps.hospitals.serializers import HospitalDetailSerializer
        from apps.doctors.models import Doctor
        from apps.doctors.serializers import DoctorListSerializer

        try:
            hospital = Hospital.objects.get(pk=pk)
        except Hospital.DoesNotExist:
            return Response({"success": False, "message": "Hospital not found"}, status=404)

        # Get doctors at this hospital
        doctors = Doctor.objects.filter(
            hospital=hospital, is_verified=True
        ).select_related("user").order_by("-rating")[:10]

        # Get lab tests
        try:
            from apps.labs.models import LabTest
            lab_tests = LabTest.objects.filter(hospital=hospital, is_active=True)[:20]
            from apps.labs.serializers import LabTestSerializer
            lab_data = LabTestSerializer(lab_tests, many=True).data
        except Exception:
            lab_data = []

        data = HospitalDetailSerializer(hospital).data
        data["doctors"] = DoctorListSerializer(doctors, many=True).data
        data["lab_tests"] = lab_data
        data["doctor_count"] = Doctor.objects.filter(hospital=hospital, is_verified=True).count()

        return Response({"success": True, "data": data})

    def patch(self, request, pk):
        user, _ = get_user_from_token(request)
        if not user or user.role not in ["superadmin", "hospital_admin"]:
            return Response({"success": False, "message": "Unauthorized"}, status=403)

        from apps.hospitals.models import Hospital, HospitalAdmin
        try:
            hospital = Hospital.objects.get(pk=pk)

            # Hospital admin can only edit their own hospital
            if user.role == "hospital_admin":
                if not HospitalAdmin.objects.filter(user=user, hospital=hospital).exists():
                    return Response({"success": False, "message": "Forbidden"}, status=403)
        except Hospital.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=404)

        allowed = [
            "name", "address", "phone", "email", "website",
            "total_beds", "available_beds", "icu_total", "icu_available",
            "emergency_open", "has_icu", "has_pharmacy", "has_lab",
            "specialties", "services",
        ]
        for field in allowed:
            if field in request.data:
                setattr(hospital, field, request.data[field])
        hospital.save()

        from apps.hospitals.serializers import HospitalDetailSerializer
        logger.info(f"Hospital {pk} updated by {user.email}")
        return Response({"success": True, "data": HospitalDetailSerializer(hospital).data})


class NearbyHospitalsView(APIView):
    """
    GET /api/v1/hospitals/nearby/
    Query params: lat, lng, radius (km, default 10), type, limit
    Returns hospitals sorted by distance from user location.
    Covers all of Bangladesh.
    """

    def get(self, request):
        from apps.hospitals.models import Hospital
        from apps.hospitals.serializers import HospitalListSerializer

        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        if not lat or not lng:
            return Response({
                "success": False,
                "message": "lat and lng parameters are required"
            }, status=400)

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response({"success": False, "message": "Invalid lat/lng values"}, status=400)

        # Validate Bangladesh bounds (roughly)
        if not (20.5 <= lat <= 26.7 and 88.0 <= lng <= 92.7):
            return Response({
                "success": False,
                "message": "Location is outside Bangladesh. Please use a valid location."
            }, status=400)

        radius = float(request.query_params.get("radius", 10))
        h_type = request.query_params.get("type")
        limit = min(50, int(request.query_params.get("limit", 20)))

        # Get all hospitals with coordinates
        qs = Hospital.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        )
        if h_type:
            qs = qs.filter(hospital_type=h_type)

        # Filter by emergency
        if request.query_params.get("emergency") == "true":
            qs = qs.filter(emergency_open=True)

        # Calculate distances in Python (use PostGIS in production)
        hospitals_with_dist = []
        for h in qs:
            dist = haversine_distance(lat, lng, h.latitude, h.longitude)
            if dist <= radius:
                hospitals_with_dist.append((h, round(dist, 2)))

        # Sort by distance
        hospitals_with_dist.sort(key=lambda x: x[1])
        hospitals_with_dist = hospitals_with_dist[:limit]

        data = []
        for h, dist in hospitals_with_dist:
            serialized = HospitalListSerializer(h).data
            serialized["distance_km"] = dist
            data.append(serialized)

        return Response({
            "success": True,
            "data": data,
            "total": len(data),
            "search_center": {"lat": lat, "lng": lng},
            "radius_km": radius,
        })


class HospitalBedAvailabilityView(APIView):
    """
    GET  /api/v1/hospitals/{id}/beds/
    PATCH /api/v1/hospitals/{id}/beds/  (hospital admin updates live bed count)
    Real-time bed availability tracker.
    """

    def get(self, request, pk):
        from apps.hospitals.models import Hospital
        try:
            h = Hospital.objects.get(pk=pk)
        except Hospital.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=404)

        occupancy = 0
        if h.total_beds > 0:
            occupancy = round((h.total_beds - h.available_beds) / h.total_beds * 100, 1)

        return Response({
            "success": True,
            "data": {
                "hospital_id": h.id,
                "hospital_name": h.name,
                "total_beds": h.total_beds,
                "available_beds": h.available_beds,
                "occupied_beds": h.total_beds - h.available_beds,
                "occupancy_rate": occupancy,
                "icu_total": h.icu_total,
                "icu_available": h.icu_available,
                "last_updated": timezone.now().isoformat(),
                "status": "critical" if occupancy > 90 else "high" if occupancy > 75 else "normal",
            }
        })

    def patch(self, request, pk):
        user, _ = get_user_from_token(request)
        if not user or user.role not in ["superadmin", "hospital_admin"]:
            return Response({"success": False, "message": "Unauthorized"}, status=403)

        from apps.hospitals.models import Hospital, HospitalAdmin
        try:
            h = Hospital.objects.get(pk=pk)
            if user.role == "hospital_admin":
                if not HospitalAdmin.objects.filter(user=user, hospital=h).exists():
                    return Response({"success": False, "message": "Forbidden"}, status=403)
        except Hospital.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=404)

        if "available_beds" in request.data:
            available = int(request.data["available_beds"])
            if available < 0 or available > h.total_beds:
                return Response({
                    "success": False,
                    "message": f"Available beds must be between 0 and {h.total_beds}"
                }, status=400)
            h.available_beds = available

        if "icu_available" in request.data:
            icu_avail = int(request.data["icu_available"])
            if icu_avail < 0 or icu_avail > h.icu_total:
                return Response({
                    "success": False,
                    "message": f"ICU available must be between 0 and {h.icu_total}"
                }, status=400)
            h.icu_available = icu_avail

        h.save(update_fields=["available_beds", "icu_available", "updated_at"])
        logger.info(f"Bed count updated for hospital {pk} by {user.email}")

        return Response({
            "success": True,
            "message": "Bed availability updated",
            "data": {
                "available_beds": h.available_beds,
                "icu_available": h.icu_available,
                "updated_at": timezone.now().isoformat(),
            }
        })
