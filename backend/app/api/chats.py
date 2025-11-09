"""Chat API routes."""
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.mock_data import MOCK_CHATS, MOCK_MESSAGES, MOCK_GROUPS
from app.api.schemas import MessageCreate, MessageResponse, MessageSendResponse
from app.middleware.auth import get_current_user
from app.models import User
from app.utils.transactions_loader import load_user_transactions

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from individual_agent import run_individual_agent
from credit_score_agent.credit_score_agent import CREDIT_CARD_KNOWLEDGE, run_credit_score_agent
from conversational_agent.conversational_agent import run_conversational_agent
from group_task_agent.group_task_agent import run_group_task_agent
from decider_agent.decider_agent import run_decider_agent

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
    
    if message.sender_type == "user":
        content = message.content.strip()
        trigger = "@advisor"
        if content.lower().startswith(trigger):
            user_query = content[len(trigger):].strip()
            today_str = datetime.utcnow().date().isoformat()

            if not user_query:
                agent_output = "Hi there! Add a question after `@advisor` so I know how to help. 🙂"
            else:
                chat_type = chat.get("type", "solo")
                group_data = next((g for g in MOCK_GROUPS if g["id"] == chat_id), None)
                recent_history = [
                    {"sender_type": entry["sender_type"], "content": entry["content"]}
                    for entry in MOCK_MESSAGES.get(chat_id, [])[-10:]
                ]

                chat_context = {
                    "chat_id": chat_id,
                    "chat_type": chat_type,
                    "chat_title": chat.get("title"),
                    "member_count": chat.get("member_count"),
                }
                if group_data:
                    chat_context["members"] = group_data.get("members", [])

                decider_raw = await run_decider_agent(
                    user_query=user_query,
                    chat_context=chat_context,
                    today=today_str,
                )

                digit_payload_map = {
                    "1": {"agents": ["individual"], "reason": "router_individual"},
                    "2": {"agents": ["credit_score"], "reason": "router_credit"},
                    "3": {"agents": ["group_task"], "reason": "router_group"},
                    "4": {"agents": ["conversational"], "reason": "router_conversational"},
                }

                decider_payload: dict[str, Any]
                trimmed = decider_raw.strip() if isinstance(decider_raw, str) else str(decider_raw)
                if trimmed in digit_payload_map:
                    decider_payload = digit_payload_map[trimmed]
                else:
                    try:
                        decider_payload = json.loads(trimmed)
                        if not isinstance(decider_payload, dict):
                            raise TypeError("Decider payload must be dict-like")
                    except Exception:
                        logger.warning("Decider returned non-JSON payload: %s", decider_raw)
                        decider_payload = {"agents": ["conversational"], "reason": "parse_error"}

                agent_keys = decider_payload.get("agents") or ["conversational"]
                reason = decider_payload.get("reason", "not provided")
                logger.info(
                    "Decider selected %s for chat %s (reason: %s)",
                    agent_keys,
                    chat_id,
                    reason,
                )

                valid_agents = {"individual", "credit_score", "group_task", "conversational"}
                results: list[tuple[str, str]] = []

                for key in agent_keys[:3]:
                    if key not in valid_agents:
                        continue
                    try:
                        logger.info(f"KEY: {key}")
                        if key == "individual":
                            mock_purchases = load_user_transactions(current_user.id)
                            output = await run_individual_agent(
                                mock_purchases=mock_purchases,
                                user_query=user_query,
                                today=today_str,
                            )
                        elif key == "credit_score":
                            output = await run_credit_score_agent(
                                user_cards=CREDIT_CARD_KNOWLEDGE,
                                user_query=user_query,
                                today=today_str,
                            )
                        elif key == "group_task":
                            group_context = {
                                "group": group_data or {},
                                "members": (group_data or {}).get("members", []),
                                "recent_messages": recent_history,
                                "requested_by": {"id": current_user.id, "name": current_user.name},
                            }
                            output = await run_group_task_agent(
                                group_context=group_context,
                                user_query=user_query,
                                today=today_str,
                            )
                        else:  # conversational
                            user_profile = {
                                "id": current_user.id,
                                "name": current_user.name,
                                "email": current_user.email,
                            }
                            output = await run_conversational_agent(
                                user_profile=user_profile,
                                conversation_history=recent_history,
                                user_query=user_query,
                                today=today_str,
                            )

                        results.append((key, output.strip()))
                    except Exception as agent_exc:
                        logger.exception("Agent %s failed: %s", key, agent_exc)
                        results.append((key, "I ran into an issue generating a response. Please try again later."))

                if not results:
                    agent_output = "I couldn't decide which specialist to use. Try rephrasing your request!"
                else:
                    display_names = {
                        "conversational": "Conversational Companion",
                        "individual": "Personal Spending Advisor",
                        "credit_score": "Credit Score Coach",
                        "group_task": "Group Task Assistant",
                    }
                    sections = []
                    for key, text in results:
                        title = display_names.get(key, key.title())
                        sections.append(f"**{title}:**\n{text}")
                    agent_output = "\n\n".join(sections)

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

