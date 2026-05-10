from rest_framework import serializers
from .models import VideoSession

class VideoSessionSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    appointment_ref = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = VideoSession
        fields = ["id", "room_id", "status", "appointment_ref", "patient_name",
                  "doctor_name", "started_at", "ended_at", "duration_minutes", "recording_url"]
        read_only_fields = ["id", "room_id", "started_at", "ended_at"]

    def get_patient_name(self, obj):
        try:
            return obj.appointment.patient.user.full_name
        except Exception:
            return "Patient"

    def get_doctor_name(self, obj):
        try:
            return obj.appointment.doctor.user.full_name
        except Exception:
            return "Doctor"

    def get_appointment_ref(self, obj):
        try:
            return str(obj.appointment.ref_id)
        except Exception:
            return ""

    def get_duration_minutes(self, obj):
        if obj.started_at and obj.ended_at:
            return int((obj.ended_at - obj.started_at).total_seconds() / 60)
        return 0
