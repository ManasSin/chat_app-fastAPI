from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Message(BaseModel):
    id: int
    session_id: str
    content: str
    word_count: int
    char_count: int
    sentence_count: int
    is_question: bool
    sentiment: str
    timestamp: datetime


class Analytics(BaseModel):
    word_count: int
    char_count: int
    sentence_count: int
    is_question: bool
    sentiment: str


class MessageInput(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    timestamp: Optional[datetime] = None
    client_id: str = Field(...)
    message_type: Optional[str] = Field(default="text", regex="^(text|command|system)$")


class Session(BaseModel):
    session_id: str
    total_messages: int
    total_words: int
    questions_asked: int
    avg_message_length: float
    total_positive_messages: int
    total_negative_messages: int
    total_neutral_messages: int
    last_activity: datetime


class User(BaseModel):
    id: str
    name: str
    email: str
    password: str
    created_at: datetime
    last_updated: datetime


class MessageResponse(BaseModel):
    type: str = "message_response"
    message_id: str
    original_message: str
    echo: str
    analytics: Analytics
    timestamp: datetime
    session_stats: Session


class UserSession(BaseModel):
    id: str
    user_id: str
    session_id: str
    created_at: datetime
    last_updated: datetime


class UserMessage(BaseModel):
    id: str
    user_id: str
    message_id: str
    # leave for future use
    # media_type : str
    # media_url : str
    created_at: datetime
    last_updated: datetime
