"""Build data/rosters_2026.json from each team's 2025 Cricsheet appearances.

Proxy: top 15 players per team by matches played in 2025, combining batters and
bowlers. Editable by hand after generation to reflect auction/retention moves.
"""

import json
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import ACTIVE_TEAMS_2026, TEAM_ALIASES

ROOT = Path(__file__).resolve().parent.parent
BBB_CSV = ROOT / "data" / "mock" / "IPL.csv"
OUT_PATH = ROOT / "data" / "rosters_2026.json"

SQUAD_SIZE = 15


def main() -> None:
    df = pd.read_csv(
        BBB_CSV,
        low_memory=False,
        usecols=["match_id", "season", "batting_team", "bowling_team", "batter", "bowler"],
    )
    df["season_y"] = df["season"].astype(str).str[-4:]
    df = df[df["season_y"] == "2025"]

    bat = df[["match_id", "batting_team", "batter"]].rename(
        columns={"batting_team": "team", "batter": "player"}
    )
    bowl = df[["match_id", "bowling_team", "bowler"]].rename(
        columns={"bowling_team": "team", "bowler": "player"}
    )
    appearances = pd.concat([bat, bowl], ignore_index=True).dropna()
    appearances["team_abbr"] = appearances["team"].map(TEAM_ALIASES).fillna(appearances["team"])
    matches_per_player = (
        appearances.groupby(["team_abbr", "player"])["match_id"].nunique().reset_index()
    )

    rosters = {}
    for team in ACTIVE_TEAMS_2026:
        top = (
            matches_per_player[matches_per_player["team_abbr"] == team]
            .sort_values("match_id", ascending=False)
            .head(SQUAD_SIZE)
        )
        rosters[team] = top["player"].tolist()

    out = {
        "_meta": {
            "description": "Projected 2026 IPL squads used by player-based team strength.",
            "source": "Top 15 players per team by 2025 Cricsheet appearances.",
            "squad_size": SQUAD_SIZE,
            "note": "Edit by hand to reflect auction trades and retentions.",
        },
        "rosters": rosters,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"Wrote {OUT_PATH}")
    for team, players in rosters.items():
        print(f"  {team}: {len(players)} players")


if __name__ == "__main__":
    main()
