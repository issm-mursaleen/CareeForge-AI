"""Word2Vec ranking. Refactored from ``word2vec.py``."""
from __future__ import annotations

from typing import Sequence

import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity


def _train(corpus: Sequence[list[str]], vector_size: int = 100) -> Word2Vec:
    return Word2Vec(
        sentences=list(corpus),
        vector_size=vector_size,
        window=5,
        min_count=1,
        workers=4,
        sg=1,
        epochs=5,
        alpha=0.01,
        min_alpha=0.0001,
        sample=0.005,
        negative=3,
    )


def _avg_vector(tokens: list[str], model: Word2Vec) -> np.ndarray:
    vecs = [model.wv[w] for w in tokens if w in model.wv]
    if not vecs:
        return np.zeros(model.vector_size)
    return np.mean(vecs, axis=0)


def rank_word2vec(
    processed_resumes: Sequence[list[str]],
    processed_query: list[str],
) -> list[float]:
    """Train a per-job Word2Vec on the resume corpus and rank by cosine sim."""
    if not processed_resumes:
        return []
    model = _train(processed_resumes)
    job_vec = _avg_vector(processed_query, model).reshape(1, -1)
    scores = []
    for resume in processed_resumes:
        resume_vec = _avg_vector(resume, model).reshape(1, -1)
        scores.append(float(cosine_similarity(resume_vec, job_vec)[0][0]))
    return scores
