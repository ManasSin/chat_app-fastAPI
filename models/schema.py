from pydantic import BaseModel
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


class Session(BaseModel):
    id: str
    total_messages: int
    total_words: int
    questions_asked: int
    total_positive_messages: int
    total_negative_messages: int
    total_neutral_messages: int
    created_at: datetime
    last_updated: datetime


class User(BaseModel):
    id: str
    name: str
    email: str
    password: str
    created_at: datetime
    last_updated: datetime


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
