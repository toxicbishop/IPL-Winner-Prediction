"""
Team batting and bowling strength features derived from player_stats table
AND ball-by-ball data (for death overs / boundary stats).

For each team x season, computes:
  - Top-5 batsmen avg strike rate (explosiveness)
  - Top-3 bowlers avg economy (bowling control)
  - Top-3 batsmen avg runs (batting depth)
  - Death over economy (overs 16-20, from ball-by-ball)
  - Boundary percentage (4s + 6s contribution, from ball-by-ball)
  - Batting strength (normalized composite)
  - Bowling strength (normalized composite)
  - Allrounder depth

All features are season-aggregated from the player_stats table.
ball-by-ball features are loaded from CSV when available.
"""

import os
from functools import lru_cache

import numpy as np
import pandas as pd

from config import DB_ENGINE, get_tournament_paths
from src.data.db_utils import read_query

# Current tournament DB identifier/path
CURRENT_DB_ID = "ipl"

# IPL averages for normalization (sensible defaults)
IPL_AVG_BATTING_AVG = 28.0
IPL_AVG_ECONOMY = 8.5
IPL_AVG_SR = 135.0
IPL_AVG_DEATH_ECON = 10.5  # Death overs are expensive
IPL_AVG_BOUNDARY_PCT = 55.0  # ~55% of runs from boundaries in T20

# Cache for ball-by-ball data
_ball_by_ball_cache = None


def set_db_path(path: str):
    """Note: path is ignored if DB_ENGINE=postgres, using config settings instead."""
    global CURRENT_DB_ID, _ball_by_ball_cache
    # If path looks like a full file path to a db, try to extract the tournament name
    if "icc_men" in path:
        CURRENT_DB_ID = "icc_men"
    elif "icc_women" in path:
        CURRENT_DB_ID = "icc_women"
    else:
        CURRENT_DB_ID = "ipl"
    load_player_stats_cache.cache_clear()
    _ball_by_ball_cache = None  # Force reload


@lru_cache(maxsize=1)
def load_player_stats_cache() -> pd.DataFrame:
    """Load player stats once and cache."""
    db_path = None
    if DB_ENGINE == "sqlite":
        paths = get_tournament_paths(CURRENT_DB_ID)
        db_path = paths["db"]

    query = """
        SELECT season, player_name, team, role, batting_avg, batting_sr,
               runs_scored, wickets, bowling_avg, economy
        FROM player_stats ORDER BY season, team
    """
    return read_query(query, db_path=db_path)


def load_ball_by_ball() -> pd.DataFrame:
    """Load the ball-by-ball CSV for the current tournament."""
    global _ball_by_ball_cache
    if _ball_by_ball_cache is not None:
        return _ball_by_ball_cache

    paths = get_tournament_paths(CURRENT_DB_ID)
    bbb_path = os.path.join(os.path.dirname(paths["matches"]), "ball_by_ball.csv")
    if os.path.exists(bbb_path):
        df = pd.read_csv(bbb_path)
        # Normalize team names
        from config import TEAM_ALIASES

        if "batting_team" in df.columns:
            df["batting_team"] = df["batting_team"].map(lambda x: TEAM_ALIASES.get(x, x))
        if "bowling_team" in df.columns:
            df["bowling_team"] = df["bowling_team"].map(lambda x: TEAM_ALIASES.get(x, x))
        # Extract season year
        if "season" in df.columns:
            from src.data.create_dataset import SEASON_TO_YEAR

            df["season_year"] = df["season"].astype(str).map(SEASON_TO_YEAR)
            if "date" in df.columns:
                df["year"] = pd.to_datetime(df["date"], errors="coerce").dt.year
                df["season_year"] = df["season_year"].fillna(df["year"])
            df["season_year"] = df["season_year"].fillna(0).astype(int)

        _ball_by_ball_cache = df
        return df
    else:
        # Return empty dataframe with expected columns
        return pd.DataFrame(
            columns=[
                "match_id",
                "season",
                "season_year",
                "date",
                "innings",
                "over",
                "batting_team",
                "bowling_team",
                "batter",
                "bowler",
                "runs_batter",
                "runs_total",
                "player_out",
            ]
        )


