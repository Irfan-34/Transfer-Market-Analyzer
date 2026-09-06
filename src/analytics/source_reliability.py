from typing import List, Dict, Any
from src.data.db import SessionLocal
from src.data.schema import SourceReliability
from src.utils.logging import get_logger

logger = get_logger("analytics.source_reliability")


def get_all_source_reliabilities() -> List[Dict[str, Any]]:
    """Retrieves all tracked news sources and their reliability scores."""
    session = SessionLocal()
    try:
        sources = session.query(SourceReliability).order_by(SourceReliability.reliability_score.desc()).all()
        result = []
        for s in sources:
            result.append({
                "source_name": s.source_name,
                "rumours_reported": s.rumours_reported,
                "confirmed_outcomes": s.confirmed_outcomes,
                "false_rumours": s.false_rumours,
                "accuracy_rate": round(s.accuracy_rate, 4),
                "reliability_score": round(s.reliability_score, 4),
                "last_updated": s.last_updated.isoformat() if s.last_updated else None
            })
        return result
    finally:
        session.close()


def update_source_reliability(source_name: str, was_confirmed: bool):
    """Updates a source's track record and recomputes its reliability score using Laplace smoothing prior."""
    session = SessionLocal()
    try:
        source = session.query(SourceReliability).filter(
            SourceReliability.source_name == source_name
        ).first()

        if not source:
            source = SourceReliability(source_name=source_name, rumours_reported=0, confirmed_outcomes=0, false_rumours=0)
            session.add(source)

        source.rumours_reported += 1
        if was_confirmed:
            source.confirmed_outcomes += 1
        else:
            source.false_rumours += 1

        # Accuracy rate
        raw_accuracy = source.confirmed_outcomes / max(1, source.rumours_reported)
        source.accuracy_rate = raw_accuracy

        # Empirical Bayesian / Laplace smoothing prior (prior alpha=5, beta=5)
        # Prevents 1/1 from giving 1.0 reliability score
        prior_alpha = 5
        prior_beta = 5
        smoothed_score = (source.confirmed_outcomes + prior_alpha) / (source.rumours_reported + prior_alpha + prior_beta)
        source.reliability_score = smoothed_score

        session.commit()
        logger.info(f"Updated reliability for {source_name}: Score = {smoothed_score:.4f} ({source.confirmed_outcomes}/{source.rumours_reported})")
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating source reliability for {source_name}: {e}")
    finally:
        session.close()
