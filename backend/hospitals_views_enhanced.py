"""
MedFind - Appointments Module (Enhanced Views)
Full production-level slot management, conflict detection, notifications
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta, time
import logging

logger = logging.getLogger(__name__)

BD_DAYS = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def get_user_from_token(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, Response({"success": False, "message": "Unauthorized"}, status=401)
    token = auth.replace("Bearer ", "")
    try:
        from apps.accounts.models import User
        user_id = int(token.split("_")[2])
        user = User.objects.get(id=user_id, is_active=True)
        return user, None
    except Exception:
        return None, Response({"success": False, "message": "Invalid token"}, status=401)


class AppointmentListView(APIView):
    """
    GET  /api/v1/appointments/
    POST /api/v1/appointments/
    """

    def get(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err

        from apps.appointments.models import Appointment
        from apps.appointments.serializers import AppointmentSerializer

        qs = Appointment.objects.select_related(
            "patient__user", "doctor__user", "hospital"
        )

        # Scope by role
        if user.role == "patient":
            try:
                from apps.patients.models import Patient
                patient = Patient.objects.get(user=user)
                qs = qs.filter(patient=patient)
            except Exception:
                return Response({"success": False, "message": "Patient profile not found"}, status=404)

        elif user.role == "doctor":
            try:
                from apps.doctors.models import Doctor
                doctor = Doctor.objects.get(user=user)
                qs = qs.filter(doctor=doctor)
            except Exception:
                return Response({"success": False, "message": "Doctor profile not found"}, status=404)

        elif user.role == "hospital_admin":
            from apps.hospitals.models import HospitalAdmin
            try:
                ha = HospitalAdmin.objects.get(user=user)
                qs = qs.filter(hospital=ha.hospital)
            except Exception:
                return Response({"success": False, "message": "Hospital admin profile not found"}, status=404)
        # superadmin: full access

        # Filters
        appt_status = request.query_params.get("status")
        if appt_status:
            qs = qs.filter(status=appt_status)

        doctor_id = request.query_params.get("doctor")
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)

        hospital_id = request.query_params.get("hospital")
        if hospital_id:
            qs = qs.filter(hospital_id=hospital_id)

        date_from = request.query_params.get("date_from")
        if date_from:
            qs = qs.filter(appointment_date__gte=date_from)

        date_to = request.query_params.get("date_to")
        if date_to:
            qs = qs.filter(appointment_date__lte=date_to)

        upcoming = request.query_params.get("upcoming")
        if upcoming == "true":
            qs = qs.filter(
                appointment_date__gte=timezone.now().date(),
                status__in=["pending", "confirmed"]
            )

        qs = qs.order_by("-appointment_date", "-created_at")

        page = max(1, int(request.query_params.get("page", 1)))
        limit = min(50, int(request.query_params.get("limit", 20)))
        total = qs.count()
        data = qs[(page - 1) * limit: page * limit]

        return Response({
            "success": True,
            "data": AppointmentSerializer(data, many=True).data,
            "total": total,
            "page": page,
        })

    def post(self, request):
        user, err = get_user_from_token(request)
        if err:
            return err

        from apps.appointments.models import Appointment
        from apps.appointments.serializers import CreateAppointmentSerializer, AppointmentSerializer
        from apps.doctors.models import Doctor

        doctor_id = request.data.get("doctor")
        appt_date = request.data.get("appointment_date")
        time_slot = request.data.get("time_slot")

        # Validate required fields
        if not all([doctor_id, appt_date, time_slot]):
            return Response({
                "success": False,
                "message": "doctor, appointment_date, and time_slot are required"
            }, status=400)

        # Validate date is not in the past
        try:
            appt_date_obj = datetime.strptime(appt_date, "%Y-%m-%d").date()
            if appt_date_obj < timezone.now().date():
                return Response({
                    "success": False,
                    "message": "Cannot book appointments in the past"
                }, status=400)
        except ValueError:
            return Response({"success": False, "message": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        # Check slot conflict
        conflict = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=appt_date,
            time_slot=time_slot,
            status__in=["pending", "confirmed"]
        ).exists()
        if conflict:
            return Response({
                "success": False,
                "message": "This time slot is already booked. Please choose another slot.",
                "code": "SLOT_CONFLICT"
            }, status=409)

        # Verify doctor works on this day
        try:
            doctor = Doctor.objects.get(pk=doctor_id)
            day_name = appt_date_obj.strftime("%A")
            if doctor.available_days and day_name not in doctor.available_days:
                return Response({
                    "success": False,
                    "message": f"Dr. {doctor.user.full_name} is not available on {day_name}"
                }, status=400)
        except Doctor.DoesNotExist:
            return Response({"success": False, "message": "Doctor not found"}, status=404)

        ser = CreateAppointmentSerializer(data=request.data)
        if ser.is_valid():
            appt = ser.save()
            # Calculate platform commission
            appt.commission_amount = float(appt.fee) * float(appt.hospital.commission_rate) / 100 if appt.hospital else float(appt.fee) * 0.05
            appt.save(update_fields=["commission_amount"])

            # Update doctor total_patients count
            Doctor.objects.filter(pk=doctor_id).update(total_patients=doctor.total_patients + 1)

            logger.info(f"Appointment booked: {appt.id} by {user.email}")

            # In production: send SMS/email notification
            # send_appointment_notification(appt)

            return Response({
                "success": True,
                "message": "Appointment booked successfully",
                "data": AppointmentSerializer(appt).data
            }, status=201)

        return Response({"success": False, "errors": ser.errors}, status=400)


class AppointmentDetailView(APIView):
    """
    GET    /api/v1/appointments/{id}/
    PATCH  /api/v1/appointments/{id}/  - Update status, notes
    DELETE /api/v1/appointments/{id}/  - Cancel appointment
    """

    def _get_appt(self, request, pk):
        user, err = get_user_from_token(request)
        if err:
            return None, None, err
        try:
            from apps.appointments.models import Appointment
            appt = Appointment.objects.select_related(
                "patient__user", "doctor__user", "hospital"
            ).get(pk=pk)
        except Exception:
            return None, None, Response({"success": False, "message": "Appointment not found"}, status=404)

        # Access check
        if user.role == "patient" and appt.patient.user != user:
            return None, None, Response({"success": False, "message": "Forbidden"}, status=403)
        if user.role == "doctor":
            try:
                from apps.doctors.models import Doctor
                if appt.doctor != Doctor.objects.get(user=user):
                    return None, None, Response({"success": False, "message": "Forbidden"}, status=403)
            except Exception:
                return None, None, Response({"success": False, "message": "Forbidden"}, status=403)

        return user, appt, None

    def get(self, request, pk):
        user, appt, err = self._get_appt(request, pk)
        if err:
            return err
        from apps.appointments.serializers import AppointmentSerializer
        return Response({"success": True, "data": AppointmentSerializer(appt).data})

    def patch(self, request, pk):
        user, appt, err = self._get_appt(request, pk)
        if err:
            return err

        new_status = request.data.get("status")
        valid_transitions = {
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["completed", "cancelled", "no_show"],
            "completed": [],
            "cancelled": [],
        }

        if new_status:
            if new_status not in valid_transitions.get(appt.status, []):
                return Response({
                    "success": False,
                    "message": f"Cannot change status from '{appt.status}' to '{new_status}'"
                }, status=400)
            appt.status = new_status

        if "doctor_notes" in request.data and user.role in ["doctor", "superadmin"]:
            appt.doctor_notes = request.data["doctor_notes"]

        if "prescription_id" in request.data:
            appt.prescription_id = request.data["prescription_id"]

        appt.save()
        from apps.appointments.serializers import AppointmentSerializer
        logger.info(f"Appointment {pk} updated to '{appt.status}' by {user.email}")
        return Response({
            "success": True,
            "message": f"Appointment status updated to '{appt.status}'",
            "data": AppointmentSerializer(appt).data
        })

    def delete(self, request, pk):
        user, appt, err = self._get_appt(request, pk)
        if err:
            return err

        if appt.status in ["completed", "cancelled"]:
            return Response({
                "success": False,
                "message": f"Cannot cancel a {appt.status} appointment"
            }, status=400)

        # 24-hour cancellation policy
        appt_datetime = datetime.combine(appt.appointment_date, time(9, 0))
        if datetime.now() > appt_datetime - timedelta(hours=24):
            if user.role not in ["superadmin", "hospital_admin"]:
                return Response({
                    "success": False,
                    "message": "Appointments cannot be cancelled less than 24 hours before the scheduled time"
                }, status=400)

        appt.status = "cancelled"
        appt.save(update_fields=["status"])
        logger.info(f"Appointment {pk} cancelled by {user.email}")
        return Response({"success": True, "message": "Appointment cancelled successfully"})


class AvailableSlotsView(APIView):
    """
    GET /api/v1/appointments/available-slots/
    Query params: doctor (required), date (required, YYYY-MM-DD)
    Returns list of available time slots for that doctor on that date.
    """

    def get(self, request):
        doctor_id = request.query_params.get("doctor")
        date_str = request.query_params.get("date")

        if not doctor_id or not date_str:
            return Response({
                "success": False,
                "message": "doctor and date parameters are required"
            }, status=400)

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"success": False, "message": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        if date_obj < timezone.now().date():
            return Response({"success": False, "message": "Date cannot be in the past"}, status=400)

        try:
            from apps.doctors.models import Doctor, DoctorSchedule
            doctor = Doctor.objects.get(pk=doctor_id)
        except Doctor.DoesNotExist:
            return Response({"success": False, "message": "Doctor not found"}, status=404)

        day_name = date_obj.strftime("%A")

        # Check if doctor works on this day
        schedule = DoctorSchedule.objects.filter(
            doctor=doctor, day=day_name, is_active=True
        ).first()

        if not schedule:
            return Response({
                "success": True,
                "data": {
                    "doctor_id": doctor_id,
                    "date": date_str,
                    "day": day_name,
                    "is_available": False,
                    "message": f"Dr. {doctor.user.full_name} does not work on {day_name}",
                    "slots": [],
                }
            })

        # Generate all slots
        all_slots = []
        slot_duration = 30  # minutes
        current = datetime.combine(date_obj, schedule.start_time)
        end = datetime.combine(date_obj, schedule.end_time)
        while current + timedelta(minutes=slot_duration) <= end:
            all_slots.append(current.strftime("%I:%M %p").lstrip("0"))
            current += timedelta(minutes=slot_duration)

        # Get booked slots for this date
        from apps.appointments.models import Appointment
        booked_slots = set(
            Appointment.objects.filter(
                doctor_id=doctor_id,
                appointment_date=date_obj,
                status__in=["pending", "confirmed"]
            ).values_list("time_slot", flat=True)
        )

        slots_data = [
            {
                "slot": s,
                "is_available": s not in booked_slots,
                "status": "booked" if s in booked_slots else "available"
            }
            for s in all_slots
        ]

        available_count = sum(1 for s in slots_data if s["is_available"])

        return Response({
            "success": True,
            "data": {
                "doctor_id": int(doctor_id),
                "doctor_name": doctor.user.full_name,
                "specialty": doctor.specialty,
                "date": date_str,
                "day": day_name,
                "is_available": True,
                "schedule": {
                    "start": str(schedule.start_time),
                    "end": str(schedule.end_time),
                    "max_slots": schedule.max_slots,
                },
                "available_count": available_count,
                "total_slots": len(slots_data),
                "slots": slots_data,
                "consultation_fee": str(doctor.consultation_fee),
                "video_fee": str(doctor.video_fee),
            }
        })
