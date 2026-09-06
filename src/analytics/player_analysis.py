import pandas as pd
from typing import Dict, Any, List, Optional
from src.data.db import query_duckdb
from src.utils.logging import get_logger
from src.utils.dates import calculate_age

logger = get_logger("analytics.player_analysis")


def list_players(
    search_query: Optional[str] = None,
    position: Optional[str] = None,
    league_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """Retrieves paginated player records with optional name/position/league filtering."""
    where_clauses = []
    params = []

    if search_query:
        where_clauses.append("LOWER(name) LIKE LOWER(?)")
        params.append(f"%{search_query}%")

    if position:
        where_clauses.append("LOWER(position) = LOWER(?)")
        params.append(position)

    if league_id:
        where_clauses.append("current_club_domestic_competition_id = ?")
        params.append(league_id)

    where_str = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    count_query = f"SELECT COUNT(*) FROM players {where_str}"
    total_count = query_duckdb(count_query, params).iloc[0, 0]

    data_query = f"""
    SELECT 
        player_id,
        name,
        position,
        sub_position,
        date_of_birth,
        country_of_citizenship,
        current_club_name,
        current_club_domestic_competition_id,
        market_value_in_eur,
        highest_market_value_in_eur,
        image_url
    FROM players
    {where_str}
    ORDER BY market_value_in_eur DESC NULLS LAST
    LIMIT ? OFFSET ?
    """
    data_params = params + [limit, offset]
    df = query_duckdb(data_query, data_params)

    players_list = df.to_dict(orient="records")
    for p in players_list:
        p["age"] = calculate_age(p.get("date_of_birth"))

    return {
        "total": int(total_count),
        "limit": limit,
        "offset": offset,
        "players": players_list
    }


def get_player_profile(player_id: int) -> Optional[Dict[str, Any]]:
    """Fetches comprehensive profile details for a specific player."""
    query = "SELECT * FROM players WHERE player_id = ?"
    df = query_duckdb(query, [player_id])
    if df.empty:
        return None

    player = df.iloc[0].to_dict()
    player["age"] = calculate_age(player.get("date_of_birth"))

    # Fetch appearance summary
    app_query = """
    SELECT 
        COUNT(DISTINCT game_id) as total_appearances,
        COALESCE(SUM(goals), 0) as total_goals,
        COALESCE(SUM(assists), 0) as total_assists,
        COALESCE(SUM(minutes_played), 0) as total_minutes
    FROM appearances
    WHERE player_id = ?
    """
    app_df = query_duckdb(app_query, [player_id])
    if not app_df.empty:
        app_stats = app_df.iloc[0].to_dict()
        player.update(app_stats)

    return player


def get_player_market_value_history(player_id: int) -> List[Dict[str, Any]]:
    """Retrieves historical valuation snapshots for a player."""
    query = """
    SELECT 
        date,
        market_value_in_eur,
        current_club_name,
        current_club_id
    FROM player_valuations
    WHERE player_id = ?
    ORDER BY date ASC
    """
    df = query_duckdb(query, [player_id])
    return df.to_dict(orient="records")


def get_player_transfer_history(player_id: int) -> List[Dict[str, Any]]:
    """Retrieves transfer event history for a player."""
    query = """
    SELECT 
        transfer_date,
        transfer_season,
        from_club_name,
        to_club_name,
        transfer_fee,
        market_value_in_eur
    FROM transfers
    WHERE player_id = ?
    ORDER BY transfer_date DESC
    """
    df = query_duckdb(query, [player_id])
    return df.to_dict(orient="records")
