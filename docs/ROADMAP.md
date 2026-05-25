# Implementation Roadmap — what to do next

This scaffold is functional end-to-end for the core path (auth → resume analyze → ranking → admin). What follows is the prioritised list of work to reach the "feels like a startup product" bar.

## Phase 1 — Boot the stack (1 day)
- [ ] `cp backend/.env.example backend/.env`, set `JWT_SECRET`, `GEMINI_API_KEY`, `GROQ_API_KEY`
- [ ] `docker compose up --build` and confirm `/health` returns 200
- [ ] `PYTHONPATH=. python database/seeds/seed_demo.py` to create demo accounts
- [ ] Log in as `candidate@careerforge.ai / Candi@12345` and upload a sample PDF resume

## Phase 2 — Polish what's already wired (2-3 days)
- [ ] Add toasts for backend 5xx errors (sonner already imported in layout)
- [ ] Skeleton loaders on dashboard cards while TanStack Query is fetching
- [ ] Pagination + delete on `/resumes` list
- [ ] Save ranking history page (`GET /ranking/history` not yet implemented — add it)
- [ ] Add `npm run test` for frontend (vitest + testing-library)
- [ ] Add `pytest` suite for backend (start with `tests/test_auth.py`, `tests/test_resume.py`)

## Phase 3 — Build the stubbed UI pages (2-3 days)
- [ ] **Interview page** — resume picker → role input → generate questions → answer one at a time → show score + feedback
- [ ] **Roadmap page** — resume picker → target role → render milestones as vertical timeline with checkboxes
- [ ] **Recruiter dashboard** — chart of past job_matches, average composite score per JD, time-to-shortlist

## Phase 4 — Production-readiness (2-3 days)
- [ ] Rate-limit `/auth/*` and `/chat` with slowapi
- [ ] Add `ai_logs` writes inside every Gemini/Groq call so admin cost chart works
- [ ] Add CSRF protection if you move to cookie-based auth
- [ ] Add Sentry SDK (gated on env var) for backend + frontend
- [ ] Replace the in-memory file handling with S3/GCS (file_url is already in the Resume model)
- [ ] CI: GitHub Actions running `pytest`, `npm run typecheck`, `npm run build`

## Phase 5 — Scale (later)
- [ ] Move heavy ranking jobs to a Celery worker + Redis (the service layer is already async-friendly)
- [ ] Cache SBERT embeddings per resume so re-ranking is cheap
- [ ] Multi-tenant org model (users belong to companies, recruiters share resume pools)
- [ ] Stripe billing wired to the Pricing tiers

## Known sharp edges to handle before demo

- **First request to `/resumes/analyze` is slow** — SBERT loads on first call. The FastAPI `lifespan` already warms it, but on a cold Docker build that takes ~20s. Pre-warming happens in the Dockerfile RUN layer.
- **Word2Vec on tiny corpora is noisy** — `min_count=1` to avoid empty vocab, but scores will be unstable with < 5 resumes. Consider gating Word2Vec at N ≥ 5.
- **Gemini free tier has aggressive rate limits** — the chat / interview / roadmap features will fail-soft if you exceed. Move to the paid tier or swap to Groq if usage spikes.
