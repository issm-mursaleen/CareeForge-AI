# Migration Plan — Streamlit Prototype → CareerForge AI

## 0. Why migrate

The current Streamlit app proves the AI pipeline works but cannot ship as a product:

| Limitation | Cause | Fix in CareerForge |
|------------|-------|--------------------|
| No accounts, anyone can use it | Streamlit has no auth primitives | FastAPI + JWT |
| State lost on refresh | `st.session_state` is per-tab | MongoDB persistence |
| Single-page navigation | `st.navigation` is linear | Next.js App Router |
| Cannot reuse logic outside UI | ML calls coupled to `st.spinner` / `st.write` | Pure-Python `ai_engine` package |
| No analytics / no audit trail | Nothing is persisted | Every action logged to Mongo |
| Cannot serve recruiter batch flows | UI assumes one user, one session | Recruiter dashboard with persistent jobs |
| Production-deployable? | Streamlit Cloud is demo-grade | Docker + container PaaS |

## 1. File-by-file mapping

| Old file | New location | Change |
|----------|--------------|--------|
| `app.py` | deleted | replaced by FastAPI + Next.js |
| `Models.py` | `backend/app/services/ranking_service.py` + `(dashboard)/ranking/page.tsx` | UI/logic split |
| `AI_rank.py` | `ai_engine/llm/gemini_client.py` + `backend/app/services/analyzer_service.py` | Streamlit calls stripped |
| `extraction.py` | `ai_engine/extraction/document.py` | accepts bytes, returns `ExtractedDocument` |
| `applyprocessing.py` | `ai_engine/preprocessing/text.py` + `llm_clean.py` | unchanged functions, no streamlit |
| `querypre.py` | `ai_engine/preprocessing/text.py` (`preprocess_query`) | merged |
| `bma.py` | `ai_engine/ranking/bm25.py` | unchanged signature |
| `word2vec.py` | `ai_engine/ranking/word2vec.py` | unchanged |
| `bert.py` | `ai_engine/ranking/bert.py` + `embeddings/sbert.py` | model loader extracted |
| `explainwithllm.py` | `ai_engine/llm/groq_client.py` | streamlit + `time.sleep` swapped for async `httpx` |
| `requirements.txt` | `backend/requirements.txt` (+ added: fastapi, uvicorn, motor, beanie, passlib, python-jose, httpx, structlog) | extended |
| `.env` | `backend/.env` (server-only) | never bundled |

## 2. Migration sequence

Recommended order so the team always has a green build:

**Phase A — Foundation (Day 1–2)**
1. Stand up new `careerforge-ai/` repo skeleton.
2. Lift `ai_engine/` from existing files verbatim — but remove all `import streamlit` and `st.*` calls. Replace `st.spinner` with no-op, `st.write` with `logger.debug`.
3. Verify each algorithm still runs via a standalone `python -m ai_engine.ranking.bm25 demo.json`.

**Phase B — Backend (Day 3–5)**
4. FastAPI app with `/health` + Mongo connect.
5. Auth router + bcrypt + JWT.
6. Resume upload route → calls `ai_engine.extraction` + `preprocessing` + `evaluation.ats_score` → persists.
7. Ranking route → calls `ai_engine.ranking.*` in parallel.
8. Chat + roadmap + interview routes (stubs first).

**Phase C — Frontend (Day 6–9)**
9. Next.js project + Tailwind + shadcn primitives.
10. Landing page (purely static).
11. Auth flow (register/login) + token storage + protected route middleware.
12. Resume Analyzer page calling backend.
13. Ranking page (recruiter).
14. Dashboard skeleton + Recharts cards.

**Phase D — Polish (Day 10–14)**
15. Admin dashboard.
16. Chat advisor UI.
17. File management page.
18. Docker compose works end-to-end.
19. README + screenshots + demo seed data.

## 3. Data migration

Streamlit version had no persistence — there is no data to migrate. Ship `database/seeds/seed_demo.py` that creates:
- 1 admin user (`admin@careerforge.ai` / `Admin@123`)
- 1 recruiter user
- 1 candidate user with 2 sample resumes + 1 ranking history entry

## 4. Behavioural parity checklist

Verify after migration that the new system reproduces these old behaviours:

- [ ] BM25 ranking of 5 resumes returns identical scores as old `bma.applybm25`
- [ ] Word2Vec ranking is within ±0.01 of old `word2vec` output (training is stochastic)
- [ ] BERT ranking is bit-identical (deterministic model)
- [ ] Gemini classification format `"Resume N - Relevant - reason"` still parses
- [ ] Groq "Good Fit"/"Bad Fit" prefix still detected

These become integration tests in `backend/tests/test_parity.py`.

## 5. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| BERT model size blows up Docker image | Use `sentence-transformers/all-MiniLM-L6-v2` for production (80 MB) and gate mpnet behind a flag |
| Gemini/Groq rate limits in demo | Add exponential backoff (already in `groq_client`), surface friendly error in UI |
| JWT secret leaked | Generated at deploy time, not committed; rotation procedure in `docs/OPS.md` |
| Mongo Atlas free tier slow on cold start | Connection pool warm-up in lifespan handler |
| Nltk data missing in container | Pre-download in Dockerfile RUN layer |

## 6. Rollback

If the migration breaks demo day:
- The old Streamlit app is preserved at the repo root and still runs via `streamlit run app.py`.
- The new project lives in `careerforge-ai/` so no destructive overwrite occurs.

