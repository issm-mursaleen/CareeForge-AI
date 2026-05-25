"""Singleton SentenceTransformer loader.

The model is loaded once per process, then reused by every BERT-based call.
Production containers should call ``get_sbert_model()`` at app startup
(FastAPI lifespan) so the first request isn't slow.
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# all-MiniLM-L6-v2 is 80MB and 5x faster than mpnet, with ~95% of the quality.
# Override via env if you need the bigger model.
DEFAULT_MODEL = os.getenv("SBERT_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_sbert_model(name: str = DEFAULT_MODEL) -> SentenceTransformer:
    logger.info("Loading SentenceTransformer model: %s", name)
    return SentenceTransformer(name)
