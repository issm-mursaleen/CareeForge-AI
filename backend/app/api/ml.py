"""Secure ML metrics API.

GET  /api/v1/ml/metrics   — training history  (any authenticated user)
GET  /api/v1/ml/latest    — latest run details (any authenticated user)
POST /api/v1/ml/retrain   — trigger retrain   (admin only)

All endpoints use typed Pydantic response models for strict serialisation
validation — no raw dicts are returned to the client.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator, model_validator

from ..models.user import User, UserRole
from ..services.ml_service import MLService
from .dependencies import get_current_user, require_role

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Response schemas ─────────────────────────────────────────────────────────

class MetricPoint(BaseModel):
    metric: str = Field(..., min_length=1)
    value: float = Field(..., ge=0.0, le=1.0)


class RocCurve(BaseModel):
    fpr: list[float]
    tpr: list[float]

    @model_validator(mode="after")
    def lengths_match(self) -> "RocCurve":
        if len(self.fpr) != len(self.tpr):
            raise ValueError("fpr and tpr must have equal length")
        return self


class MLMetricsSummary(BaseModel):
    id: str
    model_name: str
    algorithm: str
    dataset_size: int = Field(..., ge=0)
    accuracy: float = Field(..., ge=0.0, le=1.0)
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1_score: float = Field(..., ge=0.0, le=1.0)
    roc_auc: float = Field(..., ge=0.0, le=1.0)
    created_at: str


class MLMetricsDetail(MLMetricsSummary):
    train_size: int = Field(..., ge=0)
    test_size: int = Field(..., ge=0)
    feature_count: int = Field(..., ge=0)
    confusion_matrix: list[list[int]]
    roc_curve: RocCurve
    cv_mean: float = Field(..., ge=0.0, le=1.0)
    cv_std: float = Field(..., ge=0.0)
    cleaning_stats: dict[str, Any]
    feature_info: dict[str, Any]
    metrics: list[MetricPoint]

    @field_validator("confusion_matrix")
    @classmethod
    def valid_cm(cls, v: list[list[int]]) -> list[list[int]]:
        if v and len(v) != 2:
            raise ValueError("binary confusion matrix must be 2×2")
        for row in v:
            if len(row) != 2:
                raise ValueError("each row must have 2 elements")
        return v


class RetrainResponse(BaseModel):
    status: str
    message: str
    triggered_by: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/metrics", response_model=list[MLMetricsSummary])
async def get_metrics(
    limit: int = 20,
    _: User = Depends(get_current_user),
) -> list[MLMetricsSummary]:
    """Return the training history list (most recent first)."""
    docs = await MLService.get_metrics_history(limit=min(limit, 100))
    return [
        MLMetricsSummary(
            id=str(d.id),
            model_name=d.model_name,
            algorithm=d.algorithm,
            dataset_size=d.dataset_size,
            accuracy=d.accuracy,
            precision=d.precision,
            recall=d.recall,
            f1_score=d.f1_score,
            roc_auc=d.roc_auc,
            created_at=d.created_at.isoformat(),
        )
        for d in docs
    ]


@router.get("/latest", response_model=MLMetricsDetail)
async def get_latest(
    _: User = Depends(get_current_user),
) -> MLMetricsDetail:
    """Return the most recent model's full metrics, confusion matrix, and ROC curve."""
    doc = await MLService.get_latest_metrics()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No ML metrics found. POST /api/v1/ml/retrain (admin) to train the model.",
        )
    return MLMetricsDetail(
        id=str(doc.id),
        model_name=doc.model_name,
        algorithm=doc.algorithm,
        dataset_size=doc.dataset_size,
        train_size=doc.train_size,
        test_size=doc.test_size,
        feature_count=doc.feature_count,
        accuracy=doc.accuracy,
        precision=doc.precision,
        recall=doc.recall,
        f1_score=doc.f1_score,
        roc_auc=doc.roc_auc,
        confusion_matrix=doc.confusion_matrix,
        roc_curve=RocCurve(fpr=doc.roc_curve_fpr, tpr=doc.roc_curve_tpr),
        cv_mean=doc.cv_mean,
        cv_std=doc.cv_std,
        cleaning_stats=doc.cleaning_stats,
        feature_info=doc.feature_info,
        created_at=doc.created_at.isoformat(),
        metrics=[
            MetricPoint(metric="Accuracy",  value=doc.accuracy),
            MetricPoint(metric="Precision", value=doc.precision),
            MetricPoint(metric="Recall",    value=doc.recall),
            MetricPoint(metric="F1-Score",  value=doc.f1_score),
            MetricPoint(metric="ROC AUC",   value=doc.roc_auc),
        ],
    )


@router.post("/retrain", status_code=status.HTTP_202_ACCEPTED, response_model=RetrainResponse)
async def retrain(
    background_tasks: BackgroundTasks,
    user: User = Depends(require_role(UserRole.ADMIN)),
) -> RetrainResponse:
    """Trigger a full ML pipeline retrain in the background. Admin only."""
    async def _run() -> None:
        try:
            await MLService.run_full_pipeline()
            logger.info("retrain_completed: triggered_by=%s", str(user.id))
        except Exception as exc:
            logger.error("retrain_failed: %s triggered_by=%s", str(exc), str(user.id))

    background_tasks.add_task(_run)
    return RetrainResponse(
        status="started",
        message="Retrain pipeline started in background. Check GET /api/v1/ml/latest for results.",
        triggered_by=str(user.id),
    )
