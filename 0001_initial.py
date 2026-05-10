"""
MedFind — WebRTC Signaling Consumer
Handles WebSocket messages for video session signaling:
  - offer / answer / ice-candidate exchange between doctor and patient
  - join / leave room notifications
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class VideoSignalingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id   = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group = f"video_{self.room_id}"

        # Join channel group (max 2 peers: doctor + patient)
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()
        logger.info(f"WS connected: room={self.room_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)
        # Notify the other peer
        await self.channel_layer.group_send(
            self.room_group,
            {"type": "signaling_message", "data": {"type": "peer_left"}}
        )
        logger.info(f"WS disconnected: room={self.room_id}, code={close_code}")

    async def receive(self, text_data):
        """
        Expected message types: offer | answer | ice-candidate | join | ping
        """
        try:
            data = json.loads(text_data)
            msg_type = data.get("type", "")

            if msg_type == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
                return

            # Relay signaling message to the other peer in the room
            await self.channel_layer.group_send(
                self.room_group,
                {"type": "signaling_message", "data": data, "sender": self.channel_name}
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Bad WS message in room {self.room_id}: {e}")

    async def signaling_message(self, event):
        """Forward signaling message to this peer (skip echo back to sender)."""
        if event.get("sender") == self.channel_name:
            return
        await self.send(text_data=json.dumps(event["data"]))
