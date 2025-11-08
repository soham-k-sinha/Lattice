"""Linked account model."""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class LinkedAccount(Base, TimestampMixin):
    """LinkedAccount model for storing user's connected financial accounts."""

    __tablename__ = "linked_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    institution = Column(String, nullable=False)  # e.g., "Amazon", "DoorDash", "UberEats"
    account_name = Column(String, nullable=False)  # Display name for the account
    permissions = Column(JSONB, default={}, nullable=False)  # Account permissions/scopes
    knot_item_id = Column(String, nullable=True, unique=True, index=True)  # Knot's item ID

    # Relationships
    user = relationship("User", back_populates="linked_accounts")

    def __repr__(self) -> str:
        return f"<LinkedAccount(id={self.id}, institution={self.institution}, user_id={self.user_id})>"

