from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..models.ml_metrics import MLMetricsDoc
from ..models.resume import Resume
from ..models.user import User
from .dependencies import get_current_user

router = APIRouter()


@router.get("/summary")
async def summary(user: User = Depends(get_current_user)) -> dict:
    resumes = await Resume.find(Resume.user_id == user.id).to_list()
    if not resumes:
        return {
            "total_resumes": 0,
            "average_ats": 0,
            "top_skills": [],
            "ats_trend": [],
        }
    ats_scores = [r.ats.score for r in resumes if r.ats]
    skill_freq: dict[str, int] = {}
    for r in resumes:
        for s in r.skills:
            skill_freq[s] = skill_freq.get(s, 0) + 1
    top_skills = sorted(skill_freq.items(), key=lambda kv: kv[1], reverse=True)[:10]
    trend = [
        {"date": r.created_at.date().isoformat(), "score": r.ats.score if r.ats else 0}
        for r in sorted(resumes, key=lambda r: r.created_at)
    ]
    return {
        "total_resumes": len(resumes),
        "average_ats": round(sum(ats_scores) / len(ats_scores), 2) if ats_scores else 0,
        "top_skills": [{"skill": k, "count": v} for k, v in top_skills],
        "ats_trend": trend,
    }


@router.get("/ml-performance")
async def ml_performance(_: User = Depends(get_current_user)) -> dict:
    """Return the most recent trained-model metrics for the dashboard."""
    doc = await MLMetricsDoc.find_all().sort(-MLMetricsDoc.created_at).first_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No ML metrics found — run backend/scripts/train_model.py first.",
        )
    return {
        "model_name": doc.model_name,
        "algorithm": doc.algorithm,
        "vectorizer": doc.vectorizer,
        "accuracy": round(doc.accuracy, 4),
        "precision": round(doc.precision, 4),
        "recall": round(doc.recall, 4),
        "f1_score": round(doc.f1_score, 4),
        "train_size": doc.train_size,
        "test_size": doc.test_size,
        "num_classes": doc.num_classes,
        "created_at": doc.created_at.isoformat(),
        "metrics": [
            {"metric": "Accuracy", "value": round(doc.accuracy, 4)},
            {"metric": "Precision", "value": round(doc.precision, 4)},
            {"metric": "Recall", "value": round(doc.recall, 4)},
            {"metric": "F1-Score", "value": round(doc.f1_score, 4)},
        ],
    }
