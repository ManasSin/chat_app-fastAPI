from datetime import datetime, timezone
from typing import Optional

from schemas.schema import Session
from services import (
    session_service,
    get_sentiment_analytics,
    message_cache_service,
    redis_service,
    pubsub_service,
)
import json
import logging

logger = logging.getLogger(__name__)


def handle_websocket_message(message) -> Optional[Session]:
    """Process incoming WebSocket messages and send responses."""
    session_id = message.get("session_id")
    content = message.get("content")

    session_service.update_session_activity(session_id)
    # TODO: this needs to taken care of, but later.
    analytics = get_sentiment_analytics(content, use_cache=True)

    message_id = (
        f"{session_id}_{datetime.now(timezone.utc).timestamp()}_{hash(content)}"
    )

    message_cache_service.cache_message_analytics(message_id, analytics)

    message_data_for_cache = {
        "id": message_id,
        "session_id": session_id,
        "content": content,
        **analytics,
    }
    message_cache_service.cache_recent_message(session_id, message_data_for_cache)

    try:
        pubsub_service.publish_message(session_id, message_data_for_cache)
    except Exception:
        logger.exception("Failed to publish message to pubsub")

    session_service.update_session_stats(session_id, analytics)
    session_stats = session_service.get_session_analytics(session_id, use_cache=True)

    try:
        persist_payload = {
            "id": message_id,
            "session_id": session_id,
            "content": content,
            "analytics": analytics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        redis_service.redis_client.publish(
            "persist:messages", json.dumps(persist_payload, default=str)
        )
    except Exception as e:
        logger.exception(f"Failed to publish message to persist channel: {e}")

    response = {
        "type": "message_response",
        "message_id": message_id,
        "original_message": content,
        "echo": f"You said: {content}",
        "analytics": {
            "word_count": analytics["word_count"],
            "char_count": analytics["char_count"],
            "sentence_count": analytics["sentence_count"],
            "is_question": analytics["is_question"],
            "sentiment": analytics["sentiment"],
        },
        "session_stats": session_stats,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cache_info": {
            "message_cached": True,
            "analytics_cached": True,
            "session_updated": True,
        },
    }
