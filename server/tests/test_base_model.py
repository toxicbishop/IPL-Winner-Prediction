"""Validation guards added to BaseIPLModel.get_X_y."""

import numpy as np
import pytest

from src.models.base_model import FEATURE_COLS, TARGET_COL
from src.models.random_forest_model import RandomForestModel


@pytest.fixture()
def model():
    return RandomForestModel(save_dir="outputs/models/_test")


def test_get_X_y_happy_path(model, mock_features_df):
    X, y = model.get_X_y(mock_features_df)
    assert list(X.columns) == FEATURE_COLS
    assert len(X) == len(mock_features_df)
    assert len(y) == len(mock_features_df)


def test_get_X_y_raises_on_missing_feature_column(model, mock_features_df):
    df = mock_features_df.drop(columns=[FEATURE_COLS[0]])
    with pytest.raises(ValueError, match="missing columns"):
        model.get_X_y(df)


def test_get_X_y_raises_on_missing_target(model, mock_features_df):
    df = mock_features_df.drop(columns=[TARGET_COL])
    with pytest.raises(ValueError, match=f"Target column '{TARGET_COL}'"):
        model.get_X_y(df)


def test_get_X_y_raises_on_nan_feature(model, mock_features_df):
    df = mock_features_df.copy()
    df.loc[0, FEATURE_COLS[3]] = np.nan
    with pytest.raises(ValueError, match="NaN values found in feature columns"):
        model.get_X_y(df)


def test_get_X_y_raises_on_nan_target(model, mock_features_df):
    df = mock_features_df.copy()
    df.loc[0, TARGET_COL] = np.nan
    with pytest.raises(ValueError, match="NaN values found in target column"):
        model.get_X_y(df)
