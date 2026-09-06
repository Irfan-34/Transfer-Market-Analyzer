from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import List, Dict, Any
from api.dependencies import get_fee_model, get_prob_model
from api.schemas import (
    TransferFeePredictionRequest,
    TransferFeePredictionResponse,
    TransferProbPredictionRequest,
    TransferProbPredictionResponse
)
from src.models.fee_model import TransferFeeModel
from src.models.transfer_probability_model import TransferProbabilityModel
from src.analytics.intelligence_score import calculate_transfer_intelligence_score
from src.features.rumour_features import get_rumour_features_for_player

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/fee", response_model=TransferFeePredictionResponse)
def predict_transfer_fee(
    req: TransferFeePredictionRequest,
    model: TransferFeeModel = Depends(get_fee_model)
):
    input_data = {
        "valuation_at_transfer": req.current_market_value_eur,
        "age_at_transfer": req.age,
        "position": req.position,
        "selling_club_market_value": req.selling_club_market_value,
        "buying_club_market_value": req.buying_club_market_value
    }
    result = model.predict_fee(input_data)
    return TransferFeePredictionResponse(
        player_name=req.player_name,
        expected_fee_eur=result["expected_fee_eur"],
        fee_range_low_eur=result["fee_range_low_eur"],
        fee_range_high_eur=result["fee_range_high_eur"],
        confidence=result["confidence"]
    )


@router.post("/transfer", response_model=TransferProbPredictionResponse)
def predict_transfer_probability(
    req: TransferProbPredictionRequest,
    prob_model: TransferProbabilityModel = Depends(get_prob_model)
):
    # Retrieve rumour context features for this player-club pair
    rumour_info = get_rumour_features_for_player(req.player_name, req.buying_club_name)
    rumour_bonus = 0.15 if rumour_info["has_reliable_report"] else (0.05 if rumour_info["rumour_count"] > 0 else 0.0)

    pred = prob_model.predict_probability(
        player_market_value=req.player_market_value_eur,
        position=req.position,
        rumour_bonus=rumour_bonus
    )

    intel = calculate_transfer_intelligence_score(
        ml_probability=pred["transfer_probability"],
        source_reliability=rumour_info["max_source_reliability"],
        rumour_count=rumour_info["rumour_count"]
    )

    return TransferProbPredictionResponse(
        player_name=req.player_name,
        buying_club_name=req.buying_club_name,
        transfer_probability=pred["transfer_probability"],
        confidence=pred["confidence"],
        intelligence_score=intel["intelligence_score"],
        rating_label=intel["rating"],
        prediction_timestamp=datetime.utcnow()
    )


@router.get("/top", response_model=List[Dict[str, Any]])
def get_top_predictions():
    """Returns curated high-probability predictions across major players."""
    curated = [
        {"player_name": "Florian Wirtz", "current_club": "Bayer Leverkusen", "buying_club": "Real Madrid", "probability": 0.82, "confidence": "HIGH", "expected_fee": 130000000.0, "intelligence_score": 86.5},
        {"player_name": "Alexander Isak", "current_club": "Newcastle United", "buying_club": "Arsenal", "probability": 0.74, "confidence": "HIGH", "expected_fee": 95000000.0, "intelligence_score": 78.2},
        {"player_name": "Trent Alexander-Arnold", "current_club": "Liverpool", "buying_club": "Real Madrid", "probability": 0.88, "confidence": "HIGH", "expected_fee": 0.0, "intelligence_score": 91.0},
        {"player_name": "Viktor Gyökeres", "current_club": "Sporting CP", "buying_club": "Manchester United", "probability": 0.71, "confidence": "MEDIUM", "expected_fee": 85000000.0, "intelligence_score": 75.0},
        {"player_name": "Nico Williams", "current_club": "Athletic Bilbao", "buying_club": "Barcelona", "probability": 0.68, "confidence": "MEDIUM", "expected_fee": 58000000.0, "intelligence_score": 72.4}
    ]
    return curated
