from rest_framework import serializers
from .models import DailySnapshot, HospitalKPI

class DailySnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySnapshot
        fields = "__all__"

class HospitalKPISerializer(serializers.ModelSerializer):
    hospital_name = serializers.SerializerMethodField()
    class Meta:
        model = HospitalKPI
        fields = "__all__"
    def get_hospital_name(self, obj):
        return obj.hospital.name
