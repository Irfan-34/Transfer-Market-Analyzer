from fastapi import APIRouter
from typing import List, Dict, Any
from src.analytics.source_reliability import get_all_source_reliabilities

router = APIRouter(prefix="/sources", tags=["Source Reliability"])


@router.get("/reliability", response_model=List[Dict[str, Any]])
def get_source_reliability_track_record():
    return get_all_source_reliabilities()
