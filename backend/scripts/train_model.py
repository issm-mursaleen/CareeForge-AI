"""Train a TF-IDF + LogisticRegression job-role classifier.

End-to-end pipeline:
  1. Loads job-description CSV(s) with pandas
  2. Validates every raw row through a Pydantic schema (RawDatasetRow)
  3. Cleans / normalizes (drop NaN, drop duplicates, lowercase, whitespace)
  4. TfidfVectorizer for text features + LabelEncoder for the target
  5. Trains a LogisticRegression classifier inside an sklearn Pipeline
  6. Computes Accuracy / Precision / Recall / F1 on a held-out test split
  7. Persists metrics into MongoDB (Beanie -> MLMetricsDoc)
  8. Dumps the fitted Pipeline + LabelEncoder to backend/model.pkl with joblib

Usage (from project root, with backend venv active):
    python backend/scripts/train_model.py
    python backend/scripts/train_model.py --no-mongo        # skip db write
    python backend/scripts/train_model.py --dataset jobs    # only the small CSV
"""
from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path
from typing import Iterable

import joblib
import pandas as pd
from pydantic import BaseModel, Field, ValidationError, field_validator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

# Allow `from app...` imports when the script is run directly.
BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

DATASETS_DIR = PROJECT_ROOT / "Datsets"
MODEL_PATH = BACKEND_DIR / "model.pkl"

# Keep the classifier from over-fitting to single-sample classes that
# would also break stratified train/test splits.
MIN_SAMPLES_PER_CLASS = 10


# ---------------------------------------------------------------------------
# Pydantic validation
# ---------------------------------------------------------------------------
class RawDatasetRow(BaseModel):
    """Schema each CSV row must satisfy before it enters training."""

    job_title: str = Field(min_length=2, max_length=200)
    job_description: str = Field(min_length=20, max_length=20_000)

    @field_validator("job_title", "job_description")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()


