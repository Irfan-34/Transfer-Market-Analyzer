import sys
import uvicorn
from src.utils.config import config
from src.utils.logging import get_logger
from src.data.init_db import init_database
from src.data.monitor import run_ingestion_cycle

logger = get_logger("main")


def main():
    print("=" * 60)
    print("⚽ World Football Transfer Market Intelligence Platform")
    print("=" * 60)

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "init-db":
            logger.info("Initializing application database...")
            init_database()
            print("Database initialized successfully.")
            return
        elif cmd == "ingest":
            logger.info("Running single news ingestion cycle...")
            run_ingestion_cycle()
            print("Ingestion cycle complete.")
            return
        elif cmd == "test":
            import pytest
            sys.exit(pytest.main(["tests/"]))

    logger.info(f"Starting FastAPI server on http://{config.API_HOST}:{config.API_PORT}...")
    uvicorn.run("api.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)


if __name__ == "__main__":
    main()