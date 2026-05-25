"""Heuristic ATS scoring.

A real ATS combines:
- Format quality (parsable PDF, no images, clean sections)
- Keyword overlap with the target JD
- Section completeness (Experience, Education, Skills, Contact)
- Length and readability

We approximate this with a deterministic 0–100 score that's easy to explain
in the UI. The breakdown is returned so the dashboard can show *why*.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .skill_extractor import extract_skills

_REQUIRED_SECTIONS = ("experience", "education", "skills", "project")
_CONTACT_RE = re.compile(r"(?:\+?\d[\d\s\-()]{8,}|[\w.+-]+@[\w-]+\.[\w.-]+)")


@dataclass
class ATSReport:
    score: float
    breakdown: dict[str, float] = field(default_factory=dict)
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def compute_ats_score(resume_text: str, job_description: str | None = None) -> ATSReport:
    text = resume_text.lower()
    breakdown: dict[str, float] = {}
    notes: list[str] = []

    # 1. Section completeness — 25 pts
    sections_found = sum(1 for s in _REQUIRED_SECTIONS if s in text)
    breakdown["section_completeness"] = (sections_found / len(_REQUIRED_SECTIONS)) * 25
    if sections_found < len(_REQUIRED_SECTIONS):
        missing = [s for s in _REQUIRED_SECTIONS if s not in text]
        notes.append(f"Missing sections: {', '.join(missing)}")

    # 2. Contact info — 10 pts
    breakdown["contact_info"] = 10.0 if _CONTACT_RE.search(resume_text) else 0.0
    if breakdown["contact_info"] == 0:
        notes.append("No email or phone detected.")

    # 3. Length quality — 15 pts (sweet spot 400–1500 words)
    word_count = len(resume_text.split())
    if 400 <= word_count <= 1500:
        breakdown["length"] = 15.0
    elif word_count < 400:
        breakdown["length"] = max(0.0, (word_count / 400) * 15)
        notes.append(f"Resume is short ({word_count} words). Aim for 400+.")
    else:
        breakdown["length"] = max(0.0, 15.0 - ((word_count - 1500) / 100))
        notes.append(f"Resume is long ({word_count} words). Trim toward 1500.")

    # 4. Skill density — 25 pts
    skill_report = extract_skills(resume_text)
    skill_count = len(skill_report.found)
    breakdown["skill_density"] = min(25.0, skill_count * 1.5)

    matched_skills = skill_report.found
    missing_skills: list[str] = []

    # 5. JD match — 25 pts (only if JD provided)
    if job_description:
        jd_skills = set(extract_skills(job_description).found)
        resume_skills = set(skill_report.found)
        if jd_skills:
            overlap = len(jd_skills & resume_skills) / len(jd_skills)
            breakdown["jd_match"] = overlap * 25
            missing_skills = sorted(jd_skills - resume_skills)
            if missing_skills:
                notes.append(f"Missing JD skills: {', '.join(missing_skills[:5])}")
        else:
            breakdown["jd_match"] = 12.5  # neutral
    else:
        breakdown["jd_match"] = 12.5  # neutral

    total = round(sum(breakdown.values()), 2)
    return ATSReport(
        score=total,
        breakdown={k: round(v, 2) for k, v in breakdown.items()},
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        notes=notes,
    )
