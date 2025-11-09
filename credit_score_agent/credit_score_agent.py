"""Credit score & rewards advisor agent (heuristic version)."""
from __future__ import annotations

import asyncio
import os
import re
from typing import Sequence

from dotenv import load_dotenv
from loguru import logger

CREDIT_CARD_KNOWLEDGE = [
    # Travel / dining premium
    "Chase Sapphire Preferred — recommended score: 700+ — 2x–3x points on travel & dining, 1x elsewhere — annual fee ~$95 — good for travel redemptions and transfer partners.",
    "Chase Sapphire Reserve — recommended score: 740+ — 3x on travel & dining, Priority Pass, $300 annual travel credit — annual fee ~$550 — premium travel perks.",
    "American Express Platinum — recommended score: 740+ — 5x points on flights/hotels (booked via Amex), airport lounge access — annual fee ~$695 — premium travel benefits.",
    "American Express Gold — recommended score: 720+ — 4x restaurants & U.S. supermarkets (on up to certain caps), 3x flights booked directly — annual fee ~$250 — strong dining/grocery card.",
    "Capital One Venture Rewards — recommended score: 700+ — 2x miles on all purchases, 5x on hotels with Capital One (select) — annual fee ~$95 — simple flat-rate travel.",
    "Capital One Venture X — recommended score: 740+ — 2x–10x on travel, sizeable travel credits and lounge access — annual fee ~$395 — premium flat-rate travel card.",
    "Citi Premier — recommended score: 700+ — 3x on travel, restaurants, supermarkets, gas — annual fee ~$95 — general travel + everyday categories.",
    "Chase Ink Business Preferred — recommended score: 700+ — 3x on travel, shipping, internet & advertising — annual fee ~$95 — small-business travel/marketing spend.",
    # Cashback general-purpose
    "Citi Double Cash — recommended score: 700+ — 2% total cashback (1% when you buy, 1% when you pay) — no annual fee — simple flat-rate cashback.",
    "Citi Custom Cash — recommended score: 700+ — 5% cash back on your top eligible category each billing cycle (up to cap), 1% other purchases — no annual fee.",
    "Chase Freedom Unlimited — recommended score: 700+ — 1.5%–3% on various categories (3% dining & drugstores at times) — no annual fee — good companion to Sapphire.",
    "Chase Freedom Flex — recommended score: 700+ — rotating 5% quarterly categories, plus 5% on travel via Chase and 3% on dining — no annual fee.",
    "Discover it Cash Back — recommended score: 690+ — rotating 5% quarterly categories (match first year) — no annual fee — strong Q4 or matched rewards for first year.",
    "Wells Fargo Active Cash — recommended score: 700+ — 2% unlimited cash back — no annual fee — simple flat-rate cashback.",
    "Bank of America Customized Cash Rewards — recommended score: 700+ — 3% in user-selected category (gas, online shopping, dining, travel, drug stores, or home improvement), 2% at grocery stores and wholesale clubs — no annual fee.",
    "U.S. Bank Altitude — recommended score: 700+ — 3x on travel & mobile wallet purchases, 2x on dining — annual fee varies (some versions no fee) — mobile-pay centric.",
    # Dining / groceries / marketplace focused
    "American Express Blue Cash Preferred — recommended score: 700+ — 6% at US supermarkets (up to cap), 3% on transit and select streaming — annual fee ~$95 — grocery-heavy households.",
    "American Express Blue Cash Everyday — recommended score: 690+ — 3% at supermarkets (lower caps), no annual fee — lighter grocery option.",
    "Capital One Savor — recommended score: 700+ — 4x on dining & entertainment, 2x on groceries — annual fee for premium versions — great for dining/entertainment spenders.",
    # Airline / co-branded
    "Delta SkyMiles® Gold (AMEX) — recommended score: 700+ — 2x on purchases with Delta, priority boarding & first checked bag — annual fee around $99 — frequent Delta flyers.",
    "United Explorer Card — recommended score: 700+ — 2x on United purchases, dining, and hotel stays — annual fee ~$95 — perks and free checked bag on United.",
    "Southwest Rapid Rewards Plus — recommended score: 700+ — 2x on Southwest purchases, enhanced earning for Rapid Rewards members — annual fee low to none — domestic short-haul flyers.",
    # Hotel / co-branded
    "Marriott Bonvoy Boundless — recommended score: 700+ — 6x on Marriott, 2x on other travel — annual fee ~$95 — Marriott loyalists.",
    "Hilton Honors American Express — recommended score: 690+ — 7x on Hilton purchases (specific versions vary), complimentary elite status with some versions — annual fee varies.",
    # Store / specialty / secured
    "Costco Anywhere Visa by Citi — recommended score: 700+ — 4% on gas (up to cap), 3% on restaurants & travel, 2% at Costco & Costco.com — requires Costco membership — annual fee effectively via membership.",
    "Amazon Prime Rewards Visa — recommended score: 700+ — 5% on Amazon purchases for Prime members, 2% at restaurants/gas — no annual fee (Prime required separately).",
    "Apple Card — recommended score: 700+ — 3% on Apple purchases and select partners, 2% on Apple Pay, 1% on physical card — no annual fee — excellent Apple ecosystem integration.",
    # Travel / arrival style
    "Barclays Arrival® (if available) — recommended score: 700+ — miles on all purchases redeemable for travel statement credits — product availability varies.",
    # Student / secured (examples)
    "Discover it Student Cash Back — recommended score: 650+ (student) — rotating 5% categories with student perks — no annual fee — student-friendly building credit.",
    "Capital One Quicksilver Student — recommended score: 650+ (student) — 1.5% cashback, no annual fee — student option.",
    "Secured Credit Card (example) — recommended score: none (secured) — requires security deposit, helps build or rebuild credit — typically low rewards or none.",
    # Generic placeholder for other regionals / bank cards
    "Regional Bank Cashback Card (example) — recommended score: 680+ — 1.5%–3% on select categories, lower underwriting thresholds — good for local relationships.",
]

