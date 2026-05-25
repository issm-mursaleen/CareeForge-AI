# CareerForge AI — System Architecture

## 1. Product Vision

CareerForge AI is an AI-native career platform. It ingests resumes and job descriptions, runs them through a hybrid retrieval + LLM pipeline, and surfaces actionable insights for three user classes:

- **Candidates** — analyze their own resume, get ATS score, missing-skills report, role-fit guidance, AI-driven interview prep, and a personalised roadmap.
- **Recruiters** — batch-rank candidate pools against job descriptions using BM25 + Word2Vec + BERT, get LLM-explained shortlists, and analytics on the pipeline.
- **Admins** — monitor platform usage, AI cost, model accuracy and user growth.

## 2. High-Level Topology

```
                ┌────────────────────────────────────────────────┐
                │                Next.js 14 Frontend             │
                │  (App Router · TypeScript · Tailwind · Zustand) │
                └──────────────────┬─────────────────────────────┘
                                   │  HTTPS (JWT in Authorization header)
                                   ▼
                ┌────────────────────────────────────────────────┐
                │              FastAPI Backend                    │
                │  Routers · Services · Middleware · Dependencies │
                └───────┬─────────────────────┬──────────────────┘
                        │                     │
                        ▼                     ▼
            ┌─────────────────────┐  ┌─────────────────────────┐
            │   MongoDB (Motor)   │  │      AI Engine          │
            │  users · resumes    │  │  ranking/ preprocessing/ │
            │  job_matches ...    │  │  embeddings/ llm/ ...    │
            └─────────────────────┘  └────────┬────────────────┘
                                              │
                            ┌─────────────────┼──────────────────┐
                            ▼                 ▼                  ▼
                    ┌──────────────┐  ┌─────────────┐   ┌─────────────┐
                    │ Local models │  │  Gemini API │   │  Groq API   │
                    │ (BERT/W2V)   │  │ (gemini-2.0)│   │ (llama3-70b)│
                    └──────────────┘  └─────────────┘   └─────────────┘
```

All three runtime containers (frontend, backend, mongo) ship via `docker-compose`. The AI engine is a Python package consumed by the backend — not a separate microservice in v1 (avoids cross-process model loading cost). It can be split later when load justifies it.

## 3. Layered Architecture (Backend)

```
backend/app/
├── main.py              # FastAPI app + lifespan + router mounts
├── core/                # Settings, security, logging, exceptions
├── api/                 # HTTP layer — routers only, no business logic
│   ├── auth.py
│   ├── resume.py
│   ├── ranking.py
│   ├── chat.py
│   ├── analytics.py
│   ├── admin.py
│   └── roadmap.py
├── services/            # Business logic — uses ai_engine + db
│   ├── auth_service.py
│   ├── resume_service.py
│   ├── ranking_service.py
│   ├── analyzer_service.py
│   └── llm_service.py
├── models/              # Beanie/Pydantic ODM documents (persistence)
├── schemas/             # Pydantic DTOs (HTTP I/O contracts)
├── db/                  # Motor client + Beanie init + indexes
├── middleware/          # Error handler, request logger, CORS
└── utils/               # Hashing, JWT, file storage helpers
```

**Hard rules:**
- Routers never touch MongoDB or ai_engine directly — they call services.
- Services never construct HTTP responses — they raise typed errors and return DTOs/dicts.
- The `ai_engine` package has zero web framework imports; it can be unit tested standalone or wrapped by Celery in the future.

## 4. AI Engine Package

The existing Streamlit modules are reorganised into a pure Python library:

