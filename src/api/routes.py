import logging
import subprocess

from fastapi import APIRouter, HTTPException

from src.api import schemas, service

router = APIRouter()
logger = logging.getLogger("ipl.api.routes")


@router.get("/winner-probabilities")
def get_winner_probs(tournament: str = "ipl"):
    try:
        return service.get_winner_probabilities(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/model-performance")
def get_model_stats(tournament: str = "ipl"):
    try:
        return service.get_model_performance(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/match-fixtures")
def get_match_fixtures(tournament: str = "ipl"):
    try:
        return service.get_match_fixtures(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/shap-importance/{model_name}")
def get_shap_importance(model_name: str, tournament: str = "ipl"):
    try:
        return service.get_shap_importance(model_name, tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/intelligence")
def get_intelligence(tournament: str = "ipl"):
    try:
        return service.get_intelligence(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/simulate-h2h")
def simulate_h2h(team1: str, team2: str, tournament: str = "ipl", venue: str = None):
    try:
        return service.simulate_h2h(team1, team2, tournament, venue)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Failed to simulate h2h")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/venues")
def get_venues(tournament: str = "ipl"):
    try:
        return service.get_venues(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


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
def get_metrics_summary(tournament: str = "ipl"):
    try:
        return service.get_metrics_summary(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/predictions/win-probability")
def get_predictions_win_probability(tournament: str = "ipl"):
    try:
        return service.get_predictions_win_prob(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/features/importance")
def get_features_importance(tournament: str = "ipl"):
    try:
        return service.get_features_importance(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/insights/qualitative")
def get_insights_qualitative(tournament: str = "ipl"):
    try:
        return service.get_insights_qualitative(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/matches/upcoming")
def get_matches_upcoming(tournament: str = "ipl"):
    try:
        return service.get_matches_upcoming(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/teams")
def get_teams(tournament: str = "ipl"):
    try:
        return service.get_teams(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/teams/{team_id}")
def get_team_detail(team_id: str, tournament: str = "ipl"):
    try:
        return service.get_team_detail(team_id, tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/players")
def get_players(tournament: str = "ipl"):
    try:
        return service.get_players(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/players/{player_id}")
def get_player_detail(player_id: str, tournament: str = "ipl"):
    try:
        return service.get_player_detail(player_id, tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/seasons")
def get_seasons(tournament: str = "ipl"):
    try:
        return service.get_seasons(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/seasons/{year}")
def get_season_detail(year: str, tournament: str = "ipl"):
    try:
        return service.get_season_detail(year, tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/points-table")
def get_points_table(tournament: str = "ipl"):
    try:
        return service.get_points_table(tournament)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
