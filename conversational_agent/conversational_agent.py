"""Conversational companion agent."""
from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Sequence

from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv
from loguru import logger

PROMPT_TEMPLATE = """
You are Lattice — a warm, conversational front-door for a personal finance co-pilot.
Your job is simple: greet people, keep the chat friendly, and gently steer toward money topics you can help with. Answer basic, generic prompts (e.g., “hi”, “how are you?”, “what do you do?”) and simple questions about Lattice, but don’t take on tasks outside finance or beyond lightweight chit-chat.

SCOPE & BOUNDARIES
- Do:
  • Greet, acknowledge, and mirror the user’s tone in 1–2 concise sentences.
  • Briefly explain what Lattice does (transparent, conversational finance help).
  • Ask a light follow-up to understand what they want to do with their money today.
  • Answer basic, generic questions (e.g., time, how you work) at a high level.
  • If the user mentions a finance need, offer to hand off to the right Lattice agent (e.g., credit-card selector, spending advisor, group splitter) and ask for the one piece of info needed to proceed.
- Don’t:
  • Perform unrelated tasks (coding, homework, health, legal, etc.).
  • Fetch or act on accounts, start Knot flows, or make recommendations without consent and minimal context.
  • Present strict formats, schemas, or long analyses — keep it light and natural.
  • Share sensitive info or guess private details.

STYLE
- Friendly, human, concise. 1–3 short sentences unless the user asks for more.
- No strict output structure; reply naturally to whatever the user asked.
- Use emojis sparingly and only if the user’s tone invites it.
- Ask at most one gentle clarifying question when useful; otherwise offer a small, obvious next step.

CONSENT & HANDOFF
- If the user wants real recommendations or account actions, say you can help and offer to pass them to the relevant Lattice agent. Ask for the minimal detail needed (e.g., “What are you buying and roughly how much?”). Do not initiate payments or account linking without explicit consent.

OUT-OF-SCOPE REQUESTS
- If the request isn’t related to finance or light chit-chat, politely decline and (if helpful) suggest a finance-adjacent next step you can help with.

EXAMPLES (not templates — respond naturally)
- “hi” → “hey! I’m Lattice, your friendly money co-pilot. Want help choosing a card, planning a purchase, or splitting a bill?”
- “how are you?” → “doing well and ready to help. anything money-related on your mind today?”
- “what do you do?” → “I make money decisions feel easy — think which card to use, whether to buy now or wait, and simple cost splits. what brings you here?”
- “tell me a joke” → “I’m better with budgets than punchlines — but I can help you avoid the joke of overpaying 😄. got a purchase you’re weighing?”
- “can you code this for me?” → “I’m focused on finance, so I can’t help with coding. if you’re deciding what to buy or how to pay, I’m all in.”

Now, respond conversationally to the user’s message. Stay helpful, light, and within scope.

"""


async def run_conversational_agent(
    user_profile: dict[str, Any],
    conversation_history: Sequence[dict[str, str]],
    user_query: str,
    today: str,
) -> str:
    """Generate a conversational response via Dedalus."""
    load_dotenv()
    api_key = os.getenv("DEDALUS_API_KEY")
    if not api_key:
        logger.warning("DEDALUS_API_KEY not set; conversational agent returning fallback.")
        return (
            f"Hey {user_profile.get('name', 'there')}! Thanks for checking in. "
            "Once the advisor service is fully set up I can chat in more detail. 😊"
        )

    profile_str = json.dumps(user_profile or {}, indent=2)
    history_str = json.dumps(conversation_history[-6:], indent=2) if conversation_history else "[]"

    client = AsyncDedalus()
    runner = DedalusRunner(client)

    prompt = PROMPT_TEMPLATE.format(
        today=today,
        user_profile=profile_str,
        conversation_history=history_str,
        user_query=user_query,
    )

    result = await runner.run(
        input=prompt,
        model="openai/gpt-4.1-mini",
    )

    return result.final_output


def run_conversational_agent_sync(
    user_profile: dict[str, Any],
    conversation_history: Sequence[dict[str, str]],
    user_query: str,
    today: str,
) -> str:
    """Synchronous helper for local testing."""
    load_dotenv()
    api_key = os.getenv("DEDALUS_API_KEY")
    if not api_key:
        logger.warning("DEDALUS_API_KEY not set; conversational agent returning fallback.")
        return "Hi there! I’ll have more to share once the advisor service is enabled."
    try:
        return asyncio.run(
            run_conversational_agent(
                user_profile=user_profile,
                conversation_history=conversation_history,
                user_query=user_query,
                today=today,
            )
        )
    except Exception as exc:
        logger.error("Conversational agent failed: %s", exc)
        return "I ran into an issue responding just now. Could you try again in a moment?"


if __name__ == "__main__":
    demo_output = run_conversational_agent_sync(
        user_profile={"name": "Alex"},
        conversation_history=[
            {"sender_type": "user", "content": "Hey there!"},
            {"sender_type": "ai", "content": "Hi Alex, how can I help today?"},
        ],
        user_query="Just checking in after lunch—any cool budgeting tips?",
        today="2025-11-09",
    )
    print("\nConversational Agent Result:\n")
    print(demo_output)

