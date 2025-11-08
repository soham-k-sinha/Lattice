# Backend Requirements From Frontend Surfaces

This document summarizes every backend capability implied by the current Next.js frontend (`frontend/app/**`) and, most importantly, maps each user interaction to the external APIs it must (or must not) call. Treat it as the contract for the MVP backend.

## 1. High-Level Goals

1. Serve authenticated users who can chat with AI assistants, alone or in groups.
2. Coordinate multiple AI providers (Dedalus Labs MCP agents, Groq, Gemini) and financial APIs (Knot, X API, Snowflake REST) without over-calling them.
3. Expose clear CRUD + query endpoints for groups, chats, accounts, insights, and settings.
4. Keep the design simple enough for a hackathon MVP while leaving room to evolve.

## 2. Core Services & Responsibilities

| Service | Primary Responsibilities | External Dependencies |
| --- | --- | --- |
| API Gateway / BFF | Authn/z, request validation, response shaping for the Next frontend | Frontend, Auth provider |
| Chat Orchestrator | Persist chat threads, detect intent, fan out to AI Broker, emit structured replies (`content`, `thinking`, `action`) | AI Broker, Group Service |
| AI Broker | Route prompts to Dedalus agents, Groq, or Gemini; enforce safety + retries | Dedalus runtime, Groq, Gemini |
| Knot Integration | Link accounts, fetch merchant-scoped transactions (Amazon, UberEats, DoorDash, etc.), surface account status | Knot API |
| Group Service | Manage group metadata, memberships, invites, shared context | Postgres |
| Insights Service | Pull/aggregate Snowflake datasets, compute optimizations, expose summaries | Snowflake REST API |
| Social Context Adapter | Capture trending topics/deals from X API when explicitly requested | X API |
| Settings / Profile Service | Store user prefs (notifications, AI toggles) & security options | Postgres |

All of these modules can live in one backend app for the MVP, but the seams define where we call external APIs.

## 3. When Each External API Is Called

| Scenario | Trigger | External Calls | Notes |
| --- | --- | --- | --- |
| Onboarding “Connect with Knot” | User taps Connect button | `POST /knot/link-token`, `POST /knot/token-exchange` | Only once per user unless they unlink accounts. |
| Viewing Linked Accounts | `/accounts` route loads | `GET /knot/accounts` (scoped) | Cached for 15 min; no need to hit Knot on every click. |
| Chat about specific purchases (solo) | User mentions “Amazon cart”, “DoorDash order”, “UberEats receipt”, etc. | `GET /knot/transactions?merchant=Amazon|DoorDash|UberEats` | Knot is only called for merchants it supports (these whitelisted commerce providers). Generic banking questions bypass Knot. |
| Group expense split | Chat intent “split” inside group | `GET /knot/transactions` (merchant filter) + Dedalus Smart Split agent | Only call Knot if we need actual transaction amounts; otherwise rely on user-provided numbers. |
| Card optimizer | Chat intent “card recommendation” | Dedalus Card Agent → Groq/Gemini fallback + optional `GET /knot/cards` for rewards data | Knot returns available cards + categories; AI chooses best. |
| Price tracker | Chat intent “price tracking / best time to buy” | Dedalus Price Agent + optionally X API for trend signals | No Knot call; data comes from agents + social context. |
| Insights dashboard | `/insights` route loads or refresh job runs | `POST /snowflake/sql` for aggregates; optionally X API for trend labels | Run server-side cron to cache results; UI hits cached data. |
| Social/trend lookup | User explicitly asks “What’s trending on X for flights?” | `GET /x/search` | Do **not** call X unless prompt contains relevant keywords; keep optional. |
| Settings, Groups, basic chat | Standard CRUD | No external calls (pure Postgres) | These flows stay internal. |

## 4. MCP / AI Agent Architecture

1. **Intent Detection**: Chat Orchestrator examines a message (keywords + conversation state) to decide if it’s:
   * Reasoning-heavy (card, split, tracker) → Dedalus agent.
   * General conversation → Groq/Gemini for completion.
2. **Dedalus MCP Servers**: Provide specialized workflows:
   * `CardGuru` agent: requires card catalog + merchant category input.
   * `SplitSense` agent: needs participant list + transaction data (from Knot when available).
   * `PriceOracle` agent: consumes product metadata + optional social trend signals (X API).
