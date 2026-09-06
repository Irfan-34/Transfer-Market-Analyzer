import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file if available
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Config:
    PROJECT_NAME: str = "World Football Transfer Market Analyzer"
    VERSION: str = "1.0.0"

    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    EXTERNAL_DATA_DIR: Path = DATA_DIR / "external"

    # Databases
    DUCKDB_PATH: Path = RAW_DATA_DIR / "transfermarkt.duckdb"
    
    # Relational Database (PostgreSQL or SQLite fallback for application data)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DATA_DIR}/processed/app_database.db"
    )

    # API Configuration
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")

    # Real-Time & News Ingestion
    POLL_INTERVAL_SECONDS: int = int(os.getenv("POLL_INTERVAL_SECONDS", 300))
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


config = Config()
