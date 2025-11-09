"""Group task coordination agent."""
from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any, Iterable, Optional

from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv
from loguru import logger

PROMPT_TEMPLATE = """\
You are Lattice — a friendly group finance & task co-pilot for a chat of friends or teammates.
Keep the conversation natural while quietly doing the math and logistics: split costs, suggest fair shares, decide if the group should buy something now or later, and manage lightweight follow-ups (reminders, who’s bringing what, settle-ups).

TOOLS YOU CAN USE
- Brave Search MCP to check quick price/availability/trend signals for any items in question.

INFORMATION YOU HAVE
- Today (ISO): {today}
- Group name: {group_name}
- Members (with optional budgets/notes): {group_members}
- Currency: {currency}
- Group default rules (if any): {group_rules}
- Group expense history (paid, participants, notes): {group_history}
- Raw context dump (debug): {context_dump}
- User message: {user_message}

PRIMARY INTENTS YOU HANDLE (infer from the chat)
1) Split this cost — “Split {{amount}} among {{participants}} people” (or a subset of members).
2) Is this a good group purchase? (e.g., “Should we buy a projector for the Airbnb?”)
3) Light group tasking: reminders, checklists, who’s bringing what, RSVPs, deadlines.
4) Settle up: compute net balances and propose the fewest transactions to get even.

CONVERSATION STYLE
- Be warm, concise, and collaborative. Offer options instead of rigid instructions.
- Explain the math in one or two clear lines; show a tiny table only if it helps.
- Ask at most one clarifying question if it blocks correctness. Otherwise make a reasonable default and say so.
- Use polite confirmations before any payment or data-sensitive action.
- Avoid strict schemas/JSON. Speak naturally.

HOW TO SPLIT COSTS (default behaviour — adjust if group rules override)
- Equal split: total ÷ participants actually involved.
- Weighted split (if requested): by usage, nights stayed, portion size, or custom weights.
- Taxes/fees/tip: allocate proportionally unless group rules say otherwise.
- Rounding: default to cents; if asked, round to the nearest dollar and note the adjustment.
- Late joiners / non-participants: only charge participants who benefited.
- Multi-currency: detect and gently warn; suggest agreeing on one currency or using today’s rate.

GROUP PURCHASE EVALUATION (buy now vs wait)
- Briefly scan price/availability via Brave Search MCP if helpful (e.g. “best time to buy ___”, “average resale price ___”).
- Consider group context: current shared spend, member budgets (if provided), trip timing, urgency, scarcity.
- Give a simple call: “Buy now”, “Wait a bit”, or “Skip”, with one-line reasoning and a practical next step (set a price watch, pick a cap, list alternatives).

SETTLE-UP FLOW
- Compute each member’s net balance from the history: paid minus owed.
- Propose a minimal set of transfers (debt simplification).
- Offer to start a secure settle-up flow (Knot) only after explicit consent.
- Provide simple instructions or links the group can act on.

LIGHT TASKS YOU CAN MANAGE
- Create quick checklists (“Who’s bringing snacks, HDMI, power strip?”).
- Collect RSVPs or headcount and store the list inline.
- Set gentle reminders (“Ping us Friday 6pm to buy tickets if under $X”).
- Track decisions and next steps at the end of your message.

EDGE CASES & POLICIES
- If info is missing, state your assumption and proceed (“Assuming all {participant_hint} are in; shout if not.”).
- If conflicts arise (someone opted out), recalc immediately and show the new amounts.
- Don’t expose sensitive details; keep card numbers and private data out of chat.
- Be consent-first. Never trigger payments or share personal info without explicit okay.

OUTPUT STYLE (examples, not strict)
- Splits: “Total {amount_hint} ÷ {participant_hint} = ${per_person}. With tip, it’s about ${per_person_tip}. I assumed everyone listed; say ‘remove Alex’ to recalc.”
- Purchases: “I’d wait a bit. Prices for ___ dip mid-week, and we’re over our informal cap. Want me to remind you if it drops under $___?”
- Settle-ups: “To get even: Sam → Priya $24, Ken → Dani $18.”

Do not promise future memory; just summarise decisions and next steps clearly.
Now respond conversationally to the current group message with these guidelines."""


def _serialise(value: Any) -> str:
    if value in (None, "", [], {}):
        return "Not provided."
    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except TypeError:
        return str(value)


def _format_members(members: Iterable[dict[str, Any]]) -> str:
    formatted = []
    for member in members or []:
        name = member.get("name") or member.get("display_name") or "Member"
        role = member.get("role")
        budget = member.get("budget")
        notes = member.get("notes")
        details = []
        if role:
            details.append(f"role: {role}")
        if budget is not None:
            details.append(f"budget: {budget}")
        if notes:
            details.append(f"notes: {notes}")
        if details:
            formatted.append(f"{name} ({', '.join(details)})")
        else:
            formatted.append(name)
    if not formatted:
        return "No members listed yet."
    return ", ".join(formatted)


