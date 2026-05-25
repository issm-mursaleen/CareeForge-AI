from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from ..core.exceptions import ValidationFailed
from ..models.user import User
from ..schemas.ranking import RankedCandidate, RankingRequest, RankingResponse
from ..services.ranking_service import RankingService
from .dependencies import get_current_user

router = APIRouter()

_VALID_ALGOS = {"bm25", "word2vec", "bert"}
_ALLOWED_EXT = {".pdf", ".docx", ".txt"}


@router.post("", response_model=RankingResponse, status_code=201)
async def run_ranking(
    req: RankingRequest,
    user: User = Depends(get_current_user),
) -> RankingResponse:
    job_match = await RankingService.rank(
        recruiter=user,
        job_title=req.job_title,
        job_description=req.job_description,
        resume_ids=req.resume_ids,
        algorithms=req.algorithms,
        explain_top_k=req.explain_top_k,
    )
    return _to_response(job_match)


@router.post("/upload", response_model=RankingResponse, status_code=201)
async def rank_uploaded_files(
    files: list[UploadFile] = File(...),
    job_title: str = Form(default="Untitled role"),
    job_description: str = Form(...),
    algorithms: str = Form(default="bm25,bert"),
    explain_top_k: int = Form(default=3),
    user: User = Depends(get_current_user),
) -> RankingResponse:
    """Rank resumes uploaded directly — no prior analysis needed."""
    if not job_description.strip():
        raise ValidationFailed("job_description is required")

    algo_list = [a.strip() for a in algorithms.split(",") if a.strip() in _VALID_ALGOS]
    if not algo_list:
        raise ValidationFailed("Provide at least one valid algorithm: bm25, word2vec, bert")

    if not files:
        raise ValidationFailed("Upload at least one resume file")

    file_pairs: list[tuple[str, bytes]] = []
    for f in files:
        name = (f.filename or "resume.pdf").lower()
        if not any(name.endswith(ext) for ext in _ALLOWED_EXT):
            raise ValidationFailed(f"Unsupported file type '{f.filename}'. Use PDF, DOCX, or TXT.")
        file_pairs.append((f.filename or "resume.pdf", await f.read()))

    job_match = await RankingService.rank_raw_files(
        recruiter=user,
        job_title=job_title.strip() or "Untitled role",
        job_description=job_description,
        file_pairs=file_pairs,
        algorithms=algo_list,
        explain_top_k=explain_top_k,
    )
    return _to_response(job_match)


def _to_response(job_match) -> RankingResponse:
    return RankingResponse(
        job_match_id=str(job_match.id),
        job_title=job_match.job_title,
        algorithms=job_match.algorithms,
        ranked=[
            RankedCandidate(
                resume_id=str(c.resume_id),
                file_name=c.file_name,
                bm25=c.bm25,
                word2vec=c.word2vec,
                bert=c.bert,
                composite=c.composite or 0,
                is_good_fit=c.is_good_fit,
                explanation=c.explanation,
            )
            for c in job_match.candidates
        ],
        created_at=job_match.created_at,
    )
