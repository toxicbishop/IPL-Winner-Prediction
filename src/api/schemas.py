from typing import Any

from pydantic import BaseModel


class WinnerProbabilityResponse(BaseModel):
    team: str
    probability: float


class ModelStatsResponse(BaseModel):
    model: str
    accuracy: float
    log_loss: float


class MatchFixtureResponse(BaseModel):
    date: str
    team1: str
    team2: str
    venue: str


class IntelligenceResponse(BaseModel):
    squad_strength: dict[str, Any]
    playoff_rate: dict[str, Any]
    form_score: dict[str, Any]


class SimulateH2HRequest(BaseModel):
    team1: str
    team2: str
    tournament: str = "ipl"


class TriggerPipelineResponse(BaseModel):
    status: str
    message: str
