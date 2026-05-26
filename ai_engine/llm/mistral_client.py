"""Mistral AI client — optional dependency, only used if mistralai is installed."""
from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv

try:
    from mistralai.client import Mistral as _Mistral
    _MISTRAL_AVAILABLE = True
except ImportError:
    _Mistral = None  # type: ignore[assignment,misc]
    _MISTRAL_AVAILABLE = False

_env_file = Path(__file__).resolve().parents[2] / "backend" / ".env"
load_dotenv(_env_file, override=False)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

_CLASSIFICATION_RE = re.compile(r"Resume\s*(\d+)\s*-\s*(Relevant|Irrelevant)\s*-\s*(.*)")
_RANKING_RE = re.compile(r"(\d+)\.\s*Resume\s*(\d+)\s*-\s*(.*)")


@dataclass
class MistralClassification:
    resume_index: int
    file_name: str
    label: str
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
        if not _MISTRAL_AVAILABLE:
            raise MistralError(
                "mistralai package is not installed. "
                "Add mistralai to requirements.txt to use this client."
            )
        key = api_key or os.getenv("MISTRAL_API_KEY")
        if not key:
            raise MistralError("MISTRAL_API_KEY is not set")
        self._client = _Mistral(api_key=key)
        self._model = model

    def _chat(self, prompt: str) -> str:
        response = self._client.chat.complete(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        return (response.choices[0].message.content or "").strip()

    async def generate_content_async(self, prompt: str) -> str:
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
            "matches the job description below.\n\n"
            f"---\nJob Description:\n{job_description.strip()}\n---\n\n"
        )
        body = "".join(f"Resume {i}:\n{r.strip()}\n\n" for i, r in enumerate(resume_texts, 1))
        tail = (
            "Classify each resume as Relevant or Irrelevant, then rank the Relevant ones.\n"
            "Format:\nResume 1 - Relevant - [reason]\n1. Resume 1 - [reason]\n"
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
                    MistralRanking(rank=int(rank), file_name=file_names[idx], reason=reason.strip())
                )
        return MistralResult(classifications=classifications, rankings=rankings, raw_output=output)


GeminiClient = MistralClient
GeminiResult = MistralResult
GeminiClassification = MistralClassification
GeminiRanking = MistralRanking
GeminiError = MistralError
