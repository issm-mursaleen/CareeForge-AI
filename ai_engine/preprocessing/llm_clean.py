"""Aggressive cleaning before sending text to an LLM.

Strips boilerplate phrases, PII (emails, phones, IDs), and short noise tokens
so the model gets dense, relevant content within token limits.
"""
from __future__ import annotations

import re

from nltk.tokenize import word_tokenize

_JUNK_PHRASES = (
    "curriculum vitae",
    "references available",
    "responsible for",
    "team player",
    "hardworking",
    "detail oriented",
    "good communication",
)

_EMAIL_RE = re.compile(r"\S+@\S+")
_PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{8,}")
_ID_RE = re.compile(r"\b[a-z]*\d+[a-z]*\b")


def clean_for_llm(tokens: list[str]) -> list[str]:
    text = " ".join(tokens)
    for phrase in _JUNK_PHRASES:
        text = text.replace(phrase, "")
    text = _EMAIL_RE.sub("", text)
    text = _PHONE_RE.sub("", text)
    text = _ID_RE.sub("", text)
    return [w for w in word_tokenize(text) if len(w) > 2]
