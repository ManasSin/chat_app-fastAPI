from services import (
    get_sentiment_analytics,
    session_service,
    message_cache_service,
    redis_service,
)
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from models.models import Session as SessionModel


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
