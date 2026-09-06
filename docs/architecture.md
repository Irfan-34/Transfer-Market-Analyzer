# System Architecture

The World Football Transfer Market Analyzer is structured into a modular, decoupled data intelligence pipeline.

## 1. Storage Layers
- **Analytical Engine (DuckDB)**: Embedded OLAP engine managing 175k+ historical transfer events, 50k+ players, 650k+ market valuations, and 1.8M+ appearances.
- **Application Engine (SQLAlchemy / SQLite / PostgreSQL)**: OLTP store managing real-time news articles, transfer rumours, source reliability track records, and prediction audit logs.

## 2. Ingestion & Feature Pipelines
- **News Ingestion Engine**: Periodically polls RSS feeds (BBC, Sky, Guardian), computes SHA-256 content hashes for deduplication, extracts player/club entities, and assigns rumour status.
- **Feature Engineering Modules**:
  - `player_features.py`: Aggregates performance, appearance minutes, valuation growth, and transfer counts.
  - `club_features.py`: Computes squad market value, total spend, total income, and net transfer balance.
  - `transfer_features.py`: Prepares time-indexed historical transfer records.

## 3. Machine Learning Models
- **Market Value Model**: XGBoost / Random Forest predicting `market_value_in_eur`.
- **Transfer Fee Model**: Predicts expected transfer fee and fee range.
- **Transfer Probability Model ($P(\text{Transfer})$)**: Estimates likelihood of a specific player moving to a target buying club.

## 4. API & UI Layer
- **FastAPI Server**: Asynchronous REST API providing OpenAPI documentation and Pydantic v2 validation.
- **React Dashboard**: Modern Vite-powered glassmorphic frontend with interactive Recharts visualizations.
