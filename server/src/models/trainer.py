"""
Model training orchestrator with MLflow tracking.
Trains all individual models + ensemble, saves metrics to JSON and MLflow.
"""

import json
import logging
import os

import mlflow
import mlflow.sklearn as mlflow_sklearn
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from config import RANDOM_STATE, TEST_SIZE, get_tournament_paths
from src.models.base_model import TARGET_COL
from src.models.tune import load_best_params
from src.models.xgboost_model import XGBoostModel

logger = logging.getLogger(__name__)

# Set MLflow experiment
mlflow.set_tracking_uri(f"file:///{os.path.abspath(os.path.join('outputs', 'mlflow'))}")
mlflow.set_experiment("IPL_2026_Winner_Prediction")


def load_features(features_path: str) -> pd.DataFrame:
    if not os.path.exists(features_path):
        raise FileNotFoundError(
            f"Features file not found: {features_path}\nRun: python main.py --mode setup first."
        )
    return pd.read_csv(features_path)


def _apply_tuned_params(model, best_params: dict):
    name_map = {
        "random_forest": None,
        "xgboost": "xgboost",
        "lightgbm": "lightgbm",
        "neural_network": None,
        "extra_trees": None,
    }
    key = name_map.get(model.name)
    if key and key in best_params and best_params[key]:
        params = best_params[key]
        for attr, val in params.items():
            if hasattr(model.model, attr):
                setattr(model.model, attr, val)
        print(f"  Applied {len(params)} tuned params to {model.name}")


def train_all(df: pd.DataFrame, models_dir: str, tournament: str) -> dict:
    results = {}

    if tournament == "ipl" and "season" in df.columns:
        # Time-based split: Train on older seasons, Test on most recent completed seasons
        df_test = df[df["season"] >= 2024].copy()
        df_train = df[df["season"] < 2024].copy()
        print(f"  Time-based split: Train (<2024: {len(df_train)}), Test (>=2024: {len(df_test)})")
    else:
        df_train, df_test = train_test_split(
            df, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=df[TARGET_COL]
        )

    best_params = load_best_params()

    # Time Decay Weights
    sample_weights = None
    if "season" in df_train.columns:
        max_s = df_train["season"].max()
        # Newer matches get higher weight: exp(-0.03 * years_ago)
        # 10 years ago = exp(-0.3) = ~0.74 weight
        sample_weights = np.exp(-0.03 * (max_s - df_train["season"]))
        print("  Applying exponential time decay weights to training samples.")

    individual_models = [
        XGBoostModel(save_dir=models_dir),
    ]

    for model in individual_models:
        with mlflow.start_run(run_name=f"{tournament}_{model.name}"):
            print(f"\nTraining: {model.name.upper()}")

            if best_params:
                _apply_tuned_params(model, best_params)

            cv = model.cross_validate(df_train)
            model.train(df_train, sample_weight=sample_weights, calibrate=True)
            train_metrics = model.evaluate(df_train)
            test_metrics = model.evaluate(df_test)

            # Log metrics to MLflow
            mlflow.log_param("tournament", tournament)
            mlflow.log_param("model_type", model.name)
            mlflow.log_metric("cv_accuracy", cv["cv_mean"])
            mlflow.log_metric("train_accuracy", train_metrics["accuracy"])
            mlflow.log_metric("test_accuracy", test_metrics["accuracy"])
            mlflow.log_metric("test_precision", test_metrics["precision"])
            mlflow.log_metric("test_recall", test_metrics["recall"])
            mlflow.log_metric("test_f1", test_metrics["f1_score"])

            if "roc_auc" in test_metrics and test_metrics["roc_auc"] is not None:
                mlflow.log_metric("test_roc_auc", test_metrics["roc_auc"])

            # 2024-specific accuracy
            m_2024 = model.evaluate_2024(df_test)
            if m_2024:
                mlflow.log_metric("accuracy_2024", m_2024["accuracy"])

            # Log model
            # Use the sklearn-specific log_model to avoid attribute issues on the mlflow module
            try:
                mlflow_sklearn.log_model(model.model, f"model_{model.name}")
            except Exception:
                # Fallback: save the model artifact manually if logging fails
                tmp_dir = os.path.join(models_dir, f"model_artifact_{model.name}")
                os.makedirs(tmp_dir, exist_ok=True)
                try:
                    # Attempt sklearn joblib dump if available
                    from joblib import dump

                    dump(model.model, os.path.join(tmp_dir, "model.joblib"))
                    mlflow.log_artifacts(tmp_dir, artifact_path=f"model_{model.name}")
                except Exception:
                    # As a final fallback, skip model artifact logging
                    logger.warning(f"Could not log model artifact for {model.name}")

            model.save()

            # Save results
            results[model.name] = {
                "cv_accuracy": cv["cv_mean"],
                "cv_std": cv["cv_std"],
                "train_accuracy": train_metrics["accuracy"],
                "test_accuracy": test_metrics["accuracy"],
                "test_precision": test_metrics["precision"],
                "test_recall": test_metrics["recall"],
                "test_f1": test_metrics["f1_score"],
                "test_roc_auc": test_metrics.get("roc_auc"),
                "accuracy_2024": m_2024.get("accuracy") if m_2024 else None,
            }

            # Top features
            importance = model.feature_importance()
            if importance is not None:
                results[model.name]["top_features"] = importance.head(10).to_dict()

    return results


