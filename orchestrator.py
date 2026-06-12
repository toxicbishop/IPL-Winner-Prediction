"""
Pipeline orchestration using Prefect for IPL 2026 Winner Prediction.
Replaces manual rebuild_all.py scripts.
"""

import os
import sys

from prefect import flow, task

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import mode_predict, mode_setup, mode_train, mode_visualize


@task(name="Data Setup", log_prints=True)
def run_setup_task():
    mode_setup()


@task(name="Model Training", log_prints=True)
def run_train_task():
    mode_train()


@task(name="Winning Prediction", log_prints=True)
def run_predict_task():
    mode_predict()


@task(name="Visualization", log_prints=True)
def run_visualize_task():
    mode_visualize()


@flow(name="IPL 2026 Prediction Pipeline")
def ipl_prediction_pipeline():
    run_setup_task()
    run_train_task()
    run_predict_task()
    try:
        run_visualize_task()
    except Exception as e:
        print(f"Visualization failed: {e}")


if __name__ == "__main__":
    ipl_prediction_pipeline()
