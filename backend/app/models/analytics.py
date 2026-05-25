from __future__ import annotations

from datetime import date, datetime

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel


class Analytics(Document):
    user_id: PydanticObjectId
    date: date
    resumes_analyzed: int = 0
    rankings_run: int = 0
    interviews_taken: int = 0
    chat_messages: int = 0
    ats_score_avg: float | None = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "analytics"
        indexes = [
            IndexModel([("user_id", 1), ("date", 1)], unique=True),
        ]