CATEGORY_KEYWORDS = {
    "travel": {"travel", "flight", "air", "airline", "hotel", "vacation", "trip"},
    "dining": {"dining", "restaurant", "food", "eat", "coffee", "drink"},
    "groceries": {"grocery", "groceries", "supermarket", "market"},
    "entertainment": {"concert", "entertainment", "movie", "show"},
    "gas": {"gas", "fuel"},
    "online": {"amazon", "online", "shopping"},
}

CATEGORY_RECOMMENDATIONS = {
    "travel": [
        ("Chase Sapphire Preferred", "700+", "3x on travel/dining; strong transfer partners"),
        ("Capital One Venture Rewards", "700+", "2x everywhere with simple redemption"),
    ],
    "dining": [
        ("American Express Gold", "720+", "4x on restaurants & US supermarkets"),
        ("Capital One Savor", "700+", "4x dining & entertainment"),
    ],
    "groceries": [
        ("Amex Blue Cash Preferred", "700+", "6% at US supermarkets"),
        ("Amex Blue Cash Everyday", "690+", "3% supermarkets with no annual fee"),
    ],
    "entertainment": [
        ("Capital One Savor", "700+", "4x on entertainment and dining"),
        ("Chase Freedom Flex", "700+", "Rotating 5% categories often include entertainment"),
    ],
    "gas": [
        ("Costco Anywhere Visa", "700+", "4% back on fuel (Costco membership required)"),
        ("Bank of America Customized Cash", "700+", "3% in chosen category like gas"),
    ],
    "online": [
        ("Amazon Prime Rewards Visa", "700+", "5% back at Amazon for Prime members"),
        ("Chase Freedom Unlimited", "700+", "1.5%-3% across categories including online spends"),
    ],
}


