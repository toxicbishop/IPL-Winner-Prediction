"""
Base model class for all IPL prediction models.
Provides common interface: train, predict, evaluate, save, load.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any, cast

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score

logger = logging.getLogger(__name__)

try:
    from sklearn.frozen import FrozenEstimator as _FrozenEstimator
except ImportError:  # scikit-learn < 1.6
    _FrozenEstimator = None

from config import CV_FOLDS, MODELS_DIR, RANDOM_STATE

FEATURE_COLS = [
    "last10_top3_runs_diff",
    "last10_top_order_sr_diff",
    "last10_death_bowl_diff",
    "last10_mid_overs_econ_diff",
    "last10_pp_wickets_diff",
    "win_streak_diff",
    "last3_win_rate_diff",
    "t1_last10_form",
    "t2_last10_form",
    "t1_venue_wr",
    "t2_venue_wr",
    "toss_won_by_team1",
    "toss_decision_bat",
]

TARGET_COL = "team1_won"


class BaseIPLModel(ABC):
    """Abstract base class for IPL winner prediction models."""

    name: str = "base"

    def __init__(self, save_dir: str | None = None):
        self.save_dir = save_dir or MODELS_DIR
        self.model: Any = None
        self.is_trained = False
        self._build()

    @abstractmethod
    def _build(self):
        """Instantiate self.model with configured hyperparameters."""

    def get_X_y(self, df: pd.DataFrame):
        missing = [c for c in FEATURE_COLS if c not in df.columns]
        if missing:
            raise ValueError(f"Feature matrix missing columns: {missing}")
        if TARGET_COL not in df.columns:
            raise ValueError(f"Target column '{TARGET_COL}' missing from features dataframe.")
        X = df[FEATURE_COLS].copy()
        y = df[TARGET_COL].copy()
        nan_cols = X.columns[X.isna().any()].tolist()
        if nan_cols:
            raise ValueError(
                f"NaN values found in feature columns: {nan_cols}. "
                "Fix feature engineering before training."
            )
        if y.isna().any():
            raise ValueError(f"NaN values found in target column '{TARGET_COL}'.")
        return X, y.to_numpy()

    def train(self, df: pd.DataFrame, sample_weight=None, calibrate: bool = True):
        """Trains the model on the provided dataframe."""
        X, y = self.get_X_y(df)
        self._build()

        # Determine the correct fit arguments
        fit_params = {}
        if sample_weight is not None:
            # Handle Pipeline routing: Pipeline.fit(X, y, stepname__sample_weight=...)
            from sklearn.pipeline import Pipeline

            if isinstance(self.model, Pipeline):
                last_step_name = self.model.steps[-1][0]
                last_step_estimator = self.model.steps[-1][1]
                # Only pass if the final estimator supports sample_weight
                if (
                    hasattr(last_step_estimator, "fit")
                    and "sample_weight" in last_step_estimator.fit.__code__.co_varnames
                ):
                    fit_params[f"{last_step_name}__sample_weight"] = sample_weight
            elif (
                hasattr(self.model, "fit")
                and "sample_weight" in self.model.fit.__code__.co_varnames
            ):
                fit_params["sample_weight"] = sample_weight

        self.model.fit(X, y, **fit_params)

        if calibrate:
            # Calibrate probabilities using isotonic method for better ensemble performance
            print(f"  Calibrating {self.name} probabilities...")
            if _FrozenEstimator is not None:
                calibrated = CalibratedClassifierCV(
                    _FrozenEstimator(cast(Any, self.model)), method="isotonic"
                )
            else:
                calibrated = CalibratedClassifierCV(self.model, method="isotonic", cv="prefit")
            calibrated.fit(X, y)
            self.model = calibrated

        self.is_trained = True
        train_acc = accuracy_score(y, self.predict(X))
        return {"train_accuracy": round(float(train_acc), 4)}

    def cross_validate(self, df: pd.DataFrame) -> dict:
        X, y = self.get_X_y(df)
        cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
        scores = cross_val_score(self.model, X, y, cv=cv, scoring="accuracy", n_jobs=1)
        return {
            "cv_mean": round(float(scores.mean()), 4),
            "cv_std": round(float(scores.std()), 4),
            "cv_scores": [round(float(s), 4) for s in scores],
        }

    def evaluate(self, df: pd.DataFrame) -> dict:
        X, y = self.get_X_y(df)
        preds = self.model.predict(X)
        probs = self.predict_proba(X)[:, 1] if hasattr(self.model, "predict_proba") else None

        # Calculate scores
        acc = accuracy_score(y, preds)
        prec = precision_score(y, preds, zero_division=0)
        rec = recall_score(y, preds, zero_division=0)
        f1 = f1_score(y, preds, zero_division=0)

        metrics = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "report": classification_report(
                y, preds, target_names=["team2_won", "team1_won"], zero_division=0
            ),
        }

        if probs is not None:
            try:
                metrics["roc_auc"] = round(float(roc_auc_score(y, probs)), 4)
            except ValueError as e:
                logger.warning("ROC AUC could not be computed for %s: %s", self.name, e)
                metrics["roc_auc"] = None
        return metrics

    def evaluate_2024(self, df: pd.DataFrame) -> dict:
        """Specific evaluation on 2024 season matches."""
        if "season" not in df.columns:
            return {}
        df_2024 = df[df["season"] == 2024].copy()
        if df_2024.empty:
            return {}
        return self.evaluate(df_2024)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            X = X[FEATURE_COLS]
        return self.model.predict(X)

    def predict_proba(self, X) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            X = X[FEATURE_COLS]
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        # Fallback for models without predict_proba
        preds = self.model.predict(X)
        probs = np.zeros((len(preds), 2))
        probs[preds == 1, 1] = 0.9
        probs[preds == 0, 0] = 0.9
        return probs

    def save(self):
        os.makedirs(self.save_dir, exist_ok=True)
        path = os.path.join(self.save_dir, f"{self.name}.pkl")
        joblib.dump(self.model, path)
        print(f"Model saved: {path}")
        return path

    def load(self, path: str | None = None):
        if path is None:
            path = os.path.join(self.save_dir, f"{self.name}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"No saved model at {path}")
        self.model = joblib.load(path)
        self.is_trained = True
        print(f"Model loaded: {path}")

    def feature_importance(self) -> pd.Series | None:
        model = self.model
        # Handle calibrated models
        if hasattr(model, "estimator"):
            model = model.estimator

        # Handle Pipelines
        if hasattr(model, "steps"):
            model = model.steps[-1][1]

        if hasattr(model, "feature_importances_"):
            return pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(
                ascending=False
            )
        if hasattr(model, "coef_"):
            # Ensure it's 1D
            coef = model.coef_
            if len(coef.shape) > 1:
                coef = coef[0]
            return pd.Series(abs(coef), index=FEATURE_COLS).sort_values(
                ascending=False
            )
        return None
