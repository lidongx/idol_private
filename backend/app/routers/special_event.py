"""
Special Event API Router
Story 5.5: 特殊事件与互动彩蛋
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.special_event_service import SpecialEventService


router = APIRouter(prefix="/api/v1/events", tags=["special_events"])


@router.get("/history")
def get_event_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get special event history for current user

    Query params:
    - limit: Number of records to retrieve (default: 20)

    Returns list of triggered events
    """
    service = SpecialEventService(db)
    history = service.get_user_event_history(current_user.id, limit)

    return {
        'user_id': current_user.id,
        'events': history,
        'limit': limit
    }


@router.get("/stats")
def get_event_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get special event statistics for current user

    Returns:
    - total_events: int (总事件次数)
    - by_type: dict (各类型事件次数)
    - total_exp_from_events: int (事件总经验值)
    - interaction_rate: float (互动率)
    """
    service = SpecialEventService(db)
    stats = service.get_event_stats(current_user.id)

    return {
        'user_id': current_user.id,
        'stats': stats
    }
