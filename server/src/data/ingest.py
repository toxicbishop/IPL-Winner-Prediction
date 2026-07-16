"""
Ingests extracted CSV/JSON data into the SQLite database.
Populates: teams, venues, matches, season_stats, head_to_head, player_stats.

All data comes from the real IPL.csv dataset (extracted by create_dataset.py).
"""

import json
import os
from collections import defaultdict

import pandas as pd
from sqlalchemy import text

from config import TEAM_ALIASES, get_tournament_paths
from src.data.db_utils import execute_upsert, get_engine

# Backward-compatible standings map used by legacy tests.
# Not used by the current ingestion pipeline logic.
SEASON_STANDINGS = {
    2008: [("RR", 1), ("CSK", 2), ("DC_OLD", 3), ("MI", 4)],
    2009: [("DC_OLD", 1), ("RCB", 2), ("CSK", 3), ("MI", 4)],
    2010: [("CSK", 1), ("MI", 2), ("DC_OLD", 3), ("RR", 4)],
    2011: [("CSK", 1), ("RCB", 2), ("MI", 3), ("RR", 4)],
    2012: [("KKR", 1), ("CSK", 2), ("MI", 3), ("RCB", 4)],
    2013: [("MI", 1), ("CSK", 2), ("RR", 3), ("SRH", 4)],
    2014: [("KKR", 1), ("PBKS", 2), ("CSK", 3), ("MI", 4)],
    2015: [("MI", 1), ("CSK", 2), ("RCB", 3), ("RR", 4)],
    2016: [("SRH", 1), ("RCB", 2), ("GT", 3), ("KKR", 4)],
    2017: [("MI", 1), ("RPS", 2), ("KKR", 3), ("SRH", 4)],
    2018: [("CSK", 1), ("SRH", 2), ("KKR", 3), ("RR", 4)],
    2019: [("MI", 1), ("CSK", 2), ("DC", 3), ("SRH", 4)],
    2020: [("MI", 1), ("DC", 2), ("SRH", 3), ("RCB", 4)],
    2021: [("CSK", 1), ("KKR", 2), ("DC", 3), ("RCB", 4)],
    2022: [("GT", 1), ("RR", 2), ("LSG", 3), ("RCB", 4)],
    2023: [("CSK", 1), ("GT", 2), ("MI", 3), ("LSG", 4)],
    2024: [("KKR", 1), ("SRH", 2), ("RR", 3), ("RCB", 4)],
}

# Known venues with capacity (for venue table)
VENUE_INFO = {
    "MA Chidambaram Stadium": ("Chennai", "India", 50000),
    "Wankhede Stadium": ("Mumbai", "India", 33000),
    "M Chinnaswamy Stadium": ("Bengaluru", "India", 40000),
    "Eden Gardens": ("Kolkata", "India", 68000),
    "Arun Jaitley Stadium": ("Delhi", "India", 41820),
    "Feroz Shah Kotla": ("Delhi", "India", 41820),
    "Sawai Mansingh Stadium": ("Jaipur", "India", 30000),
    "Rajiv Gandhi International Cricket Stadium": ("Hyderabad", "India", 55000),
    "Punjab Cricket Association IS Bindra Stadium": ("Mohali", "India", 26950),
    "Punjab Cricket Association Stadium": ("Mohali", "India", 26950),
    "Narendra Modi Stadium": ("Ahmedabad", "India", 132000),
    "DY Patil Stadium": ("Mumbai", "India", 55000),
    "Brabourne Stadium": ("Mumbai", "India", 20000),
    "BRSABV Ekana Cricket Stadium": ("Lucknow", "India", 50000),
    "Maharashtra Cricket Association Stadium": ("Pune", "India", 37406),
    "Himachal Pradesh Cricket Association Stadium": ("Dharamsala", "India", 23000),
    "Saurashtra Cricket Association Stadium": ("Rajkot", "India", 28000),
    "Holkar Cricket Stadium": ("Indore", "India", 30000),
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium": ("Visakhapatnam", "India", 27000),
    "Barabati Stadium": ("Cuttack", "India", 45000),
    "Subrata Roy Sahara Stadium": ("Pune", "India", 37000),
    "Sharjah Cricket Stadium": ("Sharjah", "UAE", 16000),
    "Dubai International Cricket Stadium": ("Dubai", "UAE", 25000),
    "Sheikh Zayed Stadium": ("Abu Dhabi", "UAE", 20000),
    "Newlands": ("Cape Town", "South Africa", 25000),
    "Kingsmead": ("Durban", "South Africa", 25000),
    "New Wanderers Stadium": ("Johannesburg", "South Africa", 34000),
    "SuperSport Park": ("Centurion", "South Africa", 22000),
}


