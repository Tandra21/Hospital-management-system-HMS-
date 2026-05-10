# Django Backend for Hospital Management System
"""
Health Records Vault
"""

from django.db import models


class MedicalRecord(models.Model):
    TYPES = [
        ("prescription", "Prescription"),
        ("report", "Lab Report"),
        ("imaging", "Imaging/Scan"),
        ("discharge", "Discharge Summary"),
        ("vaccination", "Vaccination"),
        ("other", "Other"),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="medical_records"
    )

    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    hospital = models.ForeignKey(
        "hospitals.Hospital",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    record_type = models.CharField(max_length=20, choices=TYPES)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    file = models.FileField(
        upload_to="records/%Y/%m/",
        null=True,
        blank=True
    )

    date = models.DateField()
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_medical_records"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.patient} - {self.title} ({self.date})"


"""
Setup Instructions

1. Install Python dependencies:
   pip install -r requirements.txt

2. Copy `.env.example` to `.env`
   and update MongoDB connection settings.

3. Run migrations:
   python manage.py makemigrations
   python manage.py migrate

4. Start development server:
   python manage.py runserver

MongoDB:
The project uses `djongo`.
Set:
- MONGODB_URI
- MONGODB_NAME

API Endpoints:
- /api/auth/register/
- /api/auth/login/
- /api/auth/logout/
- /api/patients/
- /api/patients/<id>/
- /api/doctors/
- /api/doctors/<id>/
- /api/appointments/
- /api/appointments/<id>/
- /api/bills/
- /api/bills/<id>/
- /api/admissions/
- /api/admissions/<id>/
"""