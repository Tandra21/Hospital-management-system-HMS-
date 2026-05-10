# medfind/ai/models.py
from djongo import models
from django.utils import timezone


class ChatSession(models.Model):
    session_id  = models.CharField(max_length=64, unique=True, db_index=True)
    user_id     = models.CharField(max_length=64, blank=True, null=True)
    user_ip     = models.GenericIPAddressField(blank=True, null=True)
    language    = models.CharField(max_length=5, default='en')
    turn_count  = models.IntegerField(default=0)
    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'ai'

    def __str__(self):
        return f'Session {self.session_id[:8]} | turns={self.turn_count}'


class ChatMessage(models.Model):
    ROLES = [('user','User'),('assistant','Assistant')]

    session      = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role         = models.CharField(max_length=12, choices=ROLES)
    content      = models.TextField()
    created_at   = models.DateTimeField(default=timezone.now)
    urgency      = models.CharField(max_length=20, blank=True)
    specialist   = models.CharField(max_length=80, blank=True)
    is_emergency = models.BooleanField(default=False)

    class Meta:
        app_label = 'ai'
        ordering  = ['created_at']

    def __str__(self):
        return f'[{self.role}] {self.content[:50]}'


class HealthRecord(models.Model):
    user_id   = models.CharField(max_length=64, default='anonymous', db_index=True)
    bmi       = models.FloatField(null=True, blank=True)
    systolic  = models.IntegerField(null=True, blank=True)
    diastolic = models.IntegerField(null=True, blank=True)
    sugar     = models.FloatField(null=True, blank=True)
    weight    = models.FloatField(null=True, blank=True)
    notes     = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'ai'
        ordering  = ['-created_at']


class DoctorProfile(models.Model):
    name       = models.CharField(max_length=120)
    specialty  = models.CharField(max_length=80)
    hospital   = models.CharField(max_length=120)
    phone      = models.CharField(max_length=20, blank=True)
    fee        = models.CharField(max_length=20, blank=True)
    experience = models.CharField(max_length=20, blank=True)
    rating     = models.FloatField(default=0)
    verified   = models.BooleanField(default=False)
    city       = models.CharField(max_length=50, default='Dhaka')
    active     = models.BooleanField(default=True)

    class Meta:
        app_label = 'ai'

    def __str__(self):
        return f'{self.name} — {self.specialty}'


class HospitalProfile(models.Model):
    name      = models.CharField(max_length=120)
    type      = models.CharField(max_length=80)
    address   = models.TextField()
    phone     = models.CharField(max_length=20)
    beds      = models.IntegerField(default=0)
    rating    = models.FloatField(default=0)
    emergency = models.BooleanField(default=False)
    icu       = models.BooleanField(default=False)
    city      = models.CharField(max_length=50, default='Dhaka')
    active    = models.BooleanField(default=True)

    class Meta:
        app_label = 'ai'

    def __str__(self):
        return self.name
