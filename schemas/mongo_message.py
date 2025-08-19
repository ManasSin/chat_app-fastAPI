from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class MongoMessage(BaseModel):
    message_id: str = Field(..., alias="id")
    session_id: str
    content: str
    analytics: Optional[Dict[str, Any]] = None
    sender_id: Optional[str] = None
    created_at: Optional[datetime] = None
    raw: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
