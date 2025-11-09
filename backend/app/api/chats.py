"""Chat API routes."""
from datetime import datetime
from pathlib import Path
import sys
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.mock_data import MOCK_CHATS, MOCK_MESSAGES
from app.api.schemas import MessageCreate, MessageResponse, MessageSendResponse
from app.middleware.auth import get_current_user
from app.models import User
from app.utils.transactions_loader import load_user_transactions

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from individual_agent import run_individual_agent

router = APIRouter()

# In-memory counter for new message IDs
_message_id_counter = 100


@router.get("")
def get_chats(current_user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    """Get all chats for the current user."""
    # In mock mode, return all chats
    # In real mode, filter by user_id
    return MOCK_CHATS


@router.get("/{chat_id}")
def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get a specific chat with its messages."""
    # Find chat
    chat = next((c for c in MOCK_CHATS if c["id"] == chat_id), None)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    
    # Get messages for this chat
    messages = MOCK_MESSAGES.get(chat_id, [])
    
    return {
        **chat,
        "messages": messages,
    }


@router.post("/{chat_id}/messages", response_model=MessageSendResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    chat_id: int,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Create a new message in a chat (user or AI)."""
    global _message_id_counter
    
    # Check if chat exists
    chat = next((c for c in MOCK_CHATS if c["id"] == chat_id), None)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    
    # Create new message
    new_message = {
        "id": _message_id_counter,
        "chat_id": chat_id,
        "sender_id": current_user.id if message.sender_type == "user" else None,
        "sender_type": message.sender_type,
        "content": message.content,
        "thinking": [],
        "action": None,
        "drawer_data": None,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    _message_id_counter += 1
    
    # Add to mock messages
    if chat_id not in MOCK_MESSAGES:
        MOCK_MESSAGES[chat_id] = []
    MOCK_MESSAGES[chat_id].append(new_message)
    
    # If user message, optionally invoke the advisor agent
    if message.sender_type == "user":
        content = message.content.strip()
        content_lower = content.lower()
        trigger = "@advisor"
        if content_lower.startswith(trigger):
            agent_output = None
            ai_message: MessageResponse | None = None

            user_query = content[len(trigger):].strip()

            if not user_query:
                agent_output = "Hi there! Add a question after `@advisor` so I know how to help. 🙂"
            else:
                try:
                    logger.info(
                        "AGENT RUN: invoking individual agent for user %s with message %s",
                        current_user.id,
                        user_query,
                    )
                    mock_purchases = load_user_transactions(current_user.id)
                    today_str = datetime.utcnow().date().isoformat()
                    agent_output = await run_individual_agent(
                        mock_purchases=mock_purchases,
                        user_query=user_query,
                        today=today_str,
                    )
                except Exception as exc:
                    logger.exception(
                        "Failed to run individual agent for user %s: %s",
                        current_user.id,
                        exc,
                    )
                    agent_output = (
                        "I ran into an issue generating a personalized recommendation. "
                        "Please try again later."
                    )

            ai_response = {
                "id": _message_id_counter,
                "chat_id": chat_id,
                "sender_id": None,
                "sender_type": "ai",
                "content": agent_output,
                "thinking": [],
                "action": None,
                "drawer_data": None,
                "created_at": datetime.utcnow().isoformat(),
            }
            _message_id_counter += 1
            MOCK_MESSAGES[chat_id].append(ai_response)
            ai_message = MessageResponse(**ai_response)
        
            return MessageSendResponse(
                user_message=MessageResponse(**new_message),
                ai_message=ai_message,
            )

    return MessageSendResponse(
        user_message=MessageResponse(**new_message),
        ai_message=None,
    )

