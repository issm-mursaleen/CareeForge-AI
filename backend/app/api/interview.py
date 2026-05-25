from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ai_engine.interview import InterviewGenerator

from ..models.interview import Interview, InterviewQA
from ..models.user import User
from ..services.resume_service import ResumeService
from .dependencies import get_current_user

router = APIRouter()


class GenerateRequest(BaseModel):
    role: str = Field(min_length=2, max_length=60)
    resume_id: str
    count: int = Field(default=5, ge=1, le=15)


class GenerateResponse(BaseModel):
    interview_id: str
    questions: list[dict]


class AnswerRequest(BaseModel):
    question_index: int
    answer: str = Field(min_length=1, max_length=4000)


class AnswerResponse(BaseModel):
    score: float
    feedback: str
    strengths: list[str]
    improvements: list[str]


@router.post("/generate", response_model=GenerateResponse, status_code=201)
async def generate(req: GenerateRequest, user: User = Depends(get_current_user)) -> GenerateResponse:
    resume = await ResumeService.get_for_user(user, req.resume_id)
    gen = InterviewGenerator()
    questions = await gen.generate(req.role, resume.raw_text, count=req.count)
    interview = Interview(
        user_id=user.id,
        resume_id=resume.id,
        role=req.role,
        qa=[InterviewQA(**q.__dict__) for q in questions],
    )
    await interview.insert()
    return GenerateResponse(
        interview_id=str(interview.id),
        questions=[q.model_dump() for q in interview.qa],
    )


@router.post("/{interview_id}/answer", response_model=AnswerResponse)
async def answer(
    interview_id: str, req: AnswerRequest, user: User = Depends(get_current_user)
) -> AnswerResponse:
    from beanie import PydanticObjectId
    interview = await Interview.get(PydanticObjectId(interview_id))
    if not interview or interview.user_id != user.id:
        from ..core.exceptions import NotFound
        raise NotFound("Interview not found")
    if not (0 <= req.question_index < len(interview.qa)):
        from ..core.exceptions import ValidationFailed
        raise ValidationFailed("question_index out of range")

    gen = InterviewGenerator()
    qa = interview.qa[req.question_index]
    score = await gen.score_answer(qa.question, req.answer, interview.role)
    qa.answer = req.answer
    qa.score = score.score
    qa.feedback = score.feedback
    await interview.save()
    return AnswerResponse(
        score=score.score,
        feedback=score.feedback,
        strengths=score.strengths,
        improvements=score.improvements,
    )