def _validate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Run every row through RawDatasetRow; drop the failures."""
    kept: list[dict] = []
    rejected = 0
    for record in df.to_dict(orient="records"):
        try:
            row = RawDatasetRow(**record)
        except ValidationError:
            rejected += 1
            continue
        kept.append(row.model_dump())
    print(f"[validate] kept={len(kept)} rejected={rejected}")
    return pd.DataFrame(kept)


# ---------------------------------------------------------------------------
# Loading + cleaning
# ---------------------------------------------------------------------------
_WS = re.compile(r"\s+")


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = _WS.sub(" ", text)
    return text.strip()


def _safe_col(df: pd.DataFrame, col: str) -> pd.Series:
    if col in df.columns:
        return df[col].fillna("").astype(str)
    return pd.Series([""] * len(df), index=df.index)


def _load_jobs_description(path: Path) -> pd.DataFrame:
    """Combine Description + skills + Responsibilities + Qualifications + Experience
    into the feature text. The base Description is templated per Role, but the
    other columns vary across rows — concatenating preserves real signal that
    would otherwise be lost to deduplication."""
    df = pd.read_csv(path, on_bad_lines="skip", encoding_errors="ignore")
    text = (
        _safe_col(df, "Job Description") + " . "
        + _safe_col(df, "skills") + " . "
        + _safe_col(df, "Responsibilities") + " . "
        + _safe_col(df, "Qualifications") + " . "
        + _safe_col(df, "Experience")
    )
    return pd.DataFrame(
        {
            "job_title": _safe_col(df, "Job Title"),
            "job_description": text,
        }
    )


def _load_data_scientist(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, on_bad_lines="skip", encoding_errors="ignore")
    return pd.DataFrame(
        {
            "job_title": _safe_col(df, "Job Title"),
            "job_description": _safe_col(df, "Job Description"),
        }
    )


def load_datasets(which: str) -> pd.DataFrame:
    """`which` is one of: 'all', 'jobs', 'datascientist'."""
    frames: list[pd.DataFrame] = []
    if which in ("all", "jobs"):
        path = DATASETS_DIR / "jobs_description.csv"
        if path.exists():
            frames.append(_load_jobs_description(path))
            print(f"[load] {path.name}: {len(frames[-1])} rows")
    if which in ("all", "datascientist"):
        path = DATASETS_DIR / "DataScientist.csv"
        if path.exists():
            frames.append(_load_data_scientist(path))
            print(f"[load] {path.name}: {len(frames[-1])} rows")
    if not frames:
        raise FileNotFoundError(f"No datasets found under {DATASETS_DIR}")
    return pd.concat(frames, ignore_index=True)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.dropna(subset=["job_title", "job_description"])
    df = df[df["job_title"].astype(str).str.strip().ne("")]
    df = df[df["job_description"].astype(str).str.strip().ne("")]
    df["job_title"] = df["job_title"].astype(str).str.strip()
    df["job_description"] = df["job_description"].astype(str).map(_normalize_text)
    df = df.drop_duplicates(subset=["job_title", "job_description"])
    print(f"[clean] {before} -> {len(df)} rows after NaN/dup removal")
    return df.reset_index(drop=True)


def _prune_rare_classes(df: pd.DataFrame, min_count: int) -> pd.DataFrame:
    counts = df["job_title"].value_counts()
    keep = counts[counts >= min_count].index
    pruned = df[df["job_title"].isin(keep)].reset_index(drop=True)
    print(
        f"[prune] kept {pruned['job_title'].nunique()} classes "
        f"with >= {min_count} samples ({len(pruned)} rows)"
    )
    return pruned


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def _build_pipeline() -> Pipeline:
    """Word + character n-gram TF-IDF feeding a LinearSVC.

    - Word (1, 2) catches phrases like "data analyst", "react developer".
    - Character (3, 5) on `char_wb` catches sub-words inside skill names
      ("python", "kubernetes", camelCase fragments) that the word tokenizer
      misses, and is robust to typos / variant spellings.
    - sublinear_tf dampens dominant terms; LinearSVC is the standard
      strong baseline for short-text multi-class problems.
    """
    features = FeatureUnion(
        transformer_list=[
            (
                "word",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    sublinear_tf=True,
                    max_features=50_000,
                    stop_words="english",
                ),
            ),
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    max_df=0.95,
                    sublinear_tf=True,
                    max_features=50_000,
                ),
            ),
        ]
    )
    return Pipeline(
        steps=[
            ("features", features),
            (
                "clf",
                LinearSVC(
                    C=1.0,
                    class_weight="balanced",
                    max_iter=2000,
                ),
            ),
        ]
    )


def train_and_evaluate(df: pd.DataFrame) -> tuple[Pipeline, LabelEncoder, dict]:
    encoder = LabelEncoder()
    y = encoder.fit_transform(df["job_title"].tolist())
    X = df["job_description"].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = _build_pipeline()
    print(f"[train] fitting on {len(X_train)} rows, {len(set(y_train))} classes")
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision": float(precision_score(y_test, preds, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_test, preds, average="weighted", zero_division=0)),
        "f1_score": float(f1_score(y_test, preds, average="weighted", zero_division=0)),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "num_classes": int(len(encoder.classes_)),
    }
    print(
        "[eval] "
        + " | ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}"
                     for k, v in metrics.items())
    )
    return pipeline, encoder, metrics


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
def save_pipeline(pipeline: Pipeline, encoder: LabelEncoder, metrics: dict) -> Path:
    bundle = {
        "pipeline": pipeline,
        "label_encoder": encoder,
        "metrics": metrics,
        "classes_": list(encoder.classes_),
    }
    joblib.dump(bundle, MODEL_PATH)
    print(f"[save] wrote {MODEL_PATH} ({MODEL_PATH.stat().st_size / 1024:.1f} KB)")
    return MODEL_PATH


async def save_metrics_to_mongo(metrics: dict) -> None:
    from beanie import init_beanie
    from motor.motor_asyncio import AsyncIOMotorClient

    from app.core.config import get_settings
    from app.models import ALL_DOCUMENTS
    from app.models.ml_metrics import MLMetricsDoc

    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]
    await init_beanie(database=db, document_models=list(ALL_DOCUMENTS))

    doc = MLMetricsDoc(
        model_name="job_role_classifier",
        algorithm="LinearSVC",
        vectorizer="TfidfVectorizer(word 1-2) + TfidfVectorizer(char_wb 3-5)",
        accuracy=metrics["accuracy"],
        precision=metrics["precision"],
        recall=metrics["recall"],
        f1_score=metrics["f1_score"],
        train_size=metrics["train_size"],
        test_size=metrics["test_size"],
        num_classes=metrics["num_classes"],
        notes="Trained via backend/scripts/train_model.py",
    )
    await doc.insert()
    print(f"[mongo] inserted MLMetricsDoc id={doc.id}")
    client.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train job-role classifier")
    parser.add_argument(
        "--dataset",
        choices=["all", "jobs", "datascientist"],
        default="all",
        help="Which CSV(s) to load.",
    )
    parser.add_argument(
        "--no-mongo",
        action="store_true",
        help="Skip writing metrics to MongoDB (still saves model.pkl).",
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=MIN_SAMPLES_PER_CLASS,
        help="Drop classes with fewer than this many samples (default: 5).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    raw = load_datasets(args.dataset)
    validated = _validate_rows(raw)
    cleaned = clean_dataset(validated)
    final_df = _prune_rare_classes(cleaned, args.min_samples)

    if final_df["job_title"].nunique() < 2:
        print("[error] fewer than 2 classes survived cleaning — aborting", file=sys.stderr)
        return 1

    pipeline, encoder, metrics = train_and_evaluate(final_df)
    save_pipeline(pipeline, encoder, metrics)

    if not args.no_mongo:
        try:
            asyncio.run(save_metrics_to_mongo(metrics))
        except Exception as exc:  # noqa: BLE001
            print(f"[mongo] skipped — {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
