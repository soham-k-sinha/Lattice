"""Decider agent that routes to specialist assistants."""
from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv
from loguru import logger

PROMPT_TEMPLATE = """
You are Lattice — a ROUTER agent. Your ONLY job is to decide which downstream agent should handle the user’s message and output a SINGLE DIGIT with NO other text.

AGENTS (output exactly one of these codes)
1 = Individual Analysis/Search Agent
   - Personal finance for ONE person.
   - “Should I buy … ?”, “Buy now or wait?”, price trends, sentiment, best card to use, rewards, utilization, budget/spend analysis, past purchases from Knot data, personal affordability.
   - Keywords/cues: “I/me/my”, “should I buy”, “buy now or wait”, “which credit card”, “rewards/cashback/points”, “utilization”, “my spending”, “transactions”.

2 = Credit Score Coach
   - Card recommendations, rewards optimisation, credit score strategy.
   - Keywords/cues: “credit score”, “best card”, “cashback”, “points”, “APR”, “signup bonus”.

3 = Group Task Agent
   - Anything for a GROUP: splitting costs, settle-ups, shared purchases, reminders for group actions.
   - “Split $y among x people”, “who owes who”, “we/us/our team”, “should we buy [item] for the trip?”, “plan as a group”.
   - Keywords/cues: “split”, “settle”, “owe”, “per person”, “we/us/our”, “group”, “trip together”, “RSVP”, “reminder for everyone”.
   - If BOTH personal + group are present, prefer 3.

4 = Conversational Companion
   - Greetings, small talk, generic questions, or anything out-of-scope for finance tasks.
   - High-level “what do you do?”, “hello/hi”, casual remarks, or developer/setup questions (APIs, installs) not requesting a money decision.
   - Non-finance requests or unclear intent.

OUTPUT FORMAT (MANDATORY)
- Output ONLY one character: 1 or 2 or 3 or 4.
- No spaces, no punctuation, no words, no code fences, no newline after if possible.

EXAMPLES (for your internal guidance)
- “hi” → 4
- “what do you do?” → 4
- “Should I buy concert tickets for $120?” → 1
- “Which card should I use for Uber Eats?” → 2
- “My spending was high this week—can I afford a new monitor?” → 1
- “Split $240 dinner among 5 (Alice not included)” → 3
- “Who still owes for the Airbnb?” → 3
- “Should we buy a projector for the trip?” → 3
- “Help me integrate Knot API” → 4
- “We’re three people buying jerseys; good idea?” → 3

Now read the user’s latest message and output exactly one digit: 1, 2, 3, or 4.

METADATA
- Today (ISO): {today}
- Chat context (JSON): {chat_context}
- Latest user message: {user_query}

"""


async def run_decider_agent(
    user_query: str,
    chat_context: dict[str, Any],
    today: str,
) -> str:
    """Return the decider digit output."""
    load_dotenv()
    user_query = (user_query or "").strip()
    chat_context = chat_context or {}

    def _heuristic_route(message: str) -> str | None:
        lowered = message.lower()
        if not lowered:
            return None

        group_keywords = {"split", "settle", "owe", "per person", "we ", " our ", " group", "team", "together", "let's", "lets"}
        credit_keywords = {"credit score", "best card", "cashback", "points", "apr", "reward", "signup bonus"}
        individual_keywords = {
            "should i buy",
            "buy now",
            "buying",
            "afford",
            "my spending",
            "my budget",
            "my transactions",
            "can i buy",
        }

        if any(term in lowered for term in group_keywords):
            return "3"
        if any(term in lowered for term in credit_keywords):
            return "2"
        if any(term in lowered for term in individual_keywords):
            return "1"
        return None

    heuristic_result = _heuristic_route(user_query)
    if heuristic_result:
        return heuristic_result

    if not os.getenv("DEDALUS_API_KEY"):
        logger.warning("DEDALUS_API_KEY not set; decider returning conversational fallback.")
        return "4"

    context_str = json.dumps(chat_context, indent=2)

    client = AsyncDedalus()
    runner = DedalusRunner(client)

    prompt = PROMPT_TEMPLATE.format(
        today=today,
        user_query=user_query,
        chat_context=context_str,
    )

    result = await runner.run(
        input=prompt,
        model="openai/gpt-4.1-mini",
    )

    return result.final_output


def run_decider_agent_sync(
    user_query: str,
    chat_context: dict[str, Any],
    today: str,
) -> str:
    """Synchronous helper."""
    load_dotenv()
    try:
        return asyncio.run(
            run_decider_agent(
                user_query=user_query,
                chat_context=chat_context,
                today=today,
            )
        )
    except Exception as exc:
        logger.error("Decider agent failed: %s", exc)
        return "4"


if __name__ == "__main__":
    demo_context = {"chat_type": "group", "chat_id": 2, "member_count": 3}
    demo_output = run_decider_agent_sync(
        user_query="Let's split the dinner bill evenly please.",
        chat_context=demo_context,
        today="2025-11-09",
    )
    print("\nDecider Agent Result:\n")
    print(demo_output)

