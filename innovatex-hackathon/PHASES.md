# PHASES.md — Implementation Breakdown

This document defines the **9-phase implementation plan** for the *Diagnóstico Ley 1581 de 2012* platform (React + Vite + Tailwind + shadcn/ui frontend, FastAPI backend, PostgreSQL, Docker). It is a granular, file-anchored expansion of the high-level *Orden de Implementación* in `PLAN.md`.

> Conventions
> - Backend path prefix: `backend/app/`
> - Frontend path prefix: `frontend/src/`
> - Effort sizes: **Small** (< 1 day) · **Medium** (1–3 days) · **Large** (3–7 days)
> - Each phase is independently demoable and merges into `main`.

---

## Phase 1: Project Setup & Infrastructure

**Objective:** Provide a fully containerized, runnable skeleton (backend + frontend + DB + reverse proxy) with OAuth login working end-to-end.

**Dependencies:** None. This is the foundation.

**Tasks:**
- Create `docker-compose.yml` with four services: `postgres` (PostgreSQL 16), `backend` (FastAPI), `frontend` (Vite dev/prod), `nginx` (reverse proxy).
- Create `backend/Dockerfile` (Python 3.12-slim, uvicorn, non-root user).
- Create `frontend/Dockerfile` (node:20, multi-stage build → nginx static).
- Create `nginx/nginx.conf` defining `/api/` → backend upstream and `/` → frontend upstream, plus WebSocket-friendly upgrade headers.
- Initialize FastAPI app in `backend/app/main.py` with lifespan, CORS, and router includes stubbed.
- Create `backend/app/config.py` using `pydantic-settings` (`Settings` class reading `DATABASE_URL`, `JWT_SECRET`, `JWT_ALG`, `JWT_EXP_MINUTES`, `JWT_REFRESH_EXP_DAYS`, `GOOGLE_CLIENT_ID/SECRET`, `MICROSOFT_CLIENT_ID/SECRET`, `AI_PROVIDER`, `*_AI_API_KEY`).
- Create `backend/app/database.py` with SQLAlchemy `engine`, `SessionLocal`, `Base` (postgresql+psycopg dialect).
- Create `backend/requirements.txt` pinning `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `psycopg[binary]`, `alembic`, `pydantic-settings`, `authlib`, `python-jose`, `passlib`, `httpx`, `python-multipart`.
- Initialize Alembic: `backend/alembic.ini`, `backend/alembic/env.py` (autogenerate import target metadata → `Base.metadata`), empty `backend/alembic/versions/`.
- Scaffold React + Vite: `frontend/package.json` (react, react-router-dom, axios, zustand, @tanstack/react-query, recharts, tailwind, shadcn/ui deps), `frontend/vite.config.ts` (proxy `/api` → backend), `frontend/tsconfig.json`, `frontend/tailwind.config.ts`, `frontend/index.html`.
- Initialize shadcn/ui in `frontend/src/components/ui/` (`button`, `input`, `dialog`, `card`, `toast`).
- Implement OAuth2 flow in `backend/app/routers/auth.py` (`GET /api/auth/login/google`, `GET /api/auth/login/microsoft`, `GET /api/auth/callback/google`, `GET /api/auth/callback/microsoft`) and `backend/app/services/auth_service.py` (exchange code → userinfo → upsert user → issue access + refresh JWT).
- Create `frontend/src/pages/LoginPage.tsx` with two OAuth buttons (Google, Microsoft) hitting backend login routes.
- Create `frontend/src/api/client.ts` (axios instance with JWT interceptor + refresh logic).

**Deliverables:**
- Files: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `nginx/nginx.conf`, `backend/app/{main.py,config.py,database.py}`, `backend/requirements.txt`, `backend/alembic/*`, `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tailwind.config.ts`, `frontend/index.html`, `frontend/src/pages/LoginPage.tsx`, `frontend/src/api/client.ts`.
- Endpoints: 4 auth redirect/callback endpoints.
- DB tables: none yet (Alembic baseline only).

**Acceptance Criteria:**
- `docker-compose up` starts all four services; `http://localhost` renders `LoginPage`.
- Clicking "Login with Google" redirects to Google, returns with a valid JWT pair stored in frontend.
- `GET /api/health` returns `{"status":"ok"}` through nginx.
- `alembic upgrade head` runs without error (empty schema).

**Estimated Effort:** Large

**Key Decisions & Risks:**
- *Decision:* Use `authlib` instead of writing raw OAuth flows to reduce boilerplate.
- *Decision:* JWT access + refresh (not session cookies) to keep backend stateless and scalable.
- *Risk:* OAuth provider approval can take time → keep test-mode user provisioning in `auth_service.py` for local dev.
- *Risk:* Windows filesystem performance on mounted volumes → document optional named-volume override in `docker-compose.yml`.

---

## Phase 2: Models + Base API (Users, Companies, Roles, CRUD)

**Objective:** Persist the full domain model and expose CRUD APIs with multi-tenant isolation and frontend authentication wiring.

**Dependencies:** Phase 1 (DB engine, Alembic, OAuth, frontend scaffold).

**Tasks:**
- Create SQLAlchemy models in `backend/app/models/`:
  - `user.py` (`User`: id, email, name, provider, provider_id, created_at, updated_at)
  - `company.py` (`Company` + `UserCompanyRole` tenant join with role enum admin/auditor/reader)
  - `assessment.py` (`Assessment`, `AssessmentAnswer`, `Score`)
  - `question.py` (`Section`, `Question`)
  - `recommendation.py` (`Recommendation`, `ShareLink`)
  - `action_item.py` (`ActionItem`)
- Create Pydantic schemas in `backend/app/schemas/`: `user.py`, `company.py`, `assessment.py`, `question.py`, `report.py`.
- Generate + author Alembic migration creating all tables, indexes (`user.email` unique, `share_links.token` unique), and FKs.
- Implement multi-tenant middleware in `backend/app/middleware/tenant_middleware.py` (resolve `current_company_id` from JWT claim + header) and `backend/app/middleware/auth_middleware.py` (JWT validation, inject `current_user`).
- Implement routers:
  - `auth.py`: `POST /api/auth/refresh`, `POST /api/auth/logout`, `GET /api/auth/me`.
  - `users.py`: `GET /api/users/me`, `PATCH /api/users/me`, `GET /api/users` (admin only, scoped to company).
  - `companies.py`: `POST /api/companies`, `GET /api/companies`, `GET /api/companies/:id`, `PATCH /api/companies/:id`.
  - `roles.py` (subset of `companies.py` or separate file): assign/update/delete `UserCompanyRole`.
- Frontend:
  - Create `frontend/src/stores/authStore.ts` (zustand: user, tokens, company selection).
  - Create `frontend/src/api/companies.ts`, `users.ts`.
  - Build protected route wrapper `frontend/src/components/layout/ProtectedRoute.tsx`.
  - Build `frontend/src/pages/CompanyProfilePage.tsx`, `CompanySwitchPage.tsx`, `AdminUsersPage.tsx`.
  - Build layout shell `frontend/src/components/layout/{Header,Sidebar,Layout}.tsx`.

**Deliverables:**
- DB tables: `users`, `companies`, `user_company_roles`, `assessments`, `assessment_answers`, `sections`, `questions`, `scores`, `recommendations`, `action_items`, `share_links`.
- Endpoints: auth (3), users (3), companies (4), roles (3).
- Frontend pages: CompanyProfile, CompanySwitch, AdminUsers + global layout.

**Acceptance Criteria:**
- Authenticated request to `/api/users` returns only users from the requester's current company.
- Creating a second company and switching via `/company/switch` isolates data between tenants.
- Role enforcement: a `reader` calling `POST /api/companies` is rejected with 403.
- `alembic upgrade head` produces all 11 tables with correct FKs.

**Estimated Effort:** Large

**Key Decisions & Risks:**
- *Decision:* Resolve tenant from JWT claim + optional header (not subdomain) for MVP simplicity.
- *Decision:* Soft cascade deletes (`ON DELETE RESTRICT`) to preserve audit trail.
- *Risk:* Forgot to scope a query → leak across tenants. Mitigate with a `TenantQuery` SQLAlchemy helper in `database.py` that auto-applies company filter.

---

## Phase 3: Questionnaire (Sections, Questions, Answers, Auto-save)

**Objective:** Allow a user to start an assessment, navigate 10 sections / 43 questions freely, answer them, and have progress auto-saved.

**Dependencies:** Phase 2 (Assessment + Answer models, tenant isolation).

**Tasks:**
- Seed data: create `backend/app/seeds/questions_seed.py` defining 10 sections and 43 questions exactly per `PLAN.md` (legal references, `ai_explanation_prompt` per question).
- Routers:
  - `questions.py`: `GET /api/sections`, `GET /api/sections/:id/questions`, `GET /api/questions/:id`.
  - `assessments.py`: `POST /api/assessments` (create in_progress), `GET /api/assessments/:id`, `GET /api/assessments`, `PUT /api/assessments/:id` (status → completed), `DELETE /api/assessments/:id`.
  - `answers.py` (inside assessments router): `POST /api/assessments/:id/answers` (upsert), `GET /api/assessments/:id/answers`.
- Service layer: `backend/app/services/assessment_service.py` (start/complete, answer upsert with idempotency on (assessment_id, question_id)).
- Frontend:
  - `frontend/src/pages/AssessmentPage.tsx` orchestrating a single assessment.
  - `frontend/src/components/assessment/SectionNav.tsx` (sidebar of 10 sections with per-section completion dot).
  - `frontend/src/components/assessment/QuestionCard.tsx` (Sí / No / Parcial / N/A buttons + notes textarea).
  - `frontend/src/components/assessment/ProgressBar.tsx` (global + section progress).
  - `frontend/src/hooks/useDebounce.ts` (500ms) + `useAutosaveAnswers.ts` calling `POST /api/assessments/:id/answers`.
  - Free navigation: route `/assessment/:id` with section query param; no forced linear order.

**Deliverables:**
- DB rows: 10 sections + 43 seeded questions.
- Endpoints: 3 question + 5 assessment + 2 answer endpoints.
- Frontend: AssessmentPage with working auto-save + progress.

**Acceptance Criteria:**
- A new assessment returns empty answers; answering ~half the questions shows ~50% progress.
- Auto-save fires ≤500ms after each change; reload保留了 all answers.
- Completing all sections and calling `PUT /api/assessments/:id` with `status=completed` succeeds; incomplete returns 422.
- Tenant isolation: cannot fetch another company's assessment (404).

**Estimated Effort:** Large

**Key Decisions & Risks:**
- *Decision:* Upsert answers by composite key `(assessment_id, question_id)` to keep auto-save idempotent.
- *Decision:* Allow completion only when all non-optional questions answered (rules in `assessment_service.py`).
- *Risk:* Race conditions from rapid auto-save writes → use `INSERT ... ON CONFLICT DO UPDATE` per-question, not bulk.

---

## Phase 4: Scoring (Section + Global, Percentage, Maturity Matrix)

**Objective:** Compute per-section and global compliance scores, derive a maturity level, and surface results in the UI.

**Dependencies:** Phase 3 (answers persisted).

**Tasks:**
- Create `backend/app/services/scoring_service.py`:
  - Per-question map: `Sí=1.0`, `Parcial=0.5`, `No=0.0`, `N/A` excluded from denominator.
  - Section score = `sum / count(answered non-na)`.
  - Global = simple average across sections (equal weights, per PLAN).
  - Maturity classification per thresholds in PLAN's *Lógica de Scoring*.
- Persist rows into `scores` table (section_id, score, max_score, percentage, maturity).
- Hook scoring into `assessment_service.complete_assessment()` (trigger on `PUT /api/assessments/:id` status=completed).
- Endpoints: `GET /api/assessments/:id/scores`, `GET /api/assessments/:id/results` (aggregate: scores + metadata).
- Frontend:
  - `frontend/src/pages/ResultsPage.tsx`.
  - `frontend/src/components/dashboard/ScoreCard.tsx` (global % + maturity label/badge).
  - Section-by-section breakdown card.

**Deliverables:**
- Service: `scoring_service.py`.
- Endpoints: scores + results.
- Frontend: ResultsPage with ScoreCard + section breakdown.

**Acceptance Criteria:**
- A fully-completed all-"Sí" assessment scores 100% → "Optimizado".
- A fully-"No" assessment scores 0% → "No existe".
- "Parcial" averages correctly (e.g., 2 Sí + 2 Parcial + 0 No in a 4-question section = 75%).
- N/A questions do not inflate or deflate percentages.
- Recompleting an assessment recomputes and replaces `scores` rows, not duplicates.

**Estimated Effort:** Medium

**Key Decisions & Risks:**
- *Decision:* Store scale in `scores` and recompute on completion (no partial in-progress scoring) to avoid drift.
- *Risk:* Maturity thresholds off-by-one at boundary 20/40/60/80 → encode in a single constants module to make tests assertive.

---

## Phase 5: AI Integration (Agnostic Layer, Real-time + Final Recommendations)

**Objective:** Provide an interchangeable AI layer that (a) reveals contextual explanations per question/suggested answer during the assessment, and (b) generates prioritized recommendations + action items at completion.

**Dependencies:** Phase 3 (questions), Phase 4 (results).

**Tasks:**
- Define `backend/app/ai/base.py` with `AIService` Protocol: `explain_question`, `suggest_answer`, `generate_recommendations`, `generate_action_plan`.
- Implement providers:
  - `openai_provider.py` (httpx/chat-completions).
  - `anthropic_provider.py` (messages API).
  - `gemini_provider.py` (generative models API).
- Provider factory in `backend/app/ai/__init__.py` selected from `Settings.AI_PROVIDER` (env-driven, hot-swappable).
- Build prompts in `backend/app/ai/prompts.py` using `question.legal_reference`, `question.ai_explanation_prompt`, `Company` context (sector, size, data types), and prior answers for suggestions.
- Routers:
  - `ai_router` mounted under `routers/`: `POST /api/ai/explain` (per question), `POST /api/ai/suggest` (per question).
  - Extend `assessments.py`: `POST /api/assessments/:id/generate-recommendations` → writes rows into `recommendations` (priority high/medium/low) and seeds `action_items`.
- Frontend:
  - Add "Explicar" and "Sugerir" buttons inside `QuestionCard.tsx`.
  - `ExplainModal.tsx` showing streamed/loaded explanation.
  - `frontend/src/pages/RecommendationsPage.tsx` rendering AI recommendations by section + priority.
  - Display fallback/legal reference text if AI call fails.

**Deliverables:**
- Files: `ai/{base,openai_provider,anthropic_provider,gemini_provider}.py`, `ai/prompts.py`.
- Endpoints: explain, suggest, generate-recommendations.
- Frontend: explain modal, suggest button, RecommendationsPage.

**Acceptance Criteria:**
- Changing `AI_PROVIDER=anthropic` (vs `openai`) without code change swaps the active provider.
- "Explicar" returns a domain-relevant response referencing the question's legal_reference.
- "Sugerir" returns a recommended answer consistent with prior answers.
- Generate-recommendations produces ≥1 recommendation per failed/partial section and creates matching `action_items`.
- If provider is unreachable, endpoints degrade gracefully (503 + legal-ref fallback in UI).

**Estimated Effort:** Large

**Key Decisions & Risks:**
- *Decision:* Protocol-based (duck typing) layer so adding a 4th provider needs no core change.
- *Decision:* Company context injected into every prompt to keep answers organization-aware.
- *Risk:* Cost & latency → cache explanations per question+context hash in Redis (or skip in MVP and document).
- *Risk:* Hallucinated legal citations → explicitly instruct prompts to cite only provided `legal_reference`.

---

## Phase 6: Reports (PDF, Excel, Shareable Links)

**Objective:** Export an assessment as a formal PDF and detailed Excel, and produce a tokenized expiring share link.

**Dependencies:** Phase 4 (scores), Phase 5 (recommendations).

**Tasks:**
- `backend/app/reports/pdf_generator.py` using `reportlab`:
  - Cover page (company name, NIT, sector, date).
  - Global score + maturity badge.
  - Radar chart per section (use `reportlab.graphics.charts.radar`).
  - Prioritized recommendations list.
  - Action items summary.
- `backend/app/reports/excel_generator.py` using `openpyxl`:
  - Sheet 1: metadata + global result.
  - Sheet 2: per-question rows (section, question, answer, score contribution, notes).
  - Sheet 3: recommendations + action items.
- `ShareLink` model usage: `POST /api/assessments/:id/share` (creates token + `expires_at`), `GET /api/share/:token` (validates expiry, returns read-only result payload).
- Routers in `reports.py`: `GET /api/assessments/:id/export/pdf` (StreamingResponse), `GET /api/assessments/:id/export/excel`, share endpoints.
- Frontend `frontend/src/pages/ExportPage.tsx`:
  - Buttons "Descargar PDF" / "Descargar Excel".
  - "Crear link compartible" → copies URL; expiry indicator.
  - Shared view route `/share/:token` rendering read-only ResultsPage.

**Deliverables:**
- Generators: `pdf_generator.py`, `excel_generator.py`.
- Endpoints: export PDF, export Excel, create share link, consume share token.
- Frontend: ExportPage + public share view.

**Acceptance Criteria:**
- Downloaded PDF includes radar chart, global %, and top 3 recommendations.
- Excel opens with three correctly-named sheets and valid numeric cells.
- Share link works while token valid; after expiry returns 410 Gone.
- Only users with access to the assessment can create a share link (reader+ roles).

**Estimated Effort:** Medium

**Key Decisions & Risks:**
- *Decision:* Stream PDF/Excel from backend (don't store on disk) to keep backend stateless.
- *Decision:* Share tokens are opaque random UUIDs (not signed JWTs) so revocation is possible.
- *Risk:* Radar chart laid out incorrectly with 10 axes → pre-validate with golden dataset snippet.

---

## Phase 7: Action Plan (CRUD Items, Checklist, Assignment)

**Objective:** Track each recommendation as an actionable item with status transitions, assignment, and notes.

**Dependencies:** Phase 5 (recommendations generate action items).

**Tasks:**
- Routers in `action_plans.py`:
  - `GET /api/assessments/:id/action-items` (paginated, filter by status).
  - `POST /api/action-items` (manual add).
  - `PUT /api/action-items/:id` (edit title/notes).
  - `PATCH /api/action-items/:id/status` (`pending` → `in_progress` → `completed`).
  - `POST /api/action-items/:id/assign` (assign to a company user).
- Service `backend/app/services/action_plan_service.py` enforcing status transitions and assignment validations.
- Frontend:
  - `frontend/src/pages/ActionPlanPage.tsx`.
  - `frontend/src/components/action-plan/ActionItem.tsx` (inline status toggle, assignee dropdown, notes editor).
  - `frontend/src/components/action-plan/ChecklistView.tsx` (grouped by recommendation/section, progress summary).

**Deliverables:**
- Endpoints: 5 action-plan endpoints.
- Frontend: ActionPlanPage with interactive checklist.

**Acceptance Criteria:**
- A recommendation converted to action item appears in the checklist.
- Status changes persist and trigger a progress % at the page header.
- Assigning a user outside the company is rejected (403).
- Lector role can view but cannot mutate (403 on PATCH).

**Estimated Effort:** Small

**Key Decisions & Risks:**
- *Decision:* Status is a small enum with explicit transition checks (no dates per PLAN MVP).
- *Risk:* Concurrent status updates on the same item → last-write-wins with optimistic re-fetch; document accordingly.

---

## Phase 8: Dashboard (Charts, History, Full UI)

**Objective:** Give Admin/Auditor a unified company dashboard with trends, latest score, and historical assessments.

**Dependencies:** Phases 2–7 (data exists to visualize).

**Tasks:**
- Endpoint `GET /api/dashboard` returning aggregated payload: latest assessment summary, score trend over time, section averages, action-plan progress, counts.
- Endpoint `GET /api/assessments` extended with pagination + filtering (status, date range) for history.
- Frontend:
  - `frontend/src/pages/DashboardPage.tsx`.
  - `frontend/src/components/dashboard/ScoreCard.tsx` (reuse from Phase 4).
  - `frontend/src/components/dashboard/RadarChart.tsx` (recharts radar across sections).
  - `frontend/src/components/dashboard/TrendChart.tsx` (recharts line over assessments).
  - `frontend/src/pages/HistoryPage.tsx` (paginated list linked to past results).
  - Loading skeletons, empty states, error boundaries.
  - Polish navigation in `Header`/`Sidebar` (active route highlight, role-aware links).

**Deliverables:**
- Endpoint: `/api/dashboard` + paginated assessments.
- Frontend: DashboardPage, HistoryPage, chart components.

**Acceptance Criteria:**
- Dashboard renders within 2s of login for a company with ≥3 historical assessments.
- TrendChart plots score % across historical assessments in chronological order.
- RadarChart matches the latest assessment's per-section scores.
- Empty state appears when company has zero assessments (no broken charts).

**Estimated Effort:** Medium

**Key Decisions & Risks:**
- *Decision:* Pre-aggregate `/api/dashboard` server-side to limit client payload.
- *Risk:* recharts radar with 10 axes may overlap labels → render with rotated labels and minimum chart height.

---

## Phase 9: Security & Polish (OWASP, Responsive, Validation)

**Objective:** Harden the platform against OWASP Top 10, ensure responsive accessibility, and finalize UX polish.

**Dependencies:** All prior phases (feature-complete surface to harden).

**Tasks:**
- **Rate limiting**: add `slowapi` middleware with per-route limits (auth refresh strict, AI routes very strict).
- **Input validation**: confirm every Pydantic schema has `Field` constraints (lengths, enums, regex for NIT/email).
- **CORS**: lock `Settings.CORS_ORIGINS` to allowed domains only (no wildcard in prod).
- **HTTPS enforcement**: nginx redirects 80→443; FastAPI `TrustedHostMiddleware`.
- **Error handling**: standard `backend/app/errors.py` with `AppException` → unified JSON envelope `{type, message, details}`; map all 401/403/404/422/500.
- **Sanitization**: persist notes with escaped output; reject SSRF on any user-supplied URLs.
- **Secrets**: verify no secrets in repo, all via `.env`/Settings; add `backend/.env.example` and `frontend/.env.example`.
- **Responsive audit**: test all pages at 360 / 768 / 1280px breakpoints; collapse Sidebar to drawer on mobile.
- **Accessibility**: keyboard nav through QuestionCard/ActionItem, ARIA labels, color-contrast ≥ AA.
- **Loading skeletons & toasts**: skeleton components for dashboard/results; `useToast` for success/error feedback.
- **OWASP checklist**: verify SQLi (ORM only), XSS (React escaping + no `dangerouslySetInnerHTML` on user data), IDOR (tenant scoping), CSRF (JWT bearer), broken auth (refresh rotation), security headers in nginx.
- **CI skeleton**: `.github/workflows/ci.yml` running `ruff`, `mypy` (backend), `tsc`, `eslint`, `vitest` (frontend) on PRs.

**Deliverables:**
- `backend/app/errors.py`, `backend/.env.example`, `frontend/.env.example`, rate-limit config, updated `nginx.conf` (security headers), `.github/workflows/ci.yml`.
- Updated pages with skeletons, toasts, responsive layouts.

**Acceptance Criteria:**
- Burp/ZAP scan yields no High findings; rate limit returns 429 after threshold.
- Lighthouse mobile accessibility score ≥ 90 on Dashboard & Assessment pages.
- All endpoints reject malformed input with 422 + structured error.
- Tenant A cannot read tenant B's data by ID manipulation (404 not 403 — no existence leak).
- `docker-compose -f docker-compose.prod.yml up` exits cleanly behind HTTPS self-signed cert.

**Estimated Effort:** Medium

**Key Decisions & Risks:**
- *Decision:* Use opaque 404s (not 403) for cross-tenant resource access to avoid enumeration.
- *Decision:* Adopt slowapi now vs FastAPI native (still experimental) for stability.
- *Risk:* AI endpoint abuse / cost runaway → enforce strict rate limit + per-company daily token cap in `ai/__init__.py`.
- *Risk:* A11y regressions when adding new chart libraries → keep an automated axe-core run in CI.

---

## Phase Summary Matrix

| # | Phase | Effort | Demoable Outcome |
|---|-------|--------|------------------|
| 1 | Setup & Infra | Large | OAuth login working in Docker |
| 2 | Models + Base API | Large | Multi-tenant CRUD + admin users UI |
| 3 | Questionnaire | Large | Full 43-question flow with auto-save |
| 4 | Scoring | Medium | Maturity matrix + results page |
| 5 | AI Integration | Large | Explain/Suggest + final recommendations |
| 6 | Reports | Medium | PDF + Excel + share links |
| 7 | Action Plan | Small | Trackable checklist with assignment |
| 8 | Dashboard | Medium | Charts, trend, history |
| 9 | Security + Polish | Medium | OWASP-clean, responsive, a11y-grade app |

---

## Cross-Cutting Conventions (apply across all phases)

- **Commit hygiene:** conventional commits (`feat(assessment):`, `fix(auth):`, `chore(docker):`).
- **Testing:** backend `pytest` ≥ 70% coverage per module; frontend `vitest`+RTL for components/hooks; Playwright smoke for flows (auth → assess → results → export).
- **Migrations:** never edit a committed Alembic revision; always new revision.
- **Tenancy:** every new SQL query goes through `TenantQuery`/scoped session — no raw `.query(...)` without company filter.
- **Env:** every new setting added to `config.py` must also appear in `.env.example`.
- **API versioning:** all routers under `/api` (no explicit `/v1` for MVP — document note if changed).
- **Documentation:** each phase ends with an updated `README.md` section + OpenAPI auto-diff in CI.

---

*End of PHASES.md*
