from __future__ import annotations

from datetime import datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field


class MilestoneDoc(BaseModel):
    week: int
    title: str
    description: str
    skills: list[str] = Field(default_factory=list)


class ResourceDoc(BaseModel):
    title: str
    url: str | None = None
    type: str  # course | book | project | doc


class RoadmapDoc(Document):
    user_id: Indexed(PydanticObjectId)
    target_role: str
    skill_gaps: list[str] = Field(default_factory=list)
    milestones: list[MilestoneDoc] = Field(default_factory=list)
    resources: list[ResourceDoc] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "roadmaps"
