"""MongoDB document for Good Fit binary-classifier metrics.

Collection: ml_model_metrics
One document per training run — full history is preserved.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from beanie import Document
from pydantic import Field
from pymongo import DESCENDING, IndexModel


class GoodFitMetricsDoc(Document):
    """Persisted snapshot of a trained Good Fit binary classifier run."""

    model_name: str = "good_fit_classifier"
    algorithm: str

    # Dataset info
    dataset_size: int = 0
    train_size: int = 0
    test_size: int = 0
    feature_count: int = 0

    # Core metrics
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float = 0.0

    # Detailed evaluation artefacts
    confusion_matrix: list[list[int]] = Field(default_factory=list)
    roc_curve_fpr: list[float] = Field(default_factory=list)
    roc_curve_tpr: list[float] = Field(default_factory=list)

    # Training metadata
    cv_mean: float = 0.0
    cv_std: float = 0.0
    cleaning_stats: dict[str, Any] = Field(default_factory=dict)
    feature_info: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "ml_model_metrics"
        indexes = [
            IndexModel([("created_at", DESCENDING)]),
        ]
