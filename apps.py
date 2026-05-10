from django.contrib import admin
from .models import VideoSession

@admin.register(VideoSession)
class VideoSessionAdmin(admin.ModelAdmin):
    list_display = ("room_id", "appointment", "status", "started_at", "ended_at", "duration_minutes")
    list_filter = ("status",)
    search_fields = ("room_id",)
    readonly_fields = ("room_id", "started_at", "ended_at")
    ordering = ("-started_at",)
