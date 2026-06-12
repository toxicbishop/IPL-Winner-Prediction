"""
Feature store concept using Parquet files for centralized storage.
Provides simple read/write access to engineered features.
"""

import os

import pandas as pd

from config import PROCESSED_DIR

FEATURE_STORE_PATH = os.path.join(PROCESSED_DIR, "feature_store")
os.makedirs(FEATURE_STORE_PATH, exist_ok=True)


def save_features(df: pd.DataFrame, tournament: str, version: str = "latest"):
    """Save features to parquet feature store."""
    path = os.path.join(FEATURE_STORE_PATH, f"{tournament}_features_{version}.parquet")
    df.to_parquet(path, index=False)
    # Also save as latest
    if version != "latest":
        latest_path = os.path.join(FEATURE_STORE_PATH, f"{tournament}_features_latest.parquet")
        df.to_parquet(latest_path, index=False)
    print(f"Features saved to store: {path}")


def load_features(tournament: str, version: str = "latest") -> pd.DataFrame:
    """Load features from parquet feature store."""
    path = os.path.join(FEATURE_STORE_PATH, f"{tournament}_features_{version}.parquet")
    if not os.path.exists(path):
        # Fallback to CSV if parquet doesn't exist yet
        csv_path = os.path.join(PROCESSED_DIR, tournament, "features.csv")
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)
        raise FileNotFoundError(f"Features for {tournament} version {version} not found.")
    return pd.read_parquet(path)