def _extract_amount(text: str) -> float | None:
    if not text:
        return None
    match = re.search(r"(?:\$|usd|\b)(\d+(?:\.\d{1,2})?)", text.replace(",", ""), re.IGNORECASE)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _coerce_int(value: Any) -> Optional[int]:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return int(stripped)
    return None


async def run_group_task_agent(
    group_context: dict[str, Any],
    user_query: str,
    today: str,
) -> str:
    """Coordinate a group expense or planning request via Dedalus."""
    group_context = group_context or {}
    members = group_context.get("members") or []
    participants_count = len(members)
    if participants_count == 0:
        participants_count = _coerce_int(group_context.get("participant_count")) or 0
    amount_value = _extract_amount(user_query)

    load_dotenv()
    api_key = os.getenv("DEDALUS_API_KEY")
    base_url = os.getenv("DEDALUS_BASE_URL")
    if not api_key:
        logger.warning("DEDALUS_API_KEY not set; group task agent returning fallback.")
        if amount_value is not None and participants_count:
            try:
                per_person = amount_value / float(participants_count)
            except ZeroDivisionError:
                per_person = None
        else:
            per_person = None

        members_list = members if members else [{"name": "Member 1"}, {"name": "Member 2"}]
        split_lines = []
        for member in members_list:
            name = member.get("name") or "Member"
            if per_person is not None:
                split_lines.append(f"- {name}: ${per_person:0.2f}")
            else:
                split_lines.append(f"- {name}: amount TBD")
        split_hint = "\n".join(split_lines)
        if not split_hint:
            split_hint = "- Add members so I can help divide the total."
        amount_hint = f"${amount_value:0.2f}" if amount_value is not None else "the total amount"

        return (
            f"**Task Summary:** We’ll sort out the split once the advisor service is configured.\n"
            f"**Suggested Split:**\n{split_hint}\n"
            f"**Next Step:** Configure the Dedalus API key so I can finalise the math for {amount_hint}.\n"
            "**Notes:** I’ll then divide it instantly and track any follow-ups."
        )

    group_name = group_context.get("name") or group_context.get("title") or "Your group chat"
    currency = group_context.get("currency") or group_context.get("default_currency") or "USD"
    group_rules = group_context.get("rules") or group_context.get("policies") or "No specific rules noted."
    group_history = (
        group_context.get("history")
        or group_context.get("expenses")
        or group_context.get("recent_transactions")
        or "No past expenses recorded."
    )
    context_dump = _serialise(group_context)
    group_rules_str = _serialise(group_rules)
    group_history_str = _serialise(group_history)
    members_str = _format_members(members)
    participant_hint = (
        f"{participants_count} members"
        if participants_count
        else "everyone involved"
    )
    amount_hint = f"${amount_value:0.2f}" if amount_value is not None else "the amount mentioned"
    per_person = (
        f"{amount_value / participants_count:.2f}"
        if amount_value is not None and isinstance(participants_count, int) and participants_count > 0
        else "calculated after confirming participants"
    )
    per_person_tip = (
        f"{(amount_value * 1.15) / participants_count:.2f}"
        if (
            amount_value is not None
            and isinstance(participants_count, int)
            and participants_count > 0
        )
        else "depends on final tip"
    )

    client_options: dict[str, Any] = {"api_key": api_key}
    if base_url:
        client_options["base_url"] = base_url
    client = AsyncDedalus(**client_options)
    runner = DedalusRunner(client)

    prompt = PROMPT_TEMPLATE.format(
        today=today,
        group_name=group_name,
        group_members=members_str,
        currency=currency,
        group_rules=group_rules_str,
        group_history=group_history_str,
        context_dump=context_dump,
        user_message=user_query,
        participant_hint=participant_hint,
        amount_hint=amount_hint,
        per_person=per_person,
        per_person_tip=per_person_tip,
    )

    result = await runner.run(
        input=prompt,
        model="openai/gpt-4.1",
    )

    return result.final_output


def run_group_task_agent_sync(
    group_context: dict[str, Any],
    user_query: str,
    today: str,
) -> str:
    """Synchronous helper."""
    load_dotenv()
    api_key = os.getenv("DEDALUS_API_KEY")
    if not api_key:
        logger.warning("DEDALUS_API_KEY not set; group task agent returning fallback.")
        return "I’ll help with the split once the advisor service is configured."
    try:
        return asyncio.run(
            run_group_task_agent(
                group_context=group_context,
                user_query=user_query,
                today=today,
            )
        )
    except Exception as exc:
        logger.error("Group task agent failed: %s", exc)
        return "I couldn’t organise that split right now. Please try again shortly."


if __name__ == "__main__":
    demo_group = {
        "members": [
            {"name": "Alice Demo"},
            {"name": "Bob Test"},
            {"name": "Charlie Sample"},
        ],
        "balances": {"Alice Demo": 0, "Bob Test": 0, "Charlie Sample": 0},
    }
    demo_output = run_group_task_agent_sync(
        group_context=demo_group,
        user_query="Split $120 dinner evenly please.",
        today="2025-11-09",
    )
    print("\nGroup Task Agent Result:\n")
    print(demo_output)

