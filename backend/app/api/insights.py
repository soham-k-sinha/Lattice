"""Insights API routes."""
from typing import Any

from fastapi import APIRouter, Depends

from app.api.mock_data import MOCK_INSIGHTS, MOCK_INSIGHTS_SUMMARY
from app.middleware.auth import get_current_user
from app.models import User

router = APIRouter()


@router.get("")
def get_insights(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Get all insights (spending trends, card recommendations, rewards)."""
    return MOCK_INSIGHTS


@router.get("/summary")
def get_insights_summary(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    """Get monthly insights summary text."""
    return {
        "summary": MOCK_INSIGHTS_SUMMARY,
        "month": "November 2025",
        "generated_at": "2025-01-01T00:00:00Z",
    }

