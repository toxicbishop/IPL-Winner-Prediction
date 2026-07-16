"""
Feature engineering for IPL match prediction.

Features generated per match row (team1 vs team2):
 - Toss win / decision
 - Win percentage: all-time (smoothed), last 3 seasons, last 5 matches
 - Head-to-head win rate (last 3 seasons)
 - Home ground advantage
 - Recent titles (last 5 seasons only)
 - Season form
 - Venue win rate for each team
 - Venue pitch features
 - Team batting/bowling strength (from real player stats)
"""

import os

import pandas as pd

from config import get_tournament_paths
from src.data.db_utils import get_connection
from src.features.team_strength import (
    get_recent_team_stats,
    load_ball_by_ball,
    set_db_path,
)

# Kept for backward-compatible tests and reporting utilities.
# This constant is intentionally not used as a predictive feature.
TITLE_COUNTS = {
    "CSK": 5,
    "MI": 5,
    "KKR": 3,
    "SRH": 1,
    "RR": 1,
    "GT": 1,
    "RCB": 0,
    "DC": 0,
    "PBKS": 0,
    "LSG": 0,
}


def get_all_time_win_rates(matches: pd.DataFrame) -> dict:
    """
    Returns {team: bayesian_smoothed_win_rate} using ONLY the provided matches.
    Bayesian smoothing: blend raw win rate with 0.5 prior (10 ghost matches).
    """
    rates = {}
    all_teams = set(matches["team1"]) | set(matches["team2"])
    prior_weight = 10
    for team in all_teams:
        played = int(((matches["team1"] == team) | (matches["team2"] == team)).sum())
        won = int((matches["winner"] == team).sum())
        rates[team] = (won + prior_weight * 0.5) / (played + prior_weight)
    return rates


def get_last_n_seasons_wr(
    matches: pd.DataFrame, team: str, before_season: int, n_seasons: int = 3
) -> float:
    """Win rate over the N most recent completed seasons before `before_season`."""
    relevant = matches[
        (matches["season"] < before_season)
        & ((matches["team1"] == team) | (matches["team2"] == team))
    ]
    if len(relevant) == 0:
        return 0.5

    available_seasons = sorted(relevant["season"].unique())[-n_seasons:]
    recent = relevant[relevant["season"].isin(available_seasons)]

    if len(recent) == 0:
        return 0.5

    wins = (recent["winner"] == team).sum()
    prior_weight = 4
    return (wins + prior_weight * 0.5) / (len(recent) + prior_weight)


def get_recent_form(matches: pd.DataFrame, team: str, before_idx: int, n: int = 5) -> float:
    """Exponentially weighted win rate of `team` in its last `n` matches."""
    past = matches.iloc[:before_idx]
    team_matches = past[(past["team1"] == team) | (past["team2"] == team)]
    recent = team_matches.tail(n)
    if len(recent) == 0:
        return 0.5

    # Weights: 1.0 for most recent, 0.6 for 5th oldest
    weights = [0.6, 0.7, 0.8, 0.9, 1.0][-len(recent) :]
    results = (recent["winner"] == team).astype(int).tolist()

    weighted_wins = sum(w * res for w, res in zip(weights, results, strict=False))
    return weighted_wins / sum(weights)


def get_last_n_match_ids(matches: pd.DataFrame, team: str, before_idx: int, n: int = 5) -> list:
    """Returns the match IDs for the last N matches of a team."""
    past = matches.iloc[:before_idx]
    team_matches = past[(past["team1"] == team) | (past["team2"] == team)]
    return team_matches.tail(n)["match_id"].tolist()


def get_last_n_form(matches: pd.DataFrame, team: str, before_idx: int, n: int = 10) -> float:
    """Simple win rate over last n matches (no weighting). Good for stability."""
    past = matches.iloc[:before_idx]
    team_matches = past[(past["team1"] == team) | (past["team2"] == team)]
    recent = team_matches.tail(n)
    if len(recent) == 0:
        return 0.5
    wins = (recent["winner"] == team).sum()
    return wins / len(recent)


