"""
SQLite database schema creation for IPL prediction.
Creates tables: teams, matches, venues, season_stats, head_to_head.
"""

import os

from config import get_tournament_paths

CREATE_TABLES_SQL = """
-- Teams master table
CREATE TABLE IF NOT EXISTS teams (
    team_id     TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    home_venue  TEXT,
    titles      INTEGER DEFAULT 0,
    founded     INTEGER,
    active      INTEGER DEFAULT 1
);

-- Venues table
CREATE TABLE IF NOT EXISTS venues (
    venue_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    city        TEXT,
    country     TEXT DEFAULT 'India',
    capacity    INTEGER
);

-- Matches table
CREATE TABLE IF NOT EXISTS matches (
    match_id        INTEGER PRIMARY KEY,
    season          INTEGER NOT NULL,
    team1           TEXT NOT NULL,
    team2           TEXT NOT NULL,
    toss_winner     TEXT,
    toss_decision   TEXT,
    winner          TEXT,
    win_by_runs     INTEGER DEFAULT 0,
    win_by_wickets  INTEGER DEFAULT 0,
    venue           TEXT,
    is_playoff      INTEGER DEFAULT 0,
    is_final        INTEGER DEFAULT 0,
    FOREIGN KEY (team1)   REFERENCES teams(team_id),
    FOREIGN KEY (team2)   REFERENCES teams(team_id),
    FOREIGN KEY (winner)  REFERENCES teams(team_id)
);

-- Season standings summary
CREATE TABLE IF NOT EXISTS season_stats (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    season          INTEGER NOT NULL,
    team            TEXT NOT NULL,
    matches_played  INTEGER DEFAULT 0,
    wins            INTEGER DEFAULT 0,
    losses          INTEGER DEFAULT 0,
    points          INTEGER DEFAULT 0,
    nrr             REAL DEFAULT 0.0,
    reached_playoff INTEGER DEFAULT 0,
    reached_final   INTEGER DEFAULT 0,
    won_title       INTEGER DEFAULT 0,
    UNIQUE(season, team),
    FOREIGN KEY (team) REFERENCES teams(team_id)
);

-- Head-to-head records
CREATE TABLE IF NOT EXISTS head_to_head (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    team_a      TEXT NOT NULL,
    team_b      TEXT NOT NULL,
    season      INTEGER NOT NULL,
    wins_a      INTEGER DEFAULT 0,
    wins_b      INTEGER DEFAULT 0,
    UNIQUE(team_a, team_b, season),
    FOREIGN KEY (team_a) REFERENCES teams(team_id),
    FOREIGN KEY (team_b) REFERENCES teams(team_id)
);

-- Player stats per season
CREATE TABLE IF NOT EXISTS player_stats (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    season          INTEGER NOT NULL,
    player_name     TEXT NOT NULL,
    team            TEXT NOT NULL,
    role            TEXT,
    batting_avg     REAL DEFAULT 0.0,
    batting_sr      REAL DEFAULT 0.0,
    runs_scored     INTEGER DEFAULT 0,
    wickets         INTEGER DEFAULT 0,
    bowling_avg     REAL DEFAULT 0.0,
    economy         REAL DEFAULT 0.0,
    UNIQUE(season, player_name)
);
"""

INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_matches_season  ON matches(season);
CREATE INDEX IF NOT EXISTS idx_matches_team1   ON matches(team1);
CREATE INDEX IF NOT EXISTS idx_matches_team2   ON matches(team2);
CREATE INDEX IF NOT EXISTS idx_matches_winner  ON matches(winner);
CREATE INDEX IF NOT EXISTS idx_season_stats_season ON season_stats(season);
CREATE INDEX IF NOT EXISTS idx_season_stats_team   ON season_stats(team);
"""


from sqlalchemy import text

from config import DB_ENGINE
from src.data.db_utils import get_engine


def get_schema_sql():
    if DB_ENGINE == "postgres":
        # PostgreSQL specific adjustments
        return (
            CREATE_TABLES_SQL.replace("AUTOINCREMENT", "")
            .replace("REAL", "DOUBLE PRECISION")
            .replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")
        )
    return CREATE_TABLES_SQL


def setup_database(db_path: str):
    if DB_ENGINE == "sqlite":
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    engine = get_engine(db_path)
    try:
        with engine.begin() as conn:
            schema = get_schema_sql()

            # Execute individual statements for compatibility
            for statement in schema.split(";"):
                if statement.strip():
                    conn.execute(text(statement))

            for statement in INDEXES_SQL.split(";"):
                if statement.strip():
                    conn.execute(text(statement))

        print(f"Database initialized using {DB_ENGINE} engine.")
    except Exception as e:
        print(f"Error setting up database: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tournament", default="ipl")
    args = parser.parse_args()
    paths = get_tournament_paths(args.tournament)
    setup_database(paths["db"])
