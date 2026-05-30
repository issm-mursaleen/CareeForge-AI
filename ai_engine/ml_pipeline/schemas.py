"""Pydantic schemas for every ML pipeline stage.

Data Gathering     → RawCandidateRecord
Data Cleaning      → CleaningStats
Feature Engineering → FeatureInfo
Model Training     → TrainingResult
Model Evaluation   → EvaluationResult
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class RawCandidateRecord(BaseModel):
    """Atomic training record: one candidate evaluated against one job.

    Data Gathering stage: sourced from job_matches + resumes MongoDB
    collections.  label=1 → Good Fit, label=0 → Bad Fit.
    """

    candidate_id: str = Field(description="Unique ID (resume_id or composite key)")
    resume_text: str = Field(description="Full extracted resume text")
    job_description: str = Field(description="Job description the candidate was matched to")
    skills: list[str] = Field(default_factory=list, description="Skills extracted from resume")
    experience_years: float = Field(default=0.0, ge=0.0, le=70.0)
    education: str = Field(default="unknown")
    target_label: int = Field(..., ge=0, le=1, description="1 = Good Fit, 0 = Bad Fit")

    @field_validator("resume_text", "job_description")
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("text field cannot be empty")
        return v.strip()

    @field_validator("candidate_id")
    @classmethod
    def valid_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("candidate_id cannot be empty")
        return v.strip()


class CleaningStats(BaseModel):
    """Statistics produced by the Data Cleaning stage."""

    records_before: int
    records_after: int
    removed_missing: int = 0
    removed_duplicates: int = 0
    removed_outliers: int = 0

    @property
    def total_removed(self) -> int:
        return self.records_before - self.records_after


class FeatureInfo(BaseModel):
    """Metadata from the Feature Engineering stage."""

    total_features: int
    tfidf_resume_features: int
    tfidf_jd_features: int
    numeric_features: int
    categorical_features: int
    positive_class_ratio: float = 0.0


class TrainingResult(BaseModel):
    """Output from the Model Training stage."""

    model_name: str
    algorithm: str
    train_size: int
    test_size: int
    cv_scores: list[float] = Field(default_factory=list)
    cv_mean: float = 0.0
    cv_std: float = 0.0
    model_path: str


class EvaluationResult(BaseModel):
    """Comprehensive metrics from the Model Evaluation stage."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    confusion_matrix: list[list[int]]
    roc_curve_fpr: list[float]
    roc_curve_tpr: list[float]
    classification_report: str
