from __future__ import annotations

from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import DESCENDING, IndexModel


class AILog(Document):
    user_id: PydanticObjectId | None = None
    feature: str  # resume_analysis | ranking | interview | chat | roadmap
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    success: bool = True
    error: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "ai_logs"
        indexes = [
            IndexModel([("created_at", DESCENDING)], expireAfterSeconds=60 * 60 * 24 * 90),
            IndexModel([("user_id", 1)]),
        ]
