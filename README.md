# CareerForge AI

> Full-stack AI-native career platform — resume analysis, recruiter ranking, interview prep, and career roadmaps. Migration of a Streamlit IR project into a production-grade SaaS architecture.

![stack](https://img.shields.io/badge/backend-FastAPI-009688) ![next](https://img.shields.io/badge/frontend-Next.js%2014-000) ![db](https://img.shields.io/badge/db-MongoDB-47A248) ![ai](https://img.shields.io/badge/AI-BM25%20·%20Word2Vec%20·%20BERT%20·%20Gemini%20·%20Groq-7c3aed)

## What's in here

| Path | Purpose |
|------|---------|
| `ai_engine/` | Pure Python ML library — extraction, preprocessing, ranking, embeddings, LLM clients, evaluation, interview, roadmap |
| `backend/` | FastAPI service — auth, resume, ranking, chat, roadmap, interview, analytics, admin |
| `frontend/` | Next.js 14 App Router + Tailwind + Zustand + TanStack Query |
| `database/` | Schemas + seed scripts |
| `docs/` | Architecture, migration plan, ER diagram, API reference |
| `docker-compose.yml` | One-command local stack |

## Quickstart (Docker — recommended)

```bash
# 1. Configure secrets
cp backend/.env.example backend/.env
# Edit backend/.env — set JWT_SECRET, GEMINI_API_KEY, GROQ_API_KEY

# 2. Boot the whole stack
docker compose up --build

# 3. Open:
#   Frontend       → http://localhost:3000
#   API docs       → http://localhost:8000/docs
#   Mongo Express  → http://localhost:8081  (admin / admin)
```

Generate a JWT secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## Quickstart (local dev, no Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # then edit secrets
PYTHONPATH=.. uvicorn app.main:app --reload
```

> NLTK + SBERT models are downloaded lazily on first request — first call will be slow.

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### Mongo

```bash
docker run -d --name cf-mongo -p 27017:27017 mongo:7
```

## Environment variables

### Backend (`backend/.env`)

| Key | Required | Default | Notes |
|-----|----------|---------|-------|
| `JWT_SECRET` | ✅ | — | 32+ chars; rotate regularly |
| `MONGODB_URI` | ✅ | `mongodb://localhost:27017` | |
| `MONGODB_DB` | | `careerforge` | |
| `ALLOWED_ORIGINS` | | `["http://localhost:3000"]` | JSON list |
| `GEMINI_API_KEY` | for chat / interview / roadmap | — | aistudio.google.com |
| `GROQ_API_KEY` | for ranking explanations | — | console.groq.com |
| `SBERT_MODEL` | | `sentence-transformers/all-MiniLM-L6-v2` | swap to mpnet for higher quality |
| `MAX_UPLOAD_MB` | | `5` | |

### Frontend (`frontend/.env.local`)

| Key | Default |
|-----|---------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api/v1` |

## Project documentation

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — system topology, layered architecture, AI pipeline diagrams
- **[docs/MIGRATION.md](docs/MIGRATION.md)** — Streamlit → CareerForge file-by-file mapping + phased plan
- **[docs/ER_DIAGRAM.md](docs/ER_DIAGRAM.md)** — Mongo collections + indexes
- **[docs/API.md](docs/API.md)** — REST endpoint reference

## Architecture at a glance

```
Next.js 14 (frontend) ── JWT ──▶ FastAPI (backend) ──▶ MongoDB
                                       │
                                       ├─▶ ai_engine.ranking (BM25 / W2V / BERT)
                                       ├─▶ ai_engine.evaluation (ATS / skills / quality)
                                       ├─▶ ai_engine.llm.gemini_client
                                       └─▶ ai_engine.llm.groq_client
```

## Features delivered in this scaffold

- ✅ JWT auth with refresh + role-based access (user / recruiter / admin)
- ✅ Resume upload + ATS scoring + skill extraction + quality audit
- ✅ Multi-algorithm ranking (BM25 + Word2Vec + BERT) with composite score
- ✅ LLM "Good Fit / Bad Fit" explanations for top K candidates
- ✅ AI career advisor chat (Gemini)
- ✅ Interview question generation + answer scoring
- ✅ 12-week career roadmap planner
- ✅ Analytics summary + admin overview
- ✅ Modern landing page with hero / features / pricing / footer
- ✅ Dashboard with ATS-trend line chart, top-skill bar chart, radar
- ✅ Docker-compose stack

## What's intentionally stubbed

These work at the backend level but the dedicated UI pages show "Coming online" — extend the pattern from `analyzer/` or `ranking/`:

- Interview UI (backend `/interview` is live)
- Roadmap UI (backend `/roadmap` is live)
- Full recruiter analytics page

## Migrating from the old Streamlit app

The original `app.py` / `Models.py` / `AI_rank.py` still sit at the repo root and continue to run via `streamlit run app.py` — they are not touched. See [docs/MIGRATION.md](docs/MIGRATION.md) for the file-by-file mapping.

## Deployment

- **Frontend** → Vercel: `vercel --prod` from `frontend/`
- **Backend** → Fly.io / Render / Railway: deploy the `backend/Dockerfile`
- **Mongo** → MongoDB Atlas free tier
- Set production env vars in the platform's secret manager

## License

MIT — semester project.
