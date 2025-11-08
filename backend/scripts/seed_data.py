"""Seed script to populate database with demo data."""
from datetime import datetime

from passlib.context import CryptContext

from app.models import (
    User,
    Chat,
    ChatMember,
    Message,
    GroupContext,
    LinkedAccount,
    OnboardingStatus,
    ChatType,
    ChatMemberRole,
    SenderType,
    MessageAction,
    SessionLocal,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_database() -> None:
    """Seed the database with demo data."""
    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping...")
            return

        print("Seeding database...")

        # Create demo users
        user1 = User(
            name="Alice Demo",
            email="alice@demo.com",
            hashed_password=pwd_context.hash("password123"),
            onboarding_status=OnboardingStatus.COMPLETE,
            preferences={"notifications": True, "theme": "dark"},
        )
        user2 = User(
            name="Bob Test",
            email="bob@test.com",
            hashed_password=pwd_context.hash("password123"),
            onboarding_status=OnboardingStatus.COMPLETE,
            preferences={"notifications": False, "theme": "light"},
        )
        user3 = User(
            name="Charlie Sample",
            email="charlie@sample.com",
            hashed_password=pwd_context.hash("password123"),
            onboarding_status=OnboardingStatus.INCOMPLETE,
            preferences={},
        )

        db.add_all([user1, user2, user3])
        db.commit()
        print(f"✓ Created {3} demo users")

        # Create solo chat for Alice
        solo_chat = Chat(
            type=ChatType.SOLO,
            owner_id=user1.id,
            title="Personal Assistant",
        )
        db.add(solo_chat)
        db.commit()

        # Add Alice as member
        solo_member = ChatMember(
            chat_id=solo_chat.id,
            user_id=user1.id,
            role=ChatMemberRole.OWNER,
        )
        db.add(solo_member)
        db.commit()

        # Add some messages
        msg1 = Message(
            chat_id=solo_chat.id,
            sender_id=user1.id,
            sender_type=SenderType.USER,
            content="What's the best credit card for groceries?",
        )
        msg2 = Message(
            chat_id=solo_chat.id,
            sender_id=None,
            sender_type=SenderType.AI,
            content="Based on your spending, I recommend the Blue Cash Preferred® Card for 6% cash back on groceries.",
            thinking=[
                "Analyzing spending patterns",
                "Comparing reward rates",
                "Calculating potential savings",
            ],
            action=MessageAction.CARD,
            drawer_data={
                "recommendation": "Blue Cash Preferred",
                "cash_back_rate": "6%",
                "category": "groceries",
                "annual_fee": "$95",
            },
        )
        db.add_all([msg1, msg2])
        db.commit()
        print(f"✓ Created solo chat with {2} messages")

        # Create group chat
        group_chat = Chat(
            type=ChatType.GROUP,
            owner_id=user1.id,
            title="Weekend Trip Planning",
        )
        db.add(group_chat)
        db.commit()

        # Add group members
        group_member1 = ChatMember(
            chat_id=group_chat.id,
            user_id=user1.id,
            role=ChatMemberRole.OWNER,
        )
        group_member2 = ChatMember(
            chat_id=group_chat.id,
            user_id=user2.id,
            role=ChatMemberRole.MEMBER,
        )
        db.add_all([group_member1, group_member2])
        db.commit()

        # Create group context
        group_context = GroupContext(
            chat_id=group_chat.id,
            context_summary="Planning weekend trip expenses",
            total_spend=450.75,
            last_activity_at=datetime.utcnow(),
        )
        db.add(group_context)
        db.commit()

        # Add group messages
        group_msg1 = Message(
            chat_id=group_chat.id,
            sender_id=user1.id,
            sender_type=SenderType.USER,
            content="Split our Airbnb cost of $300 between Alice and Bob",
        )
        group_msg2 = Message(
            chat_id=group_chat.id,
            sender_id=None,
            sender_type=SenderType.AI,
            content="I've calculated the split: Alice owes $150, Bob owes $150.",
            thinking=["Identifying participants", "Calculating equal split"],
            action=MessageAction.SPLIT,
            drawer_data={
                "total": 300,
                "participants": ["Alice", "Bob"],
                "split": {"Alice": 150, "Bob": 150},
            },
        )
        db.add_all([group_msg1, group_msg2])
        db.commit()
        print(f"✓ Created group chat with {2} messages")

        # Create linked accounts
        account1 = LinkedAccount(
            user_id=user1.id,
            institution="Amazon",
            account_name="Primary Amazon Account",
            permissions={"transactions": True, "cards": True},
            knot_item_id="knot_demo_amazon_123",
        )
        account2 = LinkedAccount(
            user_id=user1.id,
            institution="DoorDash",
            account_name="DoorDash Account",
            permissions={"transactions": True},
            knot_item_id="knot_demo_doordash_456",
        )
        account3 = LinkedAccount(
            user_id=user2.id,
            institution="UberEats",
            account_name="UberEats Account",
            permissions={"transactions": True},
            knot_item_id="knot_demo_ubereats_789",
        )
        db.add_all([account1, account2, account3])
        db.commit()
        print(f"✓ Created {3} linked accounts")

        print("\n✅ Database seeded successfully!")
        print("\nDemo credentials:")
        print("  Email: alice@demo.com")
        print("  Password: password123")
        print("  Email: bob@test.com")
        print("  Password: password123")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

