from __future__ import annotations

from beanie import Document
from pydantic import Field, field_validator


class MLTrainingRecord(Document):
    """One training sample stored in MongoDB Atlas.

    Seeded from CSV via database/seeds/seed_ml_training.py.
    Consumed by ml_service._build_raw_records() at retrain time.
    """

    candidate_id: str = Field(..., min_length=1)
    resume_text: str = Field(..., min_length=10)
    job_description: str = Field(..., min_length=10)
    experience_years: float = Field(default=0.0, ge=0.0, le=70.0)
    education: str = Field(default="unknown")
    is_good_fit: int = Field(..., ge=0, le=1, description="1 = Good Fit, 0 = Bad Fit")
    composite: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("candidate_id")
    @classmethod
    def _strip_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("candidate_id cannot be blank")
        return v

    @field_validator("resume_text", "job_description")
    @classmethod
    def _strip_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("text field cannot be blank")
        return v

    @field_validator("education")
    @classmethod
    def _valid_education(cls, v: str) -> str:
        allowed = {"associate", "bachelors", "diploma", "doctorate", "masters", "unknown", "phd"}
        v = v.strip().lower()
        return v if v in allowed else "unknown"

    class Settings:
        name = "ml_training_data"
