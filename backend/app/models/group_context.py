"""Group context model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class GroupContext(Base, TimestampMixin):
    """GroupContext model for storing group-level metadata and spend tracking."""

    __tablename__ = "group_contexts"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), unique=True, nullable=False, index=True)
    context_summary = Column(Text, nullable=True)
    total_spend = Column(Float, default=0.0, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    chat = relationship("Chat", back_populates="group_context")

    def __repr__(self) -> str:
        return f"<GroupContext(chat_id={self.chat_id}, total_spend={self.total_spend})>"

