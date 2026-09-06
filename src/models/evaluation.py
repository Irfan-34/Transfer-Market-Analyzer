import numpy as np
from typing import Dict, Any
from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
    r2_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    brier_score_loss,
    log_loss
)


def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Computes standard evaluation metrics for regression models."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2)
    }


def evaluate_classification(y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
    """Computes evaluation metrics for probabilistic classification models."""
    roc_auc = roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else 0.5
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(recall, precision) if len(np.unique(y_true)) > 1 else 0.5
    brier = brier_score_loss(y_true, y_prob)
    loss = log_loss(y_true, y_prob) if len(np.unique(y_true)) > 1 else 0.0

    return {
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "brier_score": float(brier),
        "log_loss": float(loss)
    }
