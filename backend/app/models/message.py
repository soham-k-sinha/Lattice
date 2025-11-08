"""Message model."""
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin


class SenderType(str, enum.Enum):
    """Message sender type enum."""

    USER = "user"
    AI = "ai"


class MessageAction(str, enum.Enum):
    """Message action type enum."""

    CARD = "card"
    SPLIT = "split"
    TRACKER = "tracker"
    NONE = "none"


class Message(Base, TimestampMixin):
    """Message model representing chat messages."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    sender_type = Column(Enum(SenderType), nullable=False)
    content = Column(Text, nullable=False)
    thinking = Column(JSONB, default=[], nullable=False)  # Array of thinking steps
    action = Column(Enum(MessageAction), default=MessageAction.NONE, nullable=True)
    drawer_data = Column(JSONB, default={}, nullable=True)  # Context drawer payload

    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, chat_id={self.chat_id}, sender_type={self.sender_type})>"

