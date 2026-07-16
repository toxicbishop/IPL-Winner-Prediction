"""Shared fixtures for the test suite."""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.models.base_model import FEATURE_COLS, TARGET_COL  # noqa: E402


@pytest.fixture()
def mock_features_df() -> pd.DataFrame:
    """Small synthetic features DataFrame matching FEATURE_COLS + TARGET_COL.

    Balanced classes, deterministic seed, 40 rows — enough for StratifiedKFold(5).
    """
    rng = np.random.default_rng(42)
    n = 40
    data = {col: rng.uniform(0.0, 1.0, size=n) for col in FEATURE_COLS}
    data[TARGET_COL] = np.array([0, 1] * (n // 2))
    return pd.DataFrame(data)


@pytest.fixture()
def mock_matches_df() -> pd.DataFrame:
    """Tiny matches DataFrame for engineer.py helpers."""
    return pd.DataFrame(
        {
            "season": [2023, 2023, 2024, 2024, 2025, 2025],
            "team1": ["CSK", "MI", "CSK", "RCB", "MI", "RCB"],
            "team2": ["MI", "RCB", "RCB", "CSK", "RCB", "CSK"],
            "winner": ["CSK", "RCB", "CSK", "CSK", "RCB", "RCB"],
            "venue": ["Wankhede"] * 6,
        }
    )
