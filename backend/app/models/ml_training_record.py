from __future__ import annotations
from beanie import Document


class MLTrainingRecord(Document):
    candidate_id: str
    resume_text: str
    job_description: str
    experience_years: float = 0.0
    education: str = "unknown"
    is_good_fit: int  # 0 or 1
    composite: float = 0.0

    class Settings:
        name = "ml_training_data"
