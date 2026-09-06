import pandas as pd
import numpy as np
from typing import Optional
from src.data.db import query_duckdb
from src.utils.logging import get_logger

logger = get_logger("features.player_features")


def get_player_feature_dataset() -> pd.DataFrame:
    """Builds a comprehensive player feature dataset combining performance, market value, and transfer history."""
    query = """
    WITH appearance_stats AS (
        SELECT 
            player_id,
            COUNT(DISTINCT game_id) as total_appearances,
            SUM(goals) as total_goals,
            SUM(assists) as total_assists,
            SUM(minutes_played) as total_minutes,
            SUM(yellow_cards) as total_yellow_cards,
            SUM(red_cards) as total_red_cards,
            MAX(date) as last_appearance_date
        FROM appearances
        GROUP BY player_id
    ),
    valuation_history AS (
        SELECT 
            player_id,
            COUNT(date) as valuation_count,
            MIN(market_value_in_eur) as min_market_value,
            MAX(market_value_in_eur) as peak_market_value,
            AVG(market_value_in_eur) as avg_market_value
        FROM player_valuations
        GROUP BY player_id
    ),
    transfer_summary AS (
        SELECT 
            player_id,
            COUNT(*) as total_transfers_count,
            MAX(transfer_fee) as max_transfer_fee_paid,
            AVG(transfer_fee) as avg_transfer_fee_paid
        FROM transfers
        GROUP BY player_id
    )
    SELECT 
        p.player_id,
        p.name as player_name,
        p.position,
        p.sub_position,
        p.country_of_citizenship,
        p.height_in_cm,
        p.date_of_birth,
        p.market_value_in_eur as current_market_value,
        p.highest_market_value_in_eur,
        p.international_caps,
        p.international_goals,
        p.current_club_name,
        p.current_club_domestic_competition_id,
        COALESCE(ast.total_appearances, 0) as total_appearances,
        COALESCE(ast.total_goals, 0) as total_goals,
        COALESCE(ast.total_assists, 0) as total_assists,
        COALESCE(ast.total_minutes, 0) as total_minutes,
        COALESCE(vh.peak_market_value, p.highest_market_value_in_eur, 0) as peak_valuation_recorded,
        COALESCE(vh.avg_market_value, p.market_value_in_eur, 0) as avg_valuation_recorded,
        COALESCE(ts.total_transfers_count, 0) as total_transfers_count,
        COALESCE(ts.max_transfer_fee_paid, 0) as max_transfer_fee_paid
    FROM players p
    LEFT JOIN appearance_stats ast ON p.player_id = ast.player_id
    LEFT JOIN valuation_history vh ON p.player_id = vh.player_id
    LEFT JOIN transfer_summary ts ON p.player_id = ts.player_id
    """
    df = query_duckdb(query)
    
    # Calculate age
    if "date_of_birth" in df.columns:
        df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce")
        df["age"] = (pd.to_datetime("today") - df["date_of_birth"]).dt.days // 365.25
        df["age"] = df["age"].fillna(df["age"].median())
    else:
        df["age"] = 25.0

    # Calculate valuation growth ratio
    df["valuation_growth_ratio"] = np.where(
        df["avg_valuation_recorded"] > 0,
        df["current_market_value"] / df["avg_valuation_recorded"],
        1.0
    )

    return df
