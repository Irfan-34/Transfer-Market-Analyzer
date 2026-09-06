# ⚽ World Football Transfer Market Analyzer

A complete, end-to-end **Football Transfer Market Intelligence Platform** that analyzes historical Transfermarkt data, ingests current news and rumours, tracks player/club analytics, and generates ML-powered transfer predictions (market value, expected fee, and transfer probability).

---

## 🏗️ Architecture Overview

```
                                  DATA SOURCES
   ┌───────────────────────┬────────────────────────┬──────────────────────┐
   │ Historical Transfer-  │ Current Football APIs /│ Public News & RSS    │
   │ markt DuckDB Data     │ Public Feeds           │ Transfer Rumours     │
   └───────────┬───────────┴───────────┬────────────┴───────────┬──────────┘
               │                       │                        │
               └───────────────────────┼────────────────────────┘
                                       ▼
                              Data Ingestion Engine
                         (Cleaning, Deduplication, Normalization)
                                       │
                                       ▼
                       Storage & Analytical Query Layer
                     (DuckDB Analytical DB / Relational App DB)
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
             Analytics Engine                       ML Pipeline
   (Player, Club, Market Indicators)       (Value, Fee, Transfer Probabilities)
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       ▼
                                FastAPI Backend
                        (REST APIs, Analytics, Inference)
                                       │
                                       ▼
                            React + Vite Dashboard
                   (Interactive Analytics, Rumours, Predictions)
```

---

## ✨ Features

- **Historical Analytical Engine**: Leverages 175k+ transfer records, 50k+ players, 650k+ valuation snapshots, and 1.8M+ appearance records.
- **Player & Club Analytics**: In-depth profiling, net transfer spend, performance metrics, and squad valuation trends.
- **Machine Learning Suite**:
  - **Player Market Value Prediction**: Evaluates historical performance and trajectory using Random Forest & XGBoost.
  - **Expected Transfer Fee Model**: Estimates fee range based on contract status, age, position, and market benchmarks.
  - **Transfer Probability Model ($P(\text{Transfer})$)**: Estimates likelihood of a specific player moving to a target buying club.
- **News & Rumour Pipeline**: RSS ingestion, article hashing, entity extraction (player/club matching), and status classification (Confirmed, Rumour, Speculation, Denied).
- **Source Reliability System**: Empirically computes reliability scores based on past accuracy.
- **Real-Time Monitoring**: Autonomous background polling job to ingest feeds and update predictions.
- **FastAPI REST API**: Fully documented OpenAPI endpoints with Pydantic validations, pagination, and robust error handling.
- **React Dashboard**: Modern, glassmorphism UI built with Vite, Tailwind/Vanilla CSS, Lucide icons, and interactive charts.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.13+
- Node.js 18+ (for frontend dashboard)
- DuckDB (`data/raw/transfermarkt.duckdb`)

### 2. Backend Setup
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn api.main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd dashboard
npm install
npm run dev
```
Dashboard will run at `http://localhost:5173`.

### 4. Running Tests
```bash
pytest tests/
```

---

## 📁 Repository Structure

```
TM_ANALYZER/
├── api/                  # FastAPI web server & route handlers
├── config/               # Settings & environment configuration
├── dashboard/            # React + Vite frontend application
├── data/                 # Raw DuckDB & processed datasets
│   ├── raw/
│   ├── processed/
│   └── external/
├── docs/                 # System architecture, API docs & data dictionary
├── notebooks/            # Exploratory data analysis notebooks
├── src/                  # Core Python modules
│   ├── analytics/        # Business logic for player, club & market stats
│   ├── data/             # Ingestion, db connections & validators
│   ├── features/         # Feature engineering for ML models
│   ├── models/           # Market value, fee & probability models
│   └── utils/            # Logging, dates & common helpers
├── tests/                # Unit & integration tests
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-container orchestration
├── main.py               # Application CLI entrypoint
└── requirements.txt      # Python dependencies
```

---

## 🔒 Data & Ethical Principles
1. **Factual vs. Predicted**: Predictions are probabilistic estimates, clearly demarcated from confirmed transfers.
2. **No Aggressive Scraping**: Uses public APIs, RSS feeds, and standard datasets.
3. **Audit Trail**: Every news article and rumour retains source URL, ingestion timestamp, and entity matching confidence.