import pandas as pd
from typing import Dict, Any, List
from src.data.db import query_duckdb
from src.utils.logging import get_logger

logger = get_logger("analytics.market_analysis")


def get_market_summary() -> Dict[str, Any]:
    """Computes macro transfer market summary metrics across all historical data."""
    query = """
    SELECT 
        COUNT(*) as total_transfers,
        SUM(transfer_fee) as total_spending_eur,
        AVG(transfer_fee) as avg_transfer_fee_eur,
        MEDIAN(transfer_fee) as median_transfer_fee_eur,
        MAX(transfer_fee) as record_transfer_fee_eur,
        SUM(CASE WHEN transfer_fee = 0 THEN 1 ELSE 0 END) as free_transfers_count
    FROM transfers
    """
    df = query_duckdb(query)
    row = df.iloc[0]

    players_count = query_duckdb("SELECT COUNT(*) FROM players;").iloc[0, 0]
    clubs_count = query_duckdb("SELECT COUNT(*) FROM clubs;").iloc[0, 0]

    return {
        "total_transfers": int(row["total_transfers"]),
        "total_spending_eur": float(row["total_spending_eur"]),
        "avg_transfer_fee_eur": float(row["avg_transfer_fee_eur"]),
        "median_transfer_fee_eur": float(row["median_transfer_fee_eur"]),
        "record_transfer_fee_eur": float(row["record_transfer_fee_eur"]),
        "free_transfers_count": int(row["free_transfers_count"]),
        "total_players_recorded": int(players_count),
        "total_clubs_recorded": int(clubs_count)
    }


def get_spending_by_season(limit: int = 15) -> List[Dict[str, Any]]:
    """Returns annual transfer spending and volume grouped by season."""
    query = """
    SELECT 
        transfer_season as season,
        COUNT(*) as transfer_count,
        SUM(transfer_fee) as total_spending_eur,
        AVG(transfer_fee) as avg_fee_eur,
        MAX(transfer_fee) as max_fee_eur
    FROM transfers
    WHERE transfer_season IS NOT NULL AND transfer_season != ''
    GROUP BY transfer_season
    ORDER BY transfer_season DESC
    LIMIT ?
    """
    df = query_duckdb(query, [limit])
    return df.to_dict(orient="records")


def get_spending_by_league(limit: int = 10) -> List[Dict[str, Any]]:
    """Computes transfer spending broken down by buying domestic league."""
    query = """
    SELECT 
        c.domestic_competition_id as competition_id,
        comp.name as league_name,
        comp.country_name,
        COUNT(t.player_id) as total_arrivals,
        SUM(t.transfer_fee) as total_spending_eur,
        AVG(t.transfer_fee) as avg_spending_eur
    FROM transfers t
    JOIN clubs c ON TRY_CAST(c.club_id AS INTEGER) = t.to_club_id
    JOIN competitions comp ON comp.competition_id = c.domestic_competition_id
    GROUP BY c.domestic_competition_id, comp.name, comp.country_name
    ORDER BY total_spending_eur DESC
    LIMIT ?
    """
    df = query_duckdb(query, [limit])
    return df.to_dict(orient="records")


def get_top_transfers(limit: int = 20) -> List[Dict[str, Any]]:
    """Returns the highest transfer fee entries in history."""
    query = """
    SELECT 
        t.player_id,
        t.player_name,
        t.transfer_date,
        t.transfer_season,
        t.from_club_name,
        t.to_club_name,
        t.transfer_fee as fee_eur,
        t.market_value_in_eur as market_value_eur,
        p.position
    FROM transfers t
    LEFT JOIN players p ON t.player_id = p.player_id
    ORDER BY t.transfer_fee DESC
    LIMIT ?
    """
    df = query_duckdb(query, [limit])
    return df.to_dict(orient="records")


def get_position_fee_distribution() -> List[Dict[str, Any]]:
    """Computes average transfer fee and count grouped by player position."""
    query = """
    SELECT 
        COALESCE(p.position, 'Unknown') as position,
        COUNT(t.player_id) as total_transfers,
        AVG(t.transfer_fee) as avg_fee_eur,
        MEDIAN(t.transfer_fee) as median_fee_eur,
        MAX(t.transfer_fee) as max_fee_eur
    FROM transfers t
    LEFT JOIN players p ON t.player_id = p.player_id
    GROUP BY COALESCE(p.position, 'Unknown')
    ORDER BY avg_fee_eur DESC
    """
    df = query_duckdb(query)
    return df.to_dict(orient="records")
