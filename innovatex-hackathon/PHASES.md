# PHASES.md — Implementation Breakdown

This document defines the **9-phase implementation plan** for the *Diagnóstico Ley 1581 de 2012* platform (React + Vite + Tailwind + shadcn/ui frontend, FastAPI backend, PostgreSQL, Docker). It is a granular, file-anchored expansion of the high-level *Orden de Implementación* in `PLAN.md`.

> Conventions
> - Backend path prefix: `backend/app/`
> - Frontend path prefix: `frontend/src/`
> - Effort sizes: **Small** (< 1 day) · **Medium** (1–3 days) · **Large** (3–7 days)
> - Each phase is independently demoable and merges into `main`.

---

## Phase 1: Project Setup & Infrastructure 🟢 COMPLETED

**Objective:** Provide a fully containerized, runnable skeleton (backend + frontend + DB) with Supabase Auth login working end-to-end.

**Dependencies:** None.

**Tasks:**
- ✅ Create `docker-compose.yml` with backend service (postgres, frontend, nginx removed in Phase 2 Path B).
- ✅ Create `backend/Dockerfile` (Python 3.12-slim, UV package manager, non-root user).
- ✅ Create `frontend/Dockerfile` (node:20).
- ✅ Create `nginx/nginx.conf` (disabled for local dev).
- ✅ Initialize FastAPI app in `backend/app/main.py` with lifespan, CORS, router includes.
- ✅ Create `backend/app/config.py` using `pydantic-settings`.
- ✅ Create `backend/app/database.py` with SQLAlchemy `engine`, `SessionLocal`, `Base`.
- ✅ Dependencies via `pyproject.toml` + UV (not requirements.txt).
- ✅ Initialize Alembic: `backend/alembic.ini`, `backend/alembic/env.py`.
- ✅ Scaffold React + Vite: `frontend/package.json`, `vite.config.ts`, Tailwind, shadcn/ui.
- ✅ Supabase Auth: email/password login + register (NOT OAuth2 — Path B decision).
- ✅ Frontend: `LoginPage.tsx`, `RegisterPage.tsx`.
- ✅ Frontend: `api/client.ts` (Axios + JWT interceptor + refresh logic).
- ✅ Frontend: `stores/authStore.ts` (Zustand: session, user, init, signOut).
- ✅ Backend: `dependencies.py` (Supabase JWT verification ES256 via JWKS).
- ✅ Backend: `routers/auth.py` (`GET /api/auth/me`, `GET /api/auth/verify`).

**Deliverables:**
- All infrastructure files created.
- Auth: Supabase email/password working. JWT verification in backend.
- Frontend skeleton with login/register pages.

**Key Decisions:**
- *Auth:* Supabase Auth (email/password + JWT) instead of OAuth2 (Google/Microsoft).
- *Package manager:* UV instead of pip/requirements.txt.
- *DB:* PostgreSQL 16 (initially Docker, later migrated to Supabase managed in Phase 2).

---

## Phase 2: Models + Base API (Companies, Onboarding, Roles) 🟢 COMPLETED

**Objective:** Persist the full domain model (11 tables) on Supabase managed PostgreSQL, expose Companies CRUD API with tenant isolation, and wire frontend onboarding flow.

**Dependencies:** Phase 1 (Supabase Auth, FastAPI, Alembic, frontend skeleton).

**Architecture Decision (Path B):** Use Supabase's managed PostgreSQL instead of Docker PostgreSQL. `profiles` table references `auth.users(id)` directly (same database). Backend connects via Supabase pooler (IPv4) for runtime and direct connection for Alembic DDL.

**Tasks:**
- ✅ Config: Dual DATABASE_URL (direct for Alembic, pooler for FastAPI). `.env` updated.
- ✅ `docker-compose.yml`: Removed postgres service. Backend only.
- ✅ `entrypoint.sh`: alembic upgrade head → seed → uvicorn (idempotent, safe on every start).
- ✅ SQLAlchemy models (11 tables) in `backend/app/models/`:
  - `profile.py` (`Profile`: id FK→auth.users, email, full_name, avatar_url)
  - `block.py` (`Block`: slug TEXT PK, title, weight, order_num) — 3 blocks
  - `question.py` (`Question`: slug TEXT PK, block_id FK, kind (gate/scale/validation), text, weight, gate_for JSON)
  - `company.py` (`Company`: name, nit UNIQUE, sector, size, created_by FK→profiles)
  - `company_member.py` (`CompanyMember`: company_id FK, profile_id FK, role ENUM, UNIQUE(company_id, profile_id))
  - `assessment.py` (`Assessment`: company_id, created_by, status, overall_score, completed_at NULLABLE)
  - `assessment_answer.py` (`AssessmentAnswer`: composite PK (assessment_id, question_id), polymorphic answer columns (scale_resp 0/35/70/100, gate_resp BOOLEAN, validation_resp BOOLEAN), CHECK constraints)
  - `score.py` (`Score`: assessment_id, block_id, score/max_score/percentage NUMERIC, UNIQUE(assessment_id, block_id))
  - `recommendation.py` (`Recommendation`: assessment_id, block_id, ai_generated_text, priority)
  - `action_item.py` (`ActionItem`: recommendation_id, assessment_id, title, status, assigned_to)
  - `share_link.py` (`ShareLink`: assessment_id, token UUID UNIQUE, expires_at, status)