def get_recent_nrr(matches: pd.DataFrame, team: str, before_idx: int, n: int = 5) -> float:
    """Approximate NRR based on win margins in last n matches."""
    past = matches.iloc[:before_idx]
    team_matches = past[(past["team1"] == team) | (past["team2"] == team)]
    recent = team_matches.tail(n)
    if len(recent) == 0:
        return 0.0

    margins = []
    for _, row in recent.iterrows():
        if row["winner"] == team:
            margin = row["win_by_runs"] + (row["win_by_wickets"] * 5)
            margins.append(margin)
        else:
            margin = -(row["win_by_runs"] + (row["win_by_wickets"] * 5))
            margins.append(margin)

    # Average margin per match, normalized (e.g., 50 run win / 10 = 5.0)
    return sum(margins) / len(margins) / 20.0


def get_h2h_rate(
    matches: pd.DataFrame, team1: str, team2: str, before_idx: int, window_seasons: int = 3
) -> float:
    """Head-to-head win rate of team1 vs team2 over last `window_seasons` seasons."""
    past = matches.iloc[:before_idx]
    if len(past) == 0:
        return 0.5
    recent_seasons = sorted(past["season"].unique())[-window_seasons:]
    h2h = past[
        (past["season"].isin(recent_seasons))
        & (
            ((past["team1"] == team1) & (past["team2"] == team2))
            | ((past["team1"] == team2) & (past["team2"] == team1))
        )
    ]
    if len(h2h) == 0:
        return 0.5
    wins1 = (h2h["winner"] == team1).sum()
    return wins1 / len(h2h)


def get_venue_win_rate(matches: pd.DataFrame, team: str, venue: str, before_idx: int) -> float:
    """Win rate of `team` at a specific venue."""
    past = matches.iloc[:before_idx]
    at_venue = past[(past["venue"] == venue) & ((past["team1"] == team) | (past["team2"] == team))]
    if len(at_venue) == 0:
        return 0.5
    wins = (at_venue["winner"] == team).sum()
    return wins / len(at_venue)


def is_home_ground(team: str, venue: str, tournament: str = "ipl") -> int:
    """Returns 1 if venue is team's home ground. (IPL focus)"""
    if tournament != "ipl":
        return 0  # In international tourneys, usually neutral venues or whole country
    home_map = {
        "CSK": ["MA Chidambaram Stadium"],
        "MI": ["Wankhede Stadium"],
        "RCB": ["M Chinnaswamy Stadium"],
        "KKR": ["Eden Gardens"],
        "DC": ["Arun Jaitley Stadium", "Feroz Shah Kotla"],
        "RR": ["Sawai Mansingh Stadium"],
        "SRH": ["Rajiv Gandhi International Cricket Stadium"],
        "PBKS": [
            "Punjab Cricket Association IS Bindra Stadium",
            "Punjab Cricket Association Stadium",
        ],
        "GT": ["Narendra Modi Stadium"],
        "LSG": ["BRSABV Ekana Cricket Stadium"],
    }
    return int(venue in home_map.get(team, []))


def get_season_form(matches: pd.DataFrame, team: str, season: int, before_idx: int) -> float:
    """Win rate within the current season up to before_idx."""
    season_matches = matches.iloc[:before_idx]
    season_matches = season_matches[season_matches["season"] == season]
    team_matches = season_matches[
        (season_matches["team1"] == team) | (season_matches["team2"] == team)
    ]
    if len(team_matches) == 0:
        return 0.5
    wins = (team_matches["winner"] == team).sum()
    return wins / len(team_matches)


def get_win_streak(matches: pd.DataFrame, team: str, before_idx: int) -> int:
    """Consecutive wins for `team` before `before_idx`."""
    past = matches.iloc[:before_idx]
    team_matches = past[(past["team1"] == team) | (past["team2"] == team)]
    if len(team_matches) == 0:
        return 0

    streak = 0
    # Iterate backwards through team matches
    for _, match in team_matches.iloc[::-1].iterrows():
        if match["winner"] == team:
            streak += 1
        else:
            break
    return streak


def load_champions_by_season(db_path: str) -> dict:
    """Load season champions from SQLite season_stats table."""
    from config import DB_ENGINE

    if DB_ENGINE == "sqlite" and not os.path.exists(db_path):
        return {}
    from sqlalchemy import text

    try:
        conn = get_connection(db_path)
        res = conn.execute(text("SELECT season, team FROM season_stats WHERE won_title = 1"))
        return {int(season): team for season, team in res.fetchall()}
    finally:
        conn.close()


