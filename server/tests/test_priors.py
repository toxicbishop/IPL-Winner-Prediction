"""Validate data/priors_2026.json structure and content."""

import json
import os

import pytest

PRIORS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "priors_2026.json")

EXPECTED_TEAMS = {"CSK", "MI", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "LSG", "GT"}
REQUIRED_SECTIONS = ("squad_strength_2026", "playoff_rate_3yr", "season_2025_rank_score")


@pytest.fixture(scope="module")
def priors():
    with open(PRIORS_PATH) as f:
        return json.load(f)


@pytest.mark.parametrize("section", REQUIRED_SECTIONS)
def test_priors_has_all_teams(priors, section):
    assert set(priors[section].keys()) == EXPECTED_TEAMS, f"{section} missing or has extra teams"


def test_squad_strength_range(priors):
    for team, val in priors["squad_strength_2026"].items():
        assert 0 <= val <= 10, f"{team}: squad strength {val} out of [0,10]"


def test_playoff_rate_range(priors):
    for team, val in priors["playoff_rate_3yr"].items():
        assert 0 <= val <= 1, f"{team}: playoff rate {val} out of [0,1]"


def test_season_rank_range(priors):
    for team, val in priors["season_2025_rank_score"].items():
        assert 1 <= val <= 10, f"{team}: rank score {val} out of [1,10]"


def test_priors_loader_exposes_dicts():
    from src.prediction.predict import (
        PLAYOFF_RATE_3YR,
        SEASON_2025_RANK_SCORE,
        SQUAD_STRENGTH_2026,
    )

    assert set(SQUAD_STRENGTH_2026.keys()) == EXPECTED_TEAMS
    assert set(PLAYOFF_RATE_3YR.keys()) == EXPECTED_TEAMS
    assert set(SEASON_2025_RANK_SCORE.keys()) == EXPECTED_TEAMS
