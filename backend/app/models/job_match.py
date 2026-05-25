from __future__ import annotations

from datetime import datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import DESCENDING, IndexModel


class CandidateScore(BaseModel):
    resume_id: PydanticObjectId
    file_name: str
    bm25: float | None = None
    word2vec: float | None = None
    bert: float | None = None
    composite: float | None = None
    is_good_fit: bool | None = None
    explanation: str | None = None


class JobMatch(Document):
    recruiter_id: Indexed(PydanticObjectId)
    job_title: str
    job_description: str
    algorithms: list[str] = Field(default_factory=lambda: ["bm25", "bert"])
    candidates: list[CandidateScore] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "job_matches"
        indexes = [
            IndexModel([("recruiter_id", 1), ("created_at", DESCENDING)]),
        ]
