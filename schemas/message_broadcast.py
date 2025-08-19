from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime


class BroadcastMessage(BaseModel):
    id: str
    session_id: str
    content: str
    analytics: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    sender_id: Optional[str] = None
