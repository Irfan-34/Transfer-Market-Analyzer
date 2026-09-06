from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from src.analytics.club_analysis import (
    list_clubs,
    get_club_profile,
    get_club_transfer_activity
)

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.get("", response_model=Dict[str, Any])
def get_clubs(
    search: Optional[str] = Query(None, description="Search club by name"),
    league_id: Optional[str] = Query(None, description="Filter by league ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return list_clubs(search_query=search, domestic_league_id=league_id, limit=limit, offset=offset)


@router.get("/{club_id}", response_model=Dict[str, Any])
def get_club_by_id(club_id: int):
    club = get_club_profile(club_id)
    if not club:
        raise HTTPException(status_code=404, detail=f"Club with ID {club_id} not found.")
    return club


@router.get("/{club_id}/transfer-activity", response_model=Dict[str, Any])
def get_club_transfers(club_id: int, limit: int = Query(20, ge=1, le=50)):
    return get_club_transfer_activity(club_id, limit=limit)
