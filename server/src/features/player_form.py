"""Per-player career-to-date form metrics derived from ball-by-ball Cricsheet data.

Provides roster-aware team strength by aggregating individual player metrics
(batting average, strike rate, bowling economy, bowling strike rate) across a
team's projected XI, with recency weighting (recent seasons count more).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

import numpy as np
import pandas as pd

from config import BASE_DIR

BBB_CSV = os.path.join(BASE_DIR, "data", "mock", "IPL.csv")
ROSTERS_PATH = os.path.join(BASE_DIR, "data", "rosters_2026.json")

# IPL long-run averages for normalization / fallbacks
LEAGUE_BAT_AVG = 28.0
LEAGUE_BAT_SR = 135.0
LEAGUE_ECONOMY = 8.5
LEAGUE_BOWL_SR = 22.0  # balls per wicket

# Recency: each season older than the reference year gets multiplied by this.
RECENCY_DECAY = 0.7


@lru_cache(maxsize=1)
def _load_bbb() -> pd.DataFrame:
    df = pd.read_csv(
        BBB_CSV,
        low_memory=False,
        usecols=[
            "match_id",
            "season",
            "innings",
            "batter",
            "bowler",
            "runs_batter",
            "runs_bowler",
            "valid_ball",
            "balls_faced",
            "bowler_wicket",
            "player_out",
        ],
    )
    df["season_y"] = pd.to_numeric(df["season"].astype(str).str[-4:], errors="coerce").astype(
        "Int64"
    )
    return df


@lru_cache(maxsize=1)
def _load_rosters() -> dict[str, list[str]]:
    with open(ROSTERS_PATH) as f:
        return json.load(f)["rosters"]


def _season_weights(seasons: list[int], ref_year: int) -> dict[int, float]:
    return {s: RECENCY_DECAY ** max(0, ref_year - s) for s in seasons}


@lru_cache(maxsize=1)
def _batting_table() -> pd.DataFrame:
    df = _load_bbb()
    runs = df.groupby(["season_y", "batter"])["runs_batter"].sum()
    balls = df.groupby(["season_y", "batter"])["balls_faced"].sum()
    outs = (
        df[df["player_out"].notna() & (df["player_out"] != "")]
        .groupby(["season_y", "player_out"])
        .size()
    )
    tbl = pd.concat([runs, balls, outs.rename("outs")], axis=1).fillna(0)
    tbl.index.names = ["season_y", "player"]
    return tbl.reset_index()


@lru_cache(maxsize=1)
def _bowling_table() -> pd.DataFrame:
    df = _load_bbb()
    valid = df[df["valid_ball"] == 1]
    runs_conceded = valid.groupby(["season_y", "bowler"])["runs_bowler"].sum()
    balls = valid.groupby(["season_y", "bowler"]).size().rename("balls")
    wickets = valid.groupby(["season_y", "bowler"])["bowler_wicket"].sum()
    tbl = pd.concat([runs_conceded, balls, wickets], axis=1).fillna(0)
    tbl.index.names = ["season_y", "player"]
    return tbl.reset_index()


def get_player_batting(player: str, ref_year: int, lookback: int = 3) -> dict:
    tbl = _batting_table()
    rows = tbl[
        (tbl["player"] == player) & (tbl["season_y"].between(ref_year - lookback, ref_year - 1))
    ]
    if rows.empty:
        return {"bat_avg": LEAGUE_BAT_AVG, "bat_sr": LEAGUE_BAT_SR, "innings_proxy": 0}
    weights = _season_weights(rows["season_y"].tolist(), ref_year)
    w = np.array([weights[int(s)] for s in rows["season_y"]])
    runs = (rows["runs_batter"].values * w).sum()
    balls = (rows["balls_faced"].values * w).sum()
    outs = (rows["outs"].values * w).sum()
    if balls <= 0:
        return {"bat_avg": LEAGUE_BAT_AVG, "bat_sr": LEAGUE_BAT_SR, "innings_proxy": 0}
    bat_avg = runs / max(outs, 1)
    bat_sr = 100 * runs / balls
    return {"bat_avg": float(bat_avg), "bat_sr": float(bat_sr), "innings_proxy": float(balls / 20)}


def get_player_bowling(player: str, ref_year: int, lookback: int = 3) -> dict:
    tbl = _bowling_table()
    rows = tbl[
        (tbl["player"] == player) & (tbl["season_y"].between(ref_year - lookback, ref_year - 1))
    ]
    if rows.empty:
        return {"economy": LEAGUE_ECONOMY, "bowl_sr": LEAGUE_BOWL_SR, "wickets": 0}
    weights = _season_weights(rows["season_y"].tolist(), ref_year)
    w = np.array([weights[int(s)] for s in rows["season_y"]])
    runs = (rows["runs_bowler"].values * w).sum()
    balls = (rows["balls"].values * w).sum()
    wickets = (rows["bowler_wicket"].values * w).sum()
    if balls <= 0:
        return {"economy": LEAGUE_ECONOMY, "bowl_sr": LEAGUE_BOWL_SR, "wickets": 0}
    economy = 6 * runs / balls
    bowl_sr = balls / max(wickets, 1)
    return {"economy": float(economy), "bowl_sr": float(bowl_sr), "wickets": float(wickets)}


def _top_k(rows: list[dict], key: str, k: int, reverse: bool = True) -> list[dict]:
    return sorted(rows, key=lambda r: r[key], reverse=reverse)[:k]


def team_strength_from_roster(team: str, ref_year: int = 2026) -> dict:
    """Bottom-up team strength computed from the 2026 roster's projected XI.

    Batting score: mean batting-avg × SR/100 of top-6 batsmen (ranked by innings_proxy).
    Bowling score: inverse of (economy × SR) of top-4 bowlers (ranked by wickets).
    Both normalized to 0-1 relative to league averages.
    """
    rosters = _load_rosters()
    squad = rosters.get(team, [])
    if not squad:
        return {"batting_strength": 0.5, "bowling_strength": 0.5, "allround_strength": 0.2}

    bat_rows, bowl_rows = [], []
    for p in squad:
        b = get_player_batting(p, ref_year)
        bat_rows.append({"player": p, **b})
        w = get_player_bowling(p, ref_year)
        bowl_rows.append({"player": p, **w})

    top_bat = _top_k([r for r in bat_rows if r["innings_proxy"] > 0], "innings_proxy", 6)
    if not top_bat:
        top_bat = bat_rows[:6]
    bat_score = np.mean([r["bat_avg"] * r["bat_sr"] / 100 for r in top_bat])
    bat_norm = float(np.clip(bat_score / (LEAGUE_BAT_AVG * LEAGUE_BAT_SR / 100), 0, 2) / 2)

    top_bowl = _top_k([r for r in bowl_rows if r["wickets"] > 0], "wickets", 4)
    if not top_bowl:
        top_bowl = bowl_rows[:4]
    bowl_penalty = np.mean([r["economy"] * r["bowl_sr"] for r in top_bowl])
    league_penalty = LEAGUE_ECONOMY * LEAGUE_BOWL_SR
    bowl_norm = float(np.clip(league_penalty / max(bowl_penalty, 1e-6), 0, 2) / 2)

    allrounders = 0
    for p in squad:
        b = get_player_batting(p, ref_year)
        w = get_player_bowling(p, ref_year)
        if b["bat_avg"] >= 18 and w["wickets"] >= 5:
            allrounders += 1
    allround = min(allrounders / max(len(squad), 1), 1.0)

    return {
        "batting_strength": bat_norm,
        "bowling_strength": bowl_norm,
        "allround_strength": float(allround),
        "bat_bowl_balance": float(abs(bat_norm - bowl_norm)),
    }
