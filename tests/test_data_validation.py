import pandas as pd
from src.data.validators import validate_transfers, validate_player_profiles, validate_rumours
from src.data.cleaners import clean_transfers_df, clean_players_df


def test_validate_transfers_duplicate():
    sample_df = pd.DataFrame([
        {"player_id": 1, "transfer_date": "2023-07-01", "from_club_id": 10, "to_club_id": 20, "transfer_fee": 1000000.0},
        {"player_id": 1, "transfer_date": "2023-07-01", "from_club_id": 10, "to_club_id": 20, "transfer_fee": 1000000.0}
    ])
    _, report = validate_transfers(sample_df)
    assert report["duplicate_transfers"] == 1


def test_clean_transfers_negative_fee():
    sample_df = pd.DataFrame([
        {"player_id": 1, "transfer_fee": -500000.0, "player_name": " Test Player "}
    ])
    cleaned = clean_transfers_df(sample_df)
    assert cleaned.iloc[0]["transfer_fee"] == 0.0
    assert cleaned.iloc[0]["player_name"] == "Test Player"


def test_validate_rumours_deduplication():
    rumours = [
        {"player_name": "Jude Bellingham", "to_club_name": "Real Madrid", "source_name": "Marca"},
        {"player_name": "jude bellingham ", "to_club_name": "real madrid", "source_name": "marca"}
    ]
    validated = validate_rumours(rumours)
    assert len(validated) == 1
