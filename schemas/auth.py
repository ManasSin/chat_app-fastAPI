from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import timedelta


class UserCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class TokenData(BaseModel):
    sub: Optional[str] = None


class UserOut(BaseModel):
    id: str
    name: Optional[str]
    email: EmailStr

    class Config:
        orm_mode = True
