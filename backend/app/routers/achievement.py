"""
Achievement API router
Story 6.4: 成就系统与每日互动奖励
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.achievement_service import AchievementService
from app.routers.auth import get_current_user


router = APIRouter(prefix="/achievements", tags=["achievements"])


# Response models
class AchievementResponse(BaseModel):
    """Response model for achievement information"""
    id: int
    achievement_name: str
    description: str
    achievement_type: str
    achievement_type_display: str
    condition_value: int
    reward_exp: int
    icon_url: str = None
    created_at: str = None
    progress: int = 0
    is_unlocked: bool = False
    unlocked_at: str = None
    is_viewed: bool = False
    is_new: bool = False
    completion_percentage: float = 0.0

    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    """Response model for user achievement with full details"""
    id: int
    user_id: int
    achievement_id: int
    progress: int
    is_unlocked: bool
    unlocked_at: str = None
    is_viewed: bool
    viewed_at: str = None
    is_new: bool
    completion_percentage: float
    days_since_unlock: int
    achievement: dict = None

    class Config:
        from_attributes = True


class MarkViewedResponse(BaseModel):
    """Response model for marking achievement as viewed"""
    success: bool
    message: str


class AchievementStatsResponse(BaseModel):
    """Response model for achievement statistics"""
    total_achievements: int
    unlocked_count: int
    locked_count: int
    new_count: int
    completion_rate: float


@router.get("", response_model=List[AchievementResponse])
def get_all_achievements(
    include_locked: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all achievements with user progress

    Returns list of all achievements showing:
    - Achievement details (name, description, type, condition)
    - User progress towards achievement
    - Whether unlocked, viewed, is new
    - Completion percentage

    Query params:
    - include_locked: Whether to include locked achievements (default: true)
    """
    achievement_service = AchievementService(db)
    achievements = achievement_service.get_user_achievements(
        current_user.id,
        include_locked=include_locked
    )

    return [AchievementResponse(**ach) for ach in achievements]


@router.get("/new", response_model=List[UserAchievementResponse])
def get_new_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get newly unlocked achievements that user hasn't viewed yet

    Returns only achievements that are:
    - Unlocked
    - Not yet viewed (is_new = true)

    Ordered by unlock time (newest first)
    """
    achievement_service = AchievementService(db)
    new_achievements = achievement_service.get_new_achievements(current_user.id)

    return [
        UserAchievementResponse(**ua.to_dict(include_achievement_details=True))
        for ua in new_achievements
    ]


@router.get("/stats", response_model=AchievementStatsResponse)
def get_achievement_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get achievement statistics for current user

    Returns:
    - Total number of achievements
    - Unlocked count
    - Locked count
    - New (unviewed) count
    - Overall completion rate
    """
    achievement_service = AchievementService(db)
    achievements = achievement_service.get_user_achievements(
        current_user.id,
        include_locked=True
    )

    total = len(achievements)
    unlocked = sum(1 for a in achievements if a['is_unlocked'])
    locked = total - unlocked
    new = sum(1 for a in achievements if a['is_new'])
    completion_rate = (unlocked / total * 100) if total > 0 else 0.0

    return AchievementStatsResponse(
        total_achievements=total,
        unlocked_count=unlocked,
        locked_count=locked,
        new_count=new,
        completion_rate=round(completion_rate, 1)
    )


@router.put("/{achievement_id}/view", response_model=MarkViewedResponse)
def mark_achievement_as_viewed(
    achievement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an achievement as viewed by user

    Updates the is_viewed flag and sets viewed_at timestamp
    Used when user opens achievement details or notification
    """
    achievement_service = AchievementService(db)

    success = achievement_service.mark_achievement_as_viewed(
        current_user.id,
        achievement_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Achievement {achievement_id} not found or not unlocked for user"
        )

    return MarkViewedResponse(
        success=True,
        message="Achievement marked as viewed"
    )


@router.post("/check-all", response_model=List[UserAchievementResponse])
def check_all_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger check for all achievement types

    Checks:
    - Message count achievements
    - Ritual count achievements
    - Fortune check achievements
    - Moment like achievements

    Returns list of newly unlocked achievements (if any)

    Note: This is primarily for testing. In production, achievements
    are checked automatically after relevant actions.
    """
    achievement_service = AchievementService(db)
    newly_unlocked = achievement_service.check_all_achievements(current_user.id)

    return [
        UserAchievementResponse(**ua.to_dict(include_achievement_details=True))
        for ua in newly_unlocked
    ]
