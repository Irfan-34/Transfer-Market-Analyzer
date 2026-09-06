import pandas as pd
from typing import List, Dict, Any
from src.data.db import SessionLocal
from src.data.schema import Rumour, SourceReliability


def get_rumour_features_for_player(player_name: str, buying_club_name: str) -> Dict[str, Any]:
    """Calculates rumour count, distinct sources, and aggregate reliability weight for a specific player-club pair."""
    session = SessionLocal()
    try:
        rumours = session.query(Rumour).filter(
            Rumour.player_name.ilike(f"%{player_name}%"),
            Rumour.to_club_name.ilike(f"%{buying_club_name}%")
        ).all()

        if not rumours:
            return {
                "rumour_count": 0,
                "unique_sources": 0,
                "max_source_reliability": 0.5,
                "avg_source_reliability": 0.5,
                "has_reliable_report": False
            }

        sources = list(set([r.source_name for r in rumours if r.source_name]))
        reliability_records = session.query(SourceReliability).filter(
            SourceReliability.source_name.in_(sources)
        ).all()

        rel_map = {sr.source_name: sr.reliability_score for sr.reliability_records in [reliability_records] for sr in sr.reliability_records}
        rel_scores = [rel_map.get(s, 0.5) for s in sources]

        max_rel = max(rel_scores) if rel_scores else 0.5
        avg_rel = sum(rel_scores) / len(rel_scores) if rel_scores else 0.5

        return {
            "rumour_count": len(rumours),
            "unique_sources": len(sources),
            "max_source_reliability": max_rel,
            "avg_source_reliability": avg_rel,
            "has_reliable_report": max_rel >= 0.75
        }
    finally:
        session.close()
