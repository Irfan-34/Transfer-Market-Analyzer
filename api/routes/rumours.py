from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from api.dependencies import get_db
from api.schemas import RumourResponse
from src.data.schema import Rumour, RumourStatus

router = APIRouter(prefix="/rumours", tags=["Rumours"])


@router.get("", response_model=List[RumourResponse])
def get_all_rumours(
    status: str = Query(None, description="Filter by status (RUMOUR, CONFIRMED, SPECULATION, DENIED)"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Rumour)
    if status:
        query = query.filter(Rumour.status == status.upper())
    rumours = query.order_by(Rumour.created_at.desc()).limit(limit).all()
    return rumours


@router.get("/hot", response_model=List[RumourResponse])
def get_hot_rumours(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    rumours = db.query(Rumour).filter(
        Rumour.confidence_score >= 0.50
    ).order_by(Rumour.confidence_score.desc(), Rumour.created_at.desc()).limit(limit).all()
    return rumours
