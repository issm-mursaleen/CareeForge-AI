"""Mistral AI client — drop-in replacement for the old GeminiClient.

Uses ``mistral-small-latest`` by default (fast, cheap, capable).
Override via env var MISTRAL_MODEL if you want a different model.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv
from mistralai.client import Mistral

# Load .env so os.getenv() works even when called from outside the FastAPI
# boot sequence (e.g. ai_engine modules instantiated before pydantic-settings
# has populated os.environ).
_env_file = Path(__file__).resolve().parents[2] / "backend" / ".env"
load_dotenv(_env_file, override=False)  # override=False keeps already-set vars intact

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

_CLASSIFICATION_RE = re.compile(r"Resume\s*(\d+)\s*-\s*(Relevant|Irrelevant)\s*-\s*(.*)")
_RANKING_RE = re.compile(r"(\d+)\.\s*Resume\s*(\d+)\s*-\s*(.*)")


@dataclass
class MistralClassification:
    resume_index: int
    file_name: str
    label: str  # Relevant | Irrelevant
    reason: str


@dataclass
class MistralRanking:
    rank: int
    file_name: str
    reason: str


@dataclass
class MistralResult:
    classifications: list[MistralClassification]
    rankings: list[MistralRanking]
    raw_output: str


class MistralError(RuntimeError):
    pass


class MistralClient:
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        key = api_key or os.getenv("MISTRAL_API_KEY")
        if not key:
            raise MistralError("MISTRAL_API_KEY is not set")
        self._client = Mistral(api_key=key)
        self._model = model

    def _chat(self, prompt: str) -> str:
        """Synchronous chat call — will be offloaded to a thread for async use."""
        response = self._client.chat.complete(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        return (response.choices[0].message.content or "").strip()

    async def generate_content_async(self, prompt: str) -> str:
        """Async wrapper around the synchronous Mistral client."""
        return await asyncio.to_thread(self._chat, prompt)

    async def rank(
        self,
        resume_texts: Sequence[str],
        file_names: Sequence[str],
        job_description: str,
    ) -> MistralResult:
        prompt = self._build_prompt(resume_texts, job_description)
        output = await self.generate_content_async(prompt)
        return self._parse(output, file_names)

    @staticmethod
    def _build_prompt(resume_texts: Sequence[str], job_description: str) -> str:
        head = (
            "You are an expert HR assistant and recruiter with deep knowledge of "
            "resume screening. Your job is to strictly evaluate how well each resume "
            "matches the job description below. Be critical, objective, and binary — "
            "each resume is either **Relevant** or **Irrelevant**. Only mark a resume "
            "as Relevant if it directly demonstrates all required skills and experience "
            "from the job description. Do not be lenient. No partial credit.\n\n"
            f"---\nJob Description:\n{job_description.strip()}\n---\n\n"
            "Now evaluate the resumes based **only** on the job description above. "
            "Classify each resume as Relevant or Irrelevant, and then rank the "
            "**Relevant** resumes from best to worst based on fit.\n\n"
        )
        body = "".join(f"Resume {i}:\n{r.strip()}\n\n" for i, r in enumerate(resume_texts, 1))
        tail = (
            "Return your results in the following **exact** format:\n\n"
            "Resume 1 - Relevant - [One-line reason]\n"
            "Resume 2 - Irrelevant - [One-line reason]\n"
            "...\n\n"
            "Then provide a ranking of relevant resumes in this exact format:\n"
            "1. Resume 2 - Best fit due to exact skill match and domain experience\n"
            "2. Resume 5 - Good fit but slightly less experience\n\n"
            "Use only this format — no lists, no extra notes, no markdown. Begin now."
        )
        return head + body + tail

    @staticmethod
    def _parse(output: str, file_names: Sequence[str]) -> MistralResult:
        classifications: list[MistralClassification] = []
        for resume_num, label, reason in _CLASSIFICATION_RE.findall(output):
            idx = int(resume_num) - 1
            if 0 <= idx < len(file_names):
                classifications.append(
                    MistralClassification(
                        resume_index=int(resume_num),
                        file_name=file_names[idx],
                        label=label,
                        reason=reason.strip(),
                    )
                )
        rankings: list[MistralRanking] = []
        for rank, resume_num, reason in _RANKING_RE.findall(output):
            idx = int(resume_num) - 1
            if 0 <= idx < len(file_names):
                rankings.append(
                    MistralRanking(
                        rank=int(rank),
                        file_name=file_names[idx],
                        reason=reason.strip(),
                    )
                )
        return MistralResult(classifications=classifications, rankings=rankings, raw_output=output)


# ---------------------------------------------------------------------------
# Backward-compat aliases so any code that still imports GeminiClient by name
# continues to work without changes.
# ---------------------------------------------------------------------------
GeminiClient = MistralClient
GeminiResult = MistralResult
GeminiClassification = MistralClassification
GeminiRanking = MistralRanking
GeminiError = MistralError
