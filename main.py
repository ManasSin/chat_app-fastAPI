from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
import uvicorn

from models.models import MessageModel, SessionModel
from db.db import get_db, init_db, get_mongo_client
from core import settings
from services import get_sentiment_analytics, session_service, message_cache_service
import logging
from utils import connection_manager as manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database tables
init_db()

app = FastAPI(title="Chat Analytics Backend", version="1.0.0")

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=(["*"]),  # for now, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def process_message(content: str, use_cache: bool = True):
    analytics = get_sentiment_analytics(content, use_cache)
    return analytics


def get_or_create_session(db: Session, session_id: str):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        session = SessionModel(id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def update_session_stats(db: Session, session_id: str, analytics: dict):
    session = get_or_create_session(db, session_id)
    session.total_messages += 1
    session.total_words += analytics["word_count"]
    if analytics["is_question"]:
        session.questions_asked += 1
    if analytics["sentiment"] == "positive":
        session.total_positive_messages += 1
    elif analytics["sentiment"] == "negative":
        session.total_negative_messages += 1
    else:
        session.total_neutral_messages += 1
    session.last_updated = datetime.now(timezone.utc)
    db.commit()
    return session


def get_session_stats(db: Session, session_id: str):
    session = get_or_create_session(db, session_id)
    avg_message_length = (
        session.total_words / session.total_messages
        if session.total_messages > 0
        else 0
    )

    return {
        "total_messages": session.total_messages,
        "total_words": session.total_words,
        "questions_asked": session.questions_asked,
        "total_positive_messages": session.total_positive_messages,
        "total_negative_messages": session.total_negative_messages,
        "total_neutral_messages": session.total_neutral_messages,
        "avg_message_length": round(avg_message_length, 1),
    }


@app.websocket("/ws/chat/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)

    session_data = session_service.get_session(session_id)
    if not session_data:
        session_data = session_service.create_session()
        #  pylint: disable=logging-fstring-interpolation
        logger.info(f"Created new session for WebSocket: {session_id}")

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            content = message_data.get("message", "")

            session_service.update_session_activity(session_id)
            analytics = process_message(content, use_cache=True)

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
            message_cache_service.cache_recent_message(
                session_id, message_data_for_cache
            )

            session_service.update_session_stats(session_id, analytics)
            session_stats = session_service.get_session_analytics(
                session_id, use_cache=True
            )

            db = next(get_mongo_client())
            try:
                message = MessageModel(
                    session_id=session_id,
                    content=content,
                    word_count=analytics["word_count"],
                    char_count=analytics["char_count"],
                    sentence_count=analytics["sentence_count"],
                    is_question=analytics["is_question"],
                    sentiment=analytics["sentiment"],
                )
                db.add(message)
                db.commit()
                message_id = str(message.id)

            except Exception as e:
                db.rollback()
                logger.error(f"Database error: {e}")
                session_stats = {
                    "error": str(e),
                    "total_messages": 0,
                    "total_words": 0,
                    "questions_asked": 0,
                    "avg_message_length": 0,
                }
            finally:
                db.close()

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
                "cache_info": {
                    "message_cached": True,
                    "analytics_cached": True,
                    "session_updated": True,
                },
            }

            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(session_id)


@app.get("/")
async def root():
    return {"message": "Chat Analytics Backend is running"}


@app.get("/session/{session_id}/stats")
async def get_session_stats_endpoint(session_id: str, db: Session = Depends(get_db)):
    stats = session_service.get_session_analytics(session_id)
    return {"session_id": session_id, "stats": stats}


@app.get("/session/{session_id}/messages")
async def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """Get session messages with optional caching"""
    try:
        # Try to get from cache first using something like this
        # cached_messages = message_cache_service.method() # call the method from the service

        # Fallback to database
        messages = (
            db.query(MessageModel)
            .filter(MessageModel.session_id == session_id)
            .order_by(MessageModel.timestamp.desc())
            .limit(50)
            .all()
        )

        # Convert to dict format and cache
        message_list = []
        for msg in messages:
            message_data = {
                "id": msg.id,
                "content": msg.content,
                "word_count": msg.word_count,
                "char_count": msg.char_count,
                "sentence_count": msg.sentence_count,
                "is_question": msg.is_question,
                "sentiment": msg.sentiment,
                "timestamp": msg.timestamp.isoformat(),
            }
            message_list.append(message_data)

        return {
            "session_id": session_id,
            "messages": message_list,
            "source": "database",
            "cached_count": len(message_list),
        }

    except Exception as e:
        logger.error(f"Error getting session messages for {session_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving messages: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