def save_results(results: dict, results_dir: str):
    os.makedirs(results_dir, exist_ok=True)
    path = os.path.join(results_dir, "model_results.json")
    with open(path, "w") as f:
        json.dump(results, f, indent=2)


def run_sanity_check(tournament: str = "ipl"):
    """Compares the current model against a baseline with minimal features."""
    paths = get_tournament_paths(tournament)
    df = load_features(paths["features"])

    # Baseline features
    baseline_features = ["t1_last10_form", "t2_last10_form", "win_streak_diff"]

    import src.models.base_model as base_model

    print("\n" + "=" * 40)
    print("RUNNING SANITY CHECK: Baseline vs Full Features")
    print("=" * 40)

    # Split
    df_train = df[df["season"] < 2024].copy()
    df_test = df[df["season"] >= 2024].copy()

    # 1. Full Model (using XGBoost as proxy)
    from src.models.xgboost_model import XGBoostModel

    full_model = XGBoostModel()
    full_model.train(df_train)
    full_metrics = full_model.evaluate(df_test)

    # 2. Baseline Model
    # Temporarily override FEATURE_COLS
    original_features = base_model.FEATURE_COLS
    base_model.FEATURE_COLS = baseline_features

    baseline_model = XGBoostModel()
    baseline_model.train(df_train)
    baseline_metrics = baseline_model.evaluate(df_test)

    # Restore
    base_model.FEATURE_COLS = original_features

    print(f"\nBaseline (3 features: {baseline_features})")
    print(f"  Test Accuracy: {baseline_metrics['accuracy']}")

    print(f"\nFull Model ({len(original_features)} features)")
    print(f"  Test Accuracy: {full_metrics['accuracy']}")

    diff = full_metrics["accuracy"] - baseline_metrics["accuracy"]
    print(f"\nNet Gain: {diff:+.4f}")
    if diff > 0.02:
        print("[SUCCESS] Result: Advanced features are adding significant value.")
    elif diff > 0:
        print("[WARNING] Result: Marginal gain. Consider feature pruning.")
    else:
        print("[ERROR] Result: Baseline outperforms full model. Overfitting or noise detected.")
    print("=" * 40 + "\n")


def run_training(tournament: str = "ipl", sanity_check: bool = False):
    paths = get_tournament_paths(tournament)
    df = load_features(paths["features"])
    results = train_all(df, paths["models"], tournament)
    save_results(results, paths["results"])

    if sanity_check:
        run_sanity_check(tournament)

    return results


if __name__ == "__main__":
    run_training()
