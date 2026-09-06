import time
from datetime import datetime
from src.data.db import SessionLocal
from src.data.schema import IngestionRun, Rumour
from src.data.news_ingestion import ingest_rss_news_feeds
from src.models.transfer_probability_model import TransferProbabilityModel
from src.utils.config import config
from src.utils.logging import get_logger

logger = get_logger("data.monitor")


def run_ingestion_cycle() -> IngestionRun:
    """Executes a single data polling and inference update cycle."""
    logger.info("Executing real-time transfer monitoring cycle...")
    session = SessionLocal()

    start_time = datetime.utcnow()
    res = ingest_rss_news_feeds()

    run_log = IngestionRun(
        source_type="RSS_TRANSFER_NEWS",
        items_ingested=res.get("articles_ingested", 0),
        status=res.get("status", "SUCCESS"),
        log_message=f"Ingested {res.get('articles_ingested', 0)} articles and extracted {res.get('rumours_extracted', 0)} rumours.",
        ran_at=start_time
    )

    try:
        session.add(run_log)
        session.commit()
        logger.info(f"Ingestion cycle completed successfully in {time.time() - start_time.timestamp():.2f} seconds.")
        return run_log
    except Exception as e:
        session.rollback()
        logger.error(f"Error logging ingestion run: {e}")
        raise e
    finally:
        session.close()


def start_monitor_daemon(interval_seconds: int = config.POLL_INTERVAL_SECONDS):
    """Runs a non-blocking background loop for monitoring news feeds."""
    logger.info(f"Starting Transfer Monitor Daemon with interval = {interval_seconds}s...")
    while True:
        try:
            run_ingestion_cycle()
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    run_ingestion_cycle()
