from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "notification_type", "title", "message", "is_read", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_title(self, v):
        if len(v.strip()) < 3:
            raise serializers.ValidationError("Title too short.")
        return v.strip()
