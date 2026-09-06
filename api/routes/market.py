from fastapi import APIRouter, Query
from typing import Dict, Any, List
from src.analytics.market_analysis import (
    get_market_summary,
    get_spending_by_season,
    get_spending_by_league,
    get_top_transfers,
    get_position_fee_distribution
)

router = APIRouter(prefix="/market", tags=["Market Analytics"])


@router.get("/summary", response_model=Dict[str, Any])
def market_summary_endpoint():
    return get_market_summary()


@router.get("/spending", response_model=List[Dict[str, Any]])
def market_spending_by_season(limit: int = Query(15, ge=1, le=50)):
    return get_spending_by_season(limit=limit)


@router.get("/leagues", response_model=List[Dict[str, Any]])
def market_spending_by_league(limit: int = Query(10, ge=1, le=30)):
    return get_spending_by_league(limit=limit)


@router.get("/top-transfers", response_model=List[Dict[str, Any]])
def market_top_transfers(limit: int = Query(20, ge=1, le=100)):
    return get_top_transfers(limit=limit)


@router.get("/positions", response_model=List[Dict[str, Any]])
def market_positions_fee_distribution():
    return get_position_fee_distribution()
