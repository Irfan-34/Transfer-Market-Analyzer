from src.models.value_model import MarketValueModel
from src.models.fee_model import TransferFeeModel
from src.models.transfer_probability_model import TransferProbabilityModel
from src.analytics.intelligence_score import calculate_transfer_intelligence_score


def test_market_value_model():
    model = MarketValueModel(model_type="dummy")
    metrics = model.train_and_evaluate()
    assert "mae" in metrics
    assert "r2" in metrics


def test_transfer_fee_model():
    model = TransferFeeModel()
    metrics = model.train_and_evaluate()
    assert "rmse" in metrics

    pred = model.predict_fee({
        "valuation_at_transfer": 50000000.0,
        "age_at_transfer": 24,
        "position": "Attack"
    })
    assert pred["expected_fee_eur"] >= 0.0
    assert pred["fee_range_low_eur"] <= pred["fee_range_high_eur"]


def test_transfer_probability_model():
    model = TransferProbabilityModel(model_type="logistic")
    metrics = model.train_and_evaluate()
    assert "roc_auc" in metrics

    pred = model.predict_probability(player_market_value=30000000.0, position="Midfield")
    assert 0.0 <= pred["transfer_probability"] <= 1.0


def test_intelligence_score():
    score = calculate_transfer_intelligence_score(ml_probability=0.85, source_reliability=0.90, rumour_count=3)
    assert 0.0 <= score["intelligence_score"] <= 100.0
    assert score["rating"] in ["VERY HIGH CONFIDENCE", "HIGH LIKELIHOOD", "MODERATE LINK", "SPECULATIVE", "UNLIKELY"]
