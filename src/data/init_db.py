from src.data.db import engine, SessionLocal
from src.data.schema import Base, SourceReliability
from src.utils.logging import get_logger
from datetime import datetime

logger = get_logger("data.init_db")


def init_database():
    """Initializes schema tables and seeds baseline data."""
    logger.info("Initializing relational database tables...")
    Base.metadata.create_all(bind=engine)

    # Seed initial known media sources if empty
    session = SessionLocal()
    try:
        count = session.query(SourceReliability).count()
        if count == 0:
            logger.info("Seeding baseline source reliability records...")
            baseline_sources = [
                SourceReliability(source_name="BBC Sport", rumours_reported=50, confirmed_outcomes=42, false_rumours=8, accuracy_rate=0.84, reliability_score=0.82),
                SourceReliability(source_name="Sky Sports", rumours_reported=65, confirmed_outcomes=50, false_rumours=15, accuracy_rate=0.77, reliability_score=0.75),
                SourceReliability(source_name="Fabrizio Romano", rumours_reported=120, confirmed_outcomes=110, false_rumours=10, accuracy_rate=0.92, reliability_score=0.90),
                SourceReliability(source_name="The Athletic", rumours_reported=40, confirmed_outcomes=34, false_rumours=6, accuracy_rate=0.85, reliability_score=0.83),
                SourceReliability(source_name="L'Équipe", rumours_reported=35, confirmed_outcomes=25, false_rumours=10, accuracy_rate=0.71, reliability_score=0.69),
                SourceReliability(source_name="BILD", rumours_reported=30, confirmed_outcomes=21, false_rumours=9, accuracy_rate=0.70, reliability_score=0.68),
                SourceReliability(source_name="Marca", rumours_reported=45, confirmed_outcomes=27, false_rumours=18, accuracy_rate=0.60, reliability_score=0.58),
                SourceReliability(source_name="Daily Mail", rumours_reported=80, confirmed_outcomes=32, false_rumours=48, accuracy_rate=0.40, reliability_score=0.42),
            ]
            session.add_all(baseline_sources)
            session.commit()
            logger.info("Baseline source reliability records seeded successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error initializing DB: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    init_database()
