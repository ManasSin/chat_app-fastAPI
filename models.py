# from pydantic import BaseModel
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Message(Base):
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

class Session(Base):
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


SQLALCHEMY_DATABASE_URL = "sqlite:///./chat_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()