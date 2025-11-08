"""User model."""
from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin


class OnboardingStatus(str, enum.Enum):
    """Onboarding status enum."""

    INCOMPLETE = "incomplete"
    COMPLETE = "complete"
    SKIPPED = "skipped"


class User(Base, TimestampMixin):
    """User model representing authenticated users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    onboarding_status = Column(
        Enum(OnboardingStatus),
        default=OnboardingStatus.INCOMPLETE,
        nullable=False,
    )
    preferences = Column(JSONB, default={}, nullable=False)
    auth_provider_id = Column(String, nullable=True)  # For OAuth providers

    # Relationships
    owned_chats = relationship("Chat", back_populates="owner", foreign_keys="Chat.owner_id")
    chat_memberships = relationship("ChatMember", back_populates="user")
    messages = relationship("Message", back_populates="sender")
    linked_accounts = relationship("LinkedAccount", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

