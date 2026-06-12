"""Rebuild non-Cricsheet data from Cricsheet sources where possible.

Produces:
  1. data/mock/IPL.csv         -- real ball-by-ball (replaces the synthetic mock).
  2. data/priors_2026.json     -- recomputes playoff_rate_3yr and
                                  season_2025_rank_score from real results.
                                  squad_strength_2026 is preserved (subjective,
                                  not derivable from Cricsheet).

data/mock/ipl-2026-UTC.csv is left alone (future fixture list; Cricsheet only
publishes played matches).
"""

import json
from glob import glob
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "data" / "raw_datasets" / "ipl"
OUT_CSV = ROOT / "data" / "mock" / "IPL.csv"
MATCHES_CSV = ROOT / "data" / "processed" / "ipl" / "matches.csv"
PRIORS_PATH = ROOT / "data" / "priors_2026.json"

BBB_COLUMNS = [
    "match_id",
    "season",
    "year",
    "date",
    "team1",
    "team2",
    "innings",
    "batting_team",
    "bowling_team",
    "batter",
    "bowler",
    "runs_batter",
    "runs_bowler",
    "runs_total",
    "ball_id",
    "balls_faced",
    "valid_ball",
    "bowler_wicket",
    "player_out",
    "match_won_by",
    "win_outcome",
    "toss_winner",
    "toss_decision",
    "venue",
    "city",
    "result_type",
    "stage",
]


def _parse_match(file_path: Path) -> list[dict]:
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    info = data.get("info", {})
    teams = info.get("teams", []) or []
    if len(teams) < 2:
        return []
    match_id = file_path.stem
    season = str(info.get("season", "Unknown"))
    dates = info.get("dates", [""])
    date_str = dates[0] if dates else ""
    year = int(date_str[:4]) if date_str[:4].isdigit() else 0
    venue = info.get("venue", "Unknown")
    city = info.get("city", "Unknown")
    toss = info.get("toss", {})
    toss_winner = toss.get("winner", "Unknown")
    toss_decision = toss.get("decision", "Unknown")
    outcome = info.get("outcome", {})
    match_won_by = outcome.get("winner", "Unknown")
    win_outcome = ""
    by = outcome.get("by", {})
    if "runs" in by:
        win_outcome = f"{by['runs']} runs"
    elif "wickets" in by:
        win_outcome = f"{by['wickets']} wickets"
    result_type = outcome.get("result", "")
    stage = info.get("event", {}).get("stage", "League")

    # Cricsheet records the batting team in each innings; derive the batting-first team
    innings_list = data.get("innings", [])
    if not innings_list:
        return []
    team1 = innings_list[0].get("team", teams[0])
    team2 = teams[1] if teams[0] == team1 else teams[0]

    rows = []
    ball_id = 0
    for inn_idx, innings in enumerate(innings_list, start=1):
        batting_team = innings.get("team")
        bowling_team = teams[1] if teams[0] == batting_team else teams[0]
        for over_data in innings.get("overs", []):
            for d in over_data.get("deliveries", []):
                ball_id += 1
                runs = d.get("runs", {}) or {}
                extras = d.get("extras", {}) or {}
                wickets = d.get("wickets", []) or []
                legbyes = extras.get("legbyes", 0)
                byes = extras.get("byes", 0)
                is_wide = bool(extras.get("wides"))
                is_noball = bool(extras.get("noballs"))
                player_out = wickets[0].get("player_out", "") if wickets else ""
                wicket_kind = wickets[0].get("kind", "") if wickets else ""
                rows.append(
                    {
                        "match_id": match_id,
                        "season": season,
                        "year": year,
                        "date": date_str,
                        "team1": team1,
                        "team2": team2,
                        "innings": inn_idx,
                        "batting_team": batting_team,
                        "bowling_team": bowling_team,
                        "batter": d.get("batter"),
                        "bowler": d.get("bowler"),
                        "runs_batter": runs.get("batter", 0),
                        "runs_bowler": runs.get("total", 0) - legbyes - byes,
                        "runs_total": runs.get("total", 0),
                        "ball_id": ball_id,
                        "balls_faced": 0 if is_wide else 1,
                        "valid_ball": 0 if (is_wide or is_noball) else 1,
                        "bowler_wicket": 1
                        if (
                            wickets
                            and wicket_kind
                            not in ("run out", "retired hurt", "obstructing the field")
                        )
                        else 0,
                        "player_out": player_out,
                        "match_won_by": match_won_by,
                        "win_outcome": win_outcome,
                        "toss_winner": toss_winner,
                        "toss_decision": toss_decision,
                        "venue": venue,
                        "city": city,
                        "result_type": result_type,
                        "stage": stage,
                    }
                )
    return rows


