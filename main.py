from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from utils import connection_manager as manager
import asyncio
from fastapi.security import OAuth2PasswordBearer


import models.models as models
from db.db import init_db, SessionLocal
from routers.chat import router as chat_router
from core import settings
from services import pubsub_service, persist_service, auth_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database tables
init_db()

app = FastAPI(title="Chat Analytics Backend", version="1.0.0")

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=(["*"]),  # for now, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    try:
        pubsub_service.start_subscriber(loop)
        # start Mongo persist worker as well
        try:
            persist_service.start_persist_worker()
        except Exception:
            logger.exception("Failed to start persist worker")
    except Exception:
        logger.exception("Failed to start pubsub subscriber")


@app.on_event("shutdown")
async def shutdown_event():
    try:
        pubsub_service.stop_subscriber()
        try:
            persist_service.stop_persist_worker()
        except Exception:
            logger.exception("Failed to stop persist worker")
    except Exception:
        logger.exception("Failed to stop pubsub subscriber")


# we can enforce all routes to be protected by default or use a custom middleware
# app.add_middleware(AuthMiddleware)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    decoded = auth_service.verify_token(token)
    if not decoded or not decoded.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    # Fetch user from DB
    db = SessionLocal()
    try:
        user = (
            db.query(models.UserModel)
            .filter(models.UserModel.id == decoded.get("sub"))
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user
    finally:
        db.close()


app.include_router(chat_router)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
