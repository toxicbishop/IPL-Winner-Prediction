import logging
import subprocess
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.api import schemas, service
from src.middleware.api_key import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])
logger = logging.getLogger("ipl.api.routes")

# ---------------------------------------------------------------------------
# Reusable parameter types with validation
# ---------------------------------------------------------------------------
TournamentParam = Annotated[
    str,
    Query(
        min_length=2,
        max_length=10,
        pattern=r"^[a-z]+$",
        description="Tournament identifier (e.g. 'ipl')",
    ),
]
TeamIdParam = Annotated[
    str,
    Path(
        min_length=1,
        max_length=10,
        pattern=r"^[a-z0-9]+$",
        description="Team short-code (lowercase)",
    ),
]
PlayerIdParam = Annotated[
    str,
    Path(
        min_length=1,
        max_length=10,
        pattern=r"^[a-z0-9]+$",
        description="Player identifier",
    ),
]
YearParam = Annotated[
    str,
    Path(
        min_length=4,
        max_length=4,
        pattern=r"^\d{4}$",
        description="Season year (e.g. '2026')",
    ),
]
ModelNameParam = Annotated[
    str,
    Path(
        min_length=1,
        max_length=30,
        pattern=r"^[a-z0-9_]+$",
        description="ML model name (e.g. 'ensemble')",
    ),
]
TeamQueryParam = Annotated[
    str,
    Query(
        min_length=1,
        max_length=10,
        pattern=r"^[A-Za-z]+$",
        description="Team short-code",
    ),
]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/winner-probabilities")
def get_winner_probs(tournament: TournamentParam = "ipl"):
    try:
        return service.get_winner_probabilities(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/model-performance")
def get_model_stats(tournament: TournamentParam = "ipl"):
    try:
        return service.get_model_performance(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/match-fixtures")
def get_match_fixtures(tournament: TournamentParam = "ipl"):
    try:
        return service.get_match_fixtures(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/shap-importance/{model_name}")
def get_shap_importance(model_name: ModelNameParam, tournament: TournamentParam = "ipl"):
    try:
        return service.get_shap_importance(model_name, tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/intelligence")
def get_intelligence(tournament: TournamentParam = "ipl"):
    try:
        return service.get_intelligence(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/simulate-h2h")
def simulate_h2h(team1: TeamQueryParam, team2: TeamQueryParam, tournament: TournamentParam = "ipl"):
    try:
        return service.simulate_h2h(team1, team2, tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Failed to simulate h2h")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/trigger-pipeline", response_model=schemas.TriggerPipelineResponse)
def trigger_pipeline():
    try:
        return service.trigger_pipeline()
    except subprocess.TimeoutExpired:
        logger.error("Pipeline timed out")
        raise HTTPException(status_code=504, detail="Pipeline timed out.") from None
    except FileNotFoundError as e:
        logger.exception("Pipeline executable not found")
        raise HTTPException(status_code=500, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/team-logos")
def get_team_logos():
    return service.get_team_logos()


@router.get("/metrics/summary")
def get_metrics_summary(tournament: TournamentParam = "ipl"):
    try:
        return service.get_metrics_summary(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/predictions/win-probability")
def get_predictions_win_probability(tournament: TournamentParam = "ipl"):
    try:
        return service.get_predictions_win_prob(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/features/importance")
def get_features_importance(tournament: TournamentParam = "ipl"):
    try:
        return service.get_features_importance(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/insights/qualitative")
def get_insights_qualitative(tournament: TournamentParam = "ipl"):
    try:
        return service.get_insights_qualitative(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/matches/upcoming")
def get_matches_upcoming(tournament: TournamentParam = "ipl"):
    try:
        return service.get_matches_upcoming(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/teams")
def get_teams(tournament: TournamentParam = "ipl"):
    try:
        return service.get_teams(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/teams/{team_id}")
def get_team_detail(team_id: TeamIdParam, tournament: TournamentParam = "ipl"):
    try:
        return service.get_team_detail(team_id, tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/players")
def get_players(tournament: TournamentParam = "ipl"):
    try:
        return service.get_players(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/players/{player_id}")
def get_player_detail(player_id: PlayerIdParam, tournament: TournamentParam = "ipl"):
    try:
        return service.get_player_detail(player_id, tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/seasons")
def get_seasons(tournament: TournamentParam = "ipl"):
    try:
        return service.get_seasons(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/seasons/{year}")
def get_season_detail(year: YearParam, tournament: TournamentParam = "ipl"):
    try:
        return service.get_season_detail(year, tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/points-table")
def get_points_table(tournament: TournamentParam = "ipl"):
    try:
        return service.get_points_table(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
