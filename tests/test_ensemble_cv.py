"""Verify EnsembleModel.cross_validate runs real CV (not the old stub)."""

from config import CV_FOLDS
from src.models.ensemble_model import EnsembleModel


def test_cross_validate_returns_real_scores(mock_features_df):
    model = EnsembleModel(save_dir="outputs/models/_test")
    result = model.cross_validate(mock_features_df)

    assert "cv_mean" in result
    assert "cv_std" in result
    assert "cv_scores" in result
    assert len(result["cv_scores"]) == CV_FOLDS
    # Not the old hardcoded stub
    assert not (result["cv_mean"] == 0.65 and result["cv_std"] == 0.0)
    assert 0.0 <= result["cv_mean"] <= 1.0
    for s in result["cv_scores"]:
        assert 0.0 <= s <= 1.0