def rebuild_ipl_csv() -> None:
    files = sorted(glob(str(JSON_DIR / "*.json")))
    print(f"Parsing {len(files)} Cricsheet match JSONs...")
    all_rows: list[dict] = []
    for i, fp in enumerate(files, start=1):
        all_rows.extend(_parse_match(Path(fp)))
        if i % 200 == 0:
            print(f"  ...{i}/{len(files)}")
    df = pd.DataFrame(all_rows, columns=BBB_COLUMNS)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"Wrote {len(df):,} ball rows across {df['match_id'].nunique()} matches -> {OUT_CSV}")


def _compute_playoff_rate_3yr(matches: pd.DataFrame, seasons: tuple[int, ...]) -> dict[str, float]:
    subset = matches[matches["season"].isin(seasons)]
    playoff = subset[subset["stage"] != "League"]
    teams_by_season = {
        s: set(playoff[playoff["season"] == s]["team1"])
        | set(playoff[playoff["season"] == s]["team2"])
        for s in seasons
    }
    all_teams = sorted(set(matches["team1"]) | set(matches["team2"]))
    return {
        t: round(sum(1 for s in seasons if t in teams_by_season[s]) / len(seasons), 4)
        for t in all_teams
    }


def _compute_season_rank_score(matches: pd.DataFrame, season: int) -> dict[str, int]:
    """1-10 score: 10 = champion, descending by playoff finish then league wins."""
    season_df = matches[matches["season"] == season]
    playoffs = season_df[season_df["stage"] != "League"]
    league = season_df[season_df["stage"] == "League"]

    final = playoffs[playoffs["stage"] == "Final"]
    q2 = playoffs[playoffs["stage"].isin(["Qualifier 2", "Semi Final"])]
    elim = playoffs[playoffs["stage"].isin(["Eliminator", "Elimination Final"])]

    champion = final["winner"].iloc[0] if len(final) else None
    runner_up = None
    if len(final):
        row = final.iloc[0]
        runner_up = row["team1"] if row["winner"] == row["team2"] else row["team2"]
    third = (
        q2[q2["winner"] != q2["team1"]]["team1"].tolist()
        + q2[q2["winner"] != q2["team2"]]["team2"].tolist()
    )
    third = [t for t in third if t not in (champion, runner_up)]
    fourth = (
        elim[elim["winner"] != elim["team1"]]["team1"].tolist()
        + elim[elim["winner"] != elim["team2"]]["team2"].tolist()
    )
    fourth = [t for t in fourth if t not in (champion, runner_up, *third)]

    playoff_ranked = [champion, runner_up] + third[:1] + fourth[:1]
    playoff_ranked = [t for t in playoff_ranked if t]

    wins = {}
    for _, r in league.iterrows():
        for t in (r["team1"], r["team2"]):
            wins.setdefault(t, 0)
        if r["winner"] in (r["team1"], r["team2"]):
            wins[r["winner"]] += 1
    non_playoff = [t for t in wins if t not in playoff_ranked]
    non_playoff.sort(key=lambda t: wins.get(t, 0), reverse=True)

    full_order = playoff_ranked + non_playoff
    score = {}
    for idx, team in enumerate(full_order):
        score[team] = max(1, 10 - idx)
    return score


def rebuild_priors() -> None:
    with open(PRIORS_PATH) as f:
        priors = json.load(f)

    matches = pd.read_csv(MATCHES_CSV)
    active = list(priors["squad_strength_2026"].keys())

    playoff = _compute_playoff_rate_3yr(matches, (2023, 2024, 2025))
    rank = _compute_season_rank_score(matches, 2025)

    priors["playoff_rate_3yr"] = {t: playoff.get(t, 0.0) for t in active}
    priors["season_2025_rank_score"] = {t: rank.get(t, 1) for t in active}
    priors["_meta"]["playoff_rate_3yr_source"] = "Cricsheet (seasons 2023-2025)"
    priors["_meta"]["season_2025_rank_source"] = "Cricsheet 2025 final standings"

    with open(PRIORS_PATH, "w") as f:
        json.dump(priors, f, indent=2)
    print(f"Updated priors -> {PRIORS_PATH}")
    print("  playoff_rate_3yr:", priors["playoff_rate_3yr"])
    print("  season_2025_rank_score:", priors["season_2025_rank_score"])


if __name__ == "__main__":
    rebuild_ipl_csv()
    rebuild_priors()
