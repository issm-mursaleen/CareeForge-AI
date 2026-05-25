from __future__ import annotations

from datetime import datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field


class InterviewQA(BaseModel):
    question: str
    category: str
    expected_topics: list[str] = Field(default_factory=list)
    answer: str | None = None
    score: float | None = None
    feedback: str | None = None


class Interview(Document):
    user_id: Indexed(PydanticObjectId)
    resume_id: PydanticObjectId | None = None
    role: str
    qa: list[InterviewQA] = Field(default_factory=list)
    overall_score: float | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "interviews"