def normalize_team(name: str) -> str:
    if name is None:
        return ""
    clean = str(name).strip()
    return TEAM_ALIASES.get(clean, clean)


def ingest_teams(conn, teams_json_path: str, matches_df: pd.DataFrame, tournament: str):
    count = 0
    if os.path.exists(teams_json_path):
        with open(teams_json_path) as f:
            teams = json.load(f)
        for team_id, info in teams.items():
            execute_upsert(
                conn,
                "teams",
                ["team_id", "name", "home_venue", "titles", "founded", "active"],
                (team_id, info["name"], info["home"], info["titles"], info["founded"], 1),
                conflict_target="team_id",
            )
            count += 1

    # ALWAYS ensure all teams in the matches data are present in the teams table
    all_teams_in_matches = set(matches_df["team1"]) | set(matches_df["team2"])
    for t in all_teams_in_matches:
        if not t or pd.isna(t):
            continue
        # Use execute_upsert with ignore=True so we don't overwrite detailed info from JSON
        execute_upsert(
            conn,
            "teams",
            ["team_id", "name", "home_venue", "titles", "founded", "active"],
            (t, t, "TBD", 0, 1900, 1),
            conflict_target="team_id",
            ignore=True,
        )
        count += 1

    # Add retired franchises (IPL ONLY)
    if tournament == "ipl":
        retired = [
            ("DC_OLD", "Deccan Chargers", "Rajiv Gandhi International Cricket Stadium", 1, 2008),
            ("RPS", "Rising Pune Supergiant", "Maharashtra Cricket Association Stadium", 0, 2016),
            ("KTK", "Kochi Tuskers Kerala", "Jawaharlal Nehru Stadium", 0, 2011),
            ("PW", "Pune Warriors", "Maharashtra Cricket Association Stadium", 0, 2011),
            ("GL", "Gujarat Lions", "Saurashtra Cricket Association Stadium", 0, 2016),
        ]
        for row in retired:
            execute_upsert(
                conn,
                "teams",
                ["team_id", "name", "home_venue", "titles", "founded", "active"],
                row + (0,),
                conflict_target="team_id",
                ignore=True,
            )
            count += 1
    # conn.commit() removed for SQLAlchemy begin() block
    print(f"Teams ingested: {count}")


def ingest_venues(conn, df: pd.DataFrame):
    """Ingest venues from both known list and matches data."""
    # Insert known venues
    for name, (city, country, capacity) in VENUE_INFO.items():
        execute_upsert(
            conn,
            "venues",
            ["name", "city", "country", "capacity"],
            (name, city, country, capacity),
            conflict_target="name",
            ignore=True,
        )

    # conn.commit()
    count = conn.execute(text("SELECT COUNT(*) FROM venues")).fetchone()[0]
    print(f"Venues ingested: {count}")


