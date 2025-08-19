import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)


class MessageCacheService:
    def __init__(self):
        self.message_cache_ttl = 1800

    def cache_message_analytics(self, message_id: str, analytics: dict) -> bool:
        try:
            cache_key = f"message_analytics:{message_id}"
            redis_service.set_cache(cache_key, analytics, self.message_cache_ttl)
            return True
        except Exception as e:
            logger.error(f"Error caching message analytics {message_id}: {e}")
            return False

    def cache_recent_message(self, session_id: str, message_data: dict) -> bool:
        try:
            cache_key = f"recent_messages:{session_id}"
            redis_service.set_cache(cache_key, message_data, self.message_cache_ttl)
            return True
        except Exception as e:
            logger.error(f"Error caching recent message for session {session_id}: {e}")
            return False

    def get_cached_message_analytics(self, message_id: str) -> Optional[Dict[str, Any]]:
        try:
            cache_key = f"message_analytics:{message_id}"
            return redis_service.get_cache(cache_key)
        except Exception as e:
            logger.error(f"Error getting cached message analytics {message_id}: {e}")
            return None

    def get_cached_recent_message(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            cache_key = f"recent_messages:{session_id}"
            return redis_service.get_cache(cache_key)
        except Exception as e:
            logger.error(
                f"Error getting cached recent message for session {session_id}: {e}"
            )
            return None

    def get_cached_message_processing_result(
        self, content_hash: str
    ) -> Optional[Dict[str, Any]]:
        try:
            cache_key = f"message_processing:{content_hash}"
            return redis_service.get_cache(cache_key)
        except Exception as e:
            logger.error(
                f"Error getting cached message processing result {content_hash}: {e}"
            )
            return None

    def invalidate_session_messages(self, session_id: str) -> bool:
        try:
            cache_key = f"recent_messages:{session_id}"
            return redis_service.delete_cache(cache_key)
        except Exception as e:
            logger.error(f"Error invalidating session messages {session_id}: {e}")
            return False


message_cache_service = MessageCacheService()
