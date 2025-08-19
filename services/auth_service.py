from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
import jwt
from core.config import settings
from db.db import SessionLocal
from models.models import UserModel
import uuid
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt, int((expire - datetime.now(timezone.utc)).total_seconds())


class AuthService:
    def __init__(self):
        self.db_session = SessionLocal

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def register_user(
        self, name: Optional[str], email: str, password: str
    ) -> Optional[UserModel]:
        db = self.db_session()
        try:
            existing = db.query(UserModel).filter(UserModel.email == email).first()
            if existing:
                logger.info(f"Attempt to register existing email: {email}")
                return None

            user = UserModel(
                id=str(uuid.uuid4()),
                name=name,
                email=email,
                password=self._hash_password(password),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error registering user: {e}")
            return None
        finally:
            db.close()

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        db = self.db_session()
        try:
            user = db.query(UserModel).filter(UserModel.email == email).first()
            if not user:
                return None
            if not self._verify_password(password, user.password):
                return None
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
        finally:
            db.close()

    def create_token_for_user(self, user: UserModel):
        payload = {"sub": user.id, "email": user.email}
        token, expires_in = create_access_token(payload)
        return token, expires_in

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            decoded = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            return decoded
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except Exception as e:
            logger.warning(f"Token invalid: {e}")
            return None


auth_service = AuthService()
