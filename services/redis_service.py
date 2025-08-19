import redis
import json
import pickle
from typing import Optional, Any, Dict, List
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=False)
        self.default_ttl = 3600

    def _serialize(self, data: Any) -> bytes:
        try:
            return pickle.dumps(data)
        except Exception:
            return json.dumps(data, default=str).encode()

    def _deserialize(self, data: bytes) -> Any:
        try:
            return pickle.loads(data)
        except Exception:
            try:
                return json.loads(data.decode())
            except Exception:
                return data.decode()

    def set_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            serialized_value = self._serialize(value)
            ttl = ttl or self.default_ttl
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        try:
            data = self.redis_client.get(key)
            if data:
                return self._deserialize(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def delete_cache(self, key: str) -> bool:
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        try:
            info = self.redis_client.info()
            return {
                "status": "healthy",
                "version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "uptime": info.get("uptime_in_seconds", 0),
            }
        except Exception as e:
            logger.error(f"Redis health check error: {e}")
            return {"status": "unhealthy", "error": str(e)}


redis_service = RedisService()
