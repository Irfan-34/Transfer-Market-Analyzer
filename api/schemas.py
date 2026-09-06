from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class HealthCheckResponse(BaseModel):
    status: str
    database_status: str
    ml_models_loaded: bool
    version: str
    timestamp: datetime


class PlayerSummary(BaseModel):
    player_id: int
    name: str
    position: Optional[str] = None
    sub_position: Optional[str] = None
    age: Optional[int] = None
    country_of_citizenship: Optional[str] = None
    current_club_name: Optional[str] = None
    current_club_domestic_competition_id: Optional[str] = None
    market_value_in_eur: Optional[float] = 0.0
    highest_market_value_in_eur: Optional[float] = 0.0
    image_url: Optional[str] = None


class PlayerProfile(PlayerSummary):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    height_in_cm: Optional[int] = None
    foot: Optional[str] = None
    contract_expiration_date: Optional[str] = None
    agent_name: Optional[str] = None
    international_caps: Optional[int] = 0
    international_goals: Optional[int] = 0
    total_appearances: Optional[int] = 0
    total_goals: Optional[int] = 0
    total_assists: Optional[int] = 0
    total_minutes: Optional[int] = 0


class ClubSummary(BaseModel):
    club_id: str
    name: str
    domestic_competition_id: Optional[str] = None
    total_market_value: Optional[float] = 0.0
    squad_size: Optional[int] = 0
    average_age: Optional[float] = None
    foreigners_percentage: Optional[float] = None
    stadium_name: Optional[str] = None
    stadium_seats: Optional[int] = None
    coach_name: Optional[str] = None


class TransferRecord(BaseModel):
    player_id: int
    player_name: str
    transfer_date: Optional[str] = None
    transfer_season: Optional[str] = None
    from_club_name: Optional[str] = None
    to_club_name: Optional[str] = None
    fee_eur: float = 0.0
    market_value_eur: Optional[float] = 0.0
    position: Optional[str] = None


class RumourResponse(BaseModel):
    id: int
    player_name: str
    from_club_name: Optional[str] = None
    to_club_name: str
    status: str
    source_name: str
    source_url: Optional[str] = None
    published_at: Optional[datetime] = None
    confidence_score: float


class TransferFeePredictionRequest(BaseModel):
    player_id: Optional[int] = None
    player_name: str
    position: str = "Attack"
    age: int = 24
    current_market_value_eur: float = 20000000.0
    selling_club_market_value: float = 100000000.0
    buying_club_market_value: float = 300000000.0


class TransferFeePredictionResponse(BaseModel):
    player_name: str
    expected_fee_eur: float
    fee_range_low_eur: float
    fee_range_high_eur: float
    confidence: str


class TransferProbPredictionRequest(BaseModel):
    player_name: str
    player_market_value_eur: float = 25000000.0
    position: str = "Attack"
    current_club_name: Optional[str] = None
    buying_club_name: str


class TransferProbPredictionResponse(BaseModel):
    player_name: str
    buying_club_name: str
    transfer_probability: float  # 0.0 to 1.0
    confidence: str
    intelligence_score: float     # 0.0 to 100.0
    rating_label: str
    prediction_timestamp: datetime
    disclaimer: str = "This prediction is a statistical estimate, not a confirmed transfer fact."
