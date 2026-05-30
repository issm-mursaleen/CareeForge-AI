"""Data Gathering stage.

load_training_dataset() accepts raw MongoDB record dicts and validates
them into typed RawCandidateRecord Pydantic models.

Label derivation:
    - If ``is_good_fit`` is set on the record → use it directly.
    - Otherwise derive from ``composite`` ranking score: >= 0.5 → 1.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from .schemas import RawCandidateRecord

logger = logging.getLogger(__name__)

_YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:year|yr)s?", re.IGNORECASE)

# Ordered from highest to lowest — first match wins
_EDU_LEVELS: list[tuple[str, str]] = [
    (r"ph\.?d|doctor", "doctorate"),
    (r"master|m\.?sc|m\.?b\.?a|m\.?s\b", "masters"),
    (r"bachelor|b\.?sc|b\.?s\b|b\.?e\b|b\.?tech", "bachelors"),
    (r"associate", "associate"),
    (r"diploma", "diploma"),
]


def _extract_experience(text: str) -> float:
    """Heuristic: return the largest 'N years' figure found in text."""
    matches = [int(m) for m in _YEARS_RE.findall(text) if int(m) <= 60]
    return float(max(matches)) if matches else 0.0


def _extract_education(text: str) -> str:
    """Heuristic: return the highest education level mentioned."""
    lower = text.lower()
    for pattern, level in _EDU_LEVELS:
        if re.search(pattern, lower):
            return level
    return "unknown"


def load_training_dataset(records: list[dict[str, Any]]) -> list[RawCandidateRecord]:
    """Data Gathering stage: convert raw MongoDB dicts to validated Pydantic models.

    Expected keys per dict:
        candidate_id    : str
        resume_text     : str
        job_description : str
        skills          : list[str]  (optional)
        is_good_fit     : bool | None
        composite       : float | None  (used when is_good_fit is None)

    Args:
        records: Raw dicts fetched from MongoDB by the backend service.

    Returns:
        List of validated RawCandidateRecord instances.
    """
    logger.info("data_gathering_start: raw_count=%d", len(records))
    validated: list[RawCandidateRecord] = []
    skipped = 0

    for raw in records:
        try:
            resume_text = str(raw.get("resume_text") or "").strip()
            job_description = str(raw.get("job_description") or "").strip()
            if not resume_text or not job_description:
                skipped += 1
                continue

            is_good_fit = raw.get("is_good_fit")
            if is_good_fit is not None:
                label = 1 if is_good_fit else 0
            else:
                composite = float(raw.get("composite") or 0)
                label = 1 if composite >= 0.5 else 0

            # Use pre-extracted fields if provided, fall back to text heuristics
            exp_years = raw.get("experience_years")
            edu = raw.get("education")
            validated.append(
                RawCandidateRecord(
                    candidate_id=str(raw.get("candidate_id") or "missing"),
                    resume_text=resume_text,
                    job_description=job_description,
                    skills=list(raw.get("skills") or []),
                    experience_years=float(exp_years) if exp_years is not None else _extract_experience(resume_text),
                    education=str(edu) if edu else _extract_education(resume_text),
                    target_label=label,
                )
            )
        except Exception as exc:
            logger.debug("data_gathering_record_skip: %s", str(exc))
            skipped += 1

    pos = sum(r.target_label for r in validated)
    logger.info(
        "data_gathering_done: validated=%d skipped=%d positive=%d negative=%d",
        len(validated), skipped, pos, len(validated) - pos,
    )
    return validated
