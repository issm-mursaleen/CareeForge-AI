"""Model Evaluation stage.

evaluate() computes a full suite of test-set metrics:
    Accuracy          — fraction of correct predictions
    Precision         — TP / (TP + FP)
    Recall            — TP / (TP + FN)
    F1 Score          — harmonic mean of precision and recall
    Confusion Matrix  — [[TN, FP], [FN, TP]]
    ROC AUC           — area under the receiver-operating-characteristic curve
    ROC Curve         — (fpr[], tpr[]) sampled at ≤ 50 points
    Classification Report — per-class breakdown string
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from .schemas import EvaluationResult

logger = logging.getLogger(__name__)


def evaluate(model: Any, X_test: Any, y_test: Any) -> EvaluationResult:
    """Model Evaluation stage — compute comprehensive test-set metrics.

    Args:
        model:  Fitted sklearn-compatible classifier.
        X_test: Sparse feature matrix for the test split.
        y_test: Ground-truth labels for the test split.

    Returns:
        EvaluationResult with all metrics.
    """
    y_arr = np.asarray(y_test)
    y_pred = model.predict(X_test)
    unique_classes = np.unique(y_arr)
    avg = "binary" if len(unique_classes) <= 2 else "weighted"

    acc = float(accuracy_score(y_arr, y_pred))
    prec = float(precision_score(y_arr, y_pred, average=avg, zero_division=0))
    rec = float(recall_score(y_arr, y_pred, average=avg, zero_division=0))
    f1 = float(f1_score(y_arr, y_pred, average=avg, zero_division=0))

    # Confusion matrix
    cm = confusion_matrix(y_arr, y_pred).tolist()

    # ROC curve + AUC
    fpr_list: list[float] = []
    tpr_list: list[float] = []
    roc_auc_val = 0.5

    try:
        if len(unique_classes) > 1:
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)[:, 1]
            elif hasattr(model, "decision_function"):
                y_prob = model.decision_function(X_test)
            else:
                y_prob = y_pred.astype(float)

            roc_auc_val = float(roc_auc_score(y_arr, y_prob))
            fpr_arr, tpr_arr, _ = roc_curve(y_arr, y_prob)

            # Downsample to at most 50 points to keep stored JSON compact
            n = min(50, len(fpr_arr))
            idx = np.linspace(0, len(fpr_arr) - 1, n, dtype=int)
            fpr_list = [round(float(fpr_arr[i]), 4) for i in idx]
            tpr_list = [round(float(tpr_arr[i]), 4) for i in idx]
    except Exception as exc:
        logger.warning("evaluation_roc_failed: %s", str(exc))

    report = classification_report(
        y_arr,
        y_pred,
        target_names=["Bad Fit", "Good Fit"],
        zero_division=0,
    )

    result = EvaluationResult(
        accuracy=round(acc, 4),
        precision=round(prec, 4),
        recall=round(rec, 4),
        f1_score=round(f1, 4),
        roc_auc=round(roc_auc_val, 4),
        confusion_matrix=cm,
        roc_curve_fpr=fpr_list,
        roc_curve_tpr=tpr_list,
        classification_report=report,
    )
    logger.info(
        "evaluation_done: accuracy=%.4f precision=%.4f recall=%.4f f1=%.4f roc_auc=%.4f",
        result.accuracy, result.precision, result.recall, result.f1_score, result.roc_auc,
    )
    return result
