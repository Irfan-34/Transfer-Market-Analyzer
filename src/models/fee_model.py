import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from xgboost import XGBRegressor
from src.features.transfer_features import get_transfer_feature_dataset
from src.models.preprocessing import build_preprocessing_pipeline, create_time_based_split
from src.models.evaluation import evaluate_regression
from src.utils.logging import get_logger

logger = get_logger("models.fee_model")


class TransferFeeModel:
    def __init__(self):
        self.numeric_features = [
            "valuation_at_transfer", "age_at_transfer", "height_in_cm",
            "international_caps", "selling_club_market_value", "buying_club_market_value"
        ]
        self.categorical_features = ["position", "selling_league", "buying_league"]
        self.preprocessor = build_preprocessing_pipeline(self.numeric_features, self.categorical_features)
        self.model = XGBRegressor(n_estimators=120, learning_rate=0.07, max_depth=6, random_state=42)
        self.std_err = 0.0

    def train_and_evaluate(self) -> Dict[str, Any]:
        """Loads historical transfer dataset, performs time split, trains model and calculates prediction standard error."""
        logger.info("Training Transfer Fee Model...")
        df = get_transfer_feature_dataset()
        df = df[df["transfer_fee"] > 0]
        df = df.dropna(subset=["transfer_date"])

        train_df, test_df = create_time_based_split(df, date_col="transfer_date", test_ratio=0.2)

        X_train = train_df[self.numeric_features + self.categorical_features]
        y_train = np.log1p(train_df["transfer_fee"])

        X_test = test_df[self.numeric_features + self.categorical_features]
        y_test = test_df["transfer_fee"]

        X_train_trans = self.preprocessor.fit_transform(X_train)
        X_test_trans = self.preprocessor.transform(X_test)

        self.model.fit(X_train_trans, y_train)

        y_pred_log = self.model.predict(X_test_trans)
        y_pred = np.expm1(np.maximum(0, y_pred_log))

        metrics = evaluate_regression(y_test.values, y_pred)
        residuals = np.abs(y_test.values - y_pred)
        self.std_err = float(np.std(residuals))

        logger.info(f"Transfer Fee Model Evaluation: MAE={metrics['mae']:,.0f} EUR, RMSE={metrics['rmse']:,.0f} EUR, R2={metrics['r2']:.4f}")
        return metrics

    def predict_fee(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts expected transfer fee and lower/upper bound confidence range."""
        df_single = pd.DataFrame([input_data])
        for col in self.numeric_features:
            if col not in df_single.columns:
                df_single[col] = 0.0
        for col in self.categorical_features:
            if col not in df_single.columns:
                df_single[col] = "Unknown"

        X_trans = self.preprocessor.transform(df_single[self.numeric_features + self.categorical_features])
        pred_log = self.model.predict(X_trans)[0]
        expected_fee = float(np.expm1(max(0, pred_log)))

        range_delta = max(expected_fee * 0.25, 2_000_000.0)
        low_bound = max(0.0, expected_fee - range_delta)
        high_bound = expected_fee + range_delta

        return {
            "expected_fee_eur": round(expected_fee, 2),
            "fee_range_low_eur": round(low_bound, 2),
            "fee_range_high_eur": round(high_bound, 2),
            "confidence": "HIGH" if expected_fee > 5_000_000 else "MEDIUM"
        }
