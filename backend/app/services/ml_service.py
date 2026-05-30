"""ML Pipeline service — orchestrates data fetching, training, and metric storage.

This module bridges the FastAPI backend (MongoDB via Beanie) and the
pure-ML ai_engine/ml_pipeline library.

Pipeline stages executed by run_full_pipeline():
    1. Data Gathering     — fetch raw records from MongoDB
    2. Data Cleaning      — remove noise, duplicates, outliers
    3. Feature Engineering — TF-IDF + scaling + encoding
    4. Model Training     — XGBoost / RF / LR + cross-validation
    5. Model Evaluation   — accuracy, precision, recall, F1, ROC, CM
    6. Metrics Storage    — persist to ml_model_metrics collection
"""
from __future__ import annotations

import logging
from datetime import datetime

from ..models.good_fit_metrics import GoodFitMetricsDoc
from ..models.job_match import JobMatch
from ..models.resume import Resume
from ai_engine.ml_pipeline.csv_data_loader import load_csv_training_dataset
from ai_engine.ml_pipeline.data_loader import load_training_dataset
from ai_engine.ml_pipeline.evaluator import evaluate
from ai_engine.ml_pipeline.feature_engineering import extract_features
from ai_engine.ml_pipeline.model_manager import load_for_startup
from ai_engine.ml_pipeline.preprocessing import clean_dataset
from ai_engine.ml_pipeline.trainer import train_model

logger = logging.getLogger(__name__)

_MIN_TRAINING_RECORDS = 5


async def _build_raw_records() -> list[dict]:
    """Fetch training data.

    Priority order:
      1. CSV datasets (jobs_description.csv + DataScientist.csv) — 8 000 labelled rows
      2. MongoDB job_matches — real platform data with is_good_fit labels
      3. MongoDB standalone resumes — cold-start fallback (ATS-derived labels)
    """
    records: list[dict] = []

    # ── Source 1: CSV datasets ───────────────────────────────────────────────
    csv_records = load_csv_training_dataset()
    records.extend(csv_records)
    logger.info("ml_csv_records_loaded: %d", len(csv_records))

    # ── Source 2: job_matches (real labelled platform data) ──────────────────
    job_matches = await JobMatch.find_all().to_list()
    for jm in job_matches:
        for candidate in jm.candidates:
            try:
                resume = await Resume.get(candidate.resume_id)
            except Exception:
                continue
            if not resume or not resume.raw_text:
                continue
            records.append(
                {
                    "candidate_id": f"{candidate.resume_id}_{jm.id}",
                    "resume_text": resume.raw_text,
                    "job_description": jm.job_description,
                    "skills": resume.skills,
                    "is_good_fit": candidate.is_good_fit,
                    "composite": candidate.composite or 0.0,
                }
            )

    # ── Source 3: standalone resumes (cold-start supplement) ─────────────────
    if len(records) < _MIN_TRAINING_RECORDS:
        logger.info("ml_cold_start: augmenting from standalone resumes")
        seen_ids = {r["candidate_id"].split("_")[0] for r in records}
        resumes = await Resume.find_all().to_list()
        for resume in resumes:
            if not resume.raw_text or str(resume.id) in seen_ids:
                continue
            ats = resume.ats.score if resume.ats else 50.0
            records.append(
                {
                    "candidate_id": str(resume.id),
                    "resume_text": resume.raw_text,
                    "job_description": resume.predicted_role or "software engineer",
                    "skills": resume.skills,
                    "is_good_fit": None,
                    "composite": ats / 100.0,
                }
            )

    logger.info("ml_raw_records_fetched: %d", len(records))
    return records


class MLService:
    """Orchestrates the full ML pipeline lifecycle."""

    @staticmethod
    async def run_full_pipeline() -> GoodFitMetricsDoc:
        """Execute all six pipeline stages and persist metrics to MongoDB.

        Returns:
            GoodFitMetricsDoc — the newly inserted metrics document.

        Raises:
            ValueError when there is insufficient training data.
        """
        logger.info("ml_pipeline_start: %s", datetime.utcnow().isoformat())

        # ── Stage 1: Data Gathering ──────────────────────────────────────
        raw_records = await _build_raw_records()
        validated = load_training_dataset(raw_records)

        if len(validated) < _MIN_TRAINING_RECORDS:
            raise ValueError(
                f"Insufficient training data: only {len(validated)} valid records "
                f"(need ≥ {_MIN_TRAINING_RECORDS}). "
                "Upload resumes or run the ranking pipeline to generate labelled data."
            )

        # ── Stage 2: Data Cleaning ───────────────────────────────────────
        cleaned, cleaning_stats = clean_dataset(validated)

        if len(cleaned) < _MIN_TRAINING_RECORDS:
            raise ValueError(
                f"After cleaning only {len(cleaned)} records remain "
                f"(need ≥ {_MIN_TRAINING_RECORDS})."
            )

        # ── Stage 3: Feature Engineering ────────────────────────────────
        X, transformers, feature_info = extract_features(cleaned)
        y = [r.target_label for r in cleaned]

        # ── Stage 4: Model Training ──────────────────────────────────────
        train_result, fitted_model, X_test, y_test = train_model(
            X, y, transformers, feature_info.model_dump()
        )

        # ── Stage 5: Model Evaluation ────────────────────────────────────
        eval_result = evaluate(fitted_model, X_test, y_test)

        # Refresh the in-process model cache with the newly trained model
        load_for_startup()

        # ── Stage 6: Metrics Storage ─────────────────────────────────────
        doc = GoodFitMetricsDoc(
            algorithm=train_result.algorithm,
            dataset_size=len(cleaned),
            train_size=train_result.train_size,
            test_size=train_result.test_size,
            feature_count=feature_info.total_features,
            accuracy=eval_result.accuracy,
            precision=eval_result.precision,
            recall=eval_result.recall,
            f1_score=eval_result.f1_score,
            roc_auc=eval_result.roc_auc,
            confusion_matrix=eval_result.confusion_matrix,
            roc_curve_fpr=eval_result.roc_curve_fpr,
            roc_curve_tpr=eval_result.roc_curve_tpr,
            cv_mean=train_result.cv_mean,
            cv_std=train_result.cv_std,
            cleaning_stats=cleaning_stats.model_dump(),
            feature_info=feature_info.model_dump(),
        )
        await doc.insert()

        logger.info(
            "ml_pipeline_done: algorithm=%s dataset=%d accuracy=%.3f f1=%.3f roc_auc=%.3f",
            doc.algorithm, doc.dataset_size, doc.accuracy, doc.f1_score, doc.roc_auc,
        )
        return doc

    @staticmethod
    async def get_latest_metrics() -> GoodFitMetricsDoc | None:
        """Return the most recent training run metrics."""
        return (
            await GoodFitMetricsDoc.find_all()
            .sort(-GoodFitMetricsDoc.created_at)
            .first_or_none()
        )

    @staticmethod
    async def get_metrics_history(limit: int = 20) -> list[GoodFitMetricsDoc]:
        """Return the N most recent training runs (full history)."""
        return (
            await GoodFitMetricsDoc.find_all()
            .sort(-GoodFitMetricsDoc.created_at)
            .limit(limit)
            .to_list()
        )
