"""Groups API routes."""
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.mock_data import MOCK_CHATS, MOCK_GROUPS, MOCK_MESSAGES
from app.api.schemas import GroupCreate, GroupResponse
from app.middleware.auth import get_current_user
from app.models import User

router = APIRouter()

# In-memory counter for new group IDs
_group_id_counter = 100


@router.get("")
def get_groups(current_user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    """Get all groups for the current user."""
    # In mock mode, return all groups
    # In real mode, filter by user membership
    return MOCK_GROUPS


@router.get("/{group_id}")
def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get a specific group with full details."""
    group = next((g for g in MOCK_GROUPS if g["id"] == group_id), None)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )
    
    return group


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
) -> GroupResponse:
    """Create a new group."""
    global _group_id_counter
    
    # Create members list (owner + invited members)
    members = [
        {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": "owner",
        }
    ]
    
    # Add invited members (in real implementation, would look up by email)
    for i, email in enumerate(group_data.members, start=1):
        if email != current_user.email:  # Don't add owner twice
            members.append({
                "id": 900 + i,  # Mock ID
                "name": email.split("@")[0].title(),
                "email": email,
                "role": "member",
            })
    
    # Create new group
    new_group = {
        "id": _group_id_counter,
        "name": group_data.name,
        "members": members,
        "total_spend": 0.0,
        "context": f"Created by {current_user.name}",
        "last_activity": datetime.utcnow().isoformat(),
    }
    
    _group_id_counter += 1
    
    # Add to mock groups
    MOCK_GROUPS.append(new_group)
    
    # IMPORTANT: Also create a corresponding chat entry so it appears in the sidebar
    new_chat = {
        "id": _group_id_counter - 1,  # Use same ID as group
        "type": "group",
        "owner_id": current_user.id,
        "title": group_data.name,
        "created_at": datetime.utcnow().isoformat(),
        "member_count": len(members),
    }
    MOCK_CHATS.append(new_chat)
    
    # Initialize empty messages list for this chat
    MOCK_MESSAGES[_group_id_counter - 1] = []
    
    return GroupResponse(**new_group)

