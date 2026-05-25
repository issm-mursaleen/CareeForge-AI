from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ai_engine.roadmap import RoadmapPlanner

from ..models.roadmap import MilestoneDoc, ResourceDoc, RoadmapDoc
from ..models.user import User
from ..services.resume_service import ResumeService
from .dependencies import get_current_user

router = APIRouter()


class RoadmapRequest(BaseModel):
    target_role: str = Field(min_length=2, max_length=60)
    resume_id: str


class RoadmapResponse(BaseModel):
    id: str
    target_role: str
    skill_gaps: list[str]
    milestones: list[dict]
    resources: list[dict]


@router.post("", response_model=RoadmapResponse, status_code=201)
async def create_roadmap(req: RoadmapRequest, user: User = Depends(get_current_user)) -> RoadmapResponse:
    resume = await ResumeService.get_for_user(user, req.resume_id)
    planner = RoadmapPlanner()
    roadmap = await planner.plan(req.target_role, resume.raw_text)
    doc = RoadmapDoc(
        user_id=user.id,
        target_role=roadmap.target_role,
        skill_gaps=roadmap.skill_gaps,
        milestones=[MilestoneDoc(**m.__dict__) for m in roadmap.milestones],
        resources=[ResourceDoc(**r) for r in roadmap.resources],
    )
    await doc.insert()
    return RoadmapResponse(
        id=str(doc.id),
        target_role=doc.target_role,
        skill_gaps=doc.skill_gaps,
        milestones=[m.model_dump() for m in doc.milestones],
        resources=[r.model_dump() for r in doc.resources],
    )


@router.get("", response_model=list[RoadmapResponse])
async def list_roadmaps(user: User = Depends(get_current_user)) -> list[RoadmapResponse]:
    docs = await RoadmapDoc.find(RoadmapDoc.user_id == user.id).to_list()
    return [
        RoadmapResponse(
            id=str(d.id),
            target_role=d.target_role,
            skill_gaps=d.skill_gaps,
            milestones=[m.model_dump() for m in d.milestones],
            resources=[r.model_dump() for r in d.resources],
        )
        for d in docs
    ]
