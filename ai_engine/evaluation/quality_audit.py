"""Detect weak sections, vague language, missing achievements."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_WEAK_PHRASES = (
    "hardworking", "team player", "detail oriented", "fast learner",
    "responsible for", "duties included", "passionate",
)
_ACTION_VERBS = (
    "led", "built", "designed", "implemented", "deployed", "shipped",
    "architected", "automated", "reduced", "improved", "increased",
    "launched", "owned", "delivered",
)
_METRIC_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent|x|users|requests|ms|seconds|minutes|hours)\b", re.I)


@dataclass
class QualityReport:
    action_verb_count: int
    metric_count: int
    weak_phrase_hits: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


def audit_resume_quality(resume_text: str) -> QualityReport:
    lowered = resume_text.lower()
    weak_hits = [p for p in _WEAK_PHRASES if p in lowered]
    action_count = sum(1 for v in _ACTION_VERBS if re.search(rf"\b{v}\b", lowered))
    metric_count = len(_METRIC_RE.findall(resume_text))

    suggestions: list[str] = []
    if weak_hits:
        suggestions.append(
            f"Replace vague phrases ({', '.join(weak_hits[:3])}) with concrete results."
        )
    if action_count < 5:
        suggestions.append("Start more bullets with strong action verbs (Built, Shipped, Reduced…).")
    if metric_count < 3:
        suggestions.append("Quantify impact — add at least 3 measurable outcomes (%, x, time saved).")

    return QualityReport(
        action_verb_count=action_count,
        metric_count=metric_count,
        weak_phrase_hits=weak_hits,
        suggestions=suggestions,
    )
