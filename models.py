# from pydantic import BaseModel
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# class Message(BaseModel):
#     id: int
#     session_id: str
#     content: str
#     word_count: int
#     char_count: int
#     sentence_count: int
#     is_question: bool
#     sentiment: str
#     timestamp: datetime

# class Session(BaseModel):
#     id: str
#     created_at: datetime
#     total_messages: int
#     total_words: int
#     questions_count: int
#     last_updated: datetime

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
    __tablename__ = "session"

    id = Column(String, primary_key=True, index=True)
    total_messages = Column(Integer, default=0)
    total_words = Column(Integer, default=0)
    questions_asked = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))


SQLALCHEMY_DATABASE_URL = "sqlite:///./chat_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()