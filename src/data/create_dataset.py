"""
Extracts match-level summary data from the ball-by-ball IPL.csv or JSON dataset.

Produces:
  - data/raw/matches.csv
  - data/raw/teams.json
  - data/raw/player_stats.csv
"""

import glob
import json
import os
import re

import numpy as np
import pandas as pd

# Default seasonal mapping (extends as needed)
SEASON_TO_YEAR = {
    "2007/08": 2008,
    "2008": 2008,
    "2009": 2009,
    "2009/10": 2010,
    "2010": 2010,
    "2011": 2011,
    "2012": 2012,
    "2013": 2013,
    "2014": 2014,
    "2015": 2015,
    "2016": 2016,
    "2017": 2017,
    "2018": 2018,
    "2019": 2019,
    "2020/21": 2020,
    "2020": 2020,
    "2021": 2021,
    "2022": 2022,
    "2023": 2023,
    "2024": 2024,
    "2025": 2025,
}

from config import TEAM_ALIASES, TOURNAMENTS


def normalize_team(name: str) -> str:
    """Map full team name to abbreviation."""
    return TEAM_ALIASES.get(name, name)


def parse_win_outcome(outcome: str):
    """Parse '33 runs' or '5 wickets' into (win_by_runs, win_by_wickets)."""
    if pd.isna(outcome) or not isinstance(outcome, str):
        return 0, 0
    m = re.search(r"(\d+)\s+runs", outcome)
    if m:
        return int(m.group(1)), 0
    m = re.search(r"(\d+)\s+wickets?", outcome)
    if m:
        return 0, int(m.group(1))
    return 0, 0


def extract_matches(df: pd.DataFrame) -> pd.DataFrame:
    """Extract match-level summary from ball-by-ball data."""
    # Get team1 (batting first) and team2 from first innings
    innings1 = (
        df[df["innings"] == 1]
        .groupby("match_id")
        .agg(
            team1=("batting_team", "first"),
            team2=("bowling_team", "first"),
        )
        .reset_index()
    )

    # Get match-level metadata (one row per match)
    match_meta = (
        df.groupby("match_id")
        .agg(
            date=("date", "first"),
            season=("season", "first"),
            year=("year", "first"),
            match_won_by=("match_won_by", "first"),
            win_outcome=("win_outcome", "first"),
            toss_winner=("toss_winner", "first"),
            toss_decision=("toss_decision", "first"),
            venue=("venue", "first"),
            city=("city", "first"),
            result_type=("result_type", "first"),
            stage=("stage", "first"),
        )
        .reset_index()
    )

    matches = innings1.merge(match_meta, on="match_id")

    # Filter out no-results and ties with unknown winner
    matches = matches[matches["match_won_by"] != "Unknown"].copy()
    matches = matches[
        matches["result_type"].isin([None, "None", "nan", "tie", np.nan])
        | matches["result_type"].isna()
    ].copy()

    # Parse win margin
    parsed = matches["win_outcome"].apply(parse_win_outcome)
    matches["win_by_runs"] = parsed.apply(lambda x: x[0])
    matches["win_by_wickets"] = parsed.apply(lambda x: x[1])

    # Map season to integer year
    matches["season_year"] = matches["season"].map(SEASON_TO_YEAR)
    matches["season_year"] = matches["season_year"].fillna(matches["year"]).astype(int)

    # Normalize team names to abbreviations
    matches["team1"] = matches["team1"].apply(normalize_team)
    matches["team2"] = matches["team2"].apply(normalize_team)
    matches["winner"] = matches["match_won_by"].apply(normalize_team)
    matches["toss_winner"] = matches["toss_winner"].apply(normalize_team)

    # Sort by date
    matches = matches.sort_values(["season_year", "date", "match_id"]).reset_index(drop=True)
    matches["id"] = range(1, len(matches) + 1)

    result = matches[
        [
            "match_id",
            "date",
            "season_year",
            "team1",
            "team2",
            "toss_winner",
            "toss_decision",
            "winner",
            "win_by_runs",
            "win_by_wickets",
            "venue",
            "city",
            "stage",
        ]
    ].copy()
    result.columns = [
        "match_id",
        "date",
        "season",
        "team1",
        "team2",
        "toss_winner",
        "toss_decision",
        "winner",
        "win_by_runs",
        "win_by_wickets",
        "venue",
        "city",
        "stage",
    ]
    return result


