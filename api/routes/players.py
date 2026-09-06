from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from src.analytics.player_analysis import (
    list_players,
    get_player_profile,
    get_player_market_value_history,
    get_player_transfer_history
)

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("", response_model=Dict[str, Any])
def get_players(
    search: Optional[str] = Query(None, description="Search player by name"),
    position: Optional[str] = Query(None, description="Filter by position"),
    league_id: Optional[str] = Query(None, description="Filter by competition ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return list_players(search_query=search, position=position, league_id=league_id, limit=limit, offset=offset)


@router.get("/{player_id}", response_model=Dict[str, Any])
def get_player_by_id(player_id: int):
    profile = get_player_profile(player_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Player with ID {player_id} not found.")
    return profile


@router.get("/{player_id}/market-value", response_model=List[Dict[str, Any]])
def get_player_valuations(player_id: int):
    return get_player_market_value_history(player_id)


@router.get("/{player_id}/transfer-history", response_model=List[Dict[str, Any]])
def get_player_transfers(player_id: int):
    return get_player_transfer_history(player_id)
