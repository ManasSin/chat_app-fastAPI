from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    content = Column(Text)
    word_count = Column(Integer)
    char_count = Column(Integer)
    sentence_count = Column(Integer)
    is_question = Column(Boolean)
    sentiment = Column(String)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    total_messages = Column(Integer, default=0)
    total_words = Column(Integer, default=0)
    questions_asked = Column(Integer, default=0)
    total_positive_messages = Column(Integer, default=0)
    total_negative_messages = Column(Integer, default=0)
    total_neutral_messages = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))


class UserSessionModel(Base):
    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))


class UserMessageModel(Base):
    __tablename__ = "user_messages"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    message_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))
