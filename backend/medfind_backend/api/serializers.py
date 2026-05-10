"""
Serializers for API
Convert MongoDB documents to JSON
"""

from rest_framework import serializers
from .models import (
    Hospital, Doctor, Patient, Appointment, LabTest,
    Billing, Pharmacy, MedicalHistory, Address, WorkingHours
)


class AddressSerializer(serializers.Serializer):
    street = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    postal_code = serializers.CharField(required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)


class WorkingHoursSerializer(serializers.Serializer):
    day = serializers.CharField()
    opening_time = serializers.CharField()
    closing_time = serializers.CharField()
    is_closed = serializers.BooleanField()


class HospitalSerializer(serializers.Serializer):
    id = serializers.CharField(source='pk', read_only=True)
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    description = serializers.CharField(required=False)
    address = AddressSerializer()
    logo = serializers.URLField(required=False)
    website = serializers.URLField(required=False)
    license_number = serializers.CharField()
    specialties = serializers.ListField(child=serializers.CharField())
    bed_count = serializers.IntegerField(required=False)
    ambulance_available = serializers.BooleanField()
    emergency_services = serializers.BooleanField()
    rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = Address(**address_data)
        hospital = Hospital(address=address, **validated_data)
        hospital.save()
        return hospital

    def update(self, instance, validated_data):
        if 'address' in validated_data:
            address_data = validated_data.pop('address')
            instance.address = Address(**address_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DoctorSerializer(serializers.Serializer):
    id = serializers.CharField(source='pk', read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    specialization = serializers.CharField()
    qualifications = serializers.ListField(child=serializers.CharField())
    experience_years = serializers.IntegerField(required=False)
    hospital = serializers.SerializerMethodField()
    consultation_fee = serializers.FloatField()
    available_days = serializers.ListField(child=serializers.CharField())
    rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    profile_image = serializers.URLField(required=False, allow_blank=True)
    license_number = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def get_hospital(self, obj):
        """Get hospital with name and phone"""
        if obj.hospital:
            return {
                'id': str(obj.hospital.pk),
                'name': obj.hospital.name,
                'phone': obj.hospital.phone,
                'email': obj.hospital.email,
                'specialties': obj.hospital.specialties
            }
        return None

    def create(self, validated_data):
        hospital_id = validated_data.pop('hospital', None)
        if not hospital_id:
            raise serializers.ValidationError("Hospital is required")
        hospital = Hospital.objects(pk=hospital_id).first()
        if not hospital:
            raise serializers.ValidationError("Hospital not found")
        doctor = Doctor(hospital=hospital, **validated_data)
        doctor.save()
        return doctor


class PatientSerializer(serializers.Serializer):
    id = serializers.CharField(source='pk', read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    date_of_birth = serializers.DateTimeField(required=False)
    gender = serializers.ChoiceField(choices=['Male', 'Female', 'Other'], required=False)
    blood_group = serializers.ChoiceField(choices=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], required=False)
    address = AddressSerializer(required=False)
    emergency_contact = serializers.CharField(required=False)
    emergency_contact_phone = serializers.CharField(required=False)
    medical_conditions = serializers.ListField(child=serializers.CharField(), required=False)
    allergies = serializers.ListField(child=serializers.CharField(), required=False)
    medications = serializers.ListField(child=serializers.CharField(), required=False)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        patient = Patient(**validated_data)
        patient.save()
        return patient


class AppointmentSerializer(serializers.Serializer):
    id = serializers.CharField(source='pk', read_only=True)
    patient = serializers.CharField()  # Patient ID
    doctor = serializers.CharField()  # Doctor ID
    hospital = serializers.CharField()  # Hospital ID
    appointment_date = serializers.DateTimeField()
    appointment_type = serializers.ChoiceField(choices=['In-Person', 'Online', 'Phone'])
    reason_for_visit = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=['Scheduled', 'Completed', 'Cancelled', 'No-Show'])
    notes = serializers.CharField(required=False)
    prescription = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        patient_id = validated_data.pop('patient')
        doctor_id = validated_data.pop('doctor')
        hospital_id = validated_data.pop('hospital')
        
        patient = Patient.objects(pk=patient_id).first()
        doctor = Doctor.objects(pk=doctor_id).first()
        hospital = Hospital.objects(pk=hospital_id).first()
        
        if not all([patient, doctor, hospital]):
            raise serializers.ValidationError("Invalid patient, doctor, or hospital")
        
        appointment = Appointment(patient=patient, doctor=doctor, hospital=hospital, **validated_data)
        appointment.save()
        return appointment


class LabTestSerializer(serializers.Serializer):
    id = serializers.CharField(source='pk', read_only=True)
    patient = serializers.CharField()
    hospital = serializers.CharField()
    test_name = serializers.CharField()
    test_code = serializers.CharField()
    description = serializers.CharField(required=False)
    category = serializers.CharField()
    cost = serializers.FloatField()
    test_date = serializers.DateTimeField(required=False)
    result_date = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(choices=['Pending', 'Completed', 'Cancelled'])
    report_file = serializers.URLField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class BillingSerializer(serializers.Serializer):
    id = serializers.CharField(source='pk', read_only=True)
    patient = serializers.CharField()
    hospital = serializers.CharField()
    invoice_number = serializers.CharField()
    invoice_date = serializers.DateTimeField(read_only=True)
    services = serializers.ListField(child=serializers.DictField())
    total_amount = serializers.FloatField()
    discount = serializers.FloatField()
    tax = serializers.FloatField()
    payable_amount = serializers.FloatField()
    payment_method = serializers.ChoiceField(choices=['Cash', 'Card', 'Cheque', 'Online Transfer'])
    payment_status = serializers.ChoiceField(choices=['Pending', 'Paid', 'Failed', 'Refunded'])
    paid_date = serializers.DateTimeField(required=False)
    description = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class PharmacySerializer(serializers.Serializer):
    id = serializers.CharField(source='pk', read_only=True)
    medicine_name = serializers.CharField()
    medicine_code = serializers.CharField()
    description = serializers.CharField(required=False)
    generic_name = serializers.CharField(required=False)
    strength = serializers.CharField(required=False)
    form = serializers.ChoiceField(choices=['Tablet', 'Capsule', 'Liquid', 'Injection', 'Cream', 'Other'])
    quantity_in_stock = serializers.IntegerField()
    reorder_level = serializers.IntegerField(required=False)
    price = serializers.FloatField()
    supplier_name = serializers.CharField(required=False)
    manufacturer = serializers.CharField(required=False)
    batch_number = serializers.CharField(required=False)
    expiry_date = serializers.DateTimeField(required=False)
    hospital = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class MedicalHistorySerializer(serializers.Serializer):
    id = serializers.CharField(source='pk', read_only=True)
    patient = serializers.CharField()
    doctor = serializers.CharField(required=False)
    hospital = serializers.CharField()
    record_date = serializers.DateTimeField(read_only=True)
    visit_type = serializers.CharField(required=False)
    symptoms = serializers.ListField(child=serializers.CharField(), required=False)
    diagnosis = serializers.CharField(required=False)
    prescription = serializers.CharField(required=False)
    notes = serializers.CharField(required=False)
    vital_signs = serializers.DictField(required=False)
    follow_up_date = serializers.DateTimeField(required=False)
    follow_up_notes = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