3. **Orchestration**:
   * API Gateway → Chat Orchestrator (persist message) → AI Broker.
   * AI Broker enriches context (calls Postgres, Knot, Snowflake, X per scenario) before invoking an MCP agent.
   * Agent returns structured payload: `{ content, reasoning[], action, drawerData }`.
   * Broker streams “thinking” stages back to frontend to drive animations (`frontend/app/chat/[id]/page.tsx`).

## 5. Route-by-Route Requirements & API Usage

### 3.1 Landing & Navigation (`frontend/app/page.tsx`, `components/app-navigation.tsx`)

* Minimal backend involvement other than exposing login/session endpoints so the navigation knows if a user is authenticated.
* Need `/api/session` (GET) → returns user profile snippet for header display.

### 3.2 Onboarding (`frontend/app/onboarding/page.tsx`)

* Button triggers “Connect with Knot” flow. Backend must expose:
  * `POST /api/onboarding/start` → server calls Knot Link API to create a token limited to supported commerce merchants (Amazon, UberEats, DoorDash, Lyft/Uber, etc.).
  * `POST /api/onboarding/complete` → exchanges the public token for access + stores linked accounts.
* After linking, backend marks `onboardingStatus=complete` so the UI can route to `/chat/main`.

### 3.3 Chat (`frontend/app/chat/[id]/page.tsx`)

**Data Needs**
* Messages (user + AI) with `thinking` stages and optional `action` (`card`, `split`, `tracker`).
* Group metadata (`members`, `chatId`) when `id` starts with `group`.
* Context drawer payloads (card optimizer data, smart split breakdown, price tracking stats).

**Required Endpoints**
* `GET /api/chats/{chatId}` → returns metadata + latest messages for initial render.
* `POST /api/chats/{chatId}/messages` → body `{ content, senderType }`. Backend:
  1. Saves the user message.
  2. Triggers Chat Orchestrator to call AI Broker.
  3. Streams thinking messages (optional SSE/WebSocket) or responds with final AI message + drawer payload.
* `GET /api/chats` → list chats for sidebar search (id, name, type, member count).

**Processing Flow & API Calls**
1. API receives user prompt.
2. Intent detection:
   * **Card** intent → fetch user’s card catalog from Postgres; optionally call Knot Rewards endpoint (if available) for real spend categories; never hits Knot if no merchant context.
   * **Split** intent → if message references supported merchants (Amazon, UberEats, DoorDash, Airbnb, etc.), call Knot transactions filtered by merchant and date range; otherwise use user-supplied totals.
   * **Price tracking** intent → no Knot call; instead gather product metadata + optional X API trend data.
   * **General chat** → no external data.
3. Chat Orchestrator enriches with group members (Postgres) + cached insights (Snowflake) as needed.
4. AI Broker selects Dedalus agent or Groq/Gemini:
   * Dedalus agent may synchronously query Knot data via the broker if not already fetched.
5. Broker emits thinking stages + final payload (with optional `drawerData` for card/split/tracker).
6. Context drawer helpers (`ContextDrawer` UI) expect the structured data returned by the agent; no extra API call on render.

### 3.4 Groups (`frontend/app/groups/page.tsx`, `components/create-group-dialog.tsx`)

**Frontend Expectations**
* List of active groups (name, members, context snippet, total spend).
* Ability to create group with name + invited emails (modal).

**Endpoints**
* `GET /api/groups` → `[{ id, name, members, lastActivity, context, totalSpend }]`.
* `POST /api/groups` → `{ name, members[] }` creates group, sends invites, returns new `id`.
* `GET /api/groups/{id}` → full detail for chat header.

**Data Sources**
* Member info stored in Postgres.
* `context` & `totalSpend` derived from Knot transactions filtered to group members’ consented merchants. If no Knot data, backend falls back to manual annotations or values entered during group creation.

### 3.5 Accounts (`frontend/app/accounts/page.tsx`)

**UI Shows**
* List of linked accounts with permissions and delete option.
* Sandbox status banner.

**Endpoints & Calls**
* `GET /api/accounts` → backend reads from Postgres first; only if cache older than 15 min does it call Knot’s `GET /accounts`.
* `DELETE /api/accounts/{accountId}` → server calls Knot revoke endpoint, then deletes local record.
* `GET /api/accounts/status` → pure internal flag (no external call).

### 3.6 Insights (`frontend/app/insights/page.tsx`)

