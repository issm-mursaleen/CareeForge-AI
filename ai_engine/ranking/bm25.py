"""BM25 ranking. Refactored from ``bma.py``."""
from __future__ import annotations

from typing import Sequence

from rank_bm25 import BM25Okapi


def rank_bm25(processed_resumes: Sequence[list[str]], processed_query: list[str]) -> list[float]:
    """Score every resume against the query using BM25Okapi.

    Args:
        processed_resumes: list of tokenized resume token lists.
        processed_query: tokenized query.

    Returns:
        Raw BM25 scores in input order.
    """
    if not processed_resumes:
        return []
    if not all(isinstance(r, list) for r in processed_resumes):
        raise TypeError("processed_resumes must be a list of token lists")
    bm25 = BM25Okapi(list(processed_resumes))
    return list(bm25.get_scores(processed_query))
