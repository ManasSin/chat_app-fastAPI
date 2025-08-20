from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
import logging

from controllers.websocket_controller import handle_websocket_message
from services.message_validator import MessageValidator
from services import session_service, auth_service
from db.db import get_db
from schemas.auth import UserCreate, UserLogin, Token, UserOut
from utils import websocket_utils as manager
from models.models import MessageModel
from middleware.auth_middleware import AuthMiddleware
from utils.api_response import success, error

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/chat/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    token = None
    if "token" in websocket.query_params:
        token = websocket.query_params.get("token")
    else:
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

    user = None
    if token:
        decoded = auth_service.verify_token(token)
        if decoded and decoded.get("sub"):
            user_id = decoded.get("sub")
            session_service.create_session(user_id=user_id)
            user = user_id

    session_data = session_service.get_session(session_id)
    if not session_data:
        session_data = session_service.create_session()
        logger.info(f"Created new session for WebSocket: {session_id}")

    await manager.connect(websocket, session_id)

    try:
        while True:
            data = await websocket.receive_text()

            is_valid, validated_data, error_message = MessageValidator.validate_message(
                data
            )
            if not is_valid:
                error_response = {
                    "type": "error",
                    "error": error_message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await websocket.send_text(json.dumps(error_response))
                continue

            content = validated_data.message

            response = handle_websocket_message(content)

            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        manager.disconnect_websocket(websocket, session_id)
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect_websocket(websocket, session_id)


@router.get("/")
async def root():
    return success({"message": "Chat Analytics Backend is running"}, message="OK")


@router.get("/session/{session_id}/stats", dependencies=[Depends(AuthMiddleware)])
async def get_session_stats_endpoint(session_id: str, db: Session = Depends(get_db)):
    stats = session_service.get_session_analytics(session_id)
    return success(
        {"session_id": session_id, "stats": stats}, message="Session stats retrieved"
    )


@router.get("/session/{session_id}/messages", dependencies=[Depends(AuthMiddleware)])
async def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    try:
        messages = (
            db.query(MessageModel)
            .filter(MessageModel.session_id == session_id)
            .order_by(MessageModel.timestamp.desc())
            .limit(50)
            .all()
        )

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

        return success(
            {
                "session_id": session_id,
                "messages": message_list,
                "source": "database",
                "cached_count": len(message_list),
            },
            message="Messages retrieved",
        )

    except Exception as e:
        logger.error(f"Error getting session messages for {session_id}: {e}")
        return error("Error retrieving messages", status_code=500, details=str(e))


@router.post(
    "/auth/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_in: UserCreate):
    user = auth_service.register_user(user_in.name, user_in.email, user_in.password)
    if not user:
        return error("User already exists or could not be created", status_code=400)
    return success(
        UserOut.from_orm(user).dict(),
        message="User created",
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/auth/login", response_model=Token)
async def login(user_in: UserLogin):
    user = auth_service.authenticate_user(user_in.email, user_in.password)
    if not user:
        return error("Incorrect email or password", status_code=401)
    token, expires_in = auth_service.create_token_for_user(user)
    return success(
        {"access_token": token, "token_type": "bearer", "expires_in": expires_in},
        message="Login successful",
    )
