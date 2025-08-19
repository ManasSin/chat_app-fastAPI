import threading
import json
import logging
from typing import Optional
from db.db import get_mongo_client
from schemas.mongo_message import MongoMessage
import datetime

logger = logging.getLogger(__name__)


class MongoPersistService:
    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def save_message_to_mongo(self, message: dict) -> bool:
        """
        Helper to save a message dict into MongoDB `messages` collection.
        Expects message to contain at least: id, session_id, content, timestamp (optional)
        """
        try:
            mongo_db = get_mongo_client()
            if not mongo_db:
                logger.error("MongoDB client not available")
                return False

            collection = mongo_db.get_collection("messages")

            try:
                mongo_msg = MongoMessage(**message)
            except Exception as e:
                logger.exception("Invalid message schema for Mongo: %s", e)
                return False

            doc = mongo_msg.dict(by_alias=True)
            if not doc.get("created_at"):
                doc["created_at"] = datetime.datetime.utcnow()

            logger.debug("Saving message to MongoDB: %s", doc)

            collection.insert_one(doc)
            return True
        except Exception as e:
            logger.exception(f"Failed to save message to MongoDB: {e}")
            return False

    def _subscriber_loop(self):
        try:
            from services.redis_service import redis_service

            redis = redis_service.redis_client
            pubsub = redis.pubsub()
            pubsub.subscribe("persist:messages")
            logger.info(
                "MongoPersistService subscriber started on channel persist:messages"
            )

            for item in pubsub.listen():
                if not self._running:
                    break
                if item is None:
                    continue
                if item.get("type") == "message":
                    data = item.get("data")
                    try:
                        if isinstance(data, bytes):
                            data = data.decode()
                        payload = json.loads(data)
                    except Exception:
                        logger.exception("Invalid message payload for persistence")
                        continue

                    try:
                        self.save_message_to_mongo(payload)
                    except Exception:
                        logger.exception(
                            "Error while saving message from pubsub to mongo"
                        )

        except Exception as e:
            logger.exception(f"MongoPersistService error: {e}")

    def start_persist_worker(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._subscriber_loop, daemon=True)
        self._thread.start()

    def stop_persist_worker(self):
        self._running = False


persist_service = MongoPersistService()
