"""
Centralized configuration loader for IPL 2026 Winner Prediction.
Loads from config/*.yaml and maintains backward compatibility.
"""

import os

import yaml

# --- Path Resolution ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")


def load_yaml(filename):
    path = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(path):
        # Fallback if running from root
        path = os.path.join(BASE_DIR, "config", filename)
    with open(path) as f:
        return yaml.safe_load(f)


# Load YAML configs
base_cfg = load_yaml("base.yaml")
model_cfg = load_yaml("model.yaml")
data_cfg = load_yaml("data.yaml")

# --- Export Paths (Backward Compatibility) ---
DATA_DIR = os.path.join(BASE_DIR, base_cfg["paths"]["data_dir"])
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
DB_DIR = os.path.join(DATA_DIR, "db")
OUTPUTS_DIR = os.path.join(BASE_DIR, base_cfg["paths"]["outputs_dir"])
MODELS_DIR = os.path.join(OUTPUTS_DIR, "models")
RESULTS_DIR = os.path.join(OUTPUTS_DIR, "results")
SQLITE_DB_PATH = os.path.join(DB_DIR, "ipl.db")

# --- Tournament Directories ---
TOURNAMENTS = {}
for name, info in data_cfg["tournaments"].items():
    TOURNAMENTS[name] = {
        "raw_dir": os.path.join(DATA_DIR, "raw_datasets", name),
        "processed_dir": os.path.join(PROCESSED_DIR, name),
        "results_dir": os.path.join(RESULTS_DIR, name),
        "models_dir": os.path.join(MODELS_DIR, name),
        "db_name": info["db_name"],
    }


def get_tournament_paths(tournament: str):
    if tournament not in TOURNAMENTS:
        raise ValueError(f"Invalid tournament: {tournament}")
    t = TOURNAMENTS[tournament]
    return {
        "matches": os.path.join(t["processed_dir"], "matches.csv"),
        "player_stats": os.path.join(t["processed_dir"], "player_stats.csv"),
        "ball_by_ball": os.path.join(t["processed_dir"], "ball_by_ball.csv"),
        "features": os.path.join(t["processed_dir"], "features.csv"),
        "team_stats": os.path.join(t["processed_dir"], "team_stats.csv"),
        "db": os.path.join(DB_DIR, t["db_name"]),
        "results": t["results_dir"],
        "models": t["models_dir"],
    }


# Legacy path used by standalone model scripts.
FEATURES_CSV = get_tournament_paths("ipl")["features"]


# --- Data/Team Configs ---
TEAMS = data_cfg["teams"]
TEAM_ALIASES = data_cfg["team_aliases"]
RETIRED_TEAM_MAP = data_cfg["retired_team_map"]
ACTIVE_TEAMS_2026 = list(TEAMS.keys())
ICC_MEN_TEAMS = data_cfg.get("icc_men_teams", {})

# --- Seasons ---
FIRST_SEASON = data_cfg["seasons"]["first"]
LAST_KNOWN_SEASON = data_cfg["seasons"]["last_known"]
PREDICT_SEASON = data_cfg["seasons"]["predict"]

# --- Feature Engineering ---
FE_CFG = data_cfg["feature_engineering"]
FORM_WINDOW = FE_CFG["form_window"]
HOME_ADVANTAGE = FE_CFG["home_advantage"]
TOSS_FEATURES = FE_CFG["toss_features"]
VENUE_FEATURES = FE_CFG["venue_features"]
H2H_WINDOW_SEASONS = FE_CFG["h2h_window_seasons"]

# --- Model Params ---
TRAIN_CFG = model_cfg["training"]
RANDOM_STATE = TRAIN_CFG["random_state"]
TEST_SIZE = TRAIN_CFG["test_size"]
CV_FOLDS = TRAIN_CFG["cv_folds"]
MODEL_PARAMS = model_cfg["model_params"]

# --- Database Config ---
DB_ENGINE = os.environ.get("DB_ENGINE", "sqlite")  # 'sqlite' or 'postgres'
POSTGRES_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "pass": os.environ.get("POSTGRES_PASSWORD", "1234"),
    "db": os.environ.get("POSTGRES_DB", "ipl"),
}

# --- Logging ---
LOG_LEVEL = base_cfg["logging"]["level"]
LOG_FILE = os.path.join(BASE_DIR, base_cfg["logging"]["file"])
