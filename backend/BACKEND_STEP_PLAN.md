# Backend Implementation Plan (FastAPI Edition)

This checklist translates `BACKEND_PLAN.md` into an execution order you can follow during the hackathon. Work through each phase sequentially. Use feature flags and environment variables so you can swap mock integrations for real ones as you progress.

---

## Phase 1 — Project Foundation (Mock-First)

1. **Bootstrap Backend App**

   - Initialize Python project with FastAPI (Poetry or uv recommended).
   - Install packages:
     - Runtime: `fastapi`, `uvicorn[standard]`, `pydantic`, `python-dotenv`, `httpx`, `tenacity`, `loguru` (or `structlog`).
     - Auth: `python-jose[cryptography]`, `passlib[bcrypt]`.
     - DB: `sqlalchemy`, `asyncpg`, `alembic`.
   - Dev tooling: `ruff`, `mypy`, `pytest`, `pytest-asyncio`.
   - Suggested structure:
     ```
     backend/
       app/
         api/            # routers
         services/
         repositories/
         integrations/
         schemas/
         core/           # config, logging, security
       alembic/
       tests/
     ```
   - Configure `pyproject.toml` (formatting/linting) and `.env` handling.

2. **Database & ORM**

   - Spin up Postgres instance (Supabase/Neon).
   - Use SQLAlchemy ORM with Alembic migrations (or Piccolo/Tortoise if preferred).
   - Define models (User, Chat, ChatMember, Message, GroupContext, LinkedAccount).
   - Run initial migration and seed demo data via script.

3. **Authentication**

   - Implement OAuth2 password flow with JWT using FastAPI dependencies.
   - Hash passwords with `passlib`.
   - Endpoints: `POST /api/auth/signup`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/session`.
   - Apply dependency-based guard across `/api/**` (except onboarding start/auth routes).

4. **Mocked Read APIs**

   - Return seeded/mock data for:
     - `GET /api/chats`, `GET /api/chats/:id`
     - `GET /api/groups`, `GET /api/groups/:id`
     - `GET /api/accounts`
     - `GET /api/insights`, `GET /api/insights/summary`
     - `GET /api/settings`
   - Ensure responses match frontend expectations (shape and keys).

5. **Mocked Write APIs**
   - `POST /api/chats/:id/messages` — store user message, return canned AI response.
   - `POST /api/groups` — create group with mock invite handling.
   - `DELETE /api/accounts/:id` — pretend to unlink.
   - `PATCH /api/settings` — update preferences in DB.

> ✅ Goal for Phase 1: Frontend works end-to-end using mock data; you can demo without external dependencies.

---

## Phase 2 — Core Integrations (Hackathon Scope)

6. **Knot Integration (Accounts + Transactions)**

   - Add `app/integrations/knot.py` client (basic auth header, retry wrapper built with `httpx` + `tenacity`).
   - Feature flag: `FEATURE_KNOT=true|false`.
   - Wire endpoints:
     - `POST /api/onboarding/start` → Knot `POST /session/create`.
     - `POST /api/onboarding/complete` → store linked accounts.
     - `GET /api/accounts` → read from DB; refresh from Knot `GET /accounts/get` when stale.
     - Background helper for `POST /merchant/list` (prefetch supported merchants; daily cache).
     - Build transaction sync helper (`POST /transactions/sync`) for supported merchants; persist cursor per merchant-user.

7. **Chat Orchestrator + AI Broker (MVP)**

   - Create `chat_orchestrator` service module:
     1. Save user message.
     2. Detect intent (card, split, tracker, general).
     3. Fetch context: cards (DB/Knot), transactions (Knot), insights (Snowflake cache), social trends (mock for now).
     4. Call AI Broker.
     5. Persist AI response with `thinking`, `action`, `drawerData`.
   - AI Broker initial version:
     - Start with a single provider (Groq or Gemini) for general responses.
     - Structure returned payload to match frontend contract.
   - Keep Dedalus agents behind feature flag for later.

8. **Insights Service (Snowflake Stub)**
   - Build placeholder integration module `app/integrations/snowflake.py`.
   - For hackathon, create scheduled task (APScheduler or background loop) that populates insights table using mock JSON or precomputed metrics.
   - Expose `GET /api/insights` and `GET /api/insights/summary` using cached data.

> ✅ Goal for Phase 2: Flip feature flags to pull _live_ Knot account data and generate AI-driven chat replies while still having a safe fallback to mock responses.

---

## Phase 3 — Advanced Integrations & Polish

9. **Dedalus MCP Agents**

   - Integrate CardGuru, SplitSense, PriceOracle workflows.
   - Enhance context enrichment to supply required inputs (card catalog, transaction data, group members, product metadata).
   - Update AI Broker to select Dedalus vs Groq/Gemini based on intent.
   - Stream `thinking` stages via SSE/WebSocket if time permits.

10. **Snowflake Analytics (Live)**

    - Replace mock cron job with real Snowflake REST calls (`POST /snowflake/sql`).
    - Cache results in Postgres; ensure API routes read from cache only.

11. **X API Adapter (Optional)**

    - Implement `app/integrations/x.py`.
    - Call only when chat message contains trend keywords; cache responses 30 minutes.

12. **Operational Hardening**

    - Rate limiting (per user/IP) to protect external APIs.
    - Observability: structured logs (`loguru`/`structlog`), error tracking hooks.
    - Centralized exception handlers with JSON error payloads.
    - Health check endpoint `GET /health`.
    - Feature flags for each integration (`FEATURE_KNOT`, `FEATURE_AI`, `FEATURE_SNOWFLAKE`, `FEATURE_X`).

13. **Documentation & Testing**
    - Publish OpenAPI/Swagger spec for all routes.
    - Add README with env vars, setup steps, feature flag usage.
    - Smoke tests for critical flows (auth, chat post, accounts list).

> ✅ Goal for Phase 3: Demo-ready backend with live integrations, observability, and fallbacks if a provider misbehaves during the hackathon.

---

## Phase 4 — Production Hand-off (Post-Hackathon)

14. **Security & Compliance**

    - Secrets management, audit logging for Knot/AI activity.
    - Data retention policies; ensure no PAN/CVV captured.
    - Webhook receivers (Knot task updates, AI callbacks) if needed.

15. **Scalability & Reliability**
    - Migrate to queue-based orchestrations for long-running tasks.
    - Horizontal scaling, caching layer (Redis) for transactions/insights.
    - Automated CI/CD pipeline with lint/test/format checks.

---

## Daily Hackathon Checklist

- [ ] Feature flags set correctly (`.env`).
- [ ] Mock mode still works for quick demos.
- [ ] Logs monitored for external API errors.
- [ ] Cron/queues running (insights refresh).
- [ ] Database seeded with representative data.

Keep this document updated as you make decisions or adjust scope. For any changes that diverge from `BACKEND_PLAN.md`, document the reasoning so the frontend team stays aligned.
