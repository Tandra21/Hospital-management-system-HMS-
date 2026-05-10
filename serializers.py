"""
MedFind Telemedicine — WebSocket URL routing
Used by ASGI for WebRTC signaling (offer/answer/ICE exchange)
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # ws://domain/ws/session/<room_id>/
    re_path(r"^ws/session/(?P<room_id>[^/]+)/$", consumers.VideoSignalingConsumer.as_asgi()),
]
