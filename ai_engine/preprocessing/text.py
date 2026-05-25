"""Text preprocessing — tokenize, lemmatize, stopwords.

Refactored from ``applyprocessing.py`` and ``querypre.py``.
NLTK data downloads are gated behind ``ensure_nltk()`` so production
containers can pre-warm them at build time (not per request).
"""
from __future__ import annotations

import logging
from functools import lru_cache

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

_NLTK_PACKAGES = ("stopwords", "punkt", "punkt_tab", "wordnet")


def ensure_nltk() -> None:
    """Idempotent NLTK data downloader. Call once at app startup."""
    for pkg in _NLTK_PACKAGES:
        try:
            nltk.data.find(pkg)
        except LookupError:
            logger.info("Downloading NLTK package: %s", pkg)
            nltk.download(pkg, quiet=True)


@lru_cache(maxsize=1)
def _lemmatizer() -> WordNetLemmatizer:
    ensure_nltk()
    return WordNetLemmatizer()


@lru_cache(maxsize=1)
def _stopwords() -> frozenset[str]:
    ensure_nltk()
    return frozenset(stopwords.words("english"))


def preprocess(text: str) -> list[str]:
    """Lowercase → tokenize → strip non-alnum → drop stopwords → lemmatize."""
    if not text:
        return []
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t.isalnum()]
    lem = _lemmatizer()
    stops = _stopwords()
    return [lem.lemmatize(t) for t in tokens if t not in stops]


def preprocess_query(query: str) -> list[str]:
    """Same as ``preprocess`` — kept as a named alias for ranking call sites."""
    return preprocess(query)
