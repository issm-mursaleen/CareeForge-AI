"""LLM-powered interview question generator and scorer.

Uses Gemini for question generation and Groq for answer scoring — keeps
the two providers in tension so neither monopolises the workflow.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from ..llm.mistral_client import MistralClient
from ..llm.groq_client import GroqClient

logger = logging.getLogger(__name__)


@dataclass
class InterviewQuestion:
    question: str
    category: str  # technical | behavioral | system_design
    expected_topics: list[str]


@dataclass
class InterviewScore:
    score: float  # 0-10
    feedback: str
    strengths: list[str]
    improvements: list[str]


class InterviewGenerator:
    def __init__(self, mistral: MistralClient | None = None, groq: GroqClient | None = None):
        self.mistral = mistral or MistralClient()
        self.groq = groq or GroqClient()

    async def generate(self, role: str, resume_text: str, count: int = 5) -> list[InterviewQuestion]:
        prompt = (
            f"You are an interview coach for a {role} position. Read the candidate's "
            f"resume and generate {count} interview questions tailored to it. Mix "
            f"technical and behavioral. Return strict JSON: "
            f'[{{"question":"...","category":"technical|behavioral|system_design",'
            f'"expected_topics":["..."]}}]\n\n'
            f"Resume:\n{resume_text[:4000]}"
        )
        import asyncio
        response_text = await self.mistral.generate_content_async(prompt)
        try:
            raw = response_text.strip()
            # Strip ```json fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1].lstrip("json").strip()
            data = json.loads(raw)
            return [InterviewQuestion(**q) for q in data]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning("Interview generation parse failed: %s", e)
            return []

    async def score_answer(
        self, question: str, answer: str, role: str
    ) -> InterviewScore:
        prompt = (
            f"Role: {role}\nQuestion: {question}\nCandidate answer: {answer}\n\n"
            f"Return strict JSON: "
            f'{{"score": 0-10, "feedback": "1-2 sentences", '
            f'"strengths": ["..."], "improvements": ["..."]}}'
        )
        raw = await self.groq.generate_content_async(prompt)
        try:
            # Be defensive — Groq sometimes returns prose. Fallback to a neutral score.
            data = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
            return InterviewScore(**data)
        except Exception:
            return InterviewScore(
                score=5.0,
                feedback=raw[:200],
                strengths=[],
                improvements=[],
            )