# ---------------------------------------------------------------------------
# Core strength calculations
# ---------------------------------------------------------------------------


def get_team_batting_strength(team: str, season: int) -> float:
    """
    Average batting average of top-3 run-scorers for this team in this season.
    Normalized to 0-1 range.
    """
    df = load_player_stats_cache()
    batsmen = df[
        (df["team"] == team) & (df["season"] == season) & (df["batting_avg"] > 0)
    ].nlargest(3, "batting_avg")

    if len(batsmen) == 0:
        prev = df[
            (df["team"] == team) & (df["season"] == season - 1) & (df["batting_avg"] > 0)
        ].nlargest(3, "batting_avg")
        if len(prev) == 0:
            return IPL_AVG_BATTING_AVG / 60.0
        avg = prev["batting_avg"].mean()
    else:
        avg = batsmen["batting_avg"].mean()

    return float(np.clip(avg / 60.0, 0, 1))


def get_team_bowling_strength(team: str, season: int) -> float:
    """
    Average economy of top-3 wicket-takers for this team (lower economy = better).
    Normalized to 0-1 range where 1 = best (most economical).
    """
    df = load_player_stats_cache()
    bowlers = df[
        (df["team"] == team) & (df["season"] == season) & (df["wickets"] > 0) & (df["economy"] > 0)
    ].nlargest(3, "wickets")

    if len(bowlers) == 0:
        prev = df[
            (df["team"] == team) & (df["season"] == season - 1) & (df["wickets"] > 0)
        ].nlargest(3, "wickets")
        if len(prev) == 0:
            return (12.0 - IPL_AVG_ECONOMY) / 6.0
        econ = prev["economy"].mean()
    else:
        econ = bowlers["economy"].mean()

    # Lower economy = better. Map [12, 6] -> [0, 1]
    return float(np.clip((12.0 - econ) / 6.0, 0, 1))


def get_team_allrounder_strength(team: str, season: int) -> float:
    """
    Fraction of team's players who are allrounders (bat + bowl).
    Allrounders increase team flexibility and depth.
    """
    df = load_player_stats_cache()
    team_players = df[(df["team"] == team) & (df["season"] == season)]
    if len(team_players) == 0:
        return 0.2  # IPL average ~2 allrounders in 11
    allrounders = team_players[(team_players["batting_avg"] > 15) & (team_players["wickets"] > 0)]
    return min(len(allrounders) / max(len(team_players), 1), 1.0)


def get_team_advanced_metrics(team: str, season: int) -> dict:
    """
    Calculates:
      - Top 5 Batsmen SR (explosiveness)
      - Top 3 Bowlers Economy (bowling control)
      - Top 3 Batsmen avg runs (batting depth)
    """
    df = load_player_stats_cache()
    team_players = df[(df["team"] == team) & (df["season"] == season)]

    if len(team_players) == 0:
        return {
            "top5_bat_sr": IPL_AVG_SR,
            "top3_bowl_econ": IPL_AVG_ECONOMY,
            "top3_bat_runs": IPL_AVG_BATTING_AVG,
        }

    # Top 5 Batsmen by runs
    top5_bats = team_players[team_players["runs_scored"] > 0].nlargest(5, "runs_scored")
    avg_sr = top5_bats["batting_sr"].mean() if len(top5_bats) > 0 else IPL_AVG_SR
    avg_runs = top5_bats["runs_scored"].mean() if len(top5_bats) > 0 else 0

    # Top 3 Bowlers by wickets
    top3_bowls = team_players[team_players["wickets"] > 0].nlargest(3, "wickets")
    avg_econ = top3_bowls["economy"].mean() if len(top3_bowls) > 0 else IPL_AVG_ECONOMY

    return {
        "top5_bat_sr": float(avg_sr),
        "top3_bowl_econ": float(avg_econ),
        "top3_bat_runs": float(avg_runs),
    }


