"""BERT (sentence-transformers) ranking. Refactored from ``bert.py``."""
from __future__ import annotations

from typing import Sequence

from sklearn.metrics.pairwise import cosine_similarity

from ..embeddings.sbert import get_sbert_model


def rank_bert(resume_texts: Sequence[str], job_text: str) -> list[float]:
    """Score each raw resume text against the job description using SBERT."""
    if not resume_texts:
        return []
    model = get_sbert_model()
    resume_emb = model.encode(list(resume_texts), convert_to_numpy=True, show_progress_bar=False)
    job_emb = model.encode(job_text, convert_to_numpy=True).reshape(1, -1)
    return [float(s) for s in cosine_similarity(resume_emb, job_emb).flatten()]
