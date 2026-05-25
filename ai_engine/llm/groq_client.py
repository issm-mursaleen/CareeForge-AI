"""Async Groq client. Refactored from ``explainwithllm.py``.

Streamlit spinners and ``time.sleep`` retries removed in favour of an
async httpx client with proper exponential backoff. Safe to call from
FastAPI without blocking the event loop.
"""
from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

_env_file = Path(__file__).resolve().parents[2] / "backend" / ".env"
load_dotenv(_env_file, override=False)

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.1-8b-instant"

_SYSTEM_PROMPT = (
    "You are a strict and objective resume evaluator. Only mark a resume as "
    "a 'Good Fit' if it strongly matches the job description in terms of key "
    "skills, responsibilities, and qualifications. If the match is weak or "
    "partial, label it as a 'Bad Fit'. Never be lenient. Keep evaluations "
    "concise, exactly 4 lines, and clearly explain the reasoning."
)


class GroqError(RuntimeError):
    pass


@dataclass
class GroqEvaluation:
    file_name: str
    score: float
    explanation: str
    is_good_fit: bool


class GroqClient:
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise GroqError("GROQ_API_KEY is not set")
        self.model = model

    async def explain(
        self,
        algorithm_name: str,
        job_description: str,
        resume_text: str,
        score: float,
        *,
        max_retries: int = 3,
        timeout: float = 30.0,
    ) -> str:
        """Get a 4-line Good Fit / Bad Fit explanation for a single resume."""
        resume_text = resume_text[:3000]
        job_description = job_description[:1000]

        prompt = (
            f"You are an AI resume evaluator. Analyze the similarity between a "
            f"job description and a resume using the provided algorithm. Be strict. "
            f"Only mark a resume as a 'Good Fit' if it clearly matches the key "
            f"responsibilities, skills, and qualifications of the job. If the match "
            f"is partial or weak, label it as a 'Bad Fit'.\n\n"
            f"Job Description: {job_description}\n"
            f"Resume: {resume_text}\n"
            f"Similarity Score: {score:.4f}\n"
            f"Algorithm Used: {algorithm_name}\n\n"
            f"In exactly 4 lines, explain why this resume is a Good Fit or Bad Fit. "
            f"Do not suggest improvements. No bullet points. "
            f"Prefix your response with either 'Good Fit:' or 'Bad Fit:'."
        )

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(max_retries):
                try:
                    resp = await client.post(GROQ_URL, json=payload, headers=headers)
                    body = resp.json()
                    if "error" in body:
                        err = body["error"]["message"].lower()
                        if "rate limit" in err or "please try again" in err:
                            wait = 2 ** attempt + 1
                            logger.warning("Groq rate-limited, retrying in %ss", wait)
                            await asyncio.sleep(wait)
                            continue
                        if "request too large" in err:
                            return "Bad Fit: Resume too long for evaluation."
                        raise GroqError(body["error"]["message"])
                    return body["choices"][0]["message"]["content"]
                except httpx.HTTPError as e:
                    logger.warning("Groq transport error (attempt %s): %s", attempt + 1, e)
                    await asyncio.sleep(2 ** attempt)
            raise GroqError("Groq failed after retries")

    async def generate_content_async(
        self,
        prompt: str,
        system_prompt: str | None = None,
        *,
        max_retries: int = 3,
        timeout: float = 30.0,
    ) -> str:
        """General purpose chat completion."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(max_retries):
                try:
                    resp = await client.post(GROQ_URL, json=payload, headers=headers)
                    body = resp.json()
                    if "error" in body:
                        err = body["error"]["message"].lower()
                        if "rate limit" in err or "please try again" in err:
                            wait = 2 ** attempt + 1
                            logger.warning("Groq rate-limited, retrying in %ss", wait)
                            await asyncio.sleep(wait)
                            continue
                        raise GroqError(body["error"]["message"])
                    return body["choices"][0]["message"]["content"]
                except httpx.HTTPError as e:
                    logger.warning("Groq transport error (attempt %s): %s", attempt + 1, e)
                    await asyncio.sleep(2 ** attempt)
            raise GroqError("Groq failed after retries")

    async def batch_explain(
        self,
        algorithm_name: str,
        job_description: str,
        items: list[tuple[str, float, str]],
    ) -> list[GroqEvaluation]:
        """Run explanations concurrently with bounded parallelism."""
        sem = asyncio.Semaphore(3)

        async def _one(file_name: str, score: float, text: str) -> GroqEvaluation:
            async with sem:
                explanation = await self.explain(algorithm_name, job_description, text, score)
            is_good = explanation.strip().lower().startswith("good fit")
            return GroqEvaluation(file_name, score, explanation, is_good)

        return await asyncio.gather(*(_one(f, s, t) for f, s, t in items))
