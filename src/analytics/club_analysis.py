import pandas as pd
from typing import Dict, Any, List, Optional
from src.data.db import query_duckdb
from src.utils.logging import get_logger

logger = get_logger("analytics.club_analysis")


def list_clubs(
    search_query: Optional[str] = None,
    domestic_league_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """Retrieves paginated club profiles with optional search and league filter."""
    where_clauses = []
    params = []

    if search_query:
        where_clauses.append("LOWER(name) LIKE LOWER(?)")
        params.append(f"%{search_query}%")

    if domestic_league_id:
        where_clauses.append("domestic_competition_id = ?")
        params.append(domestic_league_id)

    where_str = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    count_query = f"SELECT COUNT(*) FROM clubs {where_str}"
    total_count = query_duckdb(count_query, params).iloc[0, 0]

    data_query = f"""
    SELECT 
        club_id,
        name,
        domestic_competition_id,
        total_market_value,
        squad_size,
        average_age,
        foreigners_percentage,
        stadium_name,
        stadium_seats,
        coach_name,
        url
    FROM clubs
    {where_str}
    ORDER BY total_market_value DESC NULLS LAST
    LIMIT ? OFFSET ?
    """
    data_params = params + [limit, offset]
    df = query_duckdb(data_query, data_params)

    return {
        "total": int(total_count),
        "limit": limit,
        "offset": offset,
        "clubs": df.to_dict(orient="records")
    }


def get_club_profile(club_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves complete details, active squad, and net spend balance for a club."""
    query = "SELECT * FROM clubs WHERE TRY_CAST(club_id AS INTEGER) = ?"
    df = query_duckdb(query, [club_id])
    if df.empty:
        return None

    club = df.iloc[0].to_dict()

    # Total incoming spend
    spend_df = query_duckdb(
        "SELECT SUM(transfer_fee) as total_spend, COUNT(*) as arrivals_count FROM transfers WHERE to_club_id = ?",
        [club_id]
    )
    total_spend = float(spend_df.iloc[0]["total_spend"] or 0.0)
    arrivals_count = int(spend_df.iloc[0]["arrivals_count"] or 0)

    # Total outgoing income
    income_df = query_duckdb(
        "SELECT SUM(transfer_fee) as total_income, COUNT(*) as departures_count FROM transfers WHERE from_club_id = ?",
        [club_id]
    )
    total_income = float(income_df.iloc[0]["total_income"] or 0.0)
    departures_count = int(income_df.iloc[0]["departures_count"] or 0)

    club.update({
        "total_transfer_spend": total_spend,
        "total_transfer_income": total_income,
        "net_transfer_spend": total_spend - total_income,
        "arrivals_count": arrivals_count,
        "departures_count": departures_count
    })

    return club


def get_club_transfer_activity(club_id: int, limit: int = 20) -> Dict[str, List[Dict[str, Any]]]:
    """Retrieves incoming and outgoing transfers for a specific club."""
    arrivals_query = """
    SELECT 
        player_id, player_name, transfer_date, transfer_season, from_club_name, transfer_fee, market_value_in_eur
    FROM transfers
    WHERE to_club_id = ?
    ORDER BY transfer_date DESC
    LIMIT ?
    """
    arrivals_df = query_duckdb(arrivals_query, [club_id, limit])

    departures_query = """
    SELECT 
        player_id, player_name, transfer_date, transfer_season, to_club_name, transfer_fee, market_value_in_eur
    FROM transfers
    WHERE from_club_id = ?
    ORDER BY transfer_date DESC
    LIMIT ?
    """
    departures_df = query_duckdb(departures_query, [club_id, limit])

    return {
        "arrivals": arrivals_df.to_dict(orient="records"),
        "departures": departures_df.to_dict(orient="records")
    }
