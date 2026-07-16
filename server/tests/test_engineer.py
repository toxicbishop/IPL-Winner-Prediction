"""Tests for feature-engineering helpers in src/features/engineer.py."""

import pandas as pd

from src.features.engineer import get_all_time_win_rates


def test_all_time_win_rates_bayesian_smoothing(mock_matches_df):
    rates = get_all_time_win_rates(mock_matches_df)
    # 4 distinct teams in fixture
    assert set(rates.keys()) == {"CSK", "MI", "RCB"}
    # All rates within (0, 1) — smoothing prevents 0.0 or 1.0 on small samples
    for team, wr in rates.items():
        assert 0.0 < wr < 1.0, f"{team}: {wr} should be smoothed away from extremes"


def test_all_time_win_rates_no_matches_returns_empty():
    empty = pd.DataFrame(columns=["team1", "team2", "winner", "season"])
    rates = get_all_time_win_rates(empty)
    assert rates == {}
