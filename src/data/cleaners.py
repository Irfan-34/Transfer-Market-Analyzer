import pandas as pd
import numpy as np
from src.utils.logging import get_logger

logger = get_logger("data.cleaners")


def clean_transfers_df(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and standardizes transfer DataFrame while logging transformation steps."""
    cleaned = df.copy()

    # Fill missing transfer fees with 0.0 (typically indicative of free transfers / missing data)
    if "transfer_fee" in cleaned.columns:
        null_fees = cleaned["transfer_fee"].isna().sum()
        if null_fees > 0:
            logger.info(f"Filling {null_fees} missing transfer_fee values with 0.0 EUR.")
            cleaned["transfer_fee"] = cleaned["transfer_fee"].fillna(0.0)

        # Correct negative fees to absolute values or 0
        cleaned["transfer_fee"] = cleaned["transfer_fee"].apply(lambda x: max(0.0, float(x)) if pd.notna(x) else 0.0)

    # Convert dates to datetime
    if "transfer_date" in cleaned.columns:
        cleaned["transfer_date"] = pd.to_datetime(cleaned["transfer_date"], errors="coerce")

    # Standardize string fields
    for col in ["player_name", "from_club_name", "to_club_name"]:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].astype(str).str.strip()

    return cleaned


def clean_players_df(df: pd.DataFrame) -> pd.DataFrame:
    """Sanitizes player profile attributes."""
    cleaned = df.copy()

    if "date_of_birth" in cleaned.columns:
        cleaned["date_of_birth"] = pd.to_datetime(cleaned["date_of_birth"], errors="coerce")

    if "height_in_cm" in cleaned.columns:
        # Standardize height bounds (140cm to 220cm)
        invalid_h = (cleaned["height_in_cm"] < 140) | (cleaned["height_in_cm"] > 220)
        if invalid_h.sum() > 0:
            logger.info(f"Setting {invalid_h.sum()} out-of-bound height_in_cm values to NaN.")
            cleaned.loc[invalid_h, "height_in_cm"] = np.nan

    if "position" in cleaned.columns:
        cleaned["position"] = cleaned["position"].fillna("Unknown").str.title()

    if "market_value_in_eur" in cleaned.columns:
        cleaned["market_value_in_eur"] = cleaned["market_value_in_eur"].fillna(0.0).astype(float)

    return cleaned
