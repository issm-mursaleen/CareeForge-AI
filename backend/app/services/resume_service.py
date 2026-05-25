"""Resume upload → extract → preprocess → evaluate → persist."""
from __future__ import annotations

import asyncio
from typing import Iterable

from beanie import PydanticObjectId

from ai_engine.evaluation import audit_resume_quality, compute_ats_score, extract_skills
from ai_engine.extraction import extract_text

from ..core.exceptions import NotFound, ValidationFailed
from ..core.ml_model import predict_role
from ..models.resume import ATSBreakdown, Resume
from ..models.user import User


class ResumeService:
    @staticmethod
    async def analyze_and_store(
        user: User,
        file_name: str,
        file_bytes: bytes,
        job_description: str | None = None,
    ) -> Resume:
        # CPU-bound work — offload from the event loop
        doc = await asyncio.to_thread(extract_text, file_name, file_bytes)
        if doc.is_empty:
            raise ValidationFailed("Could not extract any text from the file")

        ats, skills, quality, predicted = await asyncio.gather(
            asyncio.to_thread(compute_ats_score, doc.text, job_description),
            asyncio.to_thread(extract_skills, doc.text),
            asyncio.to_thread(audit_resume_quality, doc.text),
            asyncio.to_thread(predict_role, doc.text),
        )

        resume = Resume(
            user_id=user.id,
            file_name=file_name,
            raw_text=doc.text,
            char_count=doc.char_count,
            ats=ATSBreakdown(
                score=ats.score,
                section_completeness=ats.breakdown.get("section_completeness", 0),
                contact_info=ats.breakdown.get("contact_info", 0),
                length=ats.breakdown.get("length", 0),
                skill_density=ats.breakdown.get("skill_density", 0),
                jd_match=ats.breakdown.get("jd_match", 0),
            ),
            skills=skills.found,
            missing_skills=ats.missing_skills,
            weak_sections=quality.weak_phrase_hits,
            predicted_role=predicted,
            quality_notes=ats.notes + quality.suggestions,
        )
        await resume.insert()
        return resume

    @staticmethod
    async def list_for_user(user: User) -> list[Resume]:
        return await Resume.find(Resume.user_id == user.id).sort(-Resume.created_at).to_list()

    @staticmethod
    async def get_for_user(user: User, resume_id: str) -> Resume:
        try:
            obj_id = PydanticObjectId(resume_id)
        except Exception as e:
            raise ValidationFailed(f"Invalid resume id: {resume_id}") from e
        resume = await Resume.get(obj_id)
        if not resume or resume.user_id != user.id:
            raise NotFound("Resume not found")
        return resume

    @staticmethod
    async def get_many_for_user(user: User, resume_ids: Iterable[str]) -> list[Resume]:
        ids = list(resume_ids)
        try:
            obj_ids = [PydanticObjectId(r) for r in ids]
        except Exception as e:
            raise ValidationFailed(f"One or more resume IDs are invalid: {e}") from e
        # Use expression-based query so Beanie handles type coercion correctly
        resumes = await Resume.find(
            {"_id": {"$in": obj_ids}},
            Resume.user_id == user.id,
        ).to_list()
        return resumes
