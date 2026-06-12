"""
IPL 2026 Winner Prediction - Main Entry Point

Uses REAL IPL ball-by-ball data (IPL.csv, 2008-2025, 1169 matches).

Usage:
  python main.py --mode setup      # Extract data from IPL.csv and engineer features
  python main.py --mode train      # Train all models
  python main.py --mode predict    # Predict 2026 winner
  python main.py --mode all        # Run full pipeline end-to-end
  python main.py --mode visualize  # Generate charts (needs predict to run first)
"""

import argparse
import logging
import sys
import time

from config import LOG_FILE, LOG_LEVEL

# Logging setup
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode="a"),
    ],
)
logger = logging.getLogger(__name__)


def mode_setup():
    logger.info("=== SETUP: Extracting real IPL data and building features ===")
    t0 = time.time()

    from config import TOURNAMENTS, get_tournament_paths
    from src.data.create_dataset import run_ingestion as run_create_dataset
    from src.data.db_setup import setup_database
    from src.data.ingest import run_ingestion as run_db_ingestion
    from src.data.preprocess import run_preprocessing
    from src.features.engineer import run_feature_engineering

    logger.info("Step 1/5: Extracting match data from raw JSONs...")
    run_create_dataset()

    for tournament in TOURNAMENTS.keys():
        logger.info(f"--- Processing tournament: {tournament} ---")
        paths = get_tournament_paths(tournament)

        logger.info("Step 2/5: Creating SQLite database schema...")
        setup_database(paths["db"])

        logger.info("Step 3/5: Ingesting data into SQLite...")
        run_db_ingestion(tournament)

        logger.info("Step 4/5: Preprocessing matches...")
        run_preprocessing(tournament)

        logger.info("Step 5/5: Engineering features...")
        run_feature_engineering(tournament)

    logger.info(f"Setup complete in {time.time() - t0:.1f}s")


def mode_train(sanity_check: bool = False):
    logger.info("=== TRAIN: Training all models ===")
    t0 = time.time()

    from src.models.trainer import run_training

    results = run_training(sanity_check=sanity_check)

    logger.info(f"Training complete in {time.time() - t0:.1f}s")
    return results


def mode_predict():
    logger.info("=== PREDICT: IPL 2026 Winner Prediction ===")
    t0 = time.time()

    from src.prediction.predict_2026 import (
        predict_2026_winner,
        print_predictions,
        save_predictions,
    )

    rankings, fixtures = predict_2026_winner()
    print_predictions(rankings)
    save_predictions(rankings, fixtures)

    logger.info(f"Prediction complete in {time.time() - t0:.1f}s")
    return rankings


def mode_visualize():
    logger.info("=== VISUALIZE: Generating charts and SHAP explainability ===")
    from src.prediction.explainability import run_explainability
    from src.prediction.visualize import generate_all_charts

    generate_all_charts()

    # Explain why our top models make their predictions
    for model in ["xgboost", "lightgbm", "extra_trees"]:
        try:
            run_explainability(model)
        except Exception as e:
            logger.warning(f"SHAP explanation for {model} failed: {e}")


def mode_all(sanity_check: bool = False):
    mode_setup()
    mode_train(sanity_check=sanity_check)
    rankings = mode_predict()
    try:
        mode_visualize()
    except Exception as e:
        logger.warning(f"Visualization failed (non-critical): {e}")
    return rankings


def parse_args():
    parser = argparse.ArgumentParser(
        description="IPL 2026 Winner Prediction (Real Data)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--mode",
        choices=["setup", "train", "predict", "visualize", "all"],
        default="all",
        help="Pipeline mode to run (default: all)",
    )
    parser.add_argument(
        "--sanity-check",
        action="store_true",
        help="Run feature ablation sanity check after training",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logger.info(f"Starting IPL 2026 prediction pipeline | mode={args.mode}")

    if args.mode == "setup":
        mode_setup()
    elif args.mode == "train":
        mode_train(sanity_check=args.sanity_check)
    elif args.mode == "predict":
        mode_predict()
    elif args.mode == "visualize":
        mode_visualize()
    elif args.mode == "all":
        mode_all(sanity_check=args.sanity_check)
