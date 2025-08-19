import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from schemas.schema import Session
from services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self):
        self.session_ttl = 1800  # TODO: make configurable later
        self.user_session_ttl = 86400
        self.analytics_cache_ttl = 300

    def create_session(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            session_id = str(uuid.uuid4())
            session_data = {
                "id": session_id,
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "total_messages": 0,
                "total_words": 0,
                "questions_asked": 0,
                "total_positive_messages": 0,
                "total_negative_messages": 0,
                "total_neutral_messages": 0,
            }

            cache_key = f"session:{session_id}"
            redis_service.set_cache(cache_key, session_data, self.session_ttl)

            if user_id:
                self._store_user_session_db(session_id, user_id)

            logger.info(f"Created new session: {session_id}")
            return session_data

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            cache_key = f"session:{session_id}"
            session_data = redis_service.get_cache(cache_key)

            if session_data:
                session_data["last_activity"] = datetime.now(timezone.utc).isoformat()
                redis_service.set_cache(cache_key, session_data, self.session_ttl)
                return session_data

            session_data = self._get_session_from_db(session_id)
            if session_data:
                redis_service.set_cache(cache_key, session_data, self.session_ttl)
                return session_data

            return None

        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None

    def update_session_activity(self, session_id: str) -> bool:
        try:
            cache_key = f"session:{session_id}"
            session_data = redis_service.get_cache(cache_key)

            if session_data:
                session_data["last_activity"] = datetime.now(timezone.utc).isoformat()
                redis_service.set_cache(cache_key, session_data, self.session_ttl)
                return True

            return False

        except Exception as e:
            logger.error(f"Error updating session activity {session_id}: {e}")
            return False

    def update_session_stats(self, session_id: str, analytics: dict) -> bool:
        try:
            cache_key = f"session:{session_id}"
            session_data = redis_service.get_cache(cache_key)

            if session_data:
                session_data["total_messages"] += 1
                session_data["total_words"] += analytics.get("word_count", 0)
                if analytics.get("is_question", False):
                    session_data["questions_asked"] += 1

                sentiment = analytics.get("sentiment", "neutral")
                if sentiment == "positive":
                    session_data["total_positive_messages"] += 1
                elif sentiment == "negative":
                    session_data["total_negative_messages"] += 1
                else:
                    session_data["total_neutral_messages"] += 1

                session_data["last_activity"] = datetime.now(timezone.utc).isoformat()
                redis_service.set_cache(cache_key, session_data, self.session_ttl)
                self._update_session_stats_db(session_id, analytics)
                return True

            return False

        except Exception as e:
            logger.error(f"Error updating session stats {session_id}: {e}")
            return False

    def get_session_analytics(
        self, session_id: str, use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        try:
            if use_cache:
                cache_key = f"analytics:{session_id}"
                cached_analytics = redis_service.get_cache(cache_key)
                if cached_analytics:
                    return cached_analytics

            session_data = self.get_session(session_id)
            if not session_data:
                return None

            analytics: Session = {
                "session_id": session_id,
                "total_messages": session_data.get("total_messages", 0),
                "total_words": session_data.get("total_words", 0),
                "questions_asked": session_data.get("questions_asked", 0),
                "total_positive_messages": session_data.get(
                    "total_positive_messages", 0
                ),
                "total_negative_messages": session_data.get(
                    "total_negative_messages", 0
                ),
                "total_neutral_messages": session_data.get("total_neutral_messages", 0),
                "avg_message_length": self._calculate_avg_message_length(session_data),
                "last_activity": session_data.get("last_activity"),
                "session_age": self._calculate_session_age(
                    session_data.get("created_at")
                ),
            }

            if use_cache:
                cache_key = f"analytics:{session_id}"
                redis_service.set_cache(cache_key, analytics, self.analytics_cache_ttl)

            return analytics

        except Exception as e:
            logger.error(f"Error getting session analytics {session_id}: {e}")
            return None


session_service = SessionService()
