# Backend Requirements From Frontend Surfaces

This document summarizes every backend capability implied by the current Next.js frontend (`frontend/app/**`). Use it as the contract for the MVP server stack we need to implement.

## 1. High-Level Goals

1. Serve authenticated users who can chat with AI assistants, alone or in groups.
2. Coordinate multiple AI providers (Dedalus Labs agents, Groq, Gemini) and financial APIs (Knot, X API, Snowflake REST).
3. Provide CRUD + query endpoints for groups, chats, accounts, insights, and settings.
4. Keep the design simple enough for a hackathon MVP while leaving room to evolve.

## 2. Core Services & Responsibilities

| Service | Primary Responsibilities | External Dependencies |
| --- | --- | --- |
| API Gateway / BFF | Authn/z, request validation, response shaping for the Next frontend | Frontend, Auth provider |
| Chat Orchestrator | Persist chat threads, fan out to AI Broker, emit structured replies (`content`, `thinking`, `action`) | AI Broker, Group Service |
| AI Broker | Route prompts to Dedalus agents, Groq, or Gemini; enforce safety + retries | Dedalus runtime, Groq, Gemini |
| Group Service | Manage group metadata, memberships, invites, shared context | Postgres |
| Knot Integration | Link accounts, fetch permissions, surface status for `/accounts` + onboarding | Knot API |
| Insights Service | Pull Snowflake datasets, compute optimizations, expose summaries | Snowflake REST API |
| Settings / Profile Service | Store user prefs (notifications, AI toggles) & security options | Postgres |

All of these services can live inside a single backend app for the MVP, but the boundaries clarify modules/classes we need.

## 3. Route-by-Route Requirements

### 3.1 Landing & Navigation (`frontend/app/page.tsx`, `components/app-navigation.tsx`)

* Minimal backend involvement other than exposing login/session endpoints so the navigation knows if a user is authenticated.
* Need `/api/session` (GET) → returns user profile snippet for header display.

### 3.2 Onboarding (`frontend/app/onboarding/page.tsx`)

* Button triggers “Connect with Knot” flow. Backend must expose:
  * `POST /api/onboarding/start` → returns Knot link token.
  * `POST /api/onboarding/complete` → exchanges public token, stores linked accounts.
* After linking, frontend expects redirect to `/chat/main`. Backend should mark onboarding status to bypass future prompts.

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

**Processing Flow**
1. API receives user prompt.
2. Collect context: group members, recent transactions (via Knot), insights (via Snowflake), previous AI steps.
3. AI Broker selects Dedalus agent when reasoning chain is needed; fall back to Groq/Gemini for generic answers.
4. Orchestrator saves AI response, flags `action` if card/split/tracker details are attached.
5. If `action` exists, call the corresponding helper to compute structured data for the drawer.

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
* `context` & `totalSpend` derived from Knot transactions or manual annotations (MVP can stub).

### 3.5 Accounts (`frontend/app/accounts/page.tsx`)

**UI Shows**
* List of linked accounts with permissions and delete option.
* Sandbox status banner.

**Endpoints**
* `GET /api/accounts` → list accounts (`name`, `institution`, `permissions`).
* `DELETE /api/accounts/{accountId}` → revoke integration via Knot.
* `GET /api/accounts/status` → indicates sandbox vs production mode.

### 3.6 Insights (`frontend/app/insights/page.tsx`)

**Needs**
* Cards listing optimization, spending trends, rewards reminders.
* Monthly summary text block.

**Backend**
* `GET /api/insights` → returns array with type, title, description, metrics. Implement by querying Snowflake REST API (or mock dataset) and applying business rules.
* `GET /api/insights/summary` → text summary string.

### 3.7 Settings (`frontend/app/settings/page.tsx`)

* Sectioned view of account, connected accounts, preferences, security.
* Buttons currently inert; backend should expose:
  * `GET /api/settings` → structure matching `settingSections`.
  * `PATCH /api/settings` (per section) to update preferences.
* Sign-out should call `POST /api/logout`.

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

1. **Knot API**
   * Create Link sessions (`/onboarding/start`).
   * Exchange tokens and sync accounts.
   * Fetch transactions to inform splits/insights.

2. **Dedalus Labs Agents**
   * Provide specialized reasoning flows (card choice, smart split, tracker). Expect to send contextual payload + get structured output (content + drawer data).

3. **Groq / Gemini**
   * General-purpose completions; use as fallback models in the AI Broker.

4. **X API**
   * Optional context (social signals, trending offers). Wrap in caching layer to respect rate limits.

5. **Snowflake REST API**
   * Query aggregated spend/reward data to populate Insights cards and monthly summary.

## 6. Processing Pipelines

### Chat Message Pipeline
1. `POST /api/chats/{id}/messages` stores the user message.
2. Push job into in-process queue (or direct call for MVP).
3. AI Broker orchestrates Dedalus/Groq/Gemini calls.
4. If card/split/tracker action detected, enrich with Knot/Snowflake data.
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
