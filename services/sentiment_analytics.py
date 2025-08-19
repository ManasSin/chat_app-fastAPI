import hashlib
from typing import Dict, Any
from datetime import datetime
from services.message_cache_service import message_cache_service
import logging

logger = logging.getLogger(__name__)


def get_sentiment_analytics(content: str, use_cache: bool = True) -> Dict[str, Any]:
    try:
        content_hash = hashlib.md5(content.encode()).hexdigest()

        if use_cache:
            cached_result = message_cache_service.get_cached_message_processing_result(
                content_hash
            )
            if cached_result:
                return cached_result

        word_count = len(content.split())
        char_count = len(content)
        sentence_count = content.count(".") + content.count("?") + content.count("!")

        question_words = ["what", "how", "why", "when", "where", "who"]
        is_question = "?" in content or any(
            content.lower().startswith(word) for word in question_words
        )

        positive_words = [
            "good",
            "great",
            "excellent",
            "love",
            "like",
            "happy",
            "awesome",
        ]
        negative_words = [
            "bad",
            "terrible",
            "hate",
            "sad",
            "angry",
            "awful",
            "horrible",
        ]

        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        result = {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "is_question": is_question,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat(),
        }

        if use_cache:
            message_cache_service.cache_message_processing_result(content_hash, result)

        return result

    except Exception as e:
        #  pylint: disable=logging-fstring-interpolation
        logger.error(f"Error processing message: {e}")
        return {
            "word_count": 0,
            "char_count": len(content),
            "sentence_count": 0,
            "is_question": False,
            "sentiment": "neutral",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
