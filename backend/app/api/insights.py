"""Insights API routes."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models import User
from app.utils.transactions_loader import load_user_transactions

router = APIRouter()


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _parse_amount(transaction: dict[str, Any]) -> float:
    candidates: Iterable[Any] = (
        transaction.get("price_amount"),
        transaction.get("amount"),
        transaction.get("total"),
    )
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            return float(candidate)
        except (TypeError, ValueError):
            continue

    price = transaction.get("price") or {}
    for key in ("amount", "total", "final_total", "sub_total"):
        candidate = price.get(key)
        if candidate is None:
            continue
        try:
            return float(candidate)
        except (TypeError, ValueError):
            continue

    payments = transaction.get("payment_methods") or []
    total = 0.0
    for payment in payments:
        amount = payment.get("transaction_amount")
        if amount is None:
            continue
        try:
            total += float(amount)
        except (TypeError, ValueError):
            continue
    if total:
        return total

    return 0.0


def _collect_transactions(user_id: int) -> list[dict[str, Any]]:
    stored = load_user_transactions(user_id)
    transactions: list[dict[str, Any]] = []
    for payload in stored.values():
        merchant_info = payload.get("merchant") or {}
        merchant_name = str(merchant_info.get("name") or "").strip() or None
        merchant_id = str(merchant_info.get("id") or "").strip() or None

        for tx in payload.get("transactions") or []:
            data = dict(tx)
            data.setdefault("merchant_name", merchant_name)
            data.setdefault("merchant_id", merchant_id)
            data["parsed_amount"] = _parse_amount(data)
            data["parsed_datetime"] = _parse_datetime(data.get("datetime"))
            transactions.append(data)
    return transactions


def _generate_insights(user_id: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    transactions = _collect_transactions(user_id)
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    start_30 = now - timedelta(days=30)

    recent_transactions = [
        tx
        for tx in transactions
        if tx.get("parsed_datetime") and tx["parsed_datetime"] >= start_30
    ]

    if not recent_transactions:
        fallback_summary = {
            "summary": (
                "No recent transactions were found for the last 30 days. "
                "Once you connect a merchant account and sync transactions, "
                "I can surface spend trends, rewards tips, and optimization suggestions."
            ),
            "month": now.strftime("%B %Y"),
            "generated_at": now.isoformat(),
            "total_spend": 0.0,
            "order_count": 0,
        }
        return [], fallback_summary

    spend_total = sum(tx["parsed_amount"] for tx in recent_transactions)
    order_count = len(recent_transactions)
    average_ticket = spend_total / order_count if order_count else 0.0

    # Spend by merchant
    merchant_totals: dict[str, float] = defaultdict(float)
    merchant_orders: dict[str, list[float]] = defaultdict(list)
    last_purchase_by_merchant: dict[str, datetime] = {}

    for tx in recent_transactions:
        amount = tx["parsed_amount"]
        merchant_name = (
            str(tx.get("merchant_name") or "")
            or str(tx.get("merchant_id") or "Unknown Merchant")
        )
        merchant_name = merchant_name.strip() or "Unknown Merchant"
        merchant_totals[merchant_name] += amount
        merchant_orders[merchant_name].append(amount)
        dt = tx["parsed_datetime"]
        if dt:
            last_purchase_by_merchant[merchant_name] = max(
                last_purchase_by_merchant.get(merchant_name, dt), dt
            )

    top_merchant = None
    top_merchant_total = 0.0
    if merchant_totals:
        top_merchant = max(merchant_totals.items(), key=lambda item: item[1])[0]
        top_merchant_total = merchant_totals[top_merchant]

    # Identify delivery / dining merchants to tailor advice
    DELIVERY_KEYWORDS = ("uber", "door", "dash", "instacart", "grub", "postmate")
    has_delivery_focus = (
        top_merchant
        and any(keyword in top_merchant.lower() for keyword in DELIVERY_KEYWORDS)
    )

    largest_transaction = max(
        recent_transactions, key=lambda tx: tx["parsed_amount"], default=None
    )

    earliest = min(
        tx["parsed_datetime"] for tx in recent_transactions if tx["parsed_datetime"]
    )
    days_active = (now - earliest).days or 1
    weekly_average = spend_total / max(days_active / 7, 1)

    insights: list[dict[str, Any]] = []

    if top_merchant:
        insights.append(
            {
                "id": "spend-top-merchant",
                "type": "spending",
                "title": f"{top_merchant} is leading your spend this month",
                "description": (
                    f"You've spent ${top_merchant_total:,.2f} at {top_merchant} across "
                    f"{len(merchant_orders[top_merchant])} purchase(s) in the last 30 days."
                ),
                "impact": f"${top_merchant_total:,.0f} in 30 days",
                "date": now.isoformat(),
                "action": "Set a reminder to review this merchant's orders weekly.",
            }
        )

    if has_delivery_focus:
        insights.append(
            {
                "id": "card-delivery-optimizer",
                "type": "optimization",
                "title": "Upgrade your delivery card for richer rewards",
                "description": (
                    f"Delivery merchants like {top_merchant} dominate your spending. "
                    "Consider using the Amex Gold (4x dining & delivery) or Capital One Savor "
                    "(4x entertainment & dining) to capture richer rewards."
                ),
                "impact": "Earn 3–4x points on delivery orders",
                "date": now.isoformat(),
                "action": "Link a dining-focused rewards card before your next order.",
            }
        )

    if largest_transaction and largest_transaction["parsed_amount"] >= 150:
        merchant = (
            largest_transaction.get("merchant_name")
            or largest_transaction.get("merchant_id")
            or "that merchant"
        )
        insights.append(
            {
                "id": "large-purchase-alert",
                "type": "warning",
                "title": "A large ticket item hit your statement",
                "description": (
                    f"A recent order at {merchant} totaled "
                    f"${largest_transaction['parsed_amount']:,.2f}. "
                    "Consider setting a spending cap or splitting the purchase if it's discretionary."
                ),
                "impact": f"${largest_transaction['parsed_amount']:,.0f} single order",
                "date": (largest_transaction.get("parsed_datetime") or now).isoformat(),
                "action": "Review the receipt and confirm it matches expectations.",
            }
        )

    # Positive reinforcement or insight about consistency
    if weekly_average <= 200:
        insights.append(
            {
                "id": "spend-consistency",
                "type": "success",
                "title": "Your weekly spend is steady and manageable",
                "description": (
                    f"Average weekly spend over the past {days_active} days is "
                    f"about ${weekly_average:,.0f}. Nice job keeping expenses predictable."
                ),
                "impact": f"${weekly_average:,.0f} weekly average",
                "date": now.isoformat(),
                "action": "Stay the course—steady spending keeps goals on track.",
            }
        )

    # Generic rewards tip if not delivery heavy
    if not has_delivery_focus:
        insights.append(
            {
                "id": "rewards-reminder",
                "type": "rewards",
                "title": "Capture extra rewards on your everyday purchases",
                "description": (
                    "Rotate between high-earning cards: use a flat 2% card for general spend, "
                    "and a category bonus card (e.g., grocery or gas) when applicable."
                ),
                "impact": "Earn an extra $120+/year",
                "date": now.isoformat(),
                "action": "Assign one card per category in your wallet.",
            }
        )

    if not insights:
        insights.append(
            {
                "id": "general-tip",
                "type": "spending",
                "title": "Keep an eye on your transactions",
                "description": "Review your latest orders to spot any anomalies or duplicate charges.",
                "impact": "",
                "date": now.isoformat(),
            }
        )

    # Build summary
    top_merchant_line = (
        f"Top merchant: {top_merchant} (${top_merchant_total:,.2f})."
        if top_merchant
        else "No dominant merchant detected this month."
    )

    average_ticket_line = (
        f"Average order size is ${average_ticket:,.2f} across {order_count} orders."
    )

    latest_purchase = max(
        (tx["parsed_datetime"] for tx in recent_transactions if tx["parsed_datetime"]),
        default=None,
    )
    latest_line = (
        f"Most recent purchase: {latest_purchase.strftime('%b %d')}."
        if latest_purchase
        else ""
    )

    summary_text = (
        f"**{now.strftime('%B %Y')} Snapshot**\n\n"
        f"You spent ${spend_total:,.2f} across {order_count} tracked orders in the last 30 days.\n"
        f"{top_merchant_line} {average_ticket_line} {latest_line}".strip()
    )

    summary = {
        "summary": summary_text,
        "month": now.strftime("%B %Y"),
        "generated_at": now.isoformat(),
        "total_spend": spend_total,
        "order_count": order_count,
        "average_order_value": average_ticket,
    }

    return insights, summary


@router.get("")
def get_insights(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Generate real insights based on the user's synced transactions."""
    insights, _ = _generate_insights(current_user.id)
    return {"insights": insights}


@router.get("/summary")
def get_insights_summary(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Return a textual summary of spending alongside headline metrics."""
    _, summary = _generate_insights(current_user.id)
    return summary

