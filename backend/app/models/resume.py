from __future__ import annotations

from datetime import datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import DESCENDING, IndexModel


class ATSBreakdown(BaseModel):
    score: float
    section_completeness: float = 0
    contact_info: float = 0
    length: float = 0
    skill_density: float = 0
    jd_match: float = 0


class Resume(Document):
    user_id: Indexed(PydanticObjectId)
    file_name: str
    file_url: str | None = None
    raw_text: str
    char_count: int = 0
    ats: ATSBreakdown | None = None
    skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    weak_sections: list[str] = Field(default_factory=list)
    category: str | None = None
    predicted_role: str | None = None
    quality_notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "resumes"
        indexes = [
            IndexModel([("user_id", 1), ("created_at", DESCENDING)]),
        ]
