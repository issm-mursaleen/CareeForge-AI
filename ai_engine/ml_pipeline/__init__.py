"""ML Pipeline module — formal ML lifecycle for the Good Fit binary classifier.

Stages:
    Data Gathering     → data_loader.load_training_dataset()
    Data Cleaning      → preprocessing.clean_dataset()
    Feature Engineering → feature_engineering.extract_features()
    Model Training     → trainer.train_model()
    Model Evaluation   → evaluator.evaluate()
    Model Management   → model_manager (save / load / cache)
"""
from .data_loader import load_training_dataset
from .preprocessing import clean_dataset
from .feature_engineering import extract_features
from .trainer import train_model
from .evaluator import evaluate
from .model_manager import load_for_startup, get_loaded_model, predict_fit

__all__ = [
    "load_training_dataset",
    "clean_dataset",
    "extract_features",
    "train_model",
    "evaluate",
    "load_for_startup",
    "get_loaded_model",
    "predict_fit",
]
