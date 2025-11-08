import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()

credit_cards = [
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

user_query = "I'm ordering food from Uber Eats tonight for about $45. Which of my credit cards should I use for the best return?"


async def main():
    client = AsyncDedalus()
    runner = DedalusRunner(client)

    stream = await runner.run(
        input=f"""
You are Lattice, a financial reasoning co-pilot built with Knot's API. 
The user provides a list of their credit cards and recent spending categories. 
Your task is to determine the *optimal credit card to use* for a given purchase scenario.

Context:
The user's active credit cards (with details) are:
{credit_cards}

User's query: {user_query}

Instructions:
- Identify the category of purchase (e.g., dining, travel, groceries, entertainment, etc.)
- Use reward structures and credit health factors to reason which card offers the best effective value.
- Prefer cards with higher category bonuses and balanced utilization.
- Output the recommendation in this structure:

---
- Category: [Identified category]
- Best Card: [Card Name]
- Why: [Short explanation]
- Effective Reward Value: [e.g., $1.80 or 4x points (~$1.80 equivalent)]
- Secondary Option: [If applicable]
---
""",
        model="openai/gpt-4.1",
        mcp_servers=[
            "windsor/brave-search-mcp"
        ],
    )

    print(stream.final_output)


if __name__ == "__main__":
    asyncio.run(main())
