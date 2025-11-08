# Lattice Backend

FastAPI backend server for Lattice AI - handling chat, groups, accounts, insights, and external integrations.

## Setup

### Prerequisites

- Python 3.11+
- Poetry (or uv)
- PostgreSQL database

### Installation

1. **Install dependencies:**

```bash
poetry install
```

Or with uv:
```bash
uv pip install -e .
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

3. **Run database migrations (once Step 2 is complete):**

```bash
poetry run alembic upgrade head
```

### Running the Server

**Development mode:**

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:
```bash
python -m uvicorn app.main:app --reload
```

**Production mode:**

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   ├── services/         # Business logic
│   ├── integrations/     # External API clients (Knot, AI, Snowflake, X)
│   ├── middleware/       # Auth, rate limiting, logging
│   ├── models/           # SQLAlchemy database models
│   ├── utils/            # Helper functions
│   ├── config/           # Configuration and settings
│   └── main.py           # FastAPI app entry point
├── alembic/              # Database migrations
├── tests/                # Unit and integration tests
├── pyproject.toml        # Poetry dependencies
└── .env                  # Environment variables (gitignored)
```

## API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Feature Flags

Toggle integrations via environment variables:

- `FEATURE_KNOT=true|false` - Enable/disable Knot API integration
- `FEATURE_AI=true|false` - Enable/disable AI providers (Groq/Gemini/Dedalus)
- `FEATURE_SNOWFLAKE=true|false` - Enable/disable Snowflake analytics
- `FEATURE_X=true|false` - Enable/disable X (Twitter) API

## Development

**Linting & Formatting:**

```bash
poetry run black .
poetry run ruff check .
poetry run mypy app/
```

**Testing:**

```bash
poetry run pytest
```

## Next Steps

1. Complete Step 2: Database & ORM setup
2. Implement authentication (Step 3)
3. Build mock API endpoints (Step 4-5)
4. Integrate external APIs (Step 6+)

See `BACKEND_STEP_PLAN.md` for the full implementation roadmap.