def extract_player_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Extract per-season player batting and bowling stats from ball-by-ball data."""
    df = df.copy()
    df["season_year"] = df["season"].map(SEASON_TO_YEAR)
    df["season_year"] = df["season_year"].fillna(df["year"]).astype(int)

    # --- Batting stats ---
    batter_runs = (
        df.groupby(["season_year", "batter", "batting_team"])
        .agg(
            runs_scored=("runs_batter", "sum"),
            balls_faced=("balls_faced", "sum"),
        )
        .reset_index()
    )

    # Dismissals
    dismissed = df[df["player_out"].notna() & (df["player_out"] != "")]
    dismissals = (
        dismissed.groupby(["season_year", "player_out"]).size().reset_index(name="dismissals")
    )

    batter_runs = batter_runs.merge(
        dismissals,
        left_on=["season_year", "batter"],
        right_on=["season_year", "player_out"],
        how="left",
    )
    batter_runs["dismissals"] = batter_runs["dismissals"].fillna(0).astype(int)
    batter_runs["batting_avg"] = batter_runs["runs_scored"] / batter_runs["dismissals"].clip(
        lower=1
    )
    batter_runs["batting_sr"] = (
        batter_runs["runs_scored"] / batter_runs["balls_faced"].clip(lower=1)
    ) * 100

    # --- Bowling stats ---
    valid_balls = df[df["valid_ball"] == 1]
    bowler_stats = (
        valid_balls.groupby(["season_year", "bowler", "bowling_team"])
        .agg(
            runs_conceded=("runs_bowler", "sum"),
            balls_bowled=("valid_ball", "sum"),
            wickets=("bowler_wicket", "sum"),
        )
        .reset_index()
    )
    bowler_stats["economy"] = bowler_stats["runs_conceded"] / (
        bowler_stats["balls_bowled"] / 6
    ).clip(lower=1)
    bowler_stats["bowling_avg"] = bowler_stats["runs_conceded"] / bowler_stats["wickets"].clip(
        lower=1
    )

    # --- Combine into player stats ---
    bat = batter_runs[batter_runs["runs_scored"] >= 50].copy()
    bat["team"] = bat["batting_team"].apply(normalize_team)
    bat["player_name"] = bat["batter"]
    bat = bat[
        [
            "season_year",
            "player_name",
            "team",
            "runs_scored",
            "balls_faced",
            "dismissals",
            "batting_avg",
            "batting_sr",
        ]
    ].copy()

    bowl = bowler_stats[bowler_stats["wickets"] >= 3].copy()
    bowl["team"] = bowl["bowling_team"].apply(normalize_team)
    bowl["player_name"] = bowl["bowler"]
    bowl = bowl[
        [
            "season_year",
            "player_name",
            "team",
            "runs_conceded",
            "balls_bowled",
            "wickets",
            "economy",
            "bowling_avg",
        ]
    ].copy()

    combined = bat.merge(
        bowl[["season_year", "player_name", "wickets", "economy", "bowling_avg"]],
        on=["season_year", "player_name"],
        how="outer",
    )
    for col in [
        "runs_scored",
        "batting_avg",
        "batting_sr",
        "balls_faced",
        "dismissals",
        "wickets",
        "economy",
        "bowling_avg",
    ]:
        if col in combined.columns:
            combined[col] = (
                combined[col]
                .fillna(0)
                .astype(float if "avg" in col or "sr" in col or "economy" in col else int)
            )

    bowl_teams = bowl.set_index(["season_year", "player_name"])["team"]
    mask = combined["team"].isna()
    for idx in combined[mask].index:
        key = (combined.loc[idx, "season_year"], combined.loc[idx, "player_name"])
        if key in bowl_teams.index:
            combined.loc[idx, "team"] = bowl_teams.loc[key]

    def assign_role(row):
        return (
            "All"
            if row["runs_scored"] >= 50 and row["wickets"] >= 3
            else "Bowl"
            if row["wickets"] >= 3
            else "Bat"
        )

    combined["role"] = combined.apply(assign_role, axis=1)
    combined = combined.rename(columns={"season_year": "season"})

    return combined[
        [
            "season",
            "player_name",
            "team",
            "role",
            "batting_avg",
            "batting_sr",
            "runs_scored",
            "wickets",
            "bowling_avg",
            "economy",
        ]
    ]


def save_matches_csv(matches_df: pd.DataFrame, tournament: str):
    t_config = TOURNAMENTS[tournament]
    os.makedirs(t_config["processed_dir"], exist_ok=True)
    path = os.path.join(t_config["processed_dir"], "matches.csv")
    matches_df.to_csv(path, index=False)
    print(f"[{tournament}] Saved {len(matches_df)} matches -> {path}")


def save_player_stats_csv(player_stats_df: pd.DataFrame, tournament: str):
    t_config = TOURNAMENTS[tournament]
    os.makedirs(t_config["processed_dir"], exist_ok=True)
    path = os.path.join(t_config["processed_dir"], "player_stats.csv")
    player_stats_df.to_csv(path, index=False)
    print(f"[{tournament}] Saved {len(player_stats_df)} player records -> {path}")


def _to_legacy_match_rows(matches_df: pd.DataFrame) -> list:
    cols = [
        "season",
        "team1",
        "team2",
        "winner",
        "venue",
        "toss_winner",
        "toss_decision",
        "win_by_runs",
        "win_by_wickets",
    ]
    return [tuple(row[c] for c in cols) for _, row in matches_df.iterrows()]


def parse_cricsheet_json(file_path):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    match_id = os.path.basename(file_path).replace(".json", "")
    info = data.get("info", {})
    season = str(info.get("season", "Unknown"))
    year = int(info.get("dates", ["0000"])[0][:4])
    venue = info.get("venue", "Unknown")
    city = info.get("city", "Unknown")
    toss_winner = info.get("toss", {}).get("winner", "Unknown")
    toss_decision = info.get("toss", {}).get("decision", "Unknown")
    outcome = info.get("outcome", {})
    winner = outcome.get("winner", "Unknown")
    win_outcome = ""
    if "by" in outcome:
        by = outcome["by"]
        if "runs" in by:
            win_outcome = f"{by['runs']} runs"
        elif "wickets" in by:
            win_outcome = f"{by['wickets']} wickets"
    result_type = outcome.get("result", np.nan)
    stage = info.get("event", {}).get("stage", "League")
    rows = []
    for inn_idx, innings in enumerate(data.get("innings", [])):
        inn_num = inn_idx + 1
        batting_team = innings.get("team")
        teams = info.get("teams", [])
        bowling_team = (
            teams[1] if teams[0] == batting_team else teams[0] if len(teams) > 1 else "Unknown"
        )
        for over_data in innings.get("overs", []):
            over_num = over_data.get("over")
            for ball_idx, d in enumerate(over_data.get("deliveries", [])):
                runs = d.get("runs", {})
                extras = d.get("extras", {})
                wickets = d.get("wickets", [])
                row = {
                    "match_id": match_id,
                    "season": season,
                    "year": year,
                    "venue": venue,
                    "city": city,
                    "toss_winner": toss_winner,
                    "toss_decision": toss_decision,
                    "match_won_by": winner,
                    "win_outcome": win_outcome,
                    "result_type": result_type,
                    "stage": stage,
                    "date": info.get("dates", [""])[0],
                    "innings": inn_num,
                    "over": over_num,
                    "ball": ball_idx + 1,
                    "batting_team": batting_team,
                    "bowling_team": bowling_team,
                    "batter": d.get("batter"),
                    "bowler": d.get("bowler"),
                    "non_striker": d.get("non_striker"),
                    "runs_batter": runs.get("batter", 0),
                    "runs_extras": runs.get("extras", 0),
                    "runs_total": runs.get("total", 0),
                    "runs_bowler": runs.get("total", 0)
                    - extras.get("legbyes", 0)
                    - extras.get("byes", 0),
                    "player_out": wickets[0].get("player_out", "") if wickets else "",
                    "wicket_kind": wickets[0].get("kind", "") if wickets else "",
                }
                row["valid_ball"] = (
                    1 if not extras.get("wides") and not extras.get("noballs") else 0
                )
                row["balls_faced"] = 1 if not extras.get("wides") else 0
                row["bowler_wicket"] = (
                    1
                    if wickets and wickets[0].get("kind") not in ["run out", "retired hurt"]
                    else 0
                )
                rows.append(row)
    return rows


def load_all_jsons(folder_path):
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    print(f"Found {len(json_files)} JSON match files in {folder_path}")
    all_rows = []
    from tqdm import tqdm

    for f in tqdm(json_files, desc="Parsing JSON matches"):
        all_rows.extend(parse_cricsheet_json(f))
    return pd.DataFrame(all_rows)


def save_ball_by_ball_csv(df: pd.DataFrame, tournament: str):
    t_config = TOURNAMENTS[tournament]
    os.makedirs(t_config["processed_dir"], exist_ok=True)
    path = os.path.join(t_config["processed_dir"], "ball_by_ball.csv")
    # Save a lighter version of the dataframe to save space
    cols = [
        "match_id",
        "season",
        "date",
        "venue",
        "innings",
        "over",
        "ball",
        "batting_team",
        "bowling_team",
        "batter",
        "bowler",
        "runs_batter",
        "runs_extras",
        "runs_total",
        "runs_bowler",
        "player_out",
    ]
    df[cols].to_csv(path, index=False)
    print(f"[{tournament}] Saved {len(df)} deliveries -> {path}")


def build_all_matches(tournament: str = "ipl"):
    t_config = TOURNAMENTS[tournament]
    raw_dir = t_config["raw_dir"]

    if os.path.exists(raw_dir):
        print(f"[{tournament}] Parsing JSON files from {raw_dir}...")
        df = load_all_jsons(raw_dir)
    else:
        raise FileNotFoundError(f"Tournament dir {raw_dir} not found.")

    matches = extract_matches(df)
    player_stats = extract_player_stats(df)
    return matches, player_stats, df


def run_ingestion():
    for tournament in TOURNAMENTS.keys():
        try:
            print(f"Starting ingestion for: {tournament}")
            matches, p_stats, b_df = build_all_matches(tournament)
            save_matches_csv(matches, tournament)
            save_player_stats_csv(p_stats, tournament)
            save_ball_by_ball_csv(b_df, tournament)
        except Exception as e:
            print(f"Failed to ingest {tournament}: {e}")


if __name__ == "__main__":
    run_ingestion()
