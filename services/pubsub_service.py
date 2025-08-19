import threading
import json
import asyncio
import logging
from typing import Optional
from services.redis_service import redis_service
from utils.websocket_utils import connection_manager

logger = logging.getLogger(__name__)


class PubSubService:
    def __init__(self):
        self.redis = redis_service.redis_client
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def publish_message(self, session_id: str, message: dict) -> bool:
        try:
            channel = f"session:{session_id}"
            payload = json.dumps(message, default=str)
            self.redis.publish(channel, payload)
            return True
        except Exception as e:
            logger.error(f"Failed to publish message to {session_id}: {e}")
            return False

    def _subscriber_loop(self, loop: asyncio.AbstractEventLoop):
        try:
            pubsub = self.redis.pubsub()
            pubsub.psubscribe("session:*")
            logger.info("Redis pubsub subscriber started (pattern session:*)")

            for item in pubsub.listen():
                if not self._running:
                    break
                if item is None:
                    continue
                if item.get("type") in ("pmessage", "message"):
                    data = item.get("data")
                    try:
                        if isinstance(data, bytes):
                            data = data.decode()
                        payload = json.loads(data)
                    except Exception:
                        continue

                    channel = item.get("channel")
                    if isinstance(channel, bytes):
                        channel = channel.decode()

                    if channel and channel.startswith("session:"):
                        session_id = channel.split(":", 1)[1]

                        coro = connection_manager.send_personal_message(
                            json.dumps(payload), session_id
                        )
                        try:
                            asyncio.run_coroutine_threadsafe(coro, loop)
                        except Exception as e:
                            logger.error(f"Failed to schedule websocket send: {e}")

        except Exception as e:
            logger.exception(f"Redis subscriber loop error: {e}")

    def start_subscriber(self, loop: asyncio.AbstractEventLoop):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._subscriber_loop, args=(loop,), daemon=True
        )
        self._thread.start()

    def stop_subscriber(self):
        self._running = False
        try:
            self.redis.close()
        except Exception:
            pass


pubsub_service = PubSubService()