```
ai_engine/
├── extraction/
│   └── document.py            # PDF/DOCX/TXT → raw text (from extraction.py)
├── preprocessing/
│   ├── text.py                # tokenize, lemmatize, stopword (from applyprocessing.py)
│   └── llm_clean.py           # contact-info / boilerplate removal
├── ranking/
│   ├── bm25.py                # from bma.py
│   ├── word2vec.py            # from word2vec.py
│   └── bert.py                # from bert.py
├── embeddings/
│   └── sbert.py               # singleton SentenceTransformer loader
├── llm/
│   ├── groq_client.py         # from explainwithllm.py — async + retry
│   └── gemini_client.py       # from AI_rank.py — async
├── evaluation/
│   ├── ats_score.py           # NEW — heuristic+semantic ATS scoring
│   ├── skill_extractor.py     # NEW — regex + sbert skill graph
│   └── quality_audit.py       # NEW — weak-section detection
├── interview/
│   └── question_gen.py        # NEW — Gemini interview Q&A generator
└── roadmap/
    └── planner.py             # NEW — career roadmap generator
```

**Service-layer wrapper pattern** — every ai_engine submodule exposes a single async-friendly function. Heavy CPU work runs in `asyncio.to_thread()` so it never blocks the event loop. The SentenceTransformer is loaded once at app startup (FastAPI lifespan) — not per request.

## 5. Frontend Architecture

Next.js 14 App Router with Server Components by default, Client Components only when needed (forms, dashboards with charts, interactive uploads).

```
frontend/src/
├── app/
│   ├── (marketing)/page.tsx     # Landing page (server component)
│   ├── (auth)/login/page.tsx
│   ├── (auth)/register/page.tsx
│   ├── (dashboard)/layout.tsx   # Auth guard + sidebar
│   ├── (dashboard)/dashboard/page.tsx
│   ├── (dashboard)/analyzer/page.tsx
│   ├── (dashboard)/ranking/page.tsx
│   ├── (dashboard)/interview/page.tsx
│   ├── (dashboard)/roadmap/page.tsx
│   ├── (dashboard)/chat/page.tsx
│   └── (dashboard)/admin/page.tsx
├── components/
│   ├── ui/                       # button, card, input, dialog (shadcn-style)
│   ├── landing/                  # hero, features, pricing, testimonials
│   ├── dashboard/                # sidebar, topbar, stats-card, charts
│   ├── auth/                     # login-form, register-form
│   └── resume/                   # uploader, ats-radar, skill-matrix
├── services/api/                 # typed fetch wrappers per backend router
├── store/                        # Zustand: auth, resume, ui
├── hooks/                        # useAuth, useResume, useUpload
├── lib/                          # fetcher, axios instance, utils
└── types/                        # mirrors backend Pydantic DTOs
```

**State strategy:**
- **Server state** — TanStack Query (caching, retries, pagination)
- **Client state** — Zustand (auth token, UI flags)
- **Form state** — React Hook Form + Zod

## 6. Authentication & Authorization

- **Password storage:** bcrypt via `passlib`
- **Tokens:** JWT (HS256), access token 30 min + refresh token 7 days
- **Transport:** access token in `Authorization: Bearer`, refresh token in HttpOnly Secure cookie
- **Roles:** `user`, `recruiter`, `admin` — enforced in FastAPI dependencies (`require_role("recruiter")`)
- **Protected routes (frontend):** middleware.ts redirects unauthenticated traffic to `/login`; route groups under `(dashboard)` require a token

## 7. Data Model (MongoDB Collections)

| Collection | Purpose | Indexes |
|------------|---------|---------|
| `users` | Account, role, profile | `email` unique, `role` |
| `resumes` | Uploaded resume + parsed data + ATS score | `user_id`, `created_at desc` |
| `job_matches` | Job description + ranked candidate scores | `recruiter_id`, `created_at desc` |
| `interviews` | AI-generated Q&A sessions + scores | `user_id`, `role` |
| `analytics` | Per-user time-series counters | `user_id+date` compound |
| `ai_logs` | LLM/model call logs (cost, latency, model id) | `created_at desc`, `user_id` |
| `roadmaps` | Generated career roadmaps with milestones | `user_id` |
| `chat_history` | Chat sessions with the AI advisor | `user_id`, `session_id` |

Full schemas live in `database/schemas/*.md` and as Beanie documents in `backend/app/models/`.

## 8. AI Workflow — Resume Analysis Pipeline

