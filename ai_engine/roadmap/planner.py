"""Career roadmap generator — given current resume + target role, returns
milestones, skill gaps, and resource recommendations."""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass

from ..evaluation.skill_extractor import SKILL_TAXONOMY, extract_skills
from ..llm.groq_client import GroqClient

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

_SYSTEM_PROMPT = (
    "You are an expert career coach. Return ONLY valid JSON with no markdown, "
    "no explanation, no code fences. Your entire response must be a single JSON object."
)


class RoadmapPlanner:
    def __init__(self, groq: GroqClient | None = None):
        self.groq = groq or GroqClient()

    async def plan(self, target_role: str, resume_text: str) -> Roadmap:
        role_key = target_role.lower()
        required = set(_ROLE_SKILL_HINTS.get(role_key, []))
        have = set(extract_skills(resume_text).found)
        gaps = sorted(required - have)

        prompt = (
            f"The candidate wants to become a {target_role}. "
            f"Their current skills: {sorted(have) or '[none detected]'}. "
            f"Their skill gaps: {gaps or '[none]'}. "
            f"Generate a 12-week career roadmap. "
            f"Return ONLY this JSON structure, no other text:\n"
            f'{{"milestones":[{{"week":1,"title":"...","description":"...","skills":["..."]}}],'
            f'"resources":[{{"title":"...","url":"https://...","type":"course"}}]}}'
        )

        raw = await self.groq.generate_content_async(prompt, system_prompt=_SYSTEM_PROMPT)

        # Strip markdown fences if present
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
        raw = raw.strip()

        try:
            data = json.loads(raw)
            milestones = [Milestone(**m) for m in data.get("milestones", [])]
            resources = data.get("resources", [])
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Roadmap parse failed: %s | raw: %s", e, raw[:200])
            milestones, resources = [], []

        return Roadmap(
            target_role=target_role,
            skill_gaps=gaps,
            milestones=milestones,
            resources=resources,
        )
