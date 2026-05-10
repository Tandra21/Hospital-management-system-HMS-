# medfind/ai/admin.py
from django.contrib import admin
from .models import ChatSession, ChatMessage, HealthRecord, DoctorProfile, HospitalProfile


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display  = ['session_id', 'user_id', 'user_ip', 'language', 'turn_count', 'created_at']
    list_filter   = ['language', 'created_at']
    search_fields = ['session_id', 'user_id', 'user_ip']
    ordering      = ['-created_at']
    readonly_fields = ['session_id', 'created_at', 'updated_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ['session', 'role', 'urgency', 'specialist', 'is_emergency', 'created_at']
    list_filter   = ['role', 'is_emergency', 'urgency', 'created_at']
    search_fields = ['content', 'specialist']
    ordering      = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display  = ['user_id', 'bmi', 'systolic', 'diastolic', 'sugar', 'weight', 'created_at']
    list_filter   = ['created_at']
    search_fields = ['user_id']
    ordering      = ['-created_at']


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display  = ['name', 'specialty', 'hospital', 'city', 'rating', 'verified', 'active']
    list_filter   = ['specialty', 'city', 'verified', 'active']
    search_fields = ['name', 'specialty', 'hospital']
    ordering      = ['-rating']


@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display  = ['name', 'type', 'city', 'beds', 'rating', 'emergency', 'active']
    list_filter   = ['city', 'emergency', 'icu', 'active']
    search_fields = ['name', 'address']
    ordering      = ['-rating']
