import pandas as pd
from src.data.db import query_duckdb
from src.utils.logging import get_logger

logger = get_logger("features.club_features")


def get_club_feature_dataset() -> pd.DataFrame:
    """Builds squad and transfer activity feature metrics for all clubs."""
    query = """
    WITH club_spend AS (
        SELECT 
            to_club_id as club_id,
            SUM(transfer_fee) as total_spending,
            COUNT(*) as total_arrivals,
            AVG(transfer_fee) as avg_arrival_fee
        FROM transfers
        WHERE to_club_id IS NOT NULL
        GROUP BY to_club_id
    ),
    club_income AS (
        SELECT 
            from_club_id as club_id,
            SUM(transfer_fee) as total_income,
            COUNT(*) as total_departures,
            AVG(transfer_fee) as avg_departure_fee
        FROM transfers
        WHERE from_club_id IS NOT NULL
        GROUP BY from_club_id
    ),
    squad_stats AS (
        SELECT 
            TRY_CAST(current_club_id AS INTEGER) as club_id,
            COUNT(player_id) as active_squad_size,
            AVG(market_value_in_eur) as avg_squad_market_value,
            SUM(market_value_in_eur) as total_squad_market_value
        FROM players
        WHERE current_club_id IS NOT NULL
        GROUP BY TRY_CAST(current_club_id AS INTEGER)
    )
    SELECT 
        TRY_CAST(c.club_id AS INTEGER) as club_id,
        c.name as club_name,
        c.domestic_competition_id,
        c.total_market_value as recorded_total_market_value,
        c.squad_size,
        c.average_age,
        c.foreigners_percentage,
        c.stadium_seats,
        COALESCE(cs.total_spending, 0) as total_spending,
        COALESCE(cs.total_arrivals, 0) as total_arrivals,
        COALESCE(ci.total_income, 0) as total_income,
        COALESCE(ci.total_departures, 0) as total_departures,
        (COALESCE(ci.total_income, 0) - COALESCE(cs.total_spending, 0)) as net_transfer_balance,
        COALESCE(ss.active_squad_size, c.squad_size, 0) as active_squad_size,
        COALESCE(ss.avg_squad_market_value, 0) as avg_squad_market_value
    FROM clubs c
    LEFT JOIN club_spend cs ON TRY_CAST(c.club_id AS INTEGER) = cs.club_id
    LEFT JOIN club_income ci ON TRY_CAST(c.club_id AS INTEGER) = ci.club_id
    LEFT JOIN squad_stats ss ON TRY_CAST(c.club_id AS INTEGER) = ss.club_id
    """
    df = query_duckdb(query)
    return df
