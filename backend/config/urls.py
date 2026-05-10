from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("config.api.v1_urls")),
    path("api/donate/", include("donate.urls")),   # Donate Life — organ/blood donor
]
