FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps required by gensim, pdfplumber, sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt

# Install CPU-only PyTorch FIRST so pip doesn't pull the 2GB CUDA build
RUN pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

RUN pip install -r /app/backend/requirements.txt

# Pre-download NLTK data so first request isn't slow
RUN python -c "import nltk; [nltk.download(p, quiet=True) for p in ('stopwords','punkt','punkt_tab','wordnet')]"

# Pre-cache the SBERT model (~90MB CPU version)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY ai_engine /app/ai_engine
COPY backend /app/backend

ENV PYTHONPATH=/app
WORKDIR /app/backend

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
