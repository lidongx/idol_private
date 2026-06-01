"""
Daily Ritual API Router
Story 5.3: 每日仪式（早安/运势/晚安）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import date
from pydantic import BaseModel

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.daily_ritual_service import DailyRitualService
from app.services.fortune_service import FortuneService


router = APIRouter(prefix="/api/v1/rituals", tags=["rituals"])


# Pydantic schemas
class RitualStatusResponse(BaseModel):
    """Ritual status response schema"""
    date: str
    morning_greeting: Dict
    fortune: Dict
    night_greeting: Dict


class MorningGreetingRequest(BaseModel):
    """Morning greeting request schema"""
    idol_id: int


class NightGreetingRequest(BaseModel):
    """Night greeting request schema"""
    idol_id: int


class FortuneRequest(BaseModel):
    """Fortune request schema"""
    idol_id: int


@router.get("/status", response_model=RitualStatusResponse)
def get_ritual_status(
    ritual_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ritual completion status for current user

    Query params:
    - ritual_date: Date in YYYY-MM-DD format (default: today)

    Returns ritual status for morning greeting, fortune, and night greeting
    """
    service = DailyRitualService(db)

    # Parse date if provided
    target_date = None
    if ritual_date:
        try:
            target_date = date.fromisoformat(ritual_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

    status_data = service.check_ritual_status(current_user.id, target_date)

    return status_data


@router.post("/morning-greeting")
async def complete_morning_greeting(
    request: MorningGreetingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete morning greeting ritual

    Body:
    - idol_id: Idol ID

    Returns:
    - success: bool
    - message: str
    - greeting: str (偶像的早安问候)
    - exp_reward: int (经验值奖励)
    - ritual_id: int

    Time window: 7:00-9:00
    """
    service = DailyRitualService(db)

    try:
        result = service.complete_morning_greeting(
            user_id=current_user.id,
            idol_id=request.idol_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/night-greeting")
async def complete_night_greeting(
    request: NightGreetingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete night greeting ritual

    Body:
    - idol_id: Idol ID

    Returns:
    - success: bool
    - message: str
    - greeting: str (偶像的晚安问候)
    - exp_reward: int (经验值奖励)
    - ritual_id: int

    Time window: 22:00-24:00
    """
    service = DailyRitualService(db)

    try:
        result = service.complete_night_greeting(
            user_id=current_user.id,
            idol_id=request.idol_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/fortune")
async def get_daily_fortune(
    request: FortuneRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get/Generate daily fortune

    Body:
    - idol_id: Idol ID

    Returns:
    - success: bool
    - message: str
    - fortune: {
        score: int (0-100),
        level: str (大吉/吉/中吉/小吉/末吉/凶),
        level_emoji: str,
        description: str (AI生成的运势描述),
        lucky_color: str,
        lucky_number: int,
        lucky_direction: str,
        lucky_item: str,
        advice: {
          career: str,
          love: str,
          health: str,
          wealth: str
        }
      }
    - exp_reward: int (经验值奖励，重复查看为0)
    - ritual_id: int
    - already_checked: bool (是否已查看过)

    Time window: 全天（但每天只能查看一次，重复查看返回相同结果）
    """
    service = FortuneService(db)

    try:
        result = await service.generate_fortune(
            user_id=current_user.id,
            idol_id=request.idol_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/history")
def get_ritual_history(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ritual history for current user

    Query params:
    - limit: Number of days to retrieve (default: 30)

    Returns list of ritual records grouped by date
    """
    service = DailyRitualService(db)
    history = service.get_user_ritual_history(current_user.id, limit)

    return {
        'user_id': current_user.id,
        'history': history,
        'limit': limit
    }


@router.get("/stats")
def get_ritual_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ritual statistics for current user

    Returns:
    - total_rituals: int (总仪式次数)
    - morning_greetings: int (早安问候次数)
    - fortunes: int (运势查看次数)
    - night_greetings: int (晚安问候次数)
    - total_exp_earned: int (总获得经验值)
    - current_streak: int (当前连续天数)
    - longest_streak: int (最长连续天数)
    """
    service = DailyRitualService(db)
    stats = service.get_ritual_stats(current_user.id)

    return {
        'user_id': current_user.id,
        'stats': stats
    }


@router.get("/fortune/history")
def get_fortune_history(
    fortune_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get fortune for a specific date

    Query params:
    - fortune_date: Date in YYYY-MM-DD format (default: today)

    Returns fortune data if it exists, or null if not found
    """
    service = FortuneService(db)

    # Parse date if provided
    target_date = date.today()
    if fortune_date:
        try:
            target_date = date.fromisoformat(fortune_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

    fortune = service.get_fortune_for_date(current_user.id, target_date)

    if fortune:
        return fortune
    else:
        return {
            'date': target_date.isoformat(),
            'fortune': None,
            'message': '该日期没有运势记录'
        }
