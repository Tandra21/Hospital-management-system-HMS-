"""
MedFind - Enhanced Patients Module Views
Full professional production-level implementation
API Routes: /api/v1/patients/
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.core.exceptions import ValidationError
import json
import logging
import uuid

from .models import Patient
from .serializers import PatientSerializer, PatientDetailSerializer
from apps.appointments.models import Appointment
from apps.records.models import MedicalRecord

logger = logging.getLogger(__name__)


def get_user_from_token(request):
    """Extract and validate user from Bearer token."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, Response(
            {"success": False, "message": "Authorization token required", "code": "UNAUTHORIZED"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    token = auth_header.replace("Bearer ", "").strip()
    if not token or not token.startswith("mf_tok_"):
        return None, Response(
            {"success": False, "message": "Invalid token format", "code": "INVALID_TOKEN"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    try:
        from apps.accounts.models import User
        user_id = int(token.split("_")[2])
        user = User.objects.get(id=user_id, is_active=True)
        return user, None
    except (IndexError, ValueError, User.DoesNotExist):
        return None, Response(
            {"success": False, "message": "Invalid or expired token", "code": "TOKEN_INVALID"},
            status=status.HTTP_401_UNAUTHORIZED
        )


class PatientDashboardView(APIView):
    """
    GET /api/v1/patients/dashboard/
    Returns full dashboard data for the authenticated patient.
    """

    def get(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err

        try:
            patient = Patient.objects.select_related("user").get(user=user)
        except Patient.DoesNotExist:
            return Response(
                {"success": False, "message": "Patient profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        now = timezone.now()
        today = now.date()

        # Upcoming appointments
        upcoming_appointments = Appointment.objects.select_related(
            "doctor__user", "hospital"
        ).filter(
            patient=patient,
            appointment_date__gte=today,
            status__in=["pending", "confirmed"]
        ).order_by("appointment_date", "time_slot")[:5]

        # Recent appointments
        recent_appointments = Appointment.objects.select_related(
            "doctor__user", "hospital"
        ).filter(
            patient=patient,
            status="completed"
        ).order_by("-appointment_date")[:5]

        # Medical records stats
        records_count = MedicalRecord.objects.filter(patient=patient).count()
        recent_records = MedicalRecord.objects.filter(
            patient=patient
        ).order_by("-created_at")[:3]

        # Lab bookings (if app exists)
        try:
            from apps.labs.models import LabBooking
            lab_bookings = LabBooking.objects.filter(
                patient_name=user.full_name
            ).order_by("-created_at")[:5]
            lab_count = lab_bookings.count()
        except Exception:
            lab_bookings = []
            lab_count = 0

        # Appointment stats
        total_appointments = Appointment.objects.filter(patient=patient).count()
        upcoming_count = Appointment.objects.filter(
            patient=patient,
            appointment_date__gte=today,
            status__in=["pending", "confirmed"]
        ).count()

        # Notifications (simulated from records and appointments)
        notifications = []
        for appt in upcoming_appointments[:3]:
            notifications.append({
                "type": "appointment",
                "message": f"Upcoming appointment with {appt.doctor.user.full_name} on {appt.appointment_date}",
                "datetime": str(appt.appointment_date),
                "is_read": False,
            })

        dashboard_data = {
            "patient": {
                "id": patient.id,
                "name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "blood_group": patient.blood_group,
                "date_of_birth": str(patient.date_of_birth) if patient.date_of_birth else None,
                "age": patient.age,
                "gender": patient.gender,
                "allergies": patient.allergies,
                "chronic_conditions": patient.chronic_conditions,
                "emergency_contact_name": patient.emergency_contact_name,
                "emergency_contact_phone": patient.emergency_contact_phone,
            },
            "stats": {
                "total_appointments": total_appointments,
                "upcoming_appointments": upcoming_count,
                "medical_records": records_count,
                "lab_tests_done": lab_count,
            },
            "upcoming_appointments": [
                {
                    "id": a.id,
                    "doctor_name": a.doctor.user.full_name,
                    "specialty": a.doctor.specialty,
                    "hospital": a.hospital.name if a.hospital else None,
                    "date": str(a.appointment_date),
                    "time": a.time_slot,
                    "type": a.appointment_type,
                    "status": a.status,
                    "fee": str(a.fee),
                }
                for a in upcoming_appointments
            ],
            "recent_appointments": [
                {
                    "id": a.id,
                    "doctor_name": a.doctor.user.full_name,
                    "specialty": a.doctor.specialty,
                    "date": str(a.appointment_date),
                    "status": a.status,
                }
                for a in recent_appointments
            ],
            "notifications": notifications,
            "server_time": now.isoformat(),
        }

        logger.info(f"Dashboard loaded for patient {patient.id} (user: {user.email})")
        return Response({"success": True, "data": dashboard_data})


class PatientProfileView(APIView):
    """
    GET  /api/v1/patients/profile/  - Get own profile
    PUT  /api/v1/patients/profile/  - Update own profile
    POST /api/v1/patients/profile/  - Create profile if new
    """
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err
        try:
            patient = Patient.objects.select_related("user").get(user=user)
            return Response({"success": True, "data": PatientDetailSerializer(patient).data})
        except Patient.DoesNotExist:
            return Response({"success": False, "message": "Profile not found"}, status=404)

    def put(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err

        allowed_fields = [
            "date_of_birth", "gender", "blood_group", "height_cm", "weight_kg",
            "allergies", "chronic_conditions", "emergency_contact_name",
            "emergency_contact_phone", "address", "division",
            "insurance_provider", "insurance_number"
        ]

        try:
            patient = Patient.objects.get(user=user)
            for field in allowed_fields:
                if field in request.data:
                    val = request.data[field]
                    # Validate JSON fields
                    if field in ["allergies", "chronic_conditions"]:
                        if isinstance(val, str):
                            try:
                                val = json.loads(val)
                            except json.JSONDecodeError:
                                val = [v.strip() for v in val.split(",") if v.strip()]
                    setattr(patient, field, val)

            # Allow updating user name and phone
            user_update = {}
            if "full_name" in request.data:
                user_update["full_name"] = request.data["full_name"]
            if "phone" in request.data:
                phone = request.data["phone"]
                if len(phone) < 11:
                    return Response({"success": False, "message": "Phone must be at least 11 digits"}, status=400)
                user_update["phone"] = phone
            if user_update:
                for k, v in user_update.items():
                    setattr(user, k, v)
                user.save(update_fields=list(user_update.keys()))

            patient.save()
            logger.info(f"Profile updated for patient {patient.id}")
            return Response({
                "success": True,
                "message": "Profile updated successfully",
                "data": PatientDetailSerializer(patient).data
            })

        except Patient.DoesNotExist:
            return Response({"success": False, "message": "Profile not found"}, status=404)
        except Exception as e:
            logger.error(f"Profile update error: {e}")
            return Response({"success": False, "message": "Update failed", "detail": str(e)}, status=400)

    def post(self, request):
        """Create patient profile for newly registered user."""
        user, err = get_user_from_token(request)
        if err:
            return err
        if Patient.objects.filter(user=user).exists():
            return Response({"success": False, "message": "Profile already exists"}, status=409)
        patient = Patient.objects.create(
            user=user,
            gender=request.data.get("gender", ""),
            blood_group=request.data.get("blood_group", ""),
            division=request.data.get("division", ""),
            address=request.data.get("address", ""),
        )
        return Response({
            "success": True,
            "message": "Patient profile created",
            "data": PatientDetailSerializer(patient).data
        }, status=201)


class PatientMedicalSummaryView(APIView):
    """
    GET /api/v1/patients/medical-summary/
    Returns a comprehensive medical summary for a patient.
    """

    def get(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err

        try:
            patient = Patient.objects.get(user=user)
        except Patient.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=404)

        # All records grouped by type
        records = MedicalRecord.objects.filter(patient=patient).select_related(
            "doctor__user", "hospital"
        ).order_by("-created_at")

        diagnoses = records.filter(record_type="diagnosis")
        prescriptions = records.filter(record_type="prescription")
        lab_reports = records.filter(record_type="lab_report")
        doctor_notes = records.filter(record_type="note")

        from .serializers import MedicalRecordMinimalSerializer

        return Response({
            "success": True,
            "data": {
                "patient_id": patient.id,
                "full_name": user.full_name,
                "blood_group": patient.blood_group,
                "allergies": patient.allergies,
                "chronic_conditions": patient.chronic_conditions,
                "diagnoses": MedicalRecordMinimalSerializer(diagnoses[:10], many=True).data,
                "prescriptions": MedicalRecordMinimalSerializer(prescriptions[:10], many=True).data,
                "lab_reports": MedicalRecordMinimalSerializer(lab_reports[:10], many=True).data,
                "doctor_notes": MedicalRecordMinimalSerializer(doctor_notes[:5], many=True).data,
                "total_records": records.count(),
            }
        })


class PatientListView(APIView):
    """
    GET /api/v1/patients/ - Admin only: list all patients
    """

    def get(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err

        if user.role not in ["superadmin", "hospital_admin", "doctor"]:
            return Response({"success": False, "message": "Unauthorized"}, status=403)

        qs = Patient.objects.select_related("user").all()
        q = request.query_params.get("q")
        division = request.query_params.get("division")
        blood_group = request.query_params.get("blood_group")

        if q:
            qs = qs.filter(
                Q(user__full_name__icontains=q) | Q(user__email__icontains=q) | Q(user__phone__icontains=q)
            )
        if division:
            qs = qs.filter(division__iexact=division)
        if blood_group:
            qs = qs.filter(blood_group=blood_group)

        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 20))
        total = qs.count()
        qs = qs[(page - 1) * limit: page * limit]

        return Response({
            "success": True,
            "data": PatientSerializer(qs, many=True).data,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit,
        })
