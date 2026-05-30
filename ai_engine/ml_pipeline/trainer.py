"""Model Training stage.

train_model() implements:
    1. Stratified 80/20 train/test split
    2. 3-fold StratifiedKFold cross-validation (skipped if data is too small)
    3. Model selection: XGBoost → RandomForest → LogisticRegression
    4. Save model bundle to models/good_fit_classifier.pkl
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

from .model_manager import MODEL_PATH, ensure_model_dir
from .schemas import TrainingResult

logger = logging.getLogger(__name__)

_MIN_SAMPLES = 5
_TEST_SIZE = 0.2
_CV_FOLDS = 3
_RANDOM_STATE = 42


def _get_classifier() -> tuple[Any, str]:
    """Return the best available classifier (XGBoost → RF → LR)."""
    # 1. XGBoost
    try:
        from xgboost import XGBClassifier
        logger.info("training_using_xgboost")
        return (
            XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=_RANDOM_STATE,
                verbosity=0,
            ),
            "XGBoostClassifier",
        )
    except ImportError:
        logger.warning("xgboost_not_available_fallback_rf")

    # 2. RandomForest
    return (
        RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=_RANDOM_STATE,
            class_weight="balanced",
        ),
        "RandomForestClassifier",
    )


def train_model(
    X: Any,
    y: list[int],
    transformers: dict[str, Any],
    feature_info_dict: dict[str, Any],
) -> tuple[TrainingResult, Any, Any, Any]:
    """Model Training stage.

    Args:
        X:                 Sparse feature matrix (n_samples, n_features).
        y:                 Binary integer labels [0, 1].
        transformers:      Fitted sklearn transformers to persist in bundle.
        feature_info_dict: Serialisable FeatureInfo dict to persist in bundle.

    Returns:
        (TrainingResult, fitted_model, X_test, y_test)
    """
    y_arr = np.array(y)

    if len(y_arr) < _MIN_SAMPLES:
        raise ValueError(
            f"Too few training records ({len(y_arr)}). "
            f"Need at least {_MIN_SAMPLES}."
        )

    unique_classes = np.unique(y_arr)

    # ── Train / test split ──────────────────────────────────────────────────
    stratify = y_arr if len(unique_classes) > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_arr,
        test_size=_TEST_SIZE,
        random_state=_RANDOM_STATE,
        stratify=stratify,
    )
    logger.info(
        "training_split",
        train=len(y_train),
        test=len(y_test),
        positive_train=int(y_train.sum()),
        positive_test=int(y_test.sum()),
    )

    # ── Model selection ─────────────────────────────────────────────────────
    clf, algo_name = _get_classifier()
    logger.info("training_algorithm", algorithm=algo_name)

    # ── Cross-validation ────────────────────────────────────────────────────
    cv_scores: list[float] = []
    cv_mean = cv_std = 0.0
    if len(y_train) >= _CV_FOLDS * 2 and len(unique_classes) > 1:
        cv = StratifiedKFold(
            n_splits=_CV_FOLDS, shuffle=True, random_state=_RANDOM_STATE
        )
        try:
            scores = cross_val_score(clf, X_train, y_train, cv=cv, scoring="f1")
            cv_scores = [round(float(s), 4) for s in scores]
            cv_mean = round(float(np.mean(scores)), 4)
            cv_std = round(float(np.std(scores)), 4)
            logger.info("training_cv", folds=_CV_FOLDS, mean=cv_mean, std=cv_std)
        except Exception as exc:
            logger.warning("training_cv_skipped", reason=str(exc))

    # ── Final fit on full training set ──────────────────────────────────────
    clf.fit(X_train, y_train)

    # ── Save model bundle to disk ────────────────────────────────────────────
    ensure_model_dir()
    bundle: dict[str, Any] = {
        "model": clf,
        "transformers": transformers,
        "algorithm": algo_name,
        "classes_": unique_classes.tolist(),
        "label_map": {0: "Bad Fit", 1: "Good Fit"},
        "feature_info": feature_info_dict,
        "trained_at": datetime.utcnow().isoformat(),
        "train_size": int(len(y_train)),
        "test_size": int(len(y_test)),
    }
    joblib.dump(bundle, MODEL_PATH)
    logger.info("training_saved", path=str(MODEL_PATH), algorithm=algo_name)

    result = TrainingResult(
        model_name="good_fit_classifier",
        algorithm=algo_name,
        train_size=int(len(y_train)),
        test_size=int(len(y_test)),
        cv_scores=cv_scores,
        cv_mean=cv_mean,
        cv_std=cv_std,
        model_path=str(MODEL_PATH),
    )
    return result, clf, X_test, y_test
