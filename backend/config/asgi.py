"""
MedFind ASGI Configuration
Supports HTTP (Django) + WebSocket (Django Channels) for WebRTC signaling
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

# Import websocket URL patterns from telemedicine app
from apps.telemedicine import routing as telemedicine_routing

application = ProtocolTypeRouter({
    # Standard HTTP requests → Django views
    "http": get_asgi_application(),

    # WebSocket connections → Django Channels (WebRTC signaling)
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                telemedicine_routing.websocket_urlpatterns
            )
        )
    ),
})
