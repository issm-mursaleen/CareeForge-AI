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

## AI Lifecycle Implementation

The `ai_engine/ml_pipeline/` module implements a formal, end-to-end ML lifecycle
for the **Good Fit Binary Classifier** — a model that predicts whether a candidate
is a Good Fit (1) or Bad Fit (0) for a role, trained on resume × job-description
pairs from the platform's own MongoDB collections.

### 1. Data Gathering

**File:** `ai_engine/ml_pipeline/data_loader.py`

`load_training_dataset(records)` accepts raw MongoDB dicts (fetched by
`backend/app/services/ml_service.py` from the `job_matches` and `resumes`
collections) and validates them into typed `RawCandidateRecord` Pydantic
models.  Label derivation:

- `is_good_fit` is set on a `CandidateScore` → use it directly.
- Otherwise: `composite_score >= 0.5` → Good Fit (1), else Bad Fit (0).
- Cold-start fallback (no job-match data): `ats_score >= 60` → Good Fit.

### 2. Data Cleaning

**File:** `ai_engine/ml_pipeline/preprocessing.py`

`clean_dataset()` runs four explicit cleaning functions in sequence and
logs record counts before and after each step:

| Function | What it removes |
|----------|----------------|
| `remove_missing_values()` | Records with empty resume or job description |
| `remove_duplicates()` | Repeated `candidate_id` entries (keep first) |
| `remove_outliers()` | Resumes < 100 or > 50 000 chars; experience > 60 yrs |
| `normalize_text()` | HTML tags, extra whitespace, special characters; lowercase |

Cleaning statistics are stored in MongoDB with every training run.

### 3. Feature Engineering

**File:** `ai_engine/ml_pipeline/feature_engineering.py`

`extract_features()` builds a combined sparse feature matrix:

| Feature group | Transformer | Dimensions |
|---------------|-------------|------------|
| Resume text | `TfidfVectorizer` (unigrams + bigrams) | max 300 |
| Job description | `TfidfVectorizer` (unigrams) | max 150 |
| Numerical | `MinMaxScaler` — experience_years, resume_length_norm | 2 |
| Categorical | `OneHotEncoder` — education level | 6 |

All sub-matrices are combined via `scipy.sparse.hstack`.
Feature dimensions are persisted with every training run.

### 4. Model Training

**File:** `ai_engine/ml_pipeline/trainer.py`

`train_model()` performs:

1. Stratified 80/20 train/test split.
2. 3-fold `StratifiedKFold` cross-validation (skipped when data < 6 samples).
3. Model selection: **XGBoost → RandomForest → LogisticRegression** (first available).
4. Final fit on the full training split.
5. Save model bundle to `models/good_fit_classifier.pkl` via `joblib`.

### 5. Model Evaluation

**File:** `ai_engine/ml_pipeline/evaluator.py`

`evaluate()` computes:

- **Accuracy, Precision, Recall, F1 Score** (binary, zero-division safe)
- **Confusion Matrix** (2 × 2: TN / FP / FN / TP)
- **ROC Curve** (fpr[], tpr[] sampled at ≤ 50 points) + **AUC**
- **Classification Report** (per-class breakdown string)

---

## University Rubric Mapping

| Requirement | Implementation |
|-------------|----------------|
| **JWT Authentication** | `backend/app/core/security.py` — HS256 access (30 min) + refresh (7 day) tokens |
| **Protected Routes (backend)** | `backend/app/api/dependencies.py` — `get_current_user()`, `require_role()` |
| **Protected Routes (frontend)** | `frontend/src/components/dashboard/auth-guard.tsx` — client-side JWT check |
| **MongoDB** | `backend/app/db/mongo.py` — Motor + Beanie ODM, 10 collections |
| **Pydantic Validation** | All API schemas in `backend/app/schemas/` + ML schemas in `ai_engine/ml_pipeline/schemas.py` |
| **Data Gathering** | `ai_engine/ml_pipeline/data_loader.py` — `load_training_dataset()` |
| **Data Cleaning** | `ai_engine/ml_pipeline/preprocessing.py` — `clean_dataset()` with 4 explicit functions |
| **Feature Engineering** | `ai_engine/ml_pipeline/feature_engineering.py` — TF-IDF + MinMaxScaler + OHE |
| **Model Training** | `ai_engine/ml_pipeline/trainer.py` — XGBoost / RF / LR + CV + train/test split |
| **Model Evaluation** | `ai_engine/ml_pipeline/evaluator.py` — Accuracy / Precision / Recall / F1 / ROC-AUC / CM |
| **Metrics Storage** | `backend/app/models/good_fit_metrics.py` — `GoodFitMetricsDoc` → `ml_model_metrics` collection |
| **Model Loading at Startup** | `backend/app/main.py` lifespan → `load_good_fit_model()` — pre-warms in-process cache |
| **Secure Metrics API** | `backend/app/api/ml.py` — `GET /ml/metrics`, `GET /ml/latest`, `POST /ml/retrain` (admin) |
| **Dashboard Visualization** | `frontend/src/app/(dashboard)/dashboard/page.tsx` — confusion matrix grid + ROC curve (Recharts) |
| **Frontend Service Layer** | `frontend/src/services/ml.ts` — `getMLMetrics()`, `getLatestMLMetrics()`, `retrainModel()` |
| **FastAPI REST APIs** | `backend/app/api/` — auth, resumes, ranking, chat, roadmap, interview, analytics, admin, ml |
| **Recharts Dashboard** | `frontend/src/app/(dashboard)/dashboard/page.tsx` — ATS trend, ML bar chart, ROC curve |
| **Role-Based Auth** | `UserRole` enum (user / recruiter / admin); `require_role(UserRole.ADMIN)` on retrain endpoint |
| **BM25 Ranking** | `ai_engine/ranking/bm25.py` |
| **BERT / Embedding Ranking** | `ai_engine/ranking/bert.py` + `ai_engine/embeddings/sbert.py` |
| **LLM Integration** | `ai_engine/llm/mistral_client.py` (chat), `ai_engine/llm/groq_client.py` (explanations) |

### Retrain the Good Fit model

```bash
# Requires admin account — set role in MongoDB or via seed script
curl -X POST https://<your-backend>/api/v1/ml/retrain \
  -H "Authorization: Bearer <admin_access_token>"

# Check results
curl https://<your-backend>/api/v1/ml/latest \
  -H "Authorization: Bearer <access_token>"
```

> **Note:** On Render free tier the `models/` directory is ephemeral.
> Retrain is required after each cold restart.  For persistence, mount a
> volume or store the model bundle in MongoDB GridFS.

## License

MIT — semester project.