**Needs**
* Cards listing optimization, spending trends, rewards reminders.
* Monthly summary text block.

**Backend & Calls**
* `GET /api/insights` → returns cached data refreshed every 15 minutes by a background job:
  1. Job runs `POST /snowflake/sql` queries (spend by category, rewards earned, group trend deltas).
  2. Optional call to X API if we need trending labels (e.g., “group spending up 23%” with reference to social chatter). Only made when insights mention trends/travel.
* `GET /api/insights/summary` → serves the latest cached summary; no live call.

### 3.7 Settings (`frontend/app/settings/page.tsx`)

* Sectioned view of account, connected accounts, preferences, security.
* Buttons currently inert; backend should expose:
  * `GET /api/settings` → structure matching `settingSections`.
  * `PATCH /api/settings` (per section) to update preferences.
* Sign-out should call `POST /api/logout`. No third-party APIs.

## 4. Data Model Sketch

```
User {
  id, name, email, onboardingStatus, preferences(jsonb), authProviderId
}

Chat {
  id, type ('solo' | 'group'), ownerId, title?
}

ChatMember {
  chatId, userId, role
}

Message {
  id, chatId, senderId/null, senderType ('user'|'ai'),
  content, thinking(json), action(enum), drawerData(json), createdAt
}

GroupContext {
  chatId, contextSummary, totalSpend, lastActivityAt
}

LinkedAccount {
  id, userId, institution, accountName, permissions(json), knotItemId
}
```

MVP can store everything in a single relational DB (Supabase, Neon, etc.).

## 5. External API Touchpoints

1. **Knot API (Commerce-Focused)**
   * Link/token lifecycle during onboarding.
   * Fetch accounts & permissions for `/accounts`.
   * Fetch transaction history **only** for supported merchants (Amazon, UberEats, DoorDash, Lyft/Uber, Airbnb) when a chat/group explicitly references them.
   * Pull rewards/category metadata for card optimizer.

2. **Dedalus Labs MCP Agents**
   * Provide specialized reasoning flows (card choice, smart split, tracker); require contextual payload assembled by the AI Broker.
   * Never call external APIs directly; they receive already-fetched data from the broker.

3. **Groq / Gemini**
   * General-purpose LLM completions for open-ended chat; fallback if Dedalus agents unavailable.

4. **X API**
   * Optional context (trending deals, travel chatter) when a message contains keywords like “trending on X/twitter” or “what are people saying”.
   * Use short-lived cached responses to avoid rate limits.

5. **Snowflake REST API**
   * Query aggregated spend/reward data to populate Insights cards and monthly summary.
   * Run only in background jobs or when the cache is stale, not on every page load.

## 6. Processing Pipelines

### Chat Message Pipeline
1. `POST /api/chats/{id}/messages` stores the user message.
2. Intent detection determines which external data is required:
   * Merchant-specific? → fetch Knot transactions (commerce merchants only).
   * Group spend? → use cached Snowflake insight + optional Knot data.
   * Trend question? → call X API.
   * Otherwise → no external call.
3. AI Broker orchestrates Dedalus/Groq/Gemini with the enriched context.
4. If card/split/tracker action detected, attach drawer payload returned by the agent (already informed by Knot/Snowflake data).
5. Save AI response + drawer payload, return to client.

### Group Creation
1. `POST /api/groups` validates emails, creates group chat, sends invites via email service.
2. Optionally pre-fetch Knot data for group members to compute shared budgets.

### Insights Refresh
1. Periodic job (CRON) pulls Snowflake metrics, stores in cache table.
2. `/api/insights` returns latest cached entries to front-end.

## 7. Non-Functional Requirements

* **Auth**: Basic email/pass or OAuth; all endpoints require auth except landing/onboarding start.
* **Rate Limiting**: Simple per-user limiter to protect third-party APIs.
* **Logging**: Request/response logs, especially around AI Broker and Knot interactions.
* **Feature Flags**: Toggle between mock and live integrations to match hackathon demos.

## 8. Next Steps

1. Stand up a single backend app with modules that mirror the services above.
2. Implement read-only endpoints first (returning mocked data) to unblock the frontend.
3. Gradually wire real integrations starting with Knot (accounts) and a single LLM provider.
4. Document each endpoint contract in OpenAPI so frontend and backend stay in sync.

This plan ensures the backend aligns with all current frontend expectations while keeping scope realistic for the MVP.
