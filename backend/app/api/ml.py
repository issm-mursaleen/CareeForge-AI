"""Secure ML metrics API.

GET  /api/v1/ml/metrics   — training history  (any authenticated user)
GET  /api/v1/ml/latest    — latest run details (any authenticated user)
POST /api/v1/ml/retrain   — trigger retrain   (admin only)
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from ..models.user import User, UserRole
from ..services.ml_service import MLService
from .dependencies import get_current_user, require_role

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/metrics")
async def get_metrics(
    limit: int = 20,
    _: User = Depends(get_current_user),
) -> list[dict]:
    """Return the training history list (most recent first).

    Accessible by any authenticated user.
    """
    docs = await MLService.get_metrics_history(limit=min(limit, 100))
    return [
        {
            "id": str(d.id),
            "model_name": d.model_name,
            "algorithm": d.algorithm,
            "dataset_size": d.dataset_size,
            "accuracy": d.accuracy,
            "precision": d.precision,
            "recall": d.recall,
            "f1_score": d.f1_score,
            "roc_auc": d.roc_auc,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.get("/latest")
async def get_latest(
    _: User = Depends(get_current_user),
) -> dict:
    """Return the most recent model's full metrics, confusion matrix, and ROC curve.

    Accessible by any authenticated user.
    """
    doc = await MLService.get_latest_metrics()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No ML metrics found. "
                "POST /api/v1/ml/retrain (admin) to train the model."
            ),
        )
    return {
        "id": str(doc.id),
        "model_name": doc.model_name,
        "algorithm": doc.algorithm,
        "dataset_size": doc.dataset_size,
        "train_size": doc.train_size,
        "test_size": doc.test_size,
        "feature_count": doc.feature_count,
        "accuracy": doc.accuracy,
        "precision": doc.precision,
        "recall": doc.recall,
        "f1_score": doc.f1_score,
        "roc_auc": doc.roc_auc,
        "confusion_matrix": doc.confusion_matrix,
        "roc_curve": {
            "fpr": doc.roc_curve_fpr,
            "tpr": doc.roc_curve_tpr,
        },
        "cv_mean": doc.cv_mean,
        "cv_std": doc.cv_std,
        "cleaning_stats": doc.cleaning_stats,
        "feature_info": doc.feature_info,
        "created_at": doc.created_at.isoformat(),
        "metrics": [
            {"metric": "Accuracy", "value": doc.accuracy},
            {"metric": "Precision", "value": doc.precision},
            {"metric": "Recall", "value": doc.recall},
            {"metric": "F1-Score", "value": doc.f1_score},
            {"metric": "ROC AUC", "value": doc.roc_auc},
        ],
    }


@router.post("/retrain", status_code=status.HTTP_202_ACCEPTED)
async def retrain(
    background_tasks: BackgroundTasks,
    user: User = Depends(require_role(UserRole.ADMIN)),
) -> dict:
    """Trigger a full ML pipeline retrain in the background.

    Admin only.  Returns 202 immediately; check GET /api/v1/ml/latest for results.
    """

    async def _run_pipeline() -> None:
        try:
            await MLService.run_full_pipeline()
            logger.info("retrain_completed", triggered_by=str(user.id))
        except Exception as exc:
            logger.error("retrain_failed", error=str(exc), triggered_by=str(user.id))

    background_tasks.add_task(_run_pipeline)
    return {
        "status": "started",
        "message": (
            "Retrain pipeline started in background. "
            "Check GET /api/v1/ml/latest for updated results."
        ),
        "triggered_by": str(user.id),
    }
