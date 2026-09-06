from src.features.player_features import get_player_feature_dataset
from src.features.club_features import get_club_feature_dataset
from src.features.transfer_features import get_transfer_feature_dataset


def test_player_features_structure():
    df = get_player_feature_dataset()
    assert not df.empty
    assert "player_id" in df.columns
    assert "age" in df.columns
    assert "valuation_growth_ratio" in df.columns


def test_club_features_structure():
    df = get_club_feature_dataset()
    assert not df.empty
    assert "club_id" in df.columns
    assert "total_spending" in df.columns
    assert "net_transfer_balance" in df.columns


def test_transfer_features_structure():
    df = get_transfer_feature_dataset()
    assert not df.empty
    assert "fee_to_valuation_ratio" in df.columns
