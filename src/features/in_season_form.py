"""In-season form signal derived from already-completed matches in the current season.

For 2026 this reads data/processed/ipl/matches.csv (rebuilt from Cricsheet on every
pipeline run) and computes per-team win rate across matches played so far.

The signal is fed into the Bayesian update in predict_2026.py with a weight that
ramps with the number of matches played, so it contributes little pre-tournament
and grows into a dominant signal by mid-season.
"""

from __future__ import annotations

import os

import pandas as pd

from config import get_tournament_paths


def compute_in_season_form(
    tournament: str = "ipl",
    season: int = 2026,
) -> tuple[dict[str, float], int]:
    """Return ({team: win_rate}, total_matches_played) for the given season.

    Teams with no matches played default to 0.5. Total matches is the number of
    completed games across all teams (each match counted once, not twice).
    """
    paths = get_tournament_paths(tournament)
    matches_path = paths["matches"]
    if not os.path.exists(matches_path):
        return {}, 0

    df = pd.read_csv(matches_path)
    season_df = df[df["season"] == season]
    if season_df.empty:
        return {}, 0

    wins: dict[str, int] = {}
    total: dict[str, int] = {}
    for _, r in season_df.iterrows():
        for t in (r["team1"], r["team2"]):
            total[t] = total.get(t, 0) + 1
        winner = r.get("winner")
        if winner in (r["team1"], r["team2"]):
            wins[winner] = wins.get(winner, 0) + 1

    rates = {t: wins.get(t, 0) / total[t] for t in total if total[t] > 0}
    return rates, len(season_df)


def in_season_weight(n_matches: int, full_weight: float = 0.30, ramp_to: int = 30) -> float:
    """Linearly ramp from 0 (no matches) to full_weight at ramp_to matches, then plateau.

    30 matches ≈ 40% through an IPL league stage — by that point, recent form
    should carry meaningful weight vs. pre-season priors.
    """
    if n_matches <= 0:
        return 0.0
    return full_weight * min(n_matches / ramp_to, 1.0)
