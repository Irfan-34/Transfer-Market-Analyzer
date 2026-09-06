from fastapi import APIRouter, Query
from typing import List, Dict, Any
from src.analytics.market_analysis import get_top_transfers
from src.data.db import query_duckdb

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.get("", response_model=List[Dict[str, Any]])
def get_transfers(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    query = """
    SELECT 
        player_id, player_name, transfer_date, transfer_season,
        from_club_name, to_club_name, transfer_fee as fee_eur, market_value_in_eur
    FROM transfers
    ORDER BY transfer_date DESC NULLS LAST
    LIMIT ? OFFSET ?
    """
    df = query_duckdb(query, [limit, offset])
    return df.to_dict(orient="records")


@router.get("/latest", response_model=List[Dict[str, Any]])
def get_latest_transfers(limit: int = Query(10, ge=1, le=50)):
    query = """
    SELECT 
        player_id, player_name, transfer_date, transfer_season,
        from_club_name, to_club_name, transfer_fee as fee_eur, market_value_in_eur
    FROM transfers
    WHERE transfer_date IS NOT NULL
    ORDER BY transfer_date DESC
    LIMIT ?
    """
    df = query_duckdb(query, [limit])
    return df.to_dict(orient="records")


@router.get("/top", response_model=List[Dict[str, Any]])
def get_highest_fee_transfers(limit: int = Query(15, ge=1, le=50)):
    return get_top_transfers(limit=limit)
