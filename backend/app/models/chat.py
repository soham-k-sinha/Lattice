"""Chat models."""
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin


class ChatType(str, enum.Enum):
    """Chat type enum."""

    SOLO = "solo"
    GROUP = "group"


class Chat(Base, TimestampMixin):
    """Chat model representing conversation threads."""

    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ChatType), nullable=False, default=ChatType.SOLO)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="owned_chats", foreign_keys=[owner_id])
    members = relationship("ChatMember", back_populates="chat", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    group_context = relationship(
        "GroupContext",
        back_populates="chat",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, type={self.type}, title={self.title})>"


class ChatMemberRole(str, enum.Enum):
    """Chat member role enum."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class ChatMember(Base, TimestampMixin):
    """ChatMember model representing users in a chat."""

    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(Enum(ChatMemberRole), default=ChatMemberRole.MEMBER, nullable=False)

    # Relationships
    chat = relationship("Chat", back_populates="members")
    user = relationship("User", back_populates="chat_memberships")

    def __repr__(self) -> str:
        return f"<ChatMember(chat_id={self.chat_id}, user_id={self.user_id}, role={self.role})>"

