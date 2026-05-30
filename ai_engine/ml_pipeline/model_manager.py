"""Model Manager — persist, load, and cache the Good Fit classifier.

Model path:  <repo_root>/models/good_fit_classifier.pkl

At FastAPI startup load_for_startup() is called to pre-warm the in-process
cache so every subsequent inference call is instant (no disk I/O).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib

logger = logging.getLogger(__name__)

# ── Path setup ──────────────────────────────────────────────────────────────
# ai_engine/ml_pipeline/model_manager.py
#   parents[0] = ai_engine/ml_pipeline/
#   parents[1] = ai_engine/
#   parents[2] = repo root
MODEL_DIR = Path(__file__).resolve().parents[2] / "models"
MODEL_PATH = MODEL_DIR / "good_fit_classifier.pkl"

# In-process model cache (populated by load_for_startup)
_fit_bundle: dict[str, Any] | None = None


def ensure_model_dir() -> None:
    """Create the models/ directory if it does not exist."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


def save_model(bundle: dict[str, Any], path: Path | None = None) -> Path:
    """Persist a model bundle to disk via joblib."""
    target = path or MODEL_PATH
    ensure_model_dir()
    joblib.dump(bundle, target)
    logger.info("good_fit_model_saved: %s", str(target))
    return target


def load_model(path: Path | None = None) -> dict[str, Any] | None:
    """Load a model bundle from disk. Returns None when the file is absent."""
    target = path or MODEL_PATH
    if not target.exists():
        logger.warning("good_fit_model_not_found: %s", str(target))
        return None
    try:
        bundle = joblib.load(target)
        logger.info("good_fit_model_loaded: %s", str(target))
        return bundle
    except Exception as exc:
        logger.warning("good_fit_model_load_failed: %s", str(exc))
        return None


def load_for_startup() -> None:
    """Load the model into the process-wide cache (called at FastAPI startup)."""
    global _fit_bundle
    _fit_bundle = load_model()
    if _fit_bundle:
        algo = _fit_bundle.get("algorithm", "unknown")
        logger.info("good_fit_model_cached: algorithm=%s", algo)


def get_loaded_model() -> dict[str, Any] | None:
    """Return the cached model bundle, or None when not yet loaded."""
    return _fit_bundle


def predict_fit(
    resume_text: str,
    job_description: str,
    experience_years: float = 0.0,
    education: str = "unknown",
) -> dict[str, Any] | None:
    """Run Good Fit inference for a single candidate using the cached model.

    Returns:
        dict with keys: label (int), label_name (str), probability (float)
        None if the model has not been loaded yet.
    """
    bundle = _fit_bundle
    if not bundle:
        return None

    try:
        import numpy as np
        from scipy.sparse import csr_matrix, hstack

        t = bundle["transformers"]
        X_resume = t["tfidf_resume"].transform([resume_text])
        X_jd = t["tfidf_jd"].transform([job_description])
        numeric = np.array([[experience_years, min(len(resume_text) / 5000.0, 1.0)]])
        X_num = csr_matrix(t["scaler"].transform(numeric))
        X_cat = t["ohe"].transform(np.array([[education]]))
        X = hstack([X_resume, X_jd, X_num, X_cat], format="csr")

        model = bundle["model"]
        label = int(model.predict(X)[0])
        probability = 0.5
        if hasattr(model, "predict_proba"):
            probability = float(model.predict_proba(X)[0][1])
        label_name = bundle.get("label_map", {}).get(label, str(label))
        return {"label": label, "label_name": label_name, "probability": probability}
    except Exception as exc:
        logger.warning("good_fit_predict_failed: %s", str(exc))
        return None
