"""Async Gemini client. Refactored from ``AI_rank.py``.

Provides direct LLM-based resume classification and ranking — same prompt
contract as the old Streamlit page, but the parsing now returns typed data
instead of writing to ``st.dataframe``.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass
from typing import Sequence

import google.generativeai as genai

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-2.0-flash"

_CLASSIFICATION_RE = re.compile(r"Resume\s*(\d+)\s*-\s*(Relevant|Irrelevant)\s*-\s*(.*)")
_RANKING_RE = re.compile(r"(\d+)\.\s*Resume\s*(\d+)\s*-\s*(.*)")


@dataclass
class GeminiClassification:
    resume_index: int
    file_name: str
    label: str  # Relevant | Irrelevant
    reason: str


@dataclass
class GeminiRanking:
    rank: int
    file_name: str
    reason: str


@dataclass
class GeminiResult:
    classifications: list[GeminiClassification]
    rankings: list[GeminiRanking]
    raw_output: str


class GeminiError(RuntimeError):
    pass


class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise GeminiError("GEMINI_API_KEY is not set")
        genai.configure(api_key=key)
        self._model = genai.GenerativeModel(model)

    async def rank(
        self,
        resume_texts: Sequence[str],
        file_names: Sequence[str],
        job_description: str,
    ) -> GeminiResult:
        prompt = self._build_prompt(resume_texts, job_description)
        # google-generativeai SDK is sync; offload to a thread
        response = await asyncio.to_thread(self._model.generate_content, prompt)
        output = (response.text or "").strip()
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
    def _parse(output: str, file_names: Sequence[str]) -> GeminiResult:
        classifications: list[GeminiClassification] = []
        for resume_num, label, reason in _CLASSIFICATION_RE.findall(output):
            idx = int(resume_num) - 1
            if 0 <= idx < len(file_names):
                classifications.append(
                    GeminiClassification(
                        resume_index=int(resume_num),
                        file_name=file_names[idx],
                        label=label,
                        reason=reason.strip(),
                    )
                )
        rankings: list[GeminiRanking] = []
        for rank, resume_num, reason in _RANKING_RE.findall(output):
            idx = int(resume_num) - 1
            if 0 <= idx < len(file_names):
                rankings.append(
                    GeminiRanking(
                        rank=int(rank),
                        file_name=file_names[idx],
                        reason=reason.strip(),
                    )
                )
        return GeminiResult(classifications=classifications, rankings=rankings, raw_output=output)