def ingest_matches(conn, df: pd.DataFrame):

    season_team_wins = defaultdict(lambda: defaultdict(int))
    season_team_matches = defaultdict(lambda: defaultdict(int))

    for _, row in df.iterrows():
        season = int(row["season"])
        t1 = row["team1"]
        t2 = row["team2"]
        winner = row["winner"]
        stage = row.get("stage", "Unknown")
        is_playoff = (
            1
            if stage
            in (
                "Final",
                "Qualifier 1",
                "Qualifier 2",
                "Eliminator",
                "Semi Final",
                "Elimination Final",
            )
            else 0
        )
        is_final = 1 if stage == "Final" else 0

        execute_upsert(
            conn,
            "matches",
            [
                "match_id",
                "season",
                "team1",
                "team2",
                "toss_winner",
                "toss_decision",
                "winner",
                "win_by_runs",
                "win_by_wickets",
                "venue",
                "is_playoff",
                "is_final",
            ],
            (
                int(row["match_id"]),
                season,
                t1,
                t2,
                row["toss_winner"],
                row["toss_decision"],
                winner,
                int(row["win_by_runs"]),
                int(row["win_by_wickets"]),
                row["venue"],
                is_playoff,
                is_final,
            ),
            conflict_target="match_id",
            ignore=True,
        )
        season_team_matches[season][t1] += 1
        season_team_matches[season][t2] += 1
        if pd.notna(winner) and winner:
            season_team_wins[season][winner] += 1

    # conn.commit()

    # Populate season_stats from actual match data
    for season in sorted(season_team_matches.keys()):
        # Find who won the final this season
        final_winner = None
        final_row = df[(df["season"] == season) & (df["stage"] == "Final")]
        if len(final_row) > 0:
            final_winner = final_row.iloc[0]["winner"]

        # Find playoff teams
        playoff_stages = {
            "Final",
            "Qualifier 1",
            "Qualifier 2",
            "Eliminator",
            "Semi Final",
            "Elimination Final",
        }
        playoff_matches = df[(df["season"] == season) & (df["stage"].isin(playoff_stages))]
        playoff_teams = set()
        for _, pm in playoff_matches.iterrows():
            playoff_teams.add(pm["team1"])
            playoff_teams.add(pm["team2"])

        # Find finalists
        final_teams = set()
        for _, fm in final_row.iterrows():
            final_teams.add(fm["team1"])
            final_teams.add(fm["team2"])

        for team in season_team_matches[season]:
            played = season_team_matches[season][team]
            wins = season_team_wins[season].get(team, 0)
            losses = played - wins
            reached_playoff = 1 if team in playoff_teams else 0
            reached_final = 1 if team in final_teams else 0
            won_title = 1 if team == final_winner else 0

            execute_upsert(
                conn,
                "season_stats",
                [
                    "season",
                    "team",
                    "matches_played",
                    "wins",
                    "losses",
                    "points",
                    "reached_playoff",
                    "reached_final",
                    "won_title",
                ],
                (
                    season,
                    team,
                    played,
                    wins,
                    losses,
                    wins * 2,
                    reached_playoff,
                    reached_final,
                    won_title,
                ),
                conflict_target="season, team",
            )

    # conn.commit()
    print(f"Matches ingested: {len(df)}")
    print(f"Season stats populated for {len(season_team_matches)} seasons")


def ingest_head_to_head(conn):
    res = conn.execute(
        text("""
        SELECT season, team1, team2, winner FROM matches ORDER BY season
    """)
    )
    h2h = defaultdict(lambda: defaultdict(lambda: {"wins_a": 0, "wins_b": 0}))
    for season, t1, t2, winner in res.fetchall():
        key = (min(t1, t2), max(t1, t2))
        if winner == key[0]:
            h2h[season][key]["wins_a"] += 1
        elif winner == key[1]:
            h2h[season][key]["wins_b"] += 1

    for season, matches in h2h.items():
        for (ta, tb), rec in matches.items():
            execute_upsert(
                conn,
                "head_to_head",
                ["team_a", "team_b", "season", "wins_a", "wins_b"],
                (ta, tb, season, rec["wins_a"], rec["wins_b"]),
                conflict_target="team_a, team_b, season",
            )
    # conn.commit()
    print(f"Head-to-head records populated for {len(h2h)} seasons")


def ingest_player_stats(conn, player_stats_csv: str):
    """Ingest player stats from the extracted CSV (real ball-by-ball data)."""
    if not os.path.exists(player_stats_csv):
        print(f"Warning: {player_stats_csv} not found, skipping player stats ingestion")
        return

    df = pd.read_csv(player_stats_csv)
    count = 0
    for _, row in df.iterrows():
        execute_upsert(
            conn,
            "player_stats",
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
            ],
            (
                int(row["season"]),
                row["player_name"],
                row["team"],
                row["role"],
                float(row["batting_avg"]),
                float(row["batting_sr"]),
                int(row["runs_scored"]),
                int(row["wickets"]),
                float(row["bowling_avg"]),
                float(row["economy"]),
            ),
            conflict_target="season, player_name",
        )
        count += 1
    # conn.commit()
    print(f"Player stats ingested: {count}")


def run_ingestion(tournament: str = "ipl"):
    paths = get_tournament_paths(tournament)
    engine = get_engine(paths["db"])

    # Load matches DF early to pass to other functions
    df_matches = pd.read_csv(paths["matches"])

    with engine.begin() as conn:
        try:
            # Pass tournament-specific paths
            ingest_teams(
                conn,
                os.path.join(os.path.dirname(paths["matches"]), "..", "..", "raw", "teams.json"),
                df_matches,
                tournament,
            )
            ingest_venues(conn, df_matches)
            ingest_matches(conn, df_matches)
            ingest_head_to_head(conn)
            ingest_player_stats(conn, paths["player_stats"])
            print(f"[{tournament}] All data ingested successfully into {paths['db']}")
        except Exception as e:
            print(f"Error during {tournament} ingestion: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tournament", default="ipl")
    args = parser.parse_args()
    run_ingestion(args.tournament)
