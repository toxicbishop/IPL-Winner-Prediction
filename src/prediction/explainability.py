"""
SHAP Explainability Module: generates local and global explanations for base models.
Identifies which team characteristics (features) drive the winner prediction.
"""

import json
import logging
import os

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import get_tournament_paths
from src.models.base_model import FEATURE_COLS

logger = logging.getLogger(__name__)

try:
    import shap

    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
    logger.warning("SHAP not installed. Explainability will be skipped.")


def run_explainability(model_name: str = "xgboost", tournament: str = "ipl"):
    """Generate SHAP summary plots for the given model."""
    if not HAS_SHAP:
        return

    paths = get_tournament_paths(tournament)
    model_path = os.path.join(paths["models"], f"{model_name}.pkl")
    if not os.path.exists(model_path):
        logger.error(f"Model file not found for explainability: {model_path}")
        return

    # Load model and data
    import joblib

    model = joblib.load(model_path)
    df = pd.read_csv(paths["features"])
    X = df[FEATURE_COLS]

    # Sample a manageable subset if X is large
    if len(X) > 1000:
        X_sample = X.sample(1000, random_state=42)
    else:
        X_sample = X

    logger.info(f"Generating SHAP values for model: {model_name}...")

    # Check model type for appropriate explainer
    # XGBoost and LightGBM use TreeExplainer; Neural Network might need KernelExplainer or DeepExplainer
    try:
        # For XGBoost, it's often better to pass the booster
        if hasattr(model, "get_booster"):
            explainer = shap.TreeExplainer(model.get_booster())
        else:
            explainer = shap.TreeExplainer(model)

        shap_values = explainer.shap_values(X_sample)
        X_explain = X_sample
    except Exception as e:
        logger.warning(f"TreeExplainer failed ({e}). Falling back to KernelExplainer...")

        # Wrap predict_proba to ensure it gets numpy array or consistent dataframe
        def predict_wrapper(data):
            # If data is numpy, convert to DF with correct columns to satisfy XGBoost feature check
            if isinstance(data, np.ndarray):
                data_df = pd.DataFrame(data, columns=FEATURE_COLS)
                return model.predict_proba(data_df)
            return model.predict_proba(data)

        explainer = shap.KernelExplainer(predict_wrapper, shap.sample(X, 50))
        X_explain = X_sample.iloc[:50]
        shap_values = explainer.shap_values(X_explain)  # Use smaller subset for Kernel

    # Ensure shap_values is a 2D array for the positive class (class 1)
    if isinstance(shap_values, list):
        shap_values_class1 = shap_values[1] if len(shap_values) > 1 else shap_values[0]
    elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
        shap_values_class1 = shap_values[:, :, 1]
    else:
        shap_values_class1 = shap_values

    # Global Summary Plot
    results_dir = paths["results"]
    os.makedirs(results_dir, exist_ok=True)
    summary_plot_path = os.path.join(results_dir, f"shap_summary_{model_name}.png")

    plt.figure(figsize=(12, 8))
    shap.summary_plot(
        shap_values_class1,
        X_explain,
        show=False,
        plot_size=None,
        color_bar_label="Win Probability Driver",
    )

    plt.title(f"SHAP Feature Importance: {model_name}", fontsize=15, fontweight="bold", pad=20)
    plt.savefig(summary_plot_path, dpi=180, bbox_inches="tight")
    if model_name == "xgboost":
        # Save duplicate for backward compatibility with frontend
        plt.savefig(os.path.join(results_dir, "shap_summary_lightgbm.png"), dpi=180, bbox_inches="tight")
    plt.close()

    logger.info(f"SHAP summary plot saved to {summary_plot_path}")

    # Output top 10 impactful features to JSON for frontend
    # For global importance, compute mean absolute SHAP value
    global_importance = np.abs(shap_values_class1).mean(axis=0)

    importance_dict = dict(zip(FEATURE_COLS, global_importance, strict=False))
    sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:10]

    with open(os.path.join(results_dir, f"shap_importance_{model_name}.json"), "w") as f:
        json.dump(sorted_importance, f, indent=2)
    if model_name == "xgboost":
        # Save duplicate for backward compatibility with frontend
        with open(os.path.join(results_dir, "shap_importance_lightgbm.json"), "w") as f:
            json.dump(sorted_importance, f, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tournament", default="ipl")
    parser.add_argument("--model", default="lightgbm")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    run_explainability(args.model, args.tournament)
