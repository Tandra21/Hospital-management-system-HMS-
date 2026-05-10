from rest_framework import serializers
from .models import LabTest, LabBooking

class LabTestSerializer(serializers.ModelSerializer):
    hospital_name = serializers.SerializerMethodField()
    class Meta:
        model = LabTest
        fields = "__all__"
    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None

class LabBookingSerializer(serializers.ModelSerializer):
    test_name = serializers.SerializerMethodField()
    class Meta:
        model = LabBooking
        fields = "__all__"
    def get_test_name(self, obj):
        return obj.test.name
