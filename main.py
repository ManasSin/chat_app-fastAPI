from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
from typing import Dict
import uvicorn

from models import Message, Session, engine, Base, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chat Analytics Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def process_message(content: str):
    word_count = len(content.split())
    char_count = len(content)
    sentence_count = content.count('.') + content.count('?') + content.count('!')

    question_words = ['what', 'how', 'why', 'when', 'where', 'who']
    is_question = '?' in content or any(
        content.lower().startswith(word) for word in question_words
    )

    positive_words = ['good', 'great', 'excellent', 'love', 'like', 'happy', 'awesome']
    negative_words = ['bad', 'terrible', 'hate', 'sad', 'angry', 'awful', 'horrible']

    positive_count = sum(1 for word in positive_words if word in content.lower())
    negative_count = sum(1 for word in negative_words if word in content.lower())

    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "word_count": word_count,
        "char_count": char_count,
        "session_count": sentence_count,
        "is_question": is_question,
        "sentiment": sentiment,
        "timestamp": datetime.now().isoformat()
    }

def get_or_create_session(db: Session, session_id: str):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        session = Session(id=session_id)
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
    session.last_updated = datetime.now(timezone.utc)
    db.commit()
    return session

def get_session_stats(db: Session, session_id: str):
    session = get_or_create_session(db, session_id)
    avg_message_length = session.total_words / session.total_messages if session.total_messages > 0 else 0
 
    return {
        "total_messages": session.total_messages,
        "total_words": session.total_words,
        "questions_asked": session.questions_asked,
        "avg_message_length": round(avg_message_length, 1)
    }

@app.websocket("/ws/chat/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
 
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            content = message_data.get("content", "")
 
            analytics = process_message(content)

            db = SessionLocal()
            try:
                message = Message(
                    session_id=session_id,
                    content=content,
                    word_count=analytics["word_count"],
                    char_count=analytics["char_count"],
                    sentence_count=analytics["session_count"],
                    is_question=analytics["is_question"],
                    sentiment=analytics["sentiment"]
                )
                db.add(message)
 
                session_stats = update_session_stats(db, session_id, analytics)
 
                db.commit()

            except Exception as e:
                db.rollback()
                print(f"Database error: {e}")
                session_stats = {"error": str(e), "total_messages": 0, "total_words": 0, "questions_asked": 0, "avg_message_length": 0}
            finally:
                db.close()
 
            response = {
                "type": "message_response",
                "original_message": content,
                "echo": f"You said: {content}",
                "analytics": {
                    "word_count": analytics["word_count"],
                    "char_count": analytics["char_count"],
                    "sentence_count": analytics["session_count"],
                    "is_question": analytics["is_question"],
                    "sentiment": analytics["sentiment"]
                },
                "session_stats": session_stats
            }
 
            await websocket.send_text(json.dumps(response))
 
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(session_id)

@app.get("/")
async def root():
    return {"message": "Chat Analytics Backend is running"}

@app.get("/session/{session_id}/stats")
async def get_session_stats_endpoint(session_id: str, db: Session = Depends(get_db)):
    stats = get_session_stats(db, session_id)
    return {"session_id": session_id, "stats": stats}

@app.get("/session/{session_id}/messages")
async def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp.desc()).all()
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": msg.id,
                "content": msg.content,
                "word_count": msg.word_count,
                "char_count": msg.char_count,
                "sentence_count": msg.sentence_count,
                "is_question": msg.is_question,
                "sentiment": msg.sentiment,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
