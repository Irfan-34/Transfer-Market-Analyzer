import pandas as pd
import numpy as np
from src.data.db import query_duckdb
from src.utils.logging import get_logger

logger = get_logger("features.transfer_features")


def get_transfer_feature_dataset() -> pd.DataFrame:
    """Builds historical transfer event records joined with player and club features for model training."""
    query = """
    SELECT 
        t.player_id,
        t.player_name,
        t.transfer_date,
        t.transfer_season,
        t.from_club_id,
        t.to_club_id,
        t.from_club_name,
        t.to_club_name,
        t.transfer_fee,
        t.market_value_in_eur as valuation_at_transfer,
        p.position,
        p.sub_position,
        p.height_in_cm,
        p.date_of_birth,
        p.international_caps,
        p.country_of_citizenship,
        fc.domestic_competition_id as selling_league,
        tc.domestic_competition_id as buying_league,
        fc.total_market_value as selling_club_market_value,
        tc.total_market_value as buying_club_market_value
    FROM transfers t
    LEFT JOIN players p ON t.player_id = p.player_id
    LEFT JOIN clubs fc ON TRY_CAST(fc.club_id AS INTEGER) = t.from_club_id
    LEFT JOIN clubs tc ON TRY_CAST(tc.club_id AS INTEGER) = t.to_club_id
    WHERE t.transfer_fee IS NOT NULL
    """
    df = query_duckdb(query)

    # Process transfer date and calculate player age at time of transfer
    if "transfer_date" in df.columns and "date_of_birth" in df.columns:
        df["transfer_date"] = pd.to_datetime(df["transfer_date"], errors="coerce")
        df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce")
        df["age_at_transfer"] = (df["transfer_date"] - df["date_of_birth"]).dt.days // 365.25
        df["age_at_transfer"] = df["age_at_transfer"].fillna(25.0)

    # Position group mapping
    df["position"] = df["position"].fillna("Unknown").str.title()
    df["valuation_at_transfer"] = df["valuation_at_transfer"].fillna(0.0).astype(float)
    df["transfer_fee"] = df["transfer_fee"].fillna(0.0).astype(float)

    # Ratio of transfer fee to market value
    df["fee_to_valuation_ratio"] = np.where(
        df["valuation_at_transfer"] > 0,
        df["transfer_fee"] / df["valuation_at_transfer"],
        1.0
    )

    return df
