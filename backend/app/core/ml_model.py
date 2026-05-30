"""Global access to the trained job-role classifier.

The pipeline is loaded once on FastAPI startup (see app.main.lifespan)
and held in this module's state so request handlers can predict
synchronously without re-reading model.pkl.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from .logging import get_logger

logger = get_logger(__name__)

# backend/model.pkl  (this file is backend/app/core/ml_model.py)
MODEL_PATH = Path(__file__).resolve().parents[2] / "model.pkl"

_bundle: dict[str, Any] | None = None


def load_model(path: Path | None = None) -> dict[str, Any] | None:
    """Read model.pkl from disk into the process-wide cache. Idempotent."""
    global _bundle
    target = path or MODEL_PATH
    if not target.exists():
        logger.warning("ml_model_missing", path=str(target))
        return None
    try:
        _bundle = joblib.load(target)
        logger.info(
            "ml_model_loaded",
            path=str(target),
            classes=len(_bundle.get("classes_", [])),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("ml_model_load_failed", error=str(exc))
        _bundle = None
    return _bundle


def get_bundle() -> dict[str, Any] | None:
    return _bundle


def predict_role(text: str) -> str | None:
    """Return the model's top predicted Job Title for `text`, or None."""
    bundle = _bundle
    if not bundle or not text or not text.strip():
        return None
    pipeline = bundle.get("pipeline")
    encoder = bundle.get("label_encoder")
    if pipeline is None or encoder is None:
        return None
    try:
        idx = pipeline.predict([text])[0]
        return str(encoder.inverse_transform([idx])[0])
    except Exception as exc:  # noqa: BLE001
        logger.warning("ml_predict_failed", error=str(exc))
        return None


def load_good_fit_model() -> None:
    """Load the Good Fit binary classifier into the ai_engine's in-process cache."""
    try:
        from ai_engine.ml_pipeline.model_manager import load_for_startup
        load_for_startup()
    except Exception as exc:  # noqa: BLE001
        logger.warning("good_fit_model_load_skipped", error=str(exc))
