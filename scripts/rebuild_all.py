import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import TOURNAMENTS, get_tournament_paths
from src.data.db_setup import setup_database
from src.data.ingest import run_ingestion as run_db_ingest
from src.data.preprocess import run_preprocessing
from src.features.engineer import run_feature_engineering
from src.models.trainer import run_training
from src.prediction.explainability import run_explainability
from src.prediction.predict_2026 import predict_2026_winner, save_predictions


def rebuild(tournament: str):
    print(f"\n\n{'#' * 80}")
    print(f"### REBUILDING TOURNAMENT: {tournament.upper()}")
    print(f"{'#' * 80}")

    paths = get_tournament_paths(tournament)

    # 1. Raw Extract (already done by create_dataset.run_ingestion() which handles all)
    # But for safety, we'll assume matches.csv exists now.

    # 2. Database Setup
    setup_database(paths["db"])

    # 3. Database Ingestion
    run_db_ingest(tournament)

    # 4. Preprocessing
    run_preprocessing(tournament)

    # 5. Feature Engineering
    run_feature_engineering(tournament)

    # 6. Model Training
    run_training(tournament)

    # 7. Prediction
    rankings, fixtures = predict_2026_winner(tournament)
    save_predictions(rankings, fixtures, tournament)

    # 8. Explainability (SHAP values)
    run_explainability(model_name="xgboost", tournament=tournament)

    print(f"\n[OK] SUCCESSFULLY REBUILT {tournament.upper()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--tournament", default="ipl")
    args = parser.parse_args()

    if args.all:
        for t in TOURNAMENTS.keys():
            rebuild(t)
    else:
        rebuild(args.tournament)