# ---------------------------------------------------------------------------
# Ball-by-ball derived features (Death overs + Boundaries)
# ---------------------------------------------------------------------------


def get_death_over_economy(team: str, season: int) -> float:
    """
    Bowling economy in death overs (16-20) for the BOWLING team.
    Lower = better death bowling.
    Returns normalized score: (14 - death_econ) / 8 -> [0, 1] where 1 = best.
    """
    bbb = load_ball_by_ball()
    if len(bbb) == 0:
        return (14.0 - IPL_AVG_DEATH_ECON) / 8.0

    death = bbb[
        (bbb["bowling_team"] == team) & (bbb["season_year"] == season) & (bbb["over"] >= 16)
    ]

    if len(death) == 0:
        # Fallback to previous season
        death = bbb[
            (bbb["bowling_team"] == team) & (bbb["season_year"] == season - 1) & (bbb["over"] >= 16)
        ]

    if len(death) == 0:
        return (14.0 - IPL_AVG_DEATH_ECON) / 8.0

    total_runs = death["runs_total"].sum()
    total_balls = len(death)
    overs = total_balls / 6.0

    if overs < 1:
        return (14.0 - IPL_AVG_DEATH_ECON) / 8.0

    death_econ = total_runs / overs
    return float(np.clip((14.0 - death_econ) / 8.0, 0, 1))


def get_boundary_percentage(team: str, season: int) -> float:
    """
    Percentage of batting runs scored via boundaries (4s and 6s).
    Higher = more explosive batting lineup.
    Returns raw percentage (typically 45-65% in T20).
    """
    bbb = load_ball_by_ball()
    if len(bbb) == 0:
        return IPL_AVG_BOUNDARY_PCT

    batting = bbb[(bbb["batting_team"] == team) & (bbb["season_year"] == season)]

    if len(batting) == 0:
        batting = bbb[(bbb["batting_team"] == team) & (bbb["season_year"] == season - 1)]

    if len(batting) == 0:
        return IPL_AVG_BOUNDARY_PCT

    total_runs = batting["runs_batter"].sum()
    if total_runs == 0:
        return IPL_AVG_BOUNDARY_PCT

    boundary_runs = batting[batting["runs_batter"].isin([4, 6])]["runs_batter"].sum()
    return float(boundary_runs / total_runs * 100)


def get_powerplay_economy(team: str, season: int) -> float:
    """
    Bowling economy in powerplay (overs 0-5) for the BOWLING team.
    Lower = better new-ball bowling.
    Returns normalized score: (12 - pp_econ) / 6 -> [0, 1] where 1 = best.
    """
    bbb = load_ball_by_ball()
    if len(bbb) == 0:
        return 0.5

    pp = bbb[(bbb["bowling_team"] == team) & (bbb["season_year"] == season) & (bbb["over"] < 6)]

    if len(pp) == 0:
        pp = bbb[
            (bbb["bowling_team"] == team) & (bbb["season_year"] == season - 1) & (bbb["over"] < 6)
        ]

    if len(pp) == 0:
        return 0.5

    total_runs = pp["runs_total"].sum()
    overs = len(pp) / 6.0
    if overs < 1:
        return 0.5

    pp_econ = total_runs / overs
    return float(np.clip((12.0 - pp_econ) / 6.0, 0, 1))


def get_middle_overs_economy(team: str, season: int) -> float:
    """
    Bowling economy in middle overs (6-15) for the BOWLING team.
    Returns normalized score: (10 - mid_econ) / 5 -> [0, 1] where 1 = best.
    """
    bbb = load_ball_by_ball()
    if len(bbb) == 0:
        return 0.5

    mid = bbb[(bbb["bowling_team"] == team) & (bbb["season_year"] == season) & (bbb["over"] >= 6) & (bbb["over"] <= 15)]

    if len(mid) == 0:
        mid = bbb[(bbb["bowling_team"] == team) & (bbb["season_year"] == season - 1) & (bbb["over"] >= 6) & (bbb["over"] <= 15)]

    if len(mid) == 0:
        return 0.5

    total_runs = mid["runs_total"].sum()
    overs = len(mid) / 6.0
    if overs < 1:
        return 0.5

    mid_econ = total_runs / overs
    return float(np.clip((10.0 - mid_econ) / 5.0, 0, 1))


