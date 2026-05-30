"""MongoDB document for Good Fit binary-classifier metrics.

Collection: ml_model_metrics
One document per training run — full history is preserved.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from beanie import Document
from pydantic import Field, field_validator, model_validator
from pymongo import DESCENDING, IndexModel


class GoodFitMetricsDoc(Document):
    """Persisted snapshot of a trained Good Fit binary classifier run."""

    model_name: str = Field(default="good_fit_classifier", min_length=1)
    algorithm: str = Field(..., min_length=1)

    # Dataset info
    dataset_size: int = Field(default=0, ge=0)
    train_size: int = Field(default=0, ge=0)
    test_size: int = Field(default=0, ge=0)
    feature_count: int = Field(default=0, ge=0)

    # Core metrics — all must be in [0, 1]
    accuracy: float = Field(..., ge=0.0, le=1.0)
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1_score: float = Field(..., ge=0.0, le=1.0)
    roc_auc: float = Field(default=0.5, ge=0.0, le=1.0)

    # Detailed evaluation artefacts
    confusion_matrix: list[list[int]] = Field(default_factory=list)
    roc_curve_fpr: list[float] = Field(default_factory=list)
    roc_curve_tpr: list[float] = Field(default_factory=list)

    # Training metadata
    cv_mean: float = Field(default=0.0, ge=0.0, le=1.0)
    cv_std: float = Field(default=0.0, ge=0.0)
    cleaning_stats: dict[str, Any] = Field(default_factory=dict)
    feature_info: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("confusion_matrix")
    @classmethod
    def valid_confusion_matrix(cls, v: list[list[int]]) -> list[list[int]]:
        if v and len(v) != 2:
            raise ValueError("binary confusion matrix must be 2×2")
        for row in v:
            if len(row) != 2:
                raise ValueError("each row must have exactly 2 elements")
            for cell in row:
                if cell < 0:
                    raise ValueError("confusion matrix values must be non-negative")
        return v

    @field_validator("roc_curve_fpr", "roc_curve_tpr")
    @classmethod
    def valid_roc_values(cls, v: list[float]) -> list[float]:
        for val in v:
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"ROC value {val:.4f} must be in [0, 1]")
        return v

    @model_validator(mode="after")
    def roc_lengths_match(self) -> "GoodFitMetricsDoc":
        if len(self.roc_curve_fpr) != len(self.roc_curve_tpr):
            raise ValueError("roc_curve_fpr and roc_curve_tpr must have equal length")
        return self

    @model_validator(mode="after")
    def train_test_sizes_consistent(self) -> "GoodFitMetricsDoc":
        if self.dataset_size > 0 and (self.train_size + self.test_size) > self.dataset_size:
            raise ValueError("train_size + test_size cannot exceed dataset_size")
        return self

    class Settings:
        name = "ml_model_metrics"
        indexes = [
            IndexModel([("created_at", DESCENDING)]),
        ]
