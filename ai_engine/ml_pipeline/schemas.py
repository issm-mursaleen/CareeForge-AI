"""Pydantic schemas for every ML pipeline stage.

Data Gathering      → RawCandidateRecord
Data Cleaning       → CleaningStats
Feature Engineering → FeatureInfo
Model Training      → TrainingResult
Model Evaluation    → EvaluationResult

Every model validates its own invariants so downstream code can trust
the data it receives without defensive null-checks.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator


# ── Valid education levels (must match OneHotEncoder categories) ─────────────
_VALID_EDUCATION = {"associate", "bachelors", "diploma", "doctorate", "masters", "unknown", "phd"}


class RawCandidateRecord(BaseModel):
    """Atomic training record: one candidate evaluated against one job.

    Produced by the Data Gathering stage.
    label=1 → Good Fit, label=0 → Bad Fit.
    """

    candidate_id: str = Field(..., description="Unique ID (resume_id or composite key)")
    resume_text: str = Field(..., min_length=10, description="Full extracted resume text")
    job_description: str = Field(..., min_length=10, description="Job description text")
    skills: list[str] = Field(default_factory=list)
    experience_years: float = Field(default=0.0, ge=0.0, le=70.0)
    education: str = Field(default="unknown")
    target_label: int = Field(..., ge=0, le=1, description="1 = Good Fit, 0 = Bad Fit")

    @field_validator("resume_text", "job_description")
    @classmethod
    def non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("text field cannot be empty")
        return v

    @field_validator("candidate_id")
    @classmethod
    def valid_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("candidate_id cannot be empty")
        return v

    @field_validator("education")
    @classmethod
    def valid_education(cls, v: str) -> str:
        v = v.strip().lower()
        return v if v in _VALID_EDUCATION else "unknown"

    @field_validator("skills")
    @classmethod
    def clean_skills(cls, v: list[str]) -> list[str]:
        return [s.strip() for s in v if s and s.strip()]


class CleaningStats(BaseModel):
    """Statistics produced by the Data Cleaning stage."""

    records_before: int = Field(..., ge=0)
    records_after: int = Field(..., ge=0)
    removed_missing: int = Field(default=0, ge=0)
    removed_duplicates: int = Field(default=0, ge=0)
    removed_outliers: int = Field(default=0, ge=0)

    @property
    def total_removed(self) -> int:
        return self.records_before - self.records_after

    @model_validator(mode="after")
    def records_after_lte_before(self) -> "CleaningStats":
        if self.records_after > self.records_before:
            raise ValueError("records_after cannot exceed records_before")
        return self


class FeatureInfo(BaseModel):
    """Metadata from the Feature Engineering stage."""

    total_features: int = Field(..., ge=1)
    tfidf_resume_features: int = Field(..., ge=0)
    tfidf_jd_features: int = Field(..., ge=0)
    numeric_features: int = Field(..., ge=0)
    categorical_features: int = Field(..., ge=0)
    positive_class_ratio: float = Field(default=0.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def features_sum_to_total(self) -> "FeatureInfo":
        computed = (
            self.tfidf_resume_features
            + self.tfidf_jd_features
            + self.numeric_features
            + self.categorical_features
        )
        if computed != self.total_features:
            raise ValueError(
                f"feature sub-counts ({computed}) must sum to total_features ({self.total_features})"
            )
        return self


class TrainingResult(BaseModel):
    """Output from the Model Training stage."""

    model_name: str = Field(..., min_length=1)
    algorithm: str = Field(..., min_length=1)
    train_size: int = Field(..., ge=1)
    test_size: int = Field(..., ge=1)
    cv_scores: list[float] = Field(default_factory=list)
    cv_mean: float = Field(default=0.0, ge=0.0, le=1.0)
    cv_std: float = Field(default=0.0, ge=0.0)
    model_path: str = Field(..., min_length=1)

    @field_validator("cv_scores")
    @classmethod
    def valid_cv_scores(cls, v: list[float]) -> list[float]:
        for score in v:
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"cv_score {score} must be in [0, 1]")
        return v


class EvaluationResult(BaseModel):
    """Comprehensive metrics from the Model Evaluation stage."""

    accuracy: float = Field(..., ge=0.0, le=1.0)
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1_score: float = Field(..., ge=0.0, le=1.0)
    roc_auc: float = Field(default=0.5, ge=0.0, le=1.0)
    confusion_matrix: list[list[int]] = Field(default_factory=list)
    roc_curve_fpr: list[float] = Field(default_factory=list)
    roc_curve_tpr: list[float] = Field(default_factory=list)
    classification_report: str = Field(default="")

    @field_validator("confusion_matrix")
    @classmethod
    def valid_confusion_matrix(cls, v: list[list[int]]) -> list[list[int]]:
        if v and len(v) != 2:
            raise ValueError("binary confusion matrix must be 2×2")
        for row in v:
            if len(row) != 2:
                raise ValueError("each confusion matrix row must have 2 elements")
            for cell in row:
                if cell < 0:
                    raise ValueError("confusion matrix values must be non-negative")
        return v

    @field_validator("roc_curve_fpr", "roc_curve_tpr")
    @classmethod
    def valid_roc_curve(cls, v: list[float]) -> list[float]:
        for val in v:
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"ROC curve value {val} must be in [0, 1]")
        return v

    @model_validator(mode="after")
    def roc_curve_lengths_match(self) -> "EvaluationResult":
        if len(self.roc_curve_fpr) != len(self.roc_curve_tpr):
            raise ValueError("roc_curve_fpr and roc_curve_tpr must have the same length")
        return self