- ✅ Enums: RoleEnum (admin/auditor/reader), AssessmentStatusEnum (draft/completed), QuestionKindEnum (gate/scale/validation), PriorityEnum, ActionItemStatusEnum, ShareLinkStatusEnum.
- ✅ Alembic migration: generated + applied to Supabase. All FKs RESTRICT (except profiles→auth.users CASCADE). NUMERIC for scores. NOT NULL on critical columns. updated_at on mutable tables. Indexes on FK columns. Composite UNIQUE constraints.
- ✅ Seed data: `backend/app/seeds/data.py` + `runner.py` — 3 blocks + 11 questions from Cuestionario_Diagnostico_Privacidad.md. Idempotent INSERT ON CONFLICT DO NOTHING.
- ✅ Audit fixes applied: ON DELETE RESTRICT throughout, NUMERIC for scores, NOT NULL constraints, composite UNIQUE, FK indexes, updated_at triggers, polymorphic answer columns.
- ✅ Backend API: `schemas/company.py` (CompanyCreate, CompanyRead), `services/company_service.py` (list, create with lazy profile upsert + admin auto-assign), `routers/companies.py` (GET /api/companies, POST /api/companies, GET /api/companies/{id}).
- ✅ JWT verification: JWKS fetch with kid matching. Fixed issuer check (removed — Supabase JWT iss includes /auth/v1 path).
- ✅ Containerized: `docker-compose up --build` starts backend, auto-migrates + seeds + serves.
- 🔄 Frontend:
  - ✅ Types updated (`Company`, `CompanyCreate`, removed `mock: true`).
  - ✅ `api/companies.ts` (list, create, get with field mapping).
  - ✅ `stores/companyStore.ts` (API-backed, no localStorage mock, auto-select first company).
  - ✅ `ProtectedRoute.tsx` (API-driven onboarding redirect).
  - ✅ `OnboardingPage.tsx` (real POST /api/companies, validation error display).
  - ✅ `DashboardPage.tsx` (company banner with "Empresa actual" label, NIT, sector, size).
  - ✅ `LoginPage.tsx` + `RegisterPage.tsx` (auto-redirect if already authenticated).
  - ✅ Axios interceptor: uses authStore session (not async getSession), retries on 401 with fresh token.

**Deliverables:**
- DB tables: 11 (profiles, blocks, questions, companies, company_members, assessments, assessment_answers, scores, recommendations, action_items, share_links).
- Seed data: 3 blocks + 11 questions from canonical Cuestionario_Diagnostico_Privacidad.md.
- Endpoints: GET/POST /api/companies, GET /api/companies/{id}.
- Frontend pages: Login, Register, Onboarding, Dashboard (with company display).
- Backend containerized: `docker-compose up --build` works end-to-end.

**Acceptance Criteria:**
- ✅ Authenticated GET /api/companies returns user's companies.
- ✅ POST /api/companies creates company + assigns creator as admin (role=admin in company_members).
- ✅ Profile auto-created on first API call (lazy upsert from JWT sub + email).
- ✅ Frontend onboarding creates real company via API → redirects to dashboard showing company name.
- ✅ alembic upgrade head produces all 11 tables with correct FKs, constraints, indexes.
- ✅ Login/Register pages auto-redirect to dashboard if already authenticated.

**Key Decisions:**
- *Canonical questionnaire:* `Cuestionario_Diagnostico_Privacidad.md` (3 blocks, 11 questions, scale 0/35/70/100). PLAN.md data model is superseded.
- *Profiles:* Lazy-upsert from JWT (no Supabase trigger for MVP — Option B deferred).
- *Scoring:* P1 gate (No → Bloque 1 = 0%). P2-P10 scale 0/35/70/100. P11 validation (weight 0). Final % = sum of raw points from P2-P10.
- *Maturity matrix:* 0-39% Crítico, 40-69% Básico, 70-89% Avanzado, 90-100% Optimizado.

---

## Phase 3: Questionnaire (Blocks, Questions, Answers, Auto-save) 🔵 STARTING

**Objective:** Allow a user to start an assessment, navigate 3 blocks / 11 questions freely, answer them (gate/scale/validation), and have progress auto-saved.

**Dependencies:** Phase 2 (Assessment + Answer models, tenant isolation, seed data).

