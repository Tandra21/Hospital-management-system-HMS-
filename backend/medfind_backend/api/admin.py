"""
Admin configuration for API models
"""

from django.contrib import admin
from .models import (
    Hospital, Doctor, Patient, Appointment, LabTest,
    Billing, Pharmacy, MedicalHistory
)

# Register your models here.
admin.site.register(Hospital)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(LabTest)
admin.site.register(Billing)
admin.site.register(Pharmacy)
admin.site.register(MedicalHistory)