def get_recent_titles(
    team: str,
    before_season: int,
    champions_by_season: dict = None,
    window: int = 5,
    db_path: str = None,
) -> int:
    """
    Titles won by this team in the `window` seasons before `before_season`.
    If champions_by_season not provided, loads from DB.
    """
    if champions_by_season is None:
        if db_path is None:
            return 0  # Fallback
        champions_by_season = load_champions_by_season(db_path)
    count = 0
    for season in range(before_season - window, before_season):
        if champions_by_season.get(season) == team:
            count += 1
    return count


def build_features(matches_df: pd.DataFrame, db_path: str, tournament: str) -> pd.DataFrame:
    set_db_path(db_path)
    df = matches_df.reset_index(drop=True)
    load_champions_by_season(db_path)
    bbb_df = load_ball_by_ball()

    rows = []
    for idx, row in df.iterrows():
        t1 = row["team1"]
        t2 = row["team2"]
        venue = row["venue"]
        season = int(row["season"])

        f = {
            "match_id": row["match_id"],
            "season": season,
            "team1": t1,
            "team2": t2,
        }

        # ============================================================
        # MOMENTUM (Last 3 - 10 matches)
        # ============================================================
        f["t1_last10_form"] = get_last_n_form(df, t1, idx, 10)
        f["t2_last10_form"] = get_last_n_form(df, t2, idx, 10)

        f["t1_last3_wr"] = get_last_n_form(df, t1, idx, 3)
        f["t2_last3_wr"] = get_last_n_form(df, t2, idx, 3)
        f["last3_win_rate_diff"] = f["t1_last3_wr"] - f["t2_last3_wr"]

        s1 = get_win_streak(df, t1, idx)
        s2 = get_win_streak(df, t2, idx)
        f["win_streak_diff"] = s1 - s2

        # ============================================================
        # TEMPORAL TEAM STRENGTH (Last 10 matches)
        # ============================================================
        m_ids1 = get_last_n_match_ids(df, t1, idx, 10)
        m_ids2 = get_last_n_match_ids(df, t2, idx, 10)

        stats1 = get_recent_team_stats(t1, m_ids1, bbb_df)
        stats2 = get_recent_team_stats(t2, m_ids2, bbb_df)

        f["last10_top3_runs_diff"] = stats1["recent_top_order_runs"] - stats2["recent_top_order_runs"]
        f["last10_top_order_sr_diff"] = stats1["recent_top_order_sr"] - stats2["recent_top_order_sr"]
        f["last10_death_bowl_diff"] = stats1["recent_death_econ"] - stats2["recent_death_econ"]
        f["last10_mid_overs_econ_diff"] = stats1["recent_mid_econ"] - stats2["recent_mid_econ"]
        f["last10_pp_wickets_diff"] = stats1["recent_pp_wickets"] - stats2["recent_pp_wickets"]

        # ============================================================
        # CONTEXT (Venue, Toss)
        # ============================================================
        f["t1_venue_wr"] = get_venue_win_rate(df, t1, venue, idx)
        f["t2_venue_wr"] = get_venue_win_rate(df, t2, venue, idx)

        f["toss_won_by_team1"] = int(row.get("toss_won_by_team1", 0))
        f["toss_decision_bat"] = int(row.get("toss_decision_bat", 0))

        # Target
        f["team1_won"] = int(row["team1_won"])
        rows.append(f)

    features_df = pd.DataFrame(rows)
    return features_df


def save_features(df: pd.DataFrame, features_csv: str):
    os.makedirs(os.path.dirname(features_csv), exist_ok=True)
    df.to_csv(features_csv, index=False)
    print(f"Features saved: {len(df)} rows x {len(df.columns)} cols -> {features_csv}")


def run_feature_engineering(tournament: str = "ipl") -> pd.DataFrame:
    paths = get_tournament_paths(tournament)
    processed_matches = paths["features"].replace("features.csv", "matches_processed.csv")
    if not os.path.exists(processed_matches):
        raise FileNotFoundError(f"Processed matches not found: {processed_matches}")

    df_matches = pd.read_csv(processed_matches)
    df_features = build_features(df_matches, paths["db"], tournament)

    # Save to legacy CSV
    save_features(df_features, paths["features"])

    # Save to Feature Store (Parquet)
    from src.features.store import save_features as store_features

    store_features(df_features, tournament)

    return df_features


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tournament", default="ipl")
    args = parser.parse_args()
    run_feature_engineering(args.tournament)
