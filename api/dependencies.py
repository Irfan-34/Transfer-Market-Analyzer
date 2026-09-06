from typing import Generator
from sqlalchemy.orm import Session
from src.data.db import SessionLocal
from src.models.value_model import MarketValueModel
from src.models.fee_model import TransferFeeModel
from src.models.transfer_probability_model import TransferProbabilityModel

# Global ML Model Singletons initialized on app startup
value_model_instance = MarketValueModel(model_type="xgboost")
fee_model_instance = TransferFeeModel()
prob_model_instance = TransferProbabilityModel(model_type="xgboost")


def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency yielding database session for relational app storage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_value_model() -> MarketValueModel:
    return value_model_instance


def get_fee_model() -> TransferFeeModel:
    return fee_model_instance


def get_prob_model() -> TransferProbabilityModel:
    return prob_model_instance
