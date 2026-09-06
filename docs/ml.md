# Machine Learning Documentation

This document describes the design, features, validation strategy, and metrics for the three core ML models in the Transfer Market Analyzer.

---

## 1. Market Value Prediction Model
- **Goal**: Estimate player market value in EUR.
- **Target Variable**: `np.log1p(market_value_in_eur)`.
- **Features**: Age, position, total appearances, goals, assists, minutes, peak valuation recorded, average valuation, transfer count, max fee paid.
- **Evaluated Algorithms**: Baseline (DummyRegressor, Ridge), Random Forest, XGBoost.
- **Metrics**: MAE, RMSE, $R^2$.

---

## 2. Transfer Fee Prediction Model
- **Goal**: Estimate expected transfer fee and confidence range.
- **Data Split**: Time-indexed split (train on historical seasons, test on recent window) to eliminate temporal data leakage.
- **Features**: Market valuation at transfer, age, position, selling club tier, buying club tier.
- **Output**: Expected fee, lower bound, upper bound, confidence classification.

---

## 3. Transfer Probability Model ($P(\text{Transfer})$)
- **Goal**: Estimate likelihood of player transferring to target buying club.
- **Dataset Construction**:
  - **Positive Examples**: Historical completed player -> club transfers.
  - **Negative Examples**: Synthetic plausible player-club pairs where transfer did not occur.
- **Evaluated Algorithms**: Logistic Regression baseline, Random Forest, XGBoost Classifier.
- **Evaluation Metrics**: ROC-AUC, PR-AUC, Brier Score, Log Loss.
- **Rumour Calibration**: Probabilities are dynamically calibrated when reliable media reports exist.
