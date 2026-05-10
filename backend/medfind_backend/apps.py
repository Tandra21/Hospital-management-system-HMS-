from django.contrib import admin
from .models import DailySnapshot, HospitalKPI

@admin.register(DailySnapshot)
class DailySnapshotAdmin(admin.ModelAdmin):
    list_display = ("date", "total_appointments", "new_patients",
                    "pharmacy_orders", "total_revenue")
    date_hierarchy = "date"

@admin.register(HospitalKPI)
class HospitalKPIAdmin(admin.ModelAdmin):
    list_display = ("hospital", "date", "bed_occupancy_rate",
                    "icu_occupancy_rate", "appointments_count", "revenue")
    list_filter = ("hospital",)
    date_hierarchy = "date"