```
upload ──► extraction.document ──► preprocessing.text
                                          │
        ┌─────────────────────────────────┼──────────────────────────────┐
        ▼                                 ▼                              ▼
  evaluation.ats_score        evaluation.skill_extractor        ranking.bert (if JD present)
        │                                 │                              │
        └─────────────► persist Resume document ◄─────────────────────────┘
                                          │
                                          ▼
                          llm.groq_client (explanation, async)
                                          │
                                          ▼
                                  return AnalysisResult
```

Every step writes to `ai_logs` with `{model, tokens_in, tokens_out, latency_ms, cost_estimate}` so the Admin dashboard can chart cost over time.

## 9. AI Workflow — Recruiter Ranking Pipeline

1. Recruiter uploads N resumes + JD.
2. Backend stores each resume.
3. Service runs in parallel (asyncio.gather):
   - `bm25.rank(resumes, jd)`
   - `word2vec.rank(resumes, jd)`
   - `bert.rank(resumes, jd)`
4. Scores normalised (min-max) and combined via configurable weights (default 0.2/0.2/0.6).
5. Top K passed to `llm.groq_client` for Good Fit / Bad Fit explanation.
6. Result persisted to `job_matches` collection and streamed back to client.

## 10. Observability

- **Logs:** structlog → stdout (JSON) → docker logs / Loki
- **Errors:** Sentry SDK (optional, gated on env var)
- **Metrics:** request count, latency, AI cost — exposed at `/metrics` (Prometheus format)
- **AI cost:** every Groq/Gemini call logs cost estimate to `ai_logs`

## 11. Security

- bcrypt passwords (cost 12)
- JWT with rotating refresh tokens
- Rate limiting (slowapi) on `/auth/*` and `/chat/*`
- File upload validation: max 5 MB, MIME-type check, size check, no executable extensions
- CORS allow-list driven by `ALLOWED_ORIGINS` env var
- All secrets via env (never committed) — `.env.example` shipped
- SQL is N/A (Mongo), but Mongo injection is mitigated by Pydantic-validated DTOs (no raw dict construction from request body)
- HTTPS enforced behind reverse proxy in prod

## 12. Deployment Topology

**Local dev** — `docker-compose up` brings backend + frontend + mongo + mongo-express.

**Production (recommended path)**:
- Frontend → Vercel (free tier or Pro)
- Backend → Fly.io / Render / Railway (Docker image)
- Mongo → MongoDB Atlas (free M0)
- AI models → embedded in backend image (BERT mpnet is ~420 MB; acceptable)

## 13. Performance & Scalability Notes

- BERT model loaded once at startup (FastAPI lifespan handler), not per request.
- Word2Vec retrained per ranking job (small N). For large recruiter pools, swap to pre-trained GloVe.
- All blocking ML calls wrapped in `asyncio.to_thread()`.
- Heavy ranking (>50 resumes) can be moved to a Celery worker reading from Redis — out of scope for v1, but the service layer is designed to be drop-in compatible.
- MongoDB compound indexes on hot paths (see Section 7).

## 14. Technology Decisions

| Layer | Chosen | Why |
|-------|--------|-----|
| Backend framework | FastAPI | Async-native, Pydantic validation, OpenAPI free |
| ORM/ODM | Beanie | Pydantic-native async ODM on top of Motor |
| Frontend framework | Next.js 14 App Router | SSR/SSG, route groups, RSC for marketing |
| Styling | Tailwind + shadcn primitives | Fast, consistent, no design system lock-in |
| State | Zustand + TanStack Query | Minimal boilerplate vs Redux |
| Charts | Recharts | React-native, sufficient for dashboards |
| Auth | JWT (HS256) | Stateless, no session store required for v1 |
| Container | Docker + Compose | Standard for poly-language stacks |

## 15. Out of Scope for v1

- Stripe billing (Pricing page is a mockup)
- WebSocket-based live chat (chat uses request/response with SSE-ready endpoint)
- Multi-tenancy (every user is logically isolated by `user_id` but no org model yet)
- Background workers — synchronous in v1