def _detect_category(user_query: str) -> str:
    lowered = user_query.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in lowered for word in keywords):
            return category
    return "general"


def _format_recommendation(category: str) -> tuple[str, str]:
    recs = CATEGORY_RECOMMENDATIONS.get(category)
    if not recs:
        return (
            "Chase Freedom Unlimited",
            "700+",
        )
    name, score, *_ = recs[0]
    return name, score


def _format_backup(category: str) -> tuple[str, str] | None:
    recs = CATEGORY_RECOMMENDATIONS.get(category)
    if recs and len(recs) > 1:
        name, score, *_ = recs[1]
        return name, score
    return None


def _clean_card_name(card: str) -> str:
    match = re.match(r"([A-Za-z0-9® ]+)", card)
    return match.group(1).strip() if match else card.split("—")[0].strip()


async def run_credit_score_agent(
    user_cards: Sequence[str],
    user_query: str,
    today: str,
) -> str:
    """Return a friendly credit card recommendation using heuristics."""
    load_dotenv()
    if not os.getenv("DEDALUS_API_KEY"):
        logger.warning("DEDALUS_API_KEY not set; credit agent returning fallback.")
        return (
            "**Best Card:** Chase Freedom Unlimited — recommended score 700+\n"
            "**Why it Wins:** Flat rewards across every purchase, easy to manage. 💳\n"
            "**Rewards Snapshot:** Expect at least 1.5% cash back everywhere.\n"
            "**Backup Option:** Discover it Cash Back — recommended score 690+ — rotating 5% categories.\n"
            "**Score Health Tip:** Pay balances in full and keep utilisation under 30% to protect your score.\n"
            "**Extra Advice:** Configure the advisor service (Dedalus API key) for deeper, scenario-specific suggestions."
        )

    await asyncio.sleep(0)

    catalog = user_cards or CREDIT_CARD_KNOWLEDGE

    category = _detect_category(user_query)
    best_card_name, best_score = _format_recommendation(category)
    backup = _format_backup(category)

    best_card_details = next(
        (entry for entry in catalog if best_card_name in entry),
        best_card_name,
    )

    backup_text = ""
    if backup:
        backup_name, backup_score = backup
        backup_details = next(
            (entry for entry in catalog if backup_name in entry),
            backup_name,
        )
        backup_text = f"**Backup Option:** {backup_details} (score {backup_score})"

    category_label = category.title() if category != "general" else "Everyday spending"

    return (
        f"**Best Card:** {best_card_details} (score {best_score}+)\n"
        f"**Why it Wins:** Tailored for {category_label.lower()} — strong rewards without overcomplicating your wallet. 💳\n"
        f"**Rewards Snapshot:** Expect elevated earn rates for this category while keeping utilisation in check.\n"
        f"{backup_text}\n"
        f"**Score Health Tip:** Keep utilisation below 30% and pay in full each month to support your credit score.\n"
        f"**Extra Advice:** Set a reminder to review your statement in a week to confirm the expected rewards posted. 💡"
    )


def run_credit_score_agent_sync(
    user_cards: Sequence[str],
    user_query: str,
    today: str,
) -> str:
    """Synchronous helper for CLI/testing."""
    load_dotenv()
    if not os.getenv("DEDALUS_API_KEY"):
        logger.warning("DEDALUS_API_KEY not set; credit agent returning fallback.")
        return (
            "Set up the advisor service (Dedalus API key) to unlock tailored credit card recommendations."
        )

    return asyncio.run(
        run_credit_score_agent(
            user_cards=user_cards,
            user_query=user_query,
            today=today,
        )
    )


if __name__ == "__main__":
    result = run_credit_score_agent_sync(
        user_cards=CREDIT_CARD_KNOWLEDGE,
        user_query="Heading to a new restaurant tonight, any card suggestions?",
        today="2025-11-09",
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
