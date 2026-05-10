"""
MedFind API v1 — Complete URL Configuration
Endpoint: /api/v1/
"""
from django.urls import path, include

urlpatterns = [
    # ── Auth & Users ──────────────────────────────────────────
    path("accounts/",     include("apps.accounts.urls")),
    path("users/",        include("apps.users.urls")),

    # ── Healthcare Entities ───────────────────────────────────
    path("hospitals/",    include("apps.hospitals.urls")),
    path("doctors/",      include("apps.doctors.urls")),
    path("patients/",     include("apps.patients.urls")),

    # ── Clinical Operations ───────────────────────────────────
    path("appointments/", include("apps.appointments.urls")),
    path("pharmacy/",     include("apps.pharmacy.urls")),
    path("billing/",      include("apps.billing.urls")),
    path("labs/",         include("apps.labs.urls")),

    # ── Patient Services ──────────────────────────────────────
    path("locations/",    include("apps.locations.urls")),
    path("reviews/",      include("apps.reviews.urls")),
    path("notifications/",include("apps.notifications.urls")),
    path("records/",      include("apps.records.urls")),

    # ── Advanced Features ─────────────────────────────────────
    path("telemedicine/", include("apps.telemedicine.urls")),
    path("loyalty/",      include("apps.loyalty.urls")),
    path("campaigns/",    include("apps.campaigns.urls")),
    path("monetization/", include("apps.monetization.urls")),

    # ── Analytics & Admin ─────────────────────────────────────
    path("analytics/",    include("apps.analytics_api.urls")),
    path("admin-panel/",  include("apps.admin_panel.urls")),

    # ── System ────────────────────────────────────────────────
    path("health/",       include("apps.common.urls")),
]
