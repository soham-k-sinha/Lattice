"""Mock data for API responses when database is not available."""
from datetime import datetime, timedelta

# Mock users data
MOCK_USERS = {
    1: {
        "id": 1,
        "name": "Alice Demo",
        "email": "alice@demo.com",
        "onboarding_status": "complete",
        "preferences": {"theme": "dark", "notifications": True},
    },
    2: {
        "id": 2,
        "name": "Bob Test",
        "email": "bob@test.com",
        "onboarding_status": "complete",
        "preferences": {"theme": "light", "notifications": False},
    },
}

# Mock chats data
MOCK_CHATS = [
    {
        "id": 1,
        "type": "solo",
        "owner_id": 1,
        "title": "Personal Assistant",
        "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
        "member_count": 1,
    },
    {
        "id": 2,
        "type": "group",
        "owner_id": 1,
        "title": "Weekend Trip Planning",
        "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
        "member_count": 2,
    },
    {
        "id": 3,
        "type": "group",
        "owner_id": 1,
        "title": "Grocery Shopping Budget",
        "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "member_count": 3,
    },
]

# Mock messages data
MOCK_MESSAGES = {
    1: [],
    2: [],
    3: [],
}

# Mock groups data
MOCK_GROUPS = [
    {
        "id": 2,
        "name": "Weekend Trip Planning",
        "members": [
            {"id": 1, "name": "Alice Demo", "email": "alice@demo.com", "role": "owner"},
            {"id": 2, "name": "Bob Test", "email": "bob@test.com", "role": "member"},
        ],
        "last_activity": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
        "context": "Planning expenses for weekend getaway",
        "total_spend": 450.00,
    },
    {
        "id": 3,
        "name": "Grocery Shopping Budget",
        "members": [
            {"id": 1, "name": "Alice Demo", "email": "alice@demo.com", "role": "owner"},
            {"id": 2, "name": "Bob Test", "email": "bob@test.com", "role": "member"},
            {"id": 3, "name": "Charlie Sample", "email": "charlie@sample.com", "role": "member"},
        ],
        "last_activity": (datetime.utcnow() - timedelta(hours=12)).isoformat(),
        "context": "Tracking shared grocery expenses",
        "total_spend": 287.50,
    },
]

# Mock linked accounts data
MOCK_ACCOUNTS = [
    {
        "id": 1,
        "user_id": 1,
        "institution": "Amazon",
        "account_name": "Primary Amazon Account",
        "account_type": "shopping",
        "balance": 0.00,  # No balance for shopping accounts
        "currency": "USD",
        "permissions": {"transactions": True, "cards": True},
        "status": "active",
        "linked_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
        "last_synced": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
    },
    {
        "id": 2,
        "user_id": 1,
        "institution": "DoorDash",
        "account_name": "DoorDash Account",
        "account_type": "food_delivery",
        "balance": 0.00,  # No balance for delivery accounts
        "currency": "USD",
        "permissions": {"transactions": True},
        "status": "active",
        "linked_at": (datetime.utcnow() - timedelta(days=15)).isoformat(),
        "last_synced": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
    },
    {
        "id": 3,
        "user_id": 1,
        "institution": "UberEats",
        "account_name": "UberEats Account",
        "account_type": "food_delivery",
        "balance": 0.00,  # No balance for delivery accounts
        "currency": "USD",
        "permissions": {"transactions": True},
        "status": "active",
        "linked_at": (datetime.utcnow() - timedelta(days=10)).isoformat(),
        "last_synced": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
    },
]

# Mock insights data
MOCK_INSIGHTS = {
    "cards": [
        {
            "title": "Optimize Your Grocery Card",
            "description": "Switch to Blue Cash Preferred for 6% back on groceries",
            "potential_savings": "$360/year",
            "action": "card",
            "priority": "high",
        },
        {
            "title": "Maximize Travel Rewards",
            "description": "Use Chase Sapphire Reserve for 3x points on travel",
            "potential_savings": "$240/year",
            "action": "card",
            "priority": "medium",
        },
    ],
    "trends": [
        {
            "category": "Grocery",
            "monthly_spend": 450.00,
            "trend": "up",
            "change_percent": 12.5,
            "insight": "Spending increased 12.5% vs last month",
        },
        {
            "category": "Dining",
            "monthly_spend": 320.00,
            "trend": "down",
            "change_percent": -8.0,
            "insight": "Spending decreased 8% vs last month",
        },
        {
            "category": "Transportation",
            "monthly_spend": 180.00,
            "trend": "stable",
            "change_percent": 2.0,
            "insight": "Spending stable compared to last month",
        },
    ],
    "rewards": [
        {
            "card": "Blue Cash Preferred",
            "earned_this_month": 45.00,
            "category": "Groceries",
        },
        {
            "card": "Chase Sapphire Reserve",
            "earned_this_month": 32.00,
            "category": "Travel",
        },
    ],
    "summary": {
        "total_spend_this_month": 1250.00,
        "total_rewards_earned": 77.00,
        "top_category": "Grocery",
        "optimization_opportunities": 2,
    },
}

MOCK_INSIGHTS_SUMMARY = """
**Your Financial Summary for November 2025**

This month, you spent $1,250 across all categories and earned $77 in rewards. Your top spending category was Groceries at $450. 

**Key Insights:**
- 🎯 You could save an additional $360/year by optimizing your grocery card
- 📈 Grocery spending increased 12.5% compared to last month
- 💰 You're earning well on travel with Chase Sapphire Reserve

**Recommendations:**
1. Consider switching to Blue Cash Preferred for grocery purchases
2. Use your Chase Sapphire Reserve for all travel bookings
3. Your dining spend is down - great job controlling costs!
"""

# Mock settings data
MOCK_SETTINGS = {
    "account": {
        "name": "Alice Demo",
        "email": "alice@demo.com",
        "onboarding_status": "complete",
    },
    "connected_accounts": {
        "total": 3,
        "accounts": ["Amazon", "DoorDash", "UberEats"],
    },
    "preferences": {
        "notifications": {
            "email": True,
            "push": True,
            "spending_alerts": True,
            "reward_reminders": True,
        },
        "privacy": {
            "share_spending_data": False,
            "analytics": True,
        },
        "ai": {
            "auto_suggestions": True,
            "thinking_display": True,
        },
        "display": {
            "theme": "dark",
            "currency": "USD",
            "date_format": "MM/DD/YYYY",
        },
    },
    "security": {
        "two_factor_enabled": False,
        "last_password_change": (datetime.utcnow() - timedelta(days=45)).isoformat(),
        "active_sessions": 1,
    },
}

