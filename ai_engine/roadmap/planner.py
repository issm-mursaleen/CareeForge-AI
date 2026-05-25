"""Career roadmap generator — given current resume + target role, returns
milestones, skill gaps, and resource recommendations."""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass

from ..evaluation.skill_extractor import SKILL_TAXONOMY, extract_skills
from ..llm.mistral_client import MistralClient

logger = logging.getLogger(__name__)


@dataclass
class Milestone:
    week: int
    title: str
    description: str
    skills: list[str]


@dataclass
class Roadmap:
    target_role: str
    skill_gaps: list[str]
    milestones: list[Milestone]
    resources: list[dict]


_ROLE_SKILL_HINTS = {
    "ai engineer": ["python", "pytorch", "transformers", "langchain", "huggingface", "fastapi"],
    "data scientist": ["python", "pandas", "scikit-learn", "sql", "tensorflow"],
    "frontend developer": ["react", "next.js", "typescript", "tailwind", "zustand"],
    "backend developer": ["fastapi", "postgres", "docker", "redis", "rest", "graphql"],
    "fullstack developer": ["react", "fastapi", "typescript", "postgres", "docker"],
}


class RoadmapPlanner:
    def __init__(self, mistral: MistralClient | None = None):
        self.mistral = mistral or MistralClient()

    async def plan(self, target_role: str, resume_text: str) -> Roadmap:
        role_key = target_role.lower()
        required = set(_ROLE_SKILL_HINTS.get(role_key, []))
        have = set(extract_skills(resume_text).found)
        gaps = sorted(required - have)

        prompt = (
            f"You are a career coach. The candidate wants to become a {target_role}. "
            f"Their current skills: {sorted(have) or '[none detected]'}. "
            f"Their gaps: {gaps or '[none]'}. "
            f"Generate a 12-week roadmap as strict JSON: "
            f'{{"milestones":[{{"week":N,"title":"...","description":"...",'
            f'"skills":["..."]}}],'
            f'"resources":[{{"title":"...","url":"...","type":"course|book|project"}}]}}'
        )
        raw = await self.mistral.generate_content_async(prompt)
        if raw.startswith("```"):
            raw = raw.split("```")[1].lstrip("json").strip()
        try:
            data = json.loads(raw)
            milestones = [Milestone(**m) for m in data.get("milestones", [])]
            resources = data.get("resources", [])
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Roadmap parse failed: %s", e)
            milestones, resources = [], []

        return Roadmap(
            target_role=target_role,
            skill_gaps=gaps,
            milestones=milestones,
            resources=resources,
        )