def get_batting_split_strengths(team: str, season: int) -> dict:
    """
    Batting strength split by roles based on runs scored ranking.
    top_order: 1-3, middle_order: 4-6, finisher: 7-8
    Returns normalized values (0 to 1).
    """
    df = load_player_stats_cache()
    team_players = df[(df["team"] == team) & (df["season"] == season)]

    if len(team_players) < 8:
        team_players = df[(df["team"] == team) & (df["season"] == season - 1)]

    if len(team_players) < 8:
        return {
            "top_order_strength": 0.5,
            "middle_order_strength": 0.4,
            "finisher_strength": 0.3
        }

    batsmen = team_players[team_players["runs_scored"] > 0].sort_values("runs_scored", ascending=False)

    top3 = batsmen.iloc[0:3]
    mid3 = batsmen.iloc[3:6]
    fin2 = batsmen.iloc[6:8]

    def calc_str(group, max_avg=50.0):
        if len(group) == 0:
            return 0.3
        avg = group["batting_avg"].mean()
        sr = group["batting_sr"].mean()
        # Combine avg and SR for a strength metric, normalize to ~1.0
        score = (avg / max_avg) * 0.6 + (sr / 150.0) * 0.4
        return float(np.clip(score, 0, 1))

    return {
        "top_order_strength": calc_str(top3, 50.0),
        "middle_order_strength": calc_str(mid3, 40.0),
        "finisher_strength": calc_str(fin2, 30.0),
    }


