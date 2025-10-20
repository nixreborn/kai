"""Pydantic schemas for authentication."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """User registration request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """User login request schema."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema for JWT payload."""

    user_id: UUID | None = None


class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response schema."""

    message: str


class PasswordChange(BaseModel):
    """Password change request schema."""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
