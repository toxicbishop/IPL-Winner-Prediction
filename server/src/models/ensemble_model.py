"""
Stacking Ensemble model combining base models with a Logistic Regression meta-learner.
Uses Out-of-Fold (OOF) predictions to train the level-1 model without leakage.
"""

import os

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

from config import CV_FOLDS, MODELS_DIR, RANDOM_STATE, get_tournament_paths
from src.models.base_model import FEATURE_COLS, TARGET_COL
from src.models.extra_trees_model import ExtraTreesModel
from src.models.lightgbm_model import LightGBMModel
from src.models.random_forest_model import RandomForestModel
from src.models.xgboost_model import XGBoostModel

# (No global FEATURES_CSV)


class EnsembleModel:
    """
    Stacking ensemble:
      Level 0: RF + XGBoost + LightGBM + ExtraTrees
      Level 1: Logistic Regression meta-learner
    """

    name = "ensemble"

    def __init__(self, save_dir: str | None = None):
        self.save_dir = save_dir or MODELS_DIR
        self.base_models = [
            RandomForestModel(save_dir=self.save_dir),
            XGBoostModel(save_dir=self.save_dir),
            LightGBMModel(save_dir=self.save_dir),
            ExtraTreesModel(save_dir=self.save_dir),
        ]
        self.meta_model = XGBClassifier(
            max_depth=2,
            learning_rate=0.05,
            n_estimators=50,
            verbosity=0,
            use_label_encoder=False,
            eval_metric="logloss"
        )
        self.is_trained = False

    def _get_meta_features(self, X: pd.DataFrame) -> np.ndarray:
        """Return (n_samples, n_base_models) probability matrix."""
        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X, columns=FEATURE_COLS)

        meta = np.zeros((len(X), len(self.base_models)))
        for i, model in enumerate(self.base_models):
            probs = model.predict_proba(X)[:, 1]
            meta[:, i] = probs
        return meta

    def train(self, df: pd.DataFrame, sample_weight=None) -> dict:
        y = df[TARGET_COL].to_numpy()

        # 1. Level 0: Cross-validation to get OOF meta-features
        print(f"Training Level-0 base models with {CV_FOLDS}-fold OOF...")
        skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
        meta_train = np.zeros((len(df), len(self.base_models)))

        for fold, (train_idx, val_idx) in enumerate(skf.split(df, y)):
            train_df = df.iloc[train_idx]
            val_X = df.iloc[val_idx][FEATURE_COLS]
            fold_weights = sample_weight.iloc[train_idx] if sample_weight is not None else None

            for i, model in enumerate(self.base_models):
                # We use a fresh instance to avoid leakage from previous folds or final train
                fresh = model.__class__(save_dir=self.save_dir)
                fresh.train(train_df, sample_weight=fold_weights)
                meta_train[val_idx, i] = fresh.predict_proba(val_X)[:, 1]
            print(f"  Fold {fold + 1} complete.")

        # 2. Level 1: Train Meta-learner
        print("Training Level-1 meta-learner (XGBoost)...")
        if sample_weight is not None:
            self.meta_model.fit(meta_train, y, sample_weight=sample_weight)
        else:
            self.meta_model.fit(meta_train, y)

        # 3. Final Level 0: Retrain all base models on FULL data
        print("Finalizing base models on full training set...")
        for model in self.base_models:
            model.train(df, sample_weight=sample_weight)

        self.is_trained = True

        train_metrics = self.evaluate(df)
        print(f"Ensemble train accuracy: {train_metrics['accuracy']:.4f}")
        return train_metrics

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("Model not trained yet.")

        meta = self._get_meta_features(X)
        # Use meta-model to predict final probabilities
        final_probs_1 = self.meta_model.predict_proba(meta)[:, 1]

        final_probs = np.zeros((len(X), 2))
        final_probs[:, 1] = final_probs_1
        final_probs[:, 0] = 1.0 - final_probs_1
        return final_probs

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)

    def evaluate(self, df: pd.DataFrame) -> dict:
        y = df[TARGET_COL].to_numpy()
        preds = self.predict(df)
        probs = self.predict_proba(df)[:, 1]

        acc = accuracy_score(y, preds)
        prec = precision_score(y, preds, zero_division=0)
        rec = recall_score(y, preds, zero_division=0)
        f1 = f1_score(y, preds, zero_division=0)

        return {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(roc_auc_score(y, probs)), 4),
            "report": classification_report(
                y, preds, target_names=["team2_won", "team1_won"], zero_division=0
            ),
        }

    def cross_validate(self, df: pd.DataFrame) -> dict:
        """Runs full ensemble training/prediction in a cross-validation loop."""
        y = df[TARGET_COL].to_numpy()
        skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
        scores = []

        print(f"Ensemble Cross-Validation ({CV_FOLDS} folds)...")
        for fold, (train_idx, val_idx) in enumerate(skf.split(df, y)):
            train_df = df.iloc[train_idx]
            val_df = df.iloc[val_idx]

            # Fresh ensemble instance for each fold
            fold_ensemble = self.__class__(save_dir=self.save_dir)
            fold_ensemble.train(train_df)

            metrics = fold_ensemble.evaluate(val_df)
            scores.append(metrics["accuracy"])
            print(f"  Fold {fold + 1} accuracy: {metrics['accuracy']:.4f}")

        return {
            "cv_mean": round(float(np.mean(scores)), 4),
            "cv_std": round(float(np.std(scores)), 4),
            "cv_scores": [round(float(s), 4) for s in scores],
        }

    def evaluate_2024(self, df: pd.DataFrame) -> dict:
        """Specific evaluation on 2024 season matches."""
        if "season" not in df.columns:
            return {}
        df_2024 = df[df["season"] == 2024].copy()
        if df_2024.empty:
            return {}
        return self.evaluate(df_2024)

    def save(self):
        os.makedirs(self.save_dir, exist_ok=True)
        # Save meta-model and base model names
        data = {
            "meta_model": self.meta_model,
            "base_model_names": [m.name for m in self.base_models],
        }
        path = os.path.join(self.save_dir, f"{self.name}.pkl")
        joblib.dump(data, path)

        # Save individual base models
        for m in self.base_models:
            m.save()
        print(f"Ensemble saved: {path}")
        return path

    def load(self):
        path = os.path.join(self.save_dir, f"{self.name}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Ensemble file not found: {path}")

        data = joblib.load(path)
        self.meta_model = data["meta_model"]

        for m in self.base_models:
            m.load()

        self.is_trained = True
        print(f"Ensemble loaded: {path}")


if __name__ == "__main__":
    paths = get_tournament_paths("ipl")
    df = pd.read_csv(paths["features"])
    model = EnsembleModel()
    model.train(df)
    metrics = model.evaluate(df)
    print(f"Final train accuracy: {metrics['accuracy']:.4f}")
    model.save()
