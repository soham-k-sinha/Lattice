# ✅ Step 2 Complete: Database & ORM

## What Was Implemented

### 1. SQLAlchemy Models ✓

All models from `BACKEND_PLAN.md` have been implemented:

#### **User Model** (`app/models/user.py`)
- `id` (Integer, primary key)
- `name` (String)
- `email` (String, unique, indexed)
- `hashed_password` (String)
- `onboarding_status` (Enum: incomplete, complete, skipped)
- `preferences` (JSONB)
- `auth_provider_id` (String, nullable)
- `created_at`, `updated_at` (Timestamps)

#### **Chat Model** (`app/models/chat.py`)
- `id` (Integer, primary key)
- `type` (Enum: solo, group)
- `owner_id` (Foreign key to User)
- `title` (String, nullable)
- `created_at`, `updated_at`

#### **ChatMember Model** (`app/models/chat.py`)
- `id` (Integer, primary key)
- `chat_id` (Foreign key to Chat)
- `user_id` (Foreign key to User)
- `role` (Enum: owner, admin, member)
- `created_at`, `updated_at`

#### **Message Model** (`app/models/message.py`)
- `id` (Integer, primary key)
- `chat_id` (Foreign key to Chat)
- `sender_id` (Foreign key to User, nullable)
- `sender_type` (Enum: user, ai)
- `content` (Text)
- `thinking` (JSONB array) - AI thinking steps
- `action` (Enum: card, split, tracker, none)
- `drawer_data` (JSONB) - Context drawer payload
- `created_at`, `updated_at`

#### **GroupContext Model** (`app/models/group_context.py`)
- `id` (Integer, primary key)
- `chat_id` (Foreign key to Chat, unique)
- `context_summary` (Text)
- `total_spend` (Float)
- `last_activity_at` (DateTime)
- `created_at`, `updated_at`

#### **LinkedAccount Model** (`app/models/linked_account.py`)
- `id` (Integer, primary key)
- `user_id` (Foreign key to User)
- `institution` (String) - e.g., "Amazon", "DoorDash"
- `account_name` (String)
- `permissions` (JSONB)
- `knot_item_id` (String, unique, indexed)
- `created_at`, `updated_at`

### 2. Alembic Migrations ✓

- Alembic initialized and configured
- `alembic/env.py` set up to:
  - Import all models
  - Use `DATABASE_URL` from settings
  - Support autogenerate migrations

### 3. Database Management Scripts ✓

#### **Init Script** (`scripts/init_db.py`)
- Creates all tables directly using SQLAlchemy

#### **Seed Script** (`scripts/seed_data.py`)
- Creates demo users (Alice, Bob, Charlie)
- Creates solo chat with messages
- Creates group chat with split bill example
- Creates linked accounts for demo
- Includes realistic test data

### 4. Makefile Commands ✓

```bash
make db-init      # Create tables
make db-migrate   # Generate migration (msg="description")
make db-upgrade   # Apply migrations
make db-seed      # Populate with demo data
make db-reset     # Reset and reseed (WARNING: deletes all data)
```

## Database Schema

```
┌─────────────┐     ┌─────────────┐
│    User     │────<│LinkedAccount│
│             │     └─────────────┘
│ - id        │
│ - email     │
│ - name      │     ┌─────────────┐
│ - prefs     │────<│ ChatMember  │───>┌──────────┐
│ - onboard   │     └─────────────┘    │   Chat   │
└─────────────┘                         │          │
                                        │ - type   │
                                        │ - owner  │
                                        └──────────┘
                                             ├─────>┌──────────────┐
                                             │      │   Message    │
                                             │      │              │
                                             │      │ - content    │
                                             │      │ - thinking   │
                                             │      │ - action     │
                                             │      │ - drawer_data│
                                             │      └──────────────┘
                                             │
                                             └─────>┌──────────────┐
                                                    │GroupContext  │
                                                    │              │
                                                    │ - summary    │
                                                    │ - total_spend│
                                                    └──────────────┘
```

## Setup Instructions

### Option 1: For Hackathon (Quick Start - No Real Database Yet)

If you don't have a Postgres database yet, you can continue with mock mode for Steps 3-5.

Just ensure your `.env` has a placeholder:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/lattice_db
```

### Option 2: Using Supabase (Recommended for Hackathon)

1. **Create Supabase project:**
   - Go to https://supabase.com
   - Create a new project
   - Get your connection string from Settings → Database

2. **Update `.env`:**
   ```bash
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
   ```

3. **Run migrations:**
   ```bash
   make db-upgrade
   make db-seed
   ```

### Option 3: Using Neon

1. **Create Neon project:**
   - Go to https://neon.tech
   - Create a new project
   - Copy connection string

2. **Update `.env`:**
   ```bash
   DATABASE_URL=postgresql://[USER]:[PASSWORD]@[HOST]/[DATABASE]
   ```

3. **Run migrations:**
   ```bash
   make db-upgrade
   make db-seed
   ```

### Option 4: Local Postgres

1. **Install Postgres:**
   ```bash
   brew install postgresql  # macOS
   ```

2. **Start Postgres:**
   ```bash
   brew services start postgresql
   ```

3. **Create database:**
   ```bash
   createdb lattice_db
   ```

4. **Update `.env`:**
   ```bash
   DATABASE_URL=postgresql://localhost:5432/lattice_db
   ```

5. **Run migrations:**
   ```bash
   make db-upgrade
   make db-seed
   ```

## Working with the Database

### Create a New Migration

After modifying models:
```bash
make db-migrate msg="Add new field to User"
```

### Apply Migrations

```bash
make db-upgrade
```

### Seed Demo Data

```bash
make db-seed
```

### Reset Database (Development Only)

⚠️ **WARNING: This deletes all data!**
```bash
make db-reset
```

## Demo Credentials

After seeding, you can use:

**User 1:**
- Email: `alice@demo.com`
- Password: `password123`
- Status: Onboarding complete

**User 2:**
- Email: `bob@test.com`
- Password: `password123`
- Status: Onboarding complete

**User 3:**
- Email: `charlie@sample.com`
- Password: `password123`
- Status: Onboarding incomplete

## Accessing the Database

### Using Python

```python
from app.models import SessionLocal, User, Chat, Message

db = SessionLocal()

# Query users
users = db.query(User).all()

# Get user by email
alice = db.query(User).filter(User.email == "alice@demo.com").first()

# Get chats for user
chats = db.query(Chat).filter(Chat.owner_id == alice.id).all()

db.close()
```

### Using FastAPI Dependency

In your route handlers:
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import get_db

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

## Next Steps

Follow `BACKEND_STEP_PLAN.md`:

- ✅ **Step 1:** Bootstrap - DONE
- ✅ **Step 2:** Database & ORM - DONE
- **Step 3:** Authentication (JWT + OAuth2 password flow)
- **Step 4-5:** Mock API endpoints
- **Step 6+:** Real integrations

## Notes

- All models include `created_at` and `updated_at` timestamps
- JSONB columns allow flexible data structures (preferences, drawer_data, etc.)
- Foreign keys have proper indexes for query performance
- Relationships are set up for easy navigation between models
- Enum types ensure data consistency

---

**Status:** ✅ Step 2 Complete - Database models and migrations ready!
**Time to implement Step 3:** Authentication with JWT

