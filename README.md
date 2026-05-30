# CareerForge AI

> Full-stack AI-native career platform — resume analysis, recruiter ranking, interview prep, and career roadmaps.

![backend](https://img.shields.io/badge/backend-FastAPI-009688)
![frontend](https://img.shields.io/badge/frontend-Next.js%2014-000)
![db](https://img.shields.io/badge/db-MongoDB%20Atlas-47A248)
![ai](https://img.shields.io/badge/AI-Mistral%20·%20BM25%20·%20BERT%20·%20XGBoost-7c3aed)
![deployed](https://img.shields.io/badge/deployed-Render%20%2B%20Vercel-brightgreen)

**Live:**
- Frontend → https://caree-forge-ai-gomn.vercel.app
- Backend API → https://careerforge-backend-dfpi.onrender.com/docs

---

## Repository structure

| Path | Purpose |
|------|---------|
| `ai_engine/` | Pure Python ML library — extraction, preprocessing, ranking, embeddings, LLM clients, ML pipeline |
| `ai_engine/ml_pipeline/` | End-to-end Good Fit classifier — data loading, cleaning, features, training, evaluation |
| `backend/` | FastAPI service — auth, resume, ranking, chat, roadmap, interview, analytics, admin, ML API |
| `frontend/` | Next.js 14 App Router + Tailwind + Zustand + TanStack Query |
| `database/seeds/` | Demo account seed + ML training data seed scripts |
| `Datsets/` | `DataScientist.csv` (3 909 job postings) + `jobs_description.csv` (142 k roles) — ML training source |
| `docs/` | Architecture, migration plan, ER diagram, API reference |
| `docker-compose.yml` | One-command local stack |

---

## Quickstart (Docker — recommended)

```bash
# 1. Configure secrets
cp backend/.env.example backend/.env
# Edit backend/.env — set JWT_SECRET, MISTRAL_API_KEY, GROQ_API_KEY, MONGODB_URI

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

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### MongoDB

```bash
docker run -d --name cf-mongo -p 27017:27017 mongo:7
```

---

## Environment variables

### Backend (`backend/.env`)

| Key | Required | Default | Notes |
|-----|----------|---------|-------|
| `JWT_SECRET` | ✅ | — | 32+ chars |
| `MONGODB_URI` | ✅ | `mongodb://localhost:27017` | Atlas URI for production |
| `MONGODB_DB` | | `careerforge` | |
| `ALLOWED_ORIGINS` | | `http://localhost:3000` | Comma-separated or JSON array |
| `MISTRAL_API_KEY` | for chat / interview / roadmap | — | mistral.ai |
| `GROQ_API_KEY` | for ranking explanations | — | console.groq.com |
| `SBERT_MODEL` | | `sentence-transformers/all-MiniLM-L6-v2` | |
| `MAX_UPLOAD_MB` | | `5` | |

### Frontend (`frontend/.env.local`)

| Key | Default |
|-----|---------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api/v1` |

---

## Demo accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@careerforge.ai` | `Admin@12345` |
| Recruiter | `recruiter@careerforge.ai` | `Recruit@12345` |
| Candidate | `candidate@careerforge.ai` | `Candi@12345` |

Seed them with:
```bash
PYTHONPATH=. python database/seeds/seed_demo.py
```

---

## Architecture

```
Next.js 14 (Vercel) ── JWT ──▶ FastAPI (Render) ──▶ MongoDB Atlas
                                      │
                                      ├─▶ ai_engine.ml_pipeline   (Good Fit XGBoost)
                                      ├─▶ ai_engine.ranking       (BM25 / Word2Vec / BERT)
                                      ├─▶ ai_engine.evaluation    (ATS / skills / quality)
                                      ├─▶ ai_engine.llm.mistral   (chat / interview / roadmap)
                                      └─▶ ai_engine.llm.groq      (ranking explanations)
```

---

## Features

- ✅ JWT auth — HS256 access (30 min) + refresh (7 day) tokens, role-based access (user / recruiter / admin)
- ✅ Resume upload — ATS scoring, skill extraction, quality audit, PDF/DOCX parsing
- ✅ Multi-algorithm ranking — BM25 + Word2Vec + BERT composite score
- ✅ Good Fit binary classifier — XGBoost trained on 500 CSV-seeded records, **98% accuracy**
- ✅ LLM career advisor chat — Mistral AI, resume-aware personalised responses
- ✅ Interview question generation + answer scoring
- ✅ 12-week career roadmap planner
- ✅ Analytics dashboard — ATS trend, top skills, ML metrics, confusion matrix, ROC curve
- ✅ Admin panel — user management, system overview
- ✅ Mobile-first UI — bottom navigation bar, slide-out hamburger drawer, page animations
- ✅ Full Pydantic validation — every pipeline stage and API response model validated
- ✅ Docker-compose stack + Render / Vercel deployment

---

## AI Lifecycle — Good Fit Classifier

The `ai_engine/ml_pipeline/` module implements a complete, production-grade ML lifecycle for a **binary Good Fit classifier** that predicts whether a candidate is a Good Fit (1) or Bad Fit (0) for a role.

### Training data

Sourced from two CSV datasets stored in `Datsets/`:

| Dataset | Rows | Role in pipeline |
|---------|------|-----------------|
| `jobs_description.csv` | 142 262 | Candidate profiles (skills + responsibilities + qualification + experience) |
| `DataScientist.csv` | 3 909 | Real job postings used as the target job description |

500 records are sampled and seeded into MongoDB Atlas via `database/seeds/seed_ml_training.py`. Labels are derived from qualification score + experience years (PhD/Masters + 5 yrs → Good Fit).

### Stage 1 — Data Gathering

**`ai_engine/ml_pipeline/data_loader.py`**

`load_training_dataset(records)` fetches from the `ml_training_data` MongoDB collection and validates each row into a `RawCandidateRecord` Pydantic model with field-level constraints (non-empty text, experience in [0, 70], target_label in {0, 1}, education whitelist).

### Stage 2 — Data Cleaning

**`ai_engine/ml_pipeline/preprocessing.py`**

`clean_dataset()` runs four explicit steps:

| Function | What it removes |
|----------|----------------|
| `remove_missing_values()` | Blank resume or job description |
| `remove_duplicates()` | Repeated `candidate_id` (keep first) |
| `remove_outliers()` | Resume < 100 or > 50 000 chars; experience > 60 yrs |
| `normalize_text()` | HTML tags, extra whitespace, special chars; lowercase |

Stats (before/after counts) are persisted to MongoDB with every run.

### Stage 3 — Feature Engineering

**`ai_engine/ml_pipeline/feature_engineering.py`**

`extract_features()` builds a combined sparse feature matrix via `scipy.sparse.hstack`:

| Feature group | Transformer | Dimensions |
|---------------|-------------|------------|
| Resume text | `TfidfVectorizer` (unigrams + bigrams) | max 300 |
| Job description | `TfidfVectorizer` (unigrams) | max 150 |
| Numerical | `MinMaxScaler` — experience_years, resume_length_norm | 2 |
| Categorical | `OneHotEncoder` — education level | 6 |

A `FeatureInfo` model validates that sub-counts sum to `total_features`.

### Stage 4 — Model Training

**`ai_engine/ml_pipeline/trainer.py`**

`train_model()` performs:
1. Stratified 80/20 train/test split
2. 3-fold `StratifiedKFold` cross-validation
3. Model: **XGBoost** (falls back to RandomForest → LogisticRegression)
4. Final fit on full training split
5. Bundle saved to `models/good_fit_classifier.pkl` via `joblib`

### Stage 5 — Model Evaluation

**`ai_engine/ml_pipeline/evaluator.py`**

`evaluate()` computes and validates:

| Metric | Current result |
|--------|---------------|
| Accuracy | **98.00%** |
| Precision | **96.97%** |
| Recall | **100.00%** |
| F1-Score | **98.46%** |
| ROC AUC | **100.00%** |
| CV F1 (3-fold) | 98.64% ± 0.74% |

All metric values are validated to be in [0, 1] by `EvaluationResult`. ROC curve is downsampled to ≤ 50 points.

### Stage 6 — Metrics Storage

**`backend/app/models/good_fit_metrics.py`**

`GoodFitMetricsDoc` (Beanie Document → `ml_model_metrics` collection) stores every training run with full confusion matrix, ROC curve arrays, CV scores, cleaning stats, and feature info. Pydantic validators enforce metric bounds and confusion matrix shape.

### Pydantic Validation Layer

Every stage has strict Pydantic validation:

| Model | Key validations |
|-------|----------------|
| `RawCandidateRecord` | Non-empty text (min 10 chars), education whitelist, label in {0,1} |
| `CleaningStats` | All counts ≥ 0, `records_after ≤ records_before` |
| `FeatureInfo` | Sub-counts must sum to `total_features` |
| `TrainingResult` | `train_size/test_size ≥ 1`, cv_scores in [0,1] |
| `EvaluationResult` | All metrics in [0,1], confusion matrix 2×2, ROC fpr/tpr equal length |
| `GoodFitMetricsDoc` | Metric bounds + `train+test ≤ dataset_size` |
| `MLTrainingRecord` | Text min_length, `is_good_fit` in {0,1}, education whitelist |
| API responses | Typed `response_model=` on all 3 ML endpoints |

---

## Secure ML API

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /api/v1/ml/metrics` | Any user | Training history list |
| `GET /api/v1/ml/latest` | Any user | Full metrics + confusion matrix + ROC curve |
| `POST /api/v1/ml/retrain` | Admin only | Trigger pipeline retrain in background |

### Retrain the model

```bash
# Login as admin
TOKEN=$(curl -s -X POST https://careerforge-backend-dfpi.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@careerforge.ai","password":"Admin@12345"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Trigger retrain
curl -X POST https://careerforge-backend-dfpi.onrender.com/api/v1/ml/retrain \
  -H "Authorization: Bearer $TOKEN"

# Check results
curl https://careerforge-backend-dfpi.onrender.com/api/v1/ml/latest \
  -H "Authorization: Bearer $TOKEN"
```

### Seed training data (first time or re-seed)

```bash
# From repo root — reads CSVs locally, inserts 500 records into MongoDB Atlas
python database/seeds/seed_ml_training.py
```

> **Note:** On Render free tier the `models/` directory is ephemeral. The model `.pkl` is lost on cold restart — retrain once after each cold start. Metrics are always preserved in MongoDB Atlas.

---

## Mobile UI

The frontend is fully responsive with a mobile-first design:

- **Bottom navigation bar** — iOS-style 5-tab bar with filled icons on active tab
- **Slide-out hamburger drawer** — full nav with backdrop blur, closes on outside tap
- **Page transitions** — `fadeInUp` animation on every route change
- **Touch optimised** — `active:scale-95` press feedback, no iOS tap flash, safe-area padding
- **Landing navbar** — transparent → frosted glass on scroll, mobile dropdown menu

---

## University Rubric Mapping

| Requirement | Implementation |
|-------------|----------------|
| **JWT Authentication** | `backend/app/core/security.py` — HS256 access + refresh tokens |
| **Protected Routes (backend)** | `backend/app/api/dependencies.py` — `get_current_user()`, `require_role()` |
| **Protected Routes (frontend)** | `frontend/src/components/dashboard/auth-guard.tsx` |
| **MongoDB** | `backend/app/db/mongo.py` — Motor + Beanie ODM, 11 collections |
| **Pydantic Validation** | `backend/app/schemas/` + `ai_engine/ml_pipeline/schemas.py` + API `response_model=` |
| **Data Gathering** | `ai_engine/ml_pipeline/data_loader.py` — `load_training_dataset()` from `ml_training_data` |
| **Data Cleaning** | `ai_engine/ml_pipeline/preprocessing.py` — 4 explicit cleaning functions |
| **Feature Engineering** | `ai_engine/ml_pipeline/feature_engineering.py` — TF-IDF + MinMaxScaler + OHE |
| **Model Training** | `ai_engine/ml_pipeline/trainer.py` — XGBoost + 3-fold CV + 80/20 split |
| **Model Evaluation** | `ai_engine/ml_pipeline/evaluator.py` — Accuracy / Precision / Recall / F1 / ROC-AUC / CM |
| **Metrics Storage** | `backend/app/models/good_fit_metrics.py` → `ml_model_metrics` collection |
| **Model Loading at Startup** | `backend/app/main.py` lifespan → `load_good_fit_model()` |
| **Secure Metrics API** | `backend/app/api/ml.py` — typed Pydantic response models on all endpoints |
| **Dashboard Visualization** | `frontend/src/app/(dashboard)/dashboard/page.tsx` — confusion matrix + ROC curve (Recharts) |
| **Frontend Service Layer** | `frontend/src/services/ml.ts` — `getMLMetrics()`, `getLatestMLMetrics()`, `retrainModel()` |
| **FastAPI REST APIs** | `backend/app/api/` — auth, resumes, ranking, chat, roadmap, interview, analytics, admin, ml |
| **Role-Based Auth** | `UserRole` enum — `require_role(UserRole.ADMIN)` on retrain; recruiter-only ranking |
| **BM25 Ranking** | `ai_engine/ranking/bm25.py` |
| **BERT / Embedding Ranking** | `ai_engine/ranking/bert.py` + `ai_engine/embeddings/sbert.py` |
| **LLM Integration** | `ai_engine/llm/mistral_client.py` — Mistral AI for chat, interview, roadmap |
| **Mobile Responsive UI** | Bottom nav, slide drawer, page animations, touch feedback |
| **CSV Dataset Training** | `Datsets/jobs_description.csv` + `Datsets/DataScientist.csv` seeded into MongoDB |

---

## Deployment

| Service | Platform | Notes |
|---------|----------|-------|
| Frontend | Vercel | Auto-deploys from `main` branch |
| Backend | Render (Docker) | `backend/Dockerfile`, `dockerContext: .` |
| Database | MongoDB Atlas | Free tier M0 cluster |

> Set `ALLOWED_ORIGINS` on Render to your Vercel URL to allow CORS.

---

## License

MIT — semester project.
