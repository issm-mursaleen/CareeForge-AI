from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from ..core.config import get_settings
from ..core.exceptions import ValidationFailed
from ..models.user import User
from ..schemas.resume import (
    ATSBreakdownDTO, ResumeAnalysisResponse, ResumeDetailResponse, ResumeListItem,
)
from ..services.resume_service import ResumeService
from .dependencies import get_current_user

router = APIRouter()

_ALLOWED_EXT = {".pdf", ".docx", ".txt"}


@router.post("/analyze", response_model=ResumeAnalysisResponse, status_code=201)
async def analyze(
    file: UploadFile = File(...),
    job_description: str | None = Form(default=None),
    user: User = Depends(get_current_user),
) -> ResumeAnalysisResponse:
    _validate_file(file)
    file_bytes = await file.read()
    resume = await ResumeService.analyze_and_store(user, file.filename, file_bytes, job_description)
    return _to_analysis_dto(resume)


@router.get("", response_model=list[ResumeListItem])
async def list_resumes(user: User = Depends(get_current_user)) -> list[ResumeListItem]:
    resumes = await ResumeService.list_for_user(user)
    return [
        ResumeListItem(
            id=str(r.id),
            file_name=r.file_name,
            ats_score=r.ats.score if r.ats else None,
            created_at=r.created_at,
        )
        for r in resumes
    ]


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(resume_id: str, user: User = Depends(get_current_user)) -> ResumeDetailResponse:
    resume = await ResumeService.get_for_user(user, resume_id)
    base = _to_analysis_dto(resume)
    return ResumeDetailResponse(
        **base.model_dump(),
        raw_text_preview=resume.raw_text[:600],
    )


def _validate_file(file: UploadFile) -> None:
    name = (file.filename or "").lower()
    if not any(name.endswith(ext) for ext in _ALLOWED_EXT):
        raise ValidationFailed("Unsupported file type. Use PDF, DOCX, or TXT.")
    settings = get_settings()
    if file.size and file.size > settings.max_upload_mb * 1024 * 1024:
        raise ValidationFailed(f"File exceeds {settings.max_upload_mb} MB")


def _to_analysis_dto(resume) -> ResumeAnalysisResponse:
    ats = resume.ats
    return ResumeAnalysisResponse(
        id=str(resume.id),
        file_name=resume.file_name,
        ats=ATSBreakdownDTO(
            score=ats.score,
            section_completeness=ats.section_completeness,
            contact_info=ats.contact_info,
            length=ats.length,
            skill_density=ats.skill_density,
            jd_match=ats.jd_match,
        ),
        skills=resume.skills,
        missing_skills=resume.missing_skills,
        quality_notes=resume.quality_notes,
        suggestions=resume.quality_notes,
        predicted_role=resume.predicted_role,
        created_at=resume.created_at,
    )
