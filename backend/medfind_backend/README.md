"""Analytics models - Daily snapshots & KPI tracking"""
from django.db import models


class DailySnapshot(models.Model):
    """Daily platform-wide stats snapshot"""
    date = models.DateField(unique=True, db_index=True)
    total_appointments = models.PositiveIntegerField(default=0)
    confirmed_appointments = models.PositiveIntegerField(default=0)
    cancelled_appointments = models.PositiveIntegerField(default=0)
    new_patients = models.PositiveIntegerField(default=0)
    new_doctors = models.PositiveIntegerField(default=0)
    new_hospitals = models.PositiveIntegerField(default=0)
    pharmacy_orders = models.PositiveIntegerField(default=0)
    pharmacy_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    booking_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mf_daily_snapshots"
        ordering = ["-date"]

    def __str__(self):
        return f"Snapshot {self.date}"


class HospitalKPI(models.Model):
    """Per-hospital KPIs tracked daily"""
    hospital = models.ForeignKey("hospitals.Hospital", on_delete=models.CASCADE, related_name="kpis")
    date = models.DateField(db_index=True)
    bed_occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    icu_occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    appointments_count = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_wait_minutes = models.PositiveIntegerField(default=0)
    patient_satisfaction = models.DecimalField(max_digits=3, decimal_places=1, default=0)

    class Meta:
        db_table = "mf_hospital_kpis"
        unique_together = ["hospital", "date"]
        ordering = ["-date"]
