import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from src.features.player_features import get_player_feature_dataset
from src.models.preprocessing import build_preprocessing_pipeline
from src.models.evaluation import evaluate_regression
from src.utils.logging import get_logger

logger = get_logger("models.value_model")


class MarketValueModel:
    def __init__(self, model_type: str = "xgboost"):
        self.model_type = model_type
        self.numeric_features = [
            "age", "total_appearances", "total_goals", "total_assists",
            "total_minutes", "peak_valuation_recorded", "avg_valuation_recorded",
            "total_transfers_count", "max_transfer_fee_paid", "valuation_growth_ratio"
        ]
        self.categorical_features = ["position", "current_club_domestic_competition_id"]
        self.preprocessor = build_preprocessing_pipeline(self.numeric_features, self.categorical_features)
        
        if model_type == "dummy":
            self.model = DummyRegressor(strategy="mean")
        elif model_type == "ridge":
            self.model = Ridge(alpha=1.0)
        elif model_type == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
        else:
            self.model = XGBRegressor(n_estimators=100, learning_rate=0.08, max_depth=6, random_state=42)

    def train_and_evaluate(self) -> Dict[str, Any]:
        """Loads player features, trains the model, and evaluates metrics."""
        logger.info(f"Training Market Value Model ({self.model_type})...")
        df = get_player_feature_dataset()
        df = df.dropna(subset=["current_market_value"])
        df = df[df["current_market_value"] > 0]

        X = df[self.numeric_features + self.categorical_features]
        y = np.log1p(df["current_market_value"])  # Target log transformation

        split_idx = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        X_train_trans = self.preprocessor.fit_transform(X_train)
        X_test_trans = self.preprocessor.transform(X_test)

        self.model.fit(X_train_trans, y_train)

        y_pred_log = self.model.predict(X_test_trans)
        y_pred = np.expm1(np.maximum(0, y_pred_log))
        y_true = np.expm1(y_test)

        metrics = evaluate_regression(y_true, y_pred)
        logger.info(f"Market Value Model ({self.model_type}) Evaluation: MAE={metrics['mae']:,.0f} EUR, RMSE={metrics['rmse']:,.0f} EUR, R2={metrics['r2']:.4f}")
        return metrics

    def predict_player_value(self, player_features: Dict[str, Any]) -> float:
        """Predicts player market value given feature dictionary."""
        df_single = pd.DataFrame([player_features])
        # Ensure all expected columns exist
        for col in self.numeric_features:
            if col not in df_single.columns:
                df_single[col] = 0.0
        for col in self.categorical_features:
            if col not in df_single.columns:
                df_single[col] = "Unknown"

        X_trans = self.preprocessor.transform(df_single[self.numeric_features + self.categorical_features])
        pred_log = self.model.predict(X_trans)[0]
        return float(np.expm1(max(0, pred_log)))
