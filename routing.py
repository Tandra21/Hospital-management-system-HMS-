from django.db import models
class VideoSession(models.Model):
    STATUS = [
        ("scheduled",         "Scheduled"),
        ("waiting",           "Waiting For Doctor"),   # Patient in waiting room
        ("live",              "Live"),
        ("ended",             "Ended"),
        ("missed",            "Missed"),
    ]
    appointment = models.OneToOneField("appointments.Appointment", on_delete=models.CASCADE, related_name="video_session")
    room_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=15, choices=STATUS, default="scheduled")
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    patient_joined_at = models.DateTimeField(null=True, blank=True)   # Patient enters waiting room
    doctor_joined_at  = models.DateTimeField(null=True, blank=True)   # Doctor clicks JOIN SESSION
    recording_url = models.URLField(blank=True)
    # Auto-saved prescription after session (spec §2)
    prescription_text  = models.TextField(blank=True)
    prescription_file  = models.FileField(upload_to="prescriptions/%Y/%m/", null=True, blank=True)
    follow_up_notes    = models.TextField(blank=True)
    recommended_tests  = models.TextField(blank=True)
    class Meta:
        db_table = "mf_video_sessions"
    def __str__(self):
        return f"Session {self.room_id}"
