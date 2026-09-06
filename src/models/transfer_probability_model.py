import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from src.data.db import query_duckdb
from src.models.preprocessing import build_preprocessing_pipeline, create_time_based_split
from src.models.evaluation import evaluate_classification
from src.utils.logging import get_logger

logger = get_logger("models.transfer_probability_model")


def generate_prob_training_dataset(sample_negatives: int = 15000) -> pd.DataFrame:
    """Creates historical positive transfer examples and synthetic plausible negative pairs."""
    pos_query = """
    SELECT 
        t.player_id,
        p.name as player_name,
        p.position,
        p.market_value_in_eur as player_market_value,
        t.from_club_id as current_club_id,
        t.to_club_id as buying_club_id,
        t.transfer_date,
        1 as transferred
    FROM transfers t
    JOIN players p ON t.player_id = p.player_id
    WHERE t.from_club_id IS NOT NULL AND t.to_club_id IS NOT NULL
    LIMIT 25000
    """
    pos_df = query_duckdb(pos_query)

    # Generate plausible negative examples by permuting buying clubs
    neg_df = pos_df.sample(n=min(sample_negatives, len(pos_df)), random_state=42).copy()
    shifted_clubs = np.random.choice(pos_df["buying_club_id"].values, size=len(neg_df))
    neg_df["buying_club_id"] = shifted_clubs
    # Ensure buying club != current club for negatives
    neg_df = neg_df[neg_df["buying_club_id"] != neg_df["current_club_id"]].copy()
    neg_df["transferred"] = 0

    full_df = pd.concat([pos_df, neg_df], ignore_index=True)
    full_df["player_market_value"] = full_df["player_market_value"].fillna(0.0).astype(float)
    full_df["position"] = full_df["position"].fillna("Unknown").str.title()
    return full_df


class TransferProbabilityModel:
    def __init__(self, model_type: str = "xgboost"):
        self.model_type = model_type
        self.numeric_features = ["player_market_value"]
        self.categorical_features = ["position"]
        self.preprocessor = build_preprocessing_pipeline(self.numeric_features, self.categorical_features)
        
        if model_type == "logistic":
            self.model = LogisticRegression(max_iter=500)
        elif model_type == "random_forest":
            self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        else:
            self.model = XGBClassifier(n_estimators=100, learning_rate=0.08, max_depth=6, random_state=42)

    def train_and_evaluate(self) -> Dict[str, Any]:
        """Trains binary classification model for transfer probability estimation."""
        logger.info(f"Training Transfer Probability Model ({self.model_type})...")
        df = generate_prob_training_dataset()
        df = df.dropna(subset=["transfer_date"])

        train_df, test_df = create_time_based_split(df, date_col="transfer_date", test_ratio=0.2)

        X_train = train_df[self.numeric_features + self.categorical_features]
        y_train = train_df["transferred"]

        X_test = test_df[self.numeric_features + self.categorical_features]
        y_test = test_df["transferred"]

        X_train_trans = self.preprocessor.fit_transform(X_train)
        X_test_trans = self.preprocessor.transform(X_test)

        self.model.fit(X_train_trans, y_train)

        y_prob = self.model.predict_proba(X_test_trans)[:, 1]

        metrics = evaluate_classification(y_test.values, y_prob)
        logger.info(f"Transfer Probability Model ({self.model_type}) Evaluation: ROC-AUC={metrics['roc_auc']:.4f}, PR-AUC={metrics['pr_auc']:.4f}, Brier={metrics['brier_score']:.4f}")
        return metrics

    def predict_probability(self, player_market_value: float, position: str, rumour_bonus: float = 0.0) -> Dict[str, Any]:
        """Predicts transfer probability P(transfer) given player context and optional rumour multiplier."""
        input_df = pd.DataFrame([{
            "player_market_value": float(player_market_value or 0.0),
            "position": str(position or "Unknown").title()
        }])
        X_trans = self.preprocessor.transform(input_df[self.numeric_features + self.categorical_features])
        base_prob = float(self.model.predict_proba(X_trans)[0, 1])

        # Adjust calibrated probability with rumour evidence bonus
        calibrated_prob = min(0.98, max(0.01, base_prob + rumour_bonus))

        confidence = "HIGH" if calibrated_prob >= 0.70 or calibrated_prob <= 0.15 else "MEDIUM"
        return {
            "transfer_probability": round(calibrated_prob, 4),
            "confidence": confidence,
            "base_probability": round(base_prob, 4)
        }
