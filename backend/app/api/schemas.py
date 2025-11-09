"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr


# ============= Auth Schemas =============

class UserSignup(BaseModel):
    """User signup request schema."""
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload data."""
    user_id: int
    email: str


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    name: str
    email: str
    onboarding_status: str
    preferences: dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """Session info response schema."""
    user: UserResponse
    authenticated: bool = True


# ============= Chat Schemas =============

class MessageCreate(BaseModel):
    """Create message request schema."""
    content: str
    sender_type: str = "user"


class MessageResponse(BaseModel):
    """Message response schema."""
    id: int
    chat_id: int
    sender_id: Optional[int]
    sender_type: str
    content: str
    thinking: list[str] = []
    action: Optional[str] = None
    drawer_data: Optional[dict[str, Any]] = None
    created_at: datetime


class MessageSendResponse(BaseModel):
    """Response returned when sending a chat message."""
    user_message: MessageResponse
    ai_message: Optional[MessageResponse] = None


# ============= Group Schemas =============

class GroupCreate(BaseModel):
    """Create group request schema."""
    name: str
    members: list[str]  # List of email addresses


class GroupResponse(BaseModel):
    """Group response schema."""
    id: int
    name: str
    members: list[dict[str, Any]]
    total_spend: float = 0.0
    context: str
    last_activity: datetime


# ============= Settings Schemas =============

class SettingsUpdate(BaseModel):
    """Update settings request schema."""
    section: str  # "preferences", "notifications", etc.
    data: dict[str, Any]

