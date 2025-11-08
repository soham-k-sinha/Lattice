import asyncio
from datetime import date
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Lattice: Individual Purchase Advisor (with Brave Search MCP)
# - Analyzes recent spend (mocked for now; replace with Knot data)
# - Searches market price trends via Brave Search MCP
# - Recommends: Buy Now / Wait / Avoid
# ============================================================

# -------------------------------
# Mock recent purchases (replace with Knot API data)
# -------------------------------
MOCK_PURCHASES = [
    # Week -4
    {"date": "2025-10-12", "item": "Groceries - Trader Joe's", "category": "groceries", "amount": 86.40},
    {"date": "2025-10-13", "item": "Spotify Premium", "category": "entertainment", "amount": 10.99},
    {"date": "2025-10-14", "item": "Uber Rides", "category": "transport", "amount": 18.50},
    {"date": "2025-10-15", "item": "Dining - Chipotle", "category": "food", "amount": 14.25},
    {"date": "2025-10-16", "item": "Amazon - USB-C Cable", "category": "shopping", "amount": 12.99},
    {"date": "2025-10-17", "item": "Gym Membership", "category": "health", "amount": 35.00},
    {"date": "2025-10-18", "item": "Apple iCloud 200GB", "category": "utilities", "amount": 2.99},
    # Week -3
    {"date": "2025-10-20", "item": "Groceries - Costco", "category": "groceries", "amount": 123.88},
    {"date": "2025-10-21", "item": "Dining - Local Pizza", "category": "food", "amount": 19.75},
    {"date": "2025-10-22", "item": "Hulu", "category": "entertainment", "amount": 7.99},
    {"date": "2025-10-23", "item": "Nike Running Shorts", "category": "shopping", "amount": 38.00},
    {"date": "2025-10-24", "item": "Uber Eats", "category": "food", "amount": 26.40},
    {"date": "2025-10-25", "item": "Gas", "category": "transport", "amount": 42.10},
    # Week -2
    {"date": "2025-10-27", "item": "Groceries - Whole Foods", "category": "groceries", "amount": 94.72},
    {"date": "2025-10-28", "item": "Amazon - Study Lamp", "category": "shopping", "amount": 24.90},
    {"date": "2025-10-29", "item": "Netflix", "category": "entertainment", "amount": 15.49},
    {"date": "2025-10-30", "item": "Dining - Noodles", "category": "food", "amount": 16.75},
    {"date": "2025-10-31", "item": "Halloween Party Tickets", "category": "entertainment", "amount": 30.00},
    # Week -1
    {"date": "2025-11-01", "item": "Nike Air Max", "category": "shopping", "amount": 180.00},
    {"date": "2025-11-03", "item": "Uber Eats", "category": "food", "amount": 28.00},
    {"date": "2025-11-04", "item": "Netflix Subscription", "category": "entertainment", "amount": 20.00},
    {"date": "2025-11-05", "item": "Apple Watch Band", "category": "shopping", "amount": 60.00},
    {"date": "2025-11-06", "item": "Trader Joe’s Groceries", "category": "groceries", "amount": 95.00},
    {"date": "2025-11-07", "item": "Spotify Premium", "category": "entertainment", "amount": 10.99},
    {"date": "2025-11-07", "item": "Uber Ride", "category": "transport", "amount": 23.00},
]

# -------------------------------
# User input (what they’re considering buying)
# -------------------------------
USER_QUERY = "Should I purchase a Travis Scott concert ticket for $100?"

# -------------------------------
# Optional: let the agent know “today”
# -------------------------------
TODAY = date.today().isoformat()  # e.g., "2025-11-08"


async def main():
    client = AsyncDedalus()
    runner = DedalusRunner(client)

    prompt = f"""
You are Lattice — an individual spending advisor agent for one user.
Your job: given the user's purchase question, analyze (1) their recent spending behavior
(from provided transaction history), (2) external price trends via Brave Search MCP, and
(3) public sentiment via a Public Sentiment MCP, then return a clear recommendation:
Buy Now / Wait / Avoid.

You can and should use the MCP tools available to you:
- Brave Search MCP for real-time price / availability / trend signals.
- Public Sentiment MCP for aggregated sentiment (polarity, confidence, representative quotes/posts).

When searching, try queries like:
- "Travis Scott concert ticket price trend 2025"
- "average resale price Travis Scott tickets"
- "best time to buy concert tickets price trend"
- "price drop patterns for concert tickets near event date"
- "seasonality or demand peaks for this item"

INFORMATION YOU HAVE
--------------------
- Today (ISO): {TODAY}
- User Purchase Query: {USER_QUERY}
- Past Purchase History (mock from Knot):
{MOCK_PURCHASES}

WHAT TO DO
----------
A) PERSONAL SPENDING ANALYSIS
  1. Compute total spend in the last 7 days and in the last 30 days.
  2. Identify top categories by spend over last 30 days.
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
  3. Note seasonal effects or typical resale dynamics (e.g., concert tickets can drop right before the event, or spike after announcements).

  👉 **Show your reasoning for price trend estimation.**
     - Summarize signals you found.
     - Explain why you believe prices are trending a certain direction.
     - If uncertain, describe which factors create uncertainty.

C) PUBLIC SENTIMENT ANALYSIS (via Public Sentiment MCP)
  1. Query recent public sentiment for the event/artist/product in question.
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
Return BOTH a compact human summary and a JSON block for programmatic use, exactly like this:

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

```json
{{
  "recommendation": "<Buy Now | Wait | Avoid>",
  "confidence": "<Low | Medium | High>",
  "financials": {{
    "last_7d_spend": 0,
    "last_30d_spend": 0,
    "discretionary_30d_spend": 0,
    "recent_risk_flag": false,
    "notes": ""
  }},
  "market_view": {{
    "trend": "unclear",
    "evidence": ["", ""]
  }},
  "sentiment_view": {{
    "polarity": "mixed",
    "score": 0.0,
    "evidence": ["", ""]
  }},
  "rationale": ""
}}
CONSTRAINTS

Do not fabricate precise prices if unavailable; summarize directional trend instead.

Use Brave Search MCP and Public Sentiment MCP for external signals; do not assume trends or sentiment without checking.

Keep the final advice simple, transparent, realistic, and actionable.

Show your step-by-step reasoning for financial analysis, price trend estimation, and sentiment interpretation.

Use a lot of related emojis while explaining your step-by-step reasoning for financial analysis.

Now proceed.
    """

    result = await runner.run(
        input=prompt,
        model="openai/gpt-4.1",
        mcp_servers=[
            "windsor/brave-search-mcp",
            "aviralpoddar/Historic-Data-MCP", 
        ],
    )

    print("\n Lattice Spending Advisor Result:\n")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
