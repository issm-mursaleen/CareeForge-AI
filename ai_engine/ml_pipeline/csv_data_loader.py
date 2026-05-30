"""CSV-based training data loader for the Good Fit classifier.

Sources
-------
Datsets/jobs_description.csv  (142 k rows)
    Each row = a candidate profile: skills + responsibilities + experience + qualification.
    Used as the resume side of every training pair.

Datsets/DataScientist.csv  (3 909 rows)
    Real job postings with rich job descriptions.
    Used as the job-description side of every training pair.

Label derivation
----------------
education_score : PhD/M.Tech/MBA/MCA/M.Com → 3  |  B.Tech/BE/BSc/BCA → 2  |  others → 1
experience_score: max_years >= 10 → 2  |  max_years >= 5 → 1  |  else → 0
is_good_fit = 1  if  (education_score + experience_score) >= 4  else  0

This captures the intuition: senior candidates with strong qualifications are a
good fit; junior or under-qualified candidates are not.
"""
from __future__ import annotations

import logging
import random
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────
# parents[0] = ai_engine/ml_pipeline/
# parents[1] = ai_engine/
# parents[2] = repo root  (also /app in Docker)
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATASETS_DIR = _REPO_ROOT / "Datsets"
_JD_CSV = _DATASETS_DIR / "jobs_description.csv"
_DS_CSV = _DATASETS_DIR / "DataScientist.csv"

# ── Constants ────────────────────────────────────────────────────────────────
_SAMPLE_SIZE = 2_000   # rows sampled — kept low for Render free tier (512 MB RAM)
_RANDOM_SEED = 42

_EDU_SCORE: dict[str, int] = {
    "phd": 3, "m.tech": 3, "mba": 3, "mca": 3, "m.com": 3,
    "me": 3, "msc": 3, "ma": 2,
    "b.tech": 2, "be": 2, "bsc": 2, "bca": 2,
    "bba": 1, "ba": 1, "b.com": 1, "bhm": 1,
}

_EDU_MAP: dict[str, str] = {
    "phd": "phd",
    "m.tech": "masters", "mba": "masters", "mca": "masters",
    "m.com": "masters", "me": "masters", "msc": "masters", "ma": "masters",
    "b.tech": "bachelors", "be": "bachelors", "bsc": "bachelors",
    "bca": "bachelors", "bba": "bachelors", "ba": "bachelors",
    "b.com": "bachelors", "bhm": "bachelors",
}


def _parse_experience(exp_str: str) -> tuple[int, int]:
    """Return (min_years, max_years) from a string like '3 to 10 Years'."""
    nums = re.findall(r"\d+", str(exp_str))
    if len(nums) >= 2:
        return int(nums[0]), int(nums[1])
    if len(nums) == 1:
        v = int(nums[0])
        return v, v
    return 0, 0


def _edu_score(qual: str) -> int:
    return _EDU_SCORE.get(str(qual).strip().lower(), 1)


def _edu_label(qual: str) -> str:
    return _EDU_MAP.get(str(qual).strip().lower(), "unknown")


def _compute_label(qual: str, max_exp: int) -> int:
    edu = _edu_score(qual)
    exp = 2 if max_exp >= 10 else (1 if max_exp >= 5 else 0)
    return 1 if (edu + exp) >= 4 else 0


def load_csv_training_dataset(sample_size: int = _SAMPLE_SIZE) -> list[dict]:
    """Load and pair candidates from both CSVs into training dicts.

    Returns a list of raw record dicts compatible with
    ``ai_engine.ml_pipeline.data_loader.load_training_dataset()``.

    Args:
        sample_size: How many rows to sample from jobs_description.csv.

    Returns:
        list of dicts, each with keys:
            candidate_id, resume_text, job_description,
            experience_years, education, is_good_fit, composite
    """
    try:
        import pandas as pd
    except ImportError:
        logger.error("pandas is required for CSV data loading")
        return []

    if not _JD_CSV.exists():
        logger.warning("csv_loader_missing: %s", str(_JD_CSV))
        return []
    if not _DS_CSV.exists():
        logger.warning("csv_loader_missing: %s", str(_DS_CSV))
        return []

    logger.info("csv_loader_reading: %s", str(_JD_CSV))
    jd_df = pd.read_csv(_JD_CSV, usecols=["Experience", "Qualifications", "Job Title", "Role", "Job Description", "skills", "Responsibilities"])
    jd_df = jd_df.dropna(subset=["skills", "Job Description"])

    logger.info("csv_loader_reading: %s", str(_DS_CSV))
    ds_df = pd.read_csv(_DS_CSV, usecols=["Job Description"])
    ds_jds = ds_df["Job Description"].dropna().tolist()

    # Sample candidate rows
    rng = random.Random(_RANDOM_SEED)
    n = min(sample_size, len(jd_df))
    sample_idx = rng.sample(range(len(jd_df)), n)
    jd_sample = jd_df.iloc[sample_idx].reset_index(drop=True)

    records: list[dict] = []
    for i, row in jd_sample.iterrows():
        skills = str(row.get("skills", "")).strip()
        responsibilities = str(row.get("Responsibilities", "")).strip()
        job_desc = str(row.get("Job Description", "")).strip()
        qual = str(row.get("Qualifications", "unknown")).strip()
        exp_str = str(row.get("Experience", "0 to 5 Years"))
        role = str(row.get("Role", "")).strip()

        min_exp, max_exp = _parse_experience(exp_str)

        # Include qualification and experience so TF-IDF can learn the label signal
        resume_text = (
            f"Qualification: {qual}. Experience: {min_exp} to {max_exp} years. "
            f"Role: {role}. Skills: {skills}. {responsibilities}"
        )

        # Job description: use DataScientist.csv JDs for variety; fallback to row's own JD
        target_jd = rng.choice(ds_jds) if ds_jds else job_desc

        label = _compute_label(qual, max_exp)
        composite = (min_exp / 20.0) * 0.4 + (_edu_score(qual) / 3.0) * 0.6

        records.append({
            "candidate_id": f"csv_{i}",
            "resume_text": resume_text,
            "job_description": target_jd,
            "experience_years": float(min_exp),
            "education": _edu_label(qual),
            "is_good_fit": label,
            "composite": round(composite, 3),
        })

    good = sum(1 for r in records if r["is_good_fit"] == 1)
    bad = len(records) - good
    logger.info("csv_loader_done: total=%d good=%d bad=%d", len(records), good, bad)
    return records