def get_recent_team_stats(team: str, recent_match_ids: list, bbb_df: pd.DataFrame) -> dict:
    """Computes batting/bowling metrics from a specific set of recent matches."""
    if not recent_match_ids or bbb_df is None or bbb_df.empty:
        return {
            "recent_death_econ": IPL_AVG_DEATH_ECON,
            "recent_mid_econ": IPL_AVG_ECONOMY,
            "recent_boundary_pct": IPL_AVG_BOUNDARY_PCT,
            "recent_top_order_runs": 150.0,
            "recent_top_order_sr": 135.0,
            "recent_pp_wickets": 1.0,
        }

    # Filter BBB for these matches and team
    team_bbb = bbb_df[bbb_df["match_id"].isin(recent_match_ids)]

    # Define weights based on number of matches found
    match_ids = sorted(team_bbb["match_id"].unique())
    # We want to map each match_id to a weight. Most recent match_id (max) gets 1.0
    num_matches = len(match_ids)
    if num_matches == 0:
        return {
            "recent_death_econ": IPL_AVG_DEATH_ECON,
            "recent_mid_econ": IPL_AVG_ECONOMY,
            "recent_boundary_pct": IPL_AVG_BOUNDARY_PCT,
            "recent_top_order_runs": 150.0,
            "recent_top_order_sr": 135.0,
            "recent_pp_wickets": 1.0,
        }

    weights = np.linspace(0.6, 1.0, num_matches)
    id_to_weight = dict(zip(match_ids, weights, strict=False))

    # Simplified Weighted Mean approach:
    # 1. Calculate per-match stats
    match_stats = []
    for m_id in match_ids:
        m_data = team_bbb[team_bbb["match_id"] == m_id]

        # Death
        d = m_data[(m_data["bowling_team"] == team) & (m_data["over"] >= 16)]
        d_econ = (d["runs_total"].sum() / d.shape[0] * 6) if not d.empty else IPL_AVG_DEATH_ECON

        # Mid
        mi = m_data[(m_data["bowling_team"] == team) & (m_data["over"].between(7, 15))]
        mi_econ = (mi["runs_total"].sum() / mi.shape[0] * 6) if not mi.empty else IPL_AVG_ECONOMY

        # Batting
        tb = m_data[(m_data["batting_team"] == team) & (m_data["over"] <= 10)]
        tb_runs = tb["runs_total"].sum() if not tb.empty else 150.0
        tb_sr = (tb["runs_batter"].sum() / tb.shape[0] * 100) if not tb.empty else 135.0
        tb_b_pct = (tb["runs_batter"].isin([4, 6]).sum() / tb.shape[0] * 100) if not tb.empty else 15.0

        # PP Wickets
        pp = m_data[(m_data["bowling_team"] == team) & (m_data["over"] <= 5)]
        pp_w = pp["player_out"].count() if not pp.empty else 1.0

        match_stats.append({
            "death": d_econ,
            "mid": mi_econ,
            "runs": tb_runs,
            "sr": tb_sr,
            "bpct": tb_b_pct,
            "ppw": pp_w,
            "weight": id_to_weight[m_id]
        })

    # 2. Aggregate using weights
    total_w = sum(id_to_weight.values())
    res = {
        "recent_death_econ": sum(s["death"] * s["weight"] for s in match_stats) / total_w,
        "recent_mid_econ": sum(s["mid"] * s["weight"] for s in match_stats) / total_w,
        "recent_boundary_pct": sum(s["bpct"] * s["weight"] for s in match_stats) / total_w,
        "recent_top_order_runs": sum(s["runs"] * s["weight"] for s in match_stats) / total_w,
        "recent_top_order_sr": sum(s["sr"] * s["weight"] for s in match_stats) / total_w,
        "recent_pp_wickets": sum(s["ppw"] * s["weight"] for s in match_stats) / total_w,
    }
    return res


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def get_team_strength_features(team: str, season: int) -> dict:
    """Returns all team strength features for a given team and season."""
    if season >= 2026:
        try:
            from src.features.player_form import team_strength_from_roster

            feats = team_strength_from_roster(team, season)
            # Add advanced metrics placeholders for 2026 if not present
            feats.setdefault("top5_bat_sr", 135.0)
            feats.setdefault("top3_bowl_econ", 8.2)
            feats.setdefault("top3_bat_runs", 300.0)
            feats.setdefault("bat_bowl_balance", abs(feats.get("batting_strength", 0) - feats.get("bowling_strength", 0)))
            feats.setdefault("death_bowl_str", 0.5)
            feats.setdefault("boundary_pct", IPL_AVG_BOUNDARY_PCT)
            feats.setdefault("pp_bowl_str", 0.5)
            feats.setdefault("mid_bowl_str", 0.5)
            feats.setdefault("top_order_strength", 0.5)
            feats.setdefault("middle_order_strength", 0.4)
            feats.setdefault("finisher_strength", 0.3)
            return feats
        except Exception:
            pass

    bat = get_team_batting_strength(team, season)
    bowl = get_team_bowling_strength(team, season)
    allround = get_team_allrounder_strength(team, season)
    adv = get_team_advanced_metrics(team, season)
    death = get_death_over_economy(team, season)
    bdry = get_boundary_percentage(team, season)
    pp = get_powerplay_economy(team, season)
    mid_bowl = get_middle_overs_economy(team, season)
    bat_splits = get_batting_split_strengths(team, season)

    return {
        "batting_strength": bat,
        "bowling_strength": bowl,
        "allround_strength": allround,
        "top5_bat_sr": adv["top5_bat_sr"],
        "top3_bowl_econ": adv["top3_bowl_econ"],
        "top3_bat_runs": adv["top3_bat_runs"],
        "bat_bowl_balance": abs(bat - bowl),
        "death_bowl_str": death,
        "boundary_pct": bdry,
        "pp_bowl_str": pp,
        "mid_bowl_str": mid_bowl,
        "top_order_strength": bat_splits["top_order_strength"],
        "middle_order_strength": bat_splits["middle_order_strength"],
        "finisher_strength": bat_splits["finisher_strength"],
    }
