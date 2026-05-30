"""Feature Engineering stage.

extract_features() builds a combined sparse feature matrix from three
feature groups:

    Text (TF-IDF):
        - Resume text     — unigrams + bigrams, max 300 features
        - Job description — unigrams,           max 150 features

    Numerical (MinMaxScaler):
        - experience_years
        - resume_length_norm  (char_count / 5000, clipped at 1.0)

    Categorical (OneHotEncoder):
        - education level (associate / bachelors / diploma / doctorate /
                           masters / unknown)

All sub-matrices are stacked horizontally via scipy.sparse.hstack to
produce a single sparse matrix suitable for any sklearn-compatible model.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

from .schemas import FeatureInfo, RawCandidateRecord

logger = logging.getLogger(__name__)

_TFIDF_RESUME_MAX = 300
_TFIDF_JD_MAX = 150
_EDUCATION_CATS: list[list[str]] = [
    ["associate", "bachelors", "diploma", "doctorate", "masters", "unknown"]
]


def extract_features(
    records: list[RawCandidateRecord],
) -> tuple[Any, dict[str, Any], FeatureInfo]:
    """Feature Engineering stage — fit transformers and build feature matrix.

    Returns:
        X            : scipy CSR sparse matrix of shape (n_samples, n_features)
        transformers : dict of fitted sklearn transformers (saved with model)
        info         : FeatureInfo with dimension breakdown
    """
    logger.info("feature_engineering_start", n_records=len(records))

    resume_texts = [r.resume_text for r in records]
    jd_texts = [r.job_description for r in records]

    numeric = np.array(
        [
            [r.experience_years, min(len(r.resume_text) / 5000.0, 1.0)]
            for r in records
        ],
        dtype=float,
    )
    categorical = np.array([[r.education] for r in records])

    # ── TF-IDF: resume text ─────────────────────────────────────────────────
    tfidf_resume = TfidfVectorizer(
        max_features=_TFIDF_RESUME_MAX,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=1,
    )
    X_resume = tfidf_resume.fit_transform(resume_texts)

    # ── TF-IDF: job description ─────────────────────────────────────────────
    tfidf_jd = TfidfVectorizer(
        max_features=_TFIDF_JD_MAX,
        ngram_range=(1, 1),
        sublinear_tf=True,
        min_df=1,
    )
    X_jd = tfidf_jd.fit_transform(jd_texts)

    # ── MinMaxScaler: numerical ─────────────────────────────────────────────
    scaler = MinMaxScaler()
    X_num_dense = scaler.fit_transform(numeric)
    X_num = csr_matrix(X_num_dense)

    # ── OneHotEncoder: categorical ──────────────────────────────────────────
    ohe = OneHotEncoder(
        categories=_EDUCATION_CATS,
        handle_unknown="ignore",
        sparse_output=True,
    )
    X_cat = ohe.fit_transform(categorical)

    # ── Stack all feature groups ────────────────────────────────────────────
    X = hstack([X_resume, X_jd, X_num, X_cat], format="csr")

    transformers: dict[str, Any] = {
        "tfidf_resume": tfidf_resume,
        "tfidf_jd": tfidf_jd,
        "scaler": scaler,
        "ohe": ohe,
    }

    info = FeatureInfo(
        total_features=int(X.shape[1]),
        tfidf_resume_features=int(X_resume.shape[1]),
        tfidf_jd_features=int(X_jd.shape[1]),
        numeric_features=int(X_num.shape[1]),
        categorical_features=int(X_cat.shape[1]),
        positive_class_ratio=float(np.mean([r.target_label for r in records])),
    )

    logger.info(
        "feature_engineering_done",
        shape=f"{X.shape[0]}x{X.shape[1]}",
        resume_feats=info.tfidf_resume_features,
        jd_feats=info.tfidf_jd_features,
        num_feats=info.numeric_features,
        cat_feats=info.categorical_features,
        positive_ratio=round(info.positive_class_ratio, 3),
    )
    return X, transformers, info
