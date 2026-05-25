from __future__ import annotations

from datetime import datetime

from beanie import Document
from pydantic import Field
from pymongo import DESCENDING, IndexModel


class MLMetricsDoc(Document):
    """Persisted snapshot of a trained ML pipeline's test-set metrics."""

    model_name: str = "job_role_classifier"
    algorithm: str = "LinearSVC"
    vectorizer: str = "TfidfVectorizer(word 1-2) + TfidfVectorizer(char_wb 3-5)"
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    train_size: int = 0
    test_size: int = 0
    num_classes: int = 0
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "ml_metrics"
        indexes = [
            IndexModel([("created_at", DESCENDING)]),
        ]