**Model (canonical):** `Cuestionario_Diagnostico_Privacidad.md` — 3 blocks (Política 40%, Privacidad 36%, Gobernanza 24%), 11 questions (P1 gate, P2-P10 scale 0/35/70/100, P11 validation weight 0). Scoring: sum of raw points P2-P10 = final %. Gate: P1=No → Bloque 1 = 0%.

**Tasks:**
- 🔲 Seed data: already done in Phase 2 (`backend/app/seeds/data.py` — 3 blocks, 11 questions).
- 🔲 Routers:
  - `questions.py`: `GET /api/blocks`, `GET /api/blocks/{slug}/questions`, `GET /api/questions/{slug}`.
  - `assessments.py`: `POST /api/assessments` (create draft), `GET /api/assessments`, `GET /api/assessments/{id}`, `PUT /api/assessments/{id}` (status → completed).
  - `answers.py` (inside assessments router): `POST /api/assessments/{id}/answers` (upsert), `GET /api/assessments/{id}/answers`.
- 🔲 Service layer: `backend/app/services/assessment_service.py` (start/complete, answer upsert with idempotency on (assessment_id, question_id) composite PK).
- 🔲 Frontend:
  - `frontend/src/pages/AssessmentPage.tsx` orchestrating a single assessment.
  - `frontend/src/components/assessment/BlockNavigator.tsx` (sidebar of 3 blocks with progress).
  - `frontend/src/components/assessment/QuestionCard.tsx` (scale 0/35/70/100 buttons for scale questions, Sí/No for gate/validation, notes textarea).
  - `frontend/src/components/assessment/ProgressBar.tsx` (global + per-block progress).
  - Auto-save with debounce (500ms) via `POST /api/assessments/:id/answers`.
  - Free navigation between blocks (no forced linear order).
  - Gate logic: P1=No → P2-P5 grayed out with forced=0 (frontend already has applyGate in assessmentStore).

**Deliverables:**
- Endpoints: 3 block/question + 4 assessment + 2 answer endpoints.
- Frontend: AssessmentPage with working auto-save + progress + gate logic.

**Acceptance Criteria:**
- A new assessment returns empty answers; answering ~half the questions shows ~50% progress.
- Auto-save fires ≤500ms after each change; reload preserves all answers.
- Gate P1=No forces P2-P5 to 0 and disables those questions in the UI.
- Completing all 9 scored questions (P2-P10) and calling `PUT /api/assessments/{id}` with `status=completed` succeeds.
- Assessment uses polymorphic answer columns: scale_resp (0/35/70/100), gate_resp (bool), validation_resp (bool).

**Estimated Effort:** Large

**Key Decisions:**
- *Answer model:* Polymorphic columns per question kind (scale_resp, gate_resp, validation_resp) with CHECK constraints.
- *Gate logic:* Scoring computes Bloque 1 = 0% when P1=No (computed at completion, not persisted).
- *Seed data:* Already populated in Phase 2.

---

## Phase 4: Scoring (Block + Global, Percentage, Maturity Matrix)

**Objective:** Compute per-block and global compliance scores, derive a maturity level, and surface results in the UI.

**Dependencies:** Phase 3 (answers persisted).

**Tasks:**
- Create `backend/app/services/scoring_service.py`:
  - Per-question scale: 0/35/70/100 mapped to raw points (weight * scale/100).
  - Gate rule: P1=No → Bloque 1 = 0% regardless of P2-P5 answers.
  - Block score = sum of raw points for block's scale questions / max possible.
  - Global score = sum of P2-P10 raw points (weights sum to 100, so raw points = percentage).
  - Maturity classification: 0-39% Crítico, 40-69% Básico, 70-89% Avanzado, 90-100% Optimizado.
- Persist rows into `scores` table (block_id, score, max_score, percentage).
- Hook scoring into `assessment_service.complete_assessment()` (trigger on PUT status=completed).
- Endpoints: `GET /api/assessments/:id/scores`, `GET /api/assessments/:id/results`.
- Frontend: `ResultsPage.tsx` with ScoreCard + maturity badge + per-block breakdown.

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

| # | Phase | Effort | Demoable Outcome | Status |
|---|-------|--------|------------------|--------|
| 1 | Setup & Infra | Large | Supabase Auth (email/password) working in Docker | 🟢 DONE |
| 2 | Models + Base API | Large | 11 tables on Supabase, companies CRUD, onboarding UI | 🟢 DONE |
| 3 | Questionnaire | Large | 11-question flow (gate/scale/validation) with auto-save | 🔵 NEXT |
| 4 | Scoring | Medium | Maturity matrix + results page | ⬜ |
| 5 | AI Integration | Large | Explain/Suggest + final recommendations | ⬜ |
| 6 | Reports | Medium | PDF + Excel + share links | ⬜ |
| 7 | Action Plan | Small | Trackable checklist with assignment | ⬜ |
| 8 | Dashboard | Medium | Charts, trend, history | ⬜ |
| 9 | Security + Polish | Medium | OWASP-clean, responsive, a11y-grade app | ⬜ |

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
