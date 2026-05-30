"""Seed ml_training_data collection from CSV datasets.

Run once from repo root:
    python database/seeds/seed_ml_training.py

Uses plain pymongo (no Beanie) to avoid local version conflicts.
Reads Datsets/jobs_description.csv + Datsets/DataScientist.csv,
samples 500 records, and inserts into MongoDB Atlas.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

MONGO_URI = "mongodb+srv://dbadmin:%28Password2023%29@cluster0.1c70r.mongodb.net/careerforge?appName=Cluster0"
DB_NAME = "careerforge"
COLLECTION = "ml_training_data"


def main() -> None:
    from pymongo import MongoClient
    from ai_engine.ml_pipeline.csv_data_loader import load_csv_training_dataset

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    col = db[COLLECTION]

    existing = col.count_documents({})
    if existing > 0:
        print(f"[skip] {existing} records already in {COLLECTION}. Drop collection first to re-seed.")
        return

    print("Loading CSV datasets (500 samples)...")
    records = load_csv_training_dataset(sample_size=500)
    print(f"Loaded {len(records)} records. Inserting into MongoDB Atlas...")

    col.insert_many(records)

    good = sum(1 for r in records if r["is_good_fit"] == 1)
    print(f"Done. Inserted {len(records)} records — Good Fit: {good}, Bad Fit: {len(records)-good}")
    client.close()


if __name__ == "__main__":
    main()
