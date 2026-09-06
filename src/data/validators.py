import pandas as pd
from typing import Dict, List, Any, Tuple
from src.utils.logging import get_logger
from src.utils.dates import calculate_age

logger = get_logger("data.validators")


def validate_transfers(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Validates transfer DataFrame records, identifying anomalies while preserving data context.
    
    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: Cleaned/flagged DataFrame and validation metrics.
    """
    report = {
        "total_records": len(df),
        "duplicate_transfers": 0,
        "invalid_fees": 0,
        "missing_player_ids": 0,
        "inconsistent_clubs": 0,
        "invalid_dates": 0,
    }

    if df.empty:
        return df, report

    # Missing player ID check
    missing_players = df["player_id"].isna()
    report["missing_player_ids"] = int(missing_players.sum())
    if report["missing_player_ids"] > 0:
        logger.warning(f"Found {report['missing_player_ids']} transfer records missing player_id.")

    # Duplicate transfers check (same player, same date, same buying & selling club)
    dup_cols = [c for c in ["player_id", "transfer_date", "from_club_id", "to_club_id"] if c in df.columns]
    if len(dup_cols) == len(["player_id", "transfer_date", "from_club_id", "to_club_id"]):
        duplicates = df.duplicated(subset=dup_cols, keep="first")
        report["duplicate_transfers"] = int(duplicates.sum())
        if report["duplicate_transfers"] > 0:
            logger.info(f"Identified {report['duplicate_transfers']} duplicate transfer entries.")

    # Invalid transfer fee check (negative values)
    if "transfer_fee" in df.columns:
        neg_fees = df["transfer_fee"] < 0
        report["invalid_fees"] = int(neg_fees.sum())
        if report["invalid_fees"] > 0:
            logger.warning(f"Found {report['invalid_fees']} transfers with negative transfer fees.")

    # Inconsistent club check (selling club equals buying club)
    if "from_club_id" in df.columns and "to_club_id" in df.columns:
        same_club = (df["from_club_id"] == df["to_club_id"]) & (df["from_club_id"].notna())
        report["inconsistent_clubs"] = int(same_club.sum())
        if report["inconsistent_clubs"] > 0:
            logger.info(f"Found {report['inconsistent_clubs']} transfers where selling club equals buying club.")

    return df, report


def validate_player_profiles(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Validates player bios for impossible ages, missing market values, or missing IDs."""
    report = {
        "total_players": len(df),
        "missing_ids": 0,
        "impossible_ages": 0,
        "missing_market_values": 0,
    }

    if df.empty:
        return df, report

    report["missing_ids"] = int(df["player_id"].isna().sum())

    if "date_of_birth" in df.columns:
        ages = df["date_of_birth"].apply(lambda dob: calculate_age(dob))
        impossible = (ages < 14) | (ages > 50)
        report["impossible_ages"] = int(impossible.sum())
        if report["impossible_ages"] > 0:
            logger.warning(f"Found {report['impossible_ages']} players with impossible ages (<14 or >50).")

    if "market_value_in_eur" in df.columns:
        report["missing_market_values"] = int(df["market_value_in_eur"].isna().sum())

    return df, report


def validate_rumours(rumours: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicates and validates transfer rumour objects."""
    seen_hashes = set()
    validated = []

    for item in rumours:
        player = str(item.get("player_name", "")).strip().lower()
        to_club = str(item.get("to_club_name", "")).strip().lower()
        source = str(item.get("source_name", "")).strip().lower()

        if not player or not to_club:
            logger.warning(f"Skipping incomplete rumour item: {item}")
            continue

        item_hash = f"{player}|{to_club}|{source}"
        if item_hash in seen_hashes:
            logger.info(f"Deduplicated duplicate rumour: {player} -> {to_club}")
            continue

        seen_hashes.add(item_hash)
        validated.append(item)

    return validated
