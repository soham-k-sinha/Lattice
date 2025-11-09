"""Utilities to run the individual spending advisor agent."""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Optional

from dedalus_labs import AsyncDedalus, DedalusRunner
try:
    from dedalus_labs import APITimeoutError  # type: ignore
except ImportError:  # pragma: no cover - library version without explicit export
    class APITimeoutError(Exception):
        """Fallback timeout error type when dedalus_labs does not expose it."""
        pass
from dotenv import load_dotenv
from loguru import logger


FALLBACK_WINDOW_DAYS = 30
FALLBACK_RECENT_DAYS = 7
DEFAULT_TIMEOUT_SECONDS = 60


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _iter_transactions(mock_purchases: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for payload in (mock_purchases or {}).values():
        transactions = payload.get("transactions") or []
        for tx in transactions:
            yield tx


def _parse_datetime(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _build_deterministic_recommendation(
    mock_purchases: dict[str, Any],
    user_query: str,
    today: str,
) -> str:
    today_dt = _parse_datetime(today) or datetime.now(timezone.utc)
    if today_dt.tzinfo is None:
        today_dt = today_dt.replace(tzinfo=timezone.utc)
    start_30 = today_dt - timedelta(days=FALLBACK_WINDOW_DAYS)
    start_7 = today_dt - timedelta(days=FALLBACK_RECENT_DAYS)

    total_30 = 0.0
    total_7 = 0.0
    merchant_totals: dict[str, float] = {}

    for tx in _iter_transactions(mock_purchases):
        tx_dt = _parse_datetime(tx.get("datetime"))
        if not tx_dt:
            continue
        price = tx.get("price") or {}
        amount = _safe_float(price.get("total")) or sum(
            _safe_float(pm.get("transaction_amount")) for pm in tx.get("payment_methods") or []
        )
        merchant_name = (tx.get("merchant") or {}).get("name") or "Unknown merchant"

        if tx_dt >= start_30:
            total_30 += amount
            merchant_totals[merchant_name] = merchant_totals.get(merchant_name, 0.0) + amount
        if tx_dt >= start_7:
            total_7 += amount

    if merchant_totals:
        top_merchant, top_total = max(merchant_totals.items(), key=lambda item: item[1])
        top_line = f"Top merchant: {top_merchant} (${top_total:,.2f})."
    else:
        top_line = "Top merchant: data not yet available."

    monthly_avg = total_30 / 4 if total_30 else 0.0
    risk_flag = total_7 > (monthly_avg * 1.25) if monthly_avg else total_7 > 400
    risk_line = "Recent spend looks elevated ⚠️" if risk_flag else "Recent spend is within a steady band ✅"

    return (
        f"**Purchase Recommendation:** ⏳ Wait\n"
        f"**Reasoning Summary**\n"
        f"- Spending: ${total_7:,.2f} in the past 7 days, ${total_30:,.2f} over the last 30 days. {top_line}\n"
        "- Market: Check a couple of trusted retailers for up-to-date pricing before committing.\n"
        "- Sentiment: Scan a few recent reviews and forums to make sure there’s no major red flag. 💬\n"
        f"- Budget Check: {risk_line}\n\n"
        "**Confidence:** Medium\n"
        f"**Additional Advice:** Set a maximum price in mind before you shop for “{user_query or 'this purchase'}” and give yourself a 24-hour cool-off window before hitting buy. 🚦"
    )


async def run_individual_agent(
    mock_purchases: dict[str, Any],
    user_query: str,
    today: str,
) -> str:
    """Run the individual agent asynchronously and return the final output text."""
    load_dotenv()
    api_key = os.getenv("DEDALUS_API_KEY")
    if not api_key:
        logger.warning("DEDALUS_API_KEY not set; returning fallback recommendation.")
        return _build_deterministic_recommendation(mock_purchases, user_query, today)

    client_options: dict[str, Any] = {"api_key": api_key}
    base_url = os.getenv("DEDALUS_BASE_URL")
    if base_url:
        client_options["base_url"] = base_url

    timeout_env = os.getenv("DEDALUS_AGENT_TIMEOUT")
    try:
        timeout_seconds = int(timeout_env) if timeout_env else DEFAULT_TIMEOUT_SECONDS
    except ValueError:
        timeout_seconds = DEFAULT_TIMEOUT_SECONDS

    client = AsyncDedalus(**client_options)
    runner = DedalusRunner(client)

    prompt = f"""
You are Lattice — an individual spending advisor agent for one user.
Your job: given the user's purchase question, analyze (1) their recent spending behavior
(from provided transaction history), (2) external price trends via Brave Search MCP, and
(3) public sentiment via Brave Search MCP, then return a clear recommendation:
Buy Now / Wait / Avoid.

You can and should use the MCP tools available to you:
- Brave Search MCP for real-time price / availability / trend signals.

When searching, try queries like (fill in ____ with relevant terms regarding to the user's query):
- "___ price trend 2025"
- "average resale price ___"
- "best time to buy ___ price trend"
- "price drop patterns for ___ near event date"
- "seasonality or demand peaks for ___"

INFORMATION YOU HAVE
--------------------
- Today (ISO): {today}
- User Purchase Query: {user_query}
- Past Purchase History:
{mock_purchases}

WHAT TO DO
----------
A) PERSONAL SPENDING ANALYSIS
  1. Compute total spend in the last 7 days and in the last given amount of days.
  2. Identify top categories by spend over the last given amount of days.
  3. Detect if discretionary spend (shopping, entertainment, food delivery, etc.) is elevated
     compared to the prior weeks in this dataset. If possible, estimate a simple baseline:
     e.g., average weekly spend across the previous 3 weeks vs the most recent week.
  4. Flag risk if recent spend is >= 20% higher than baseline, or if many discretionary purchases
     occurred in the last 7 days.

  👉 **Show your reasoning process about the financial situation.**
     - Explain how you derived the baseline.
     - Explain patterns noticed (e.g., spikes in shopping or entertainment).
     - Walk through the steps you took before concluding.

B) PRICE TREND ANALYSIS (via Brave Search MCP)
  1. Use the Brave Search MCP to check current/historical pricing trends for the item.
  2. Determine if prices are likely to rise, fall, or stay flat in the near term (1–3 weeks).
  3. Note seasonal effects or typical resale dynamics (e.g., ___ prices can drop in the future, or spike after specific events).

  👉 **Show your reasoning for price trend estimation.**
     - Summarize signals you found.
     - Explain why you believe prices are trending a certain direction.
     - If uncertain, describe which factors create uncertainty.

C) PUBLIC SENTIMENT ANALYSIS (via Brave Search MCP)
  1. Query recent public sentiment for the item/product/good in question using query like: "“In the last 30 days, what’s the public sentiment around ___? Look across Reddit, X/Twitter, Trustpilot, and major retailer reviews, and surface the main praises, complaints, and any controversy.”"
  2. Return: polarity (positive/negative/mixed), a normalized score (0–1), and brief evidence (quotes/themes).
  3. Identify if the sentiment suggests high excitement or "cultural moment" scarcity.

  👉 **Show your reasoning for sentiment.**
     - What are people saying, and how strong is the consensus?
     - How does sentiment change your recommendation (e.g., fear-of-missing-out vs. prudent budgeting)?

D) DECISION & EXPLANATION
  Combine spending risk + price trend + public sentiment. Then decide:
    - "Buy Now" if spending risk is low AND prices are stable/increasing OR
      if sentiment is strongly positive and missing the event would likely be a meaningful loss *and*
      the purchase fits a realistic budget.
    - "Wait" if spending risk is moderate OR prices likely to decline OR sentiment is mixed.
    - "Avoid" if spending risk is high OR this would materially exceed a reasonable pattern/budget.

  Be **realistic and human**: if sentiment is strongly positive and the event is rare/meaningful,
  you may say it's okay to spend — but acknowledge trade-offs, budget caps, and alternative options.

OUTPUT FORMAT
-------------
Return a really informative human summary like this (can change format a bit based on what the user has said):

**Purchase Recommendation:** <Buy Now | Wait | Avoid>
**Reasoning Summary:**
- Spending: <1-2 bullet points on weekly/monthly totals and risk>
- Market: <1-2 bullet points on price trend signal and why>
- Sentiment: <1-2 bullets on polarity/strength and implications>
**Confidence Level:** <Low | Medium | High>
**Additional Advice:** <practical tip, alternatives, or timing>

**Financial Reasoning (transparent):**
- <step-by-step notes you used to analyze spend and baseline>

**Market Reasoning (transparent):**
- <step-by-step notes you used to estimate the trend>

**Sentiment Reasoning (transparent):**
- <step-by-step notes you used to interpret public sentiment>

CONSTRAINTS

If you can't find sufficient data to make a confident recommendation, use average price and don't mention that you can't find sufficient data.

Use Brave Search MCP for external signals; don't make heavy assumptions about trends but you can also base some off general knowledge.

Keep the final advice simple, transparent, realistic, and actionable.

Show your step-by-step reasoning for financial analysis, price trend estimation, and sentiment interpretation.

Use a lot of related emojis while explaining your step-by-step reasoning for financial analysis.

Now proceed.
    """

    async def _execute_agent(model: str, use_mcp: bool, timeout_value: int) -> str:
        kwargs: dict[str, Any] = {
            "input": prompt,
            "model": model,
        }
        if use_mcp:
            kwargs["mcp_servers"] = ["windsor/brave-search-mcp"]
        result = await asyncio.wait_for(
            runner.run(**kwargs),
            timeout=timeout_value,
        )
        return result.final_output

    # Attempt 1: full experience (Brave MCP, gpt-5)
    try:
        return await _execute_agent("openai/gpt-5", True, timeout_seconds)
    except (asyncio.TimeoutError, APITimeoutError) as timeout_exc:
        logger.warning(
            "Individual agent primary attempt timed out after %s seconds (%s). Retrying with lighter settings.",
            timeout_seconds,
            timeout_exc,
        )
    except Exception as primary_exc:
        logger.warning(
            "Individual agent primary attempt failed (%s). Retrying with lighter settings.",
            primary_exc,
        )

    # Attempt 2: lighter model, no MCP tools (faster & more reliable)
    secondary_timeout = max(timeout_seconds // 2, 15)
    try:
        return await _execute_agent("openai/gpt-4.1-mini", False, secondary_timeout)
    except (asyncio.TimeoutError, APITimeoutError) as timeout_exc:
        logger.error(
            "Individual agent secondary attempt also timed out after %s seconds (%s).",
            secondary_timeout,
            timeout_exc,
        )
    except Exception as secondary_exc:
        logger.exception(
            "Individual agent secondary attempt failed; falling back. Error: %s",
            secondary_exc,
        )

    return _build_deterministic_recommendation(mock_purchases, user_query, today)


def run_individual_agent_sync(
    mock_purchases: dict[str, Any],
    user_query: str,
    today: str,
) -> str:
    """Synchronous helper for running the agent in non-async contexts."""
    # if not _DEDALUS_AVAILABLE:
    #     return (
    #         "The decision advisor is temporarily unavailable because the Dedalus Labs "
    #         "agent runtime is not installed on this server."
    #     )
    load_dotenv()
    # api_key = os.getenv("DEDALUS_API_KEY")
    
    load_dotenv()
    api_key = os.getenv("DEDALUS_API_KEY")
    if not api_key:
        logger.warning("DEDALUS_API_KEY not set; returning fallback recommendation.")
        return _build_deterministic_recommendation(mock_purchases, user_query, today)

    return asyncio.run(
        run_individual_agent(
            mock_purchases=mock_purchases,
            user_query=user_query,
            today=today,
        )
    )


if __name__ == "__main__":
    # Simple manual smoke test with empty data
    demo_result = run_individual_agent_sync(
        mock_purchases={},
        user_query="Should I buy tickets to a concert this weekend?",
        today="2025-11-08",
    )
    print("\nLattice Spending Advisor Result:\n")
    print(demo_result)
