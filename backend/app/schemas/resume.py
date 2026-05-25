from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ATSBreakdownDTO(BaseModel):
    score: float
    section_completeness: float
    contact_info: float
    length: float
    skill_density: float
    jd_match: float


class ResumeAnalysisResponse(BaseModel):
    id: str
    file_name: str
    ats: ATSBreakdownDTO
    skills: list[str]
    missing_skills: list[str] = Field(default_factory=list)
    quality_notes: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    predicted_role: str | None = None
    created_at: datetime


class ResumeListItem(BaseModel):
    id: str
    file_name: str
    ats_score: float | None
    created_at: datetime


class ResumeDetailResponse(ResumeAnalysisResponse):
    raw_text_preview: str
