"""Data Cleaning stage.

Implements four explicit cleaning functions:
    remove_missing_values()  — drop empty text records
    remove_duplicates()      — drop repeated candidate_id entries
    remove_outliers()        — drop suspiciously short/long/extreme records
    normalize_text()         — strip HTML, collapse whitespace, lowercase

clean_dataset() runs all four steps and logs record counts before and after.
"""
from __future__ import annotations

import logging
import re

from .schemas import CleaningStats, RawCandidateRecord

logger = logging.getLogger(__name__)

_HTML_RE = re.compile(r"<[^>]+>")
_MULTI_SPACE_RE = re.compile(r"\s+")
_SPECIAL_RE = re.compile(r"[^\w\s\.\,\-\@\+\/]")

_MIN_RESUME_CHARS = 100
_MAX_RESUME_CHARS = 50_000
_MAX_EXPERIENCE_YEARS = 60


def normalize_text(text: str) -> str:
    """Strip HTML, collapse whitespace, remove non-printable chars, lowercase."""
    text = _HTML_RE.sub(" ", text)
    text = _SPECIAL_RE.sub(" ", text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    return text.strip().lower()


def remove_missing_values(
    records: list[RawCandidateRecord],
) -> tuple[list[RawCandidateRecord], int]:
    """Drop records where resume_text or job_description is blank."""
    before = len(records)
    cleaned = [r for r in records if r.resume_text.strip() and r.job_description.strip()]
    removed = before - len(cleaned)
    logger.info("cleaning_missing_removed: count=%d kept=%d", removed, len(cleaned))
    return cleaned, removed


def remove_duplicates(
    records: list[RawCandidateRecord],
) -> tuple[list[RawCandidateRecord], int]:
    """Keep only the first occurrence of each candidate_id."""
    before = len(records)
    seen: set[str] = set()
    cleaned: list[RawCandidateRecord] = []
    for r in records:
        if r.candidate_id not in seen:
            seen.add(r.candidate_id)
            cleaned.append(r)
    removed = before - len(cleaned)
    logger.info("cleaning_duplicates_removed: count=%d kept=%d", removed, len(cleaned))
    return cleaned, removed


def remove_outliers(
    records: list[RawCandidateRecord],
) -> tuple[list[RawCandidateRecord], int]:
    """Drop records with resume text outside the [100, 50 000] char range
    or with experience_years > 60."""
    before = len(records)
    cleaned = [
        r for r in records
        if _MIN_RESUME_CHARS <= len(r.resume_text) <= _MAX_RESUME_CHARS
        and r.experience_years <= _MAX_EXPERIENCE_YEARS
    ]
    removed = before - len(cleaned)
    logger.info("cleaning_outliers_removed: count=%d kept=%d", removed, len(cleaned))
    return cleaned, removed


def clean_dataset(
    records: list[RawCandidateRecord],
) -> tuple[list[RawCandidateRecord], CleaningStats]:
    """Full Data Cleaning pipeline — run all four cleaning steps in sequence.

    Pipeline order:
        1. remove_missing_values
        2. remove_duplicates
        3. remove_outliers
        4. normalize_text (applied to every remaining record)

    Logs record counts before and after cleaning.

    Returns:
        (cleaned_records, CleaningStats)
    """
    before = len(records)
    logger.info("cleaning_start: records_before=%d", before)

    records, missing = remove_missing_values(records)
    records, dups = remove_duplicates(records)
    records, outliers = remove_outliers(records)

    # Normalise text fields in every surviving record
    records = [
        r.model_copy(update={
            "resume_text": normalize_text(r.resume_text),
            "job_description": normalize_text(r.job_description),
        })
        for r in records
    ]

    after = len(records)
    stats = CleaningStats(
        records_before=before,
        records_after=after,
        removed_missing=missing,
        removed_duplicates=dups,
        removed_outliers=outliers,
    )
    logger.info(
        "cleaning_done: records_after=%d total_removed=%d missing=%d duplicates=%d outliers=%d",
        after, before - after, missing, dups, outliers,
    )
    return records, stats
