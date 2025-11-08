"""Settings API routes."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.mock_data import MOCK_SETTINGS
from app.api.schemas import SettingsUpdate
from app.middleware.auth import get_current_user
from app.models import User

router = APIRouter()


@router.get("")
def get_settings(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Get all user settings."""
    return MOCK_SETTINGS


@router.patch("", status_code=status.HTTP_200_OK)
def update_settings(
    settings_update: SettingsUpdate,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Update user settings (specific section)."""
    valid_sections = ["preferences", "notifications", "privacy", "ai", "display", "security"]
    
    if settings_update.section not in valid_sections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid section. Must be one of: {', '.join(valid_sections)}",
        )
    
    # Update the settings section
    # In real implementation, this would update the database
    # For mock, we'll update the in-memory data
    
    if settings_update.section == "preferences":
        # Handle nested preferences structure
        for subsection, values in settings_update.data.items():
            if subsection in MOCK_SETTINGS["preferences"]:
                MOCK_SETTINGS["preferences"][subsection].update(values)
    else:
        # For account, connected_accounts, security sections
        if settings_update.section in MOCK_SETTINGS:
            MOCK_SETTINGS[settings_update.section].update(settings_update.data)
    
    return {
        "message": f"Settings updated successfully",
        "section": settings_update.section,
        "updated_settings": MOCK_SETTINGS,
    }

