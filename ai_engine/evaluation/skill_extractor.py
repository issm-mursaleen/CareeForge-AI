"""Skill extraction via curated taxonomy + fuzzy matching.

Strategy:
- Maintain a curated taxonomy keyed by role family (DS / Backend / Frontend / etc).
- Match each resume token against the taxonomy (case-insensitive).
- Optionally enrich via SBERT cosine similarity to surface near-matches.
"""
from __future__ import annotations

from dataclasses import dataclass

SKILL_TAXONOMY: dict[str, list[str]] = {
    "languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
        "ruby", "php", "swift", "kotlin", "scala", "r", "sql",
    ],
    "ml_ai": [
        "tensorflow", "pytorch", "scikit-learn", "keras", "huggingface",
        "transformers", "spacy", "nltk", "openai", "langchain", "llamaindex",
        "bert", "gpt", "rag", "embeddings",
    ],
    "data": [
        "pandas", "numpy", "spark", "hadoop", "airflow", "dbt", "snowflake",
        "bigquery", "postgres", "mongodb", "redis", "kafka", "elasticsearch",
    ],
    "frontend": [
        "react", "next.js", "vue", "angular", "svelte", "tailwind", "redux",
        "zustand", "html", "css", "sass", "webpack", "vite",
    ],
    "backend": [
        "fastapi", "django", "flask", "express", "nestjs", "spring",
        "graphql", "rest", "grpc", "websocket",
    ],
    "devops": [
        "docker", "kubernetes", "terraform", "ansible", "jenkins", "github actions",
        "circleci", "aws", "gcp", "azure", "nginx", "linux",
    ],
}


@dataclass
class SkillReport:
    found: list[str]
    by_category: dict[str, list[str]]


def extract_skills(text: str) -> SkillReport:
    """Case-insensitive substring scan of the resume against the taxonomy."""
    lowered = text.lower()
    found: list[str] = []
    by_category: dict[str, list[str]] = {}
    for category, skills in SKILL_TAXONOMY.items():
        hits = [s for s in skills if s in lowered]
        if hits:
            by_category[category] = hits
            found.extend(hits)
    return SkillReport(found=sorted(set(found)), by_category=by_category)
