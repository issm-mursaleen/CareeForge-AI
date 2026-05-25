from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Algo = Literal["bm25", "word2vec", "bert"]


class RankingRequest(BaseModel):
    job_title: str = Field(min_length=2, max_length=120)
    job_description: str = Field(min_length=20, max_length=10000)
    resume_ids: list[str] = Field(min_length=1, max_length=100)
    algorithms: list[Algo] = Field(default_factory=lambda: ["bm25", "bert"])
    explain_top_k: int = Field(default=3, ge=0, le=20)


class RankedCandidate(BaseModel):
    resume_id: str
    file_name: str
    bm25: float | None = None
    word2vec: float | None = None
    bert: float | None = None
    composite: float
    is_good_fit: bool | None = None
    explanation: str | None = None


class RankingResponse(BaseModel):
    job_match_id: str
    job_title: str
    algorithms: list[str]
    ranked: list[RankedCandidate]
    created_at: datetime
