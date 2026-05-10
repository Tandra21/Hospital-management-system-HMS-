from rest_framework import serializers
from .models import MedicalRecord

class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    class Meta:
        model = MedicalRecord
        fields = "__all__"
    def get_patient_name(self, obj):
        return obj.patient.user.full_name
