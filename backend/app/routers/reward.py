"""
Reward API router
Story 6.3: 等级特权与里程碑奖励
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.reward_service import RewardService
from app.routers.auth import get_current_user


router = APIRouter(prefix="/rewards", tags=["rewards"])


# Response models
class RewardResponse(BaseModel):
    """Response model for reward information"""
    id: int
    level: int
    reward_type: str
    reward_type_display: str
    reward_content: dict
    description: str
    created_at: str
    is_unlocked: bool
    unlocked_at: Optional[str] = None
    is_viewed: bool = False
    is_new: bool = False

    class Config:
        from_attributes = True


class UserRewardResponse(BaseModel):
    """Response model for user's unlocked reward"""
    id: int
    user_id: int
    reward_id: int
    conversation_id: int
    unlocked_at: str
    is_viewed: bool
    viewed_at: Optional[str] = None
    is_new: bool
    days_since_unlock: int
    reward: Optional[dict] = None

    class Config:
        from_attributes = True


class ActiveNicknameResponse(BaseModel):
    """Response model for active nickname"""
    has_nickname: bool
    nickname: Optional[str] = None


class MarkViewedResponse(BaseModel):
    """Response model for marking reward as viewed"""
    success: bool
    message: str


@router.get("", response_model=List[RewardResponse])
def get_all_rewards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all rewards with locked/unlocked status for current user

    Returns list of all rewards showing:
    - Reward details (level, type, description)
    - Whether user has unlocked it
    - If unlocked: unlock time, viewed status, is_new flag
    """
    reward_service = RewardService(db)
    rewards = reward_service.get_all_rewards_with_status(current_user.id)

    return [RewardResponse(**reward) for reward in rewards]


@router.get("/unlocked", response_model=List[UserRewardResponse])
def get_unlocked_rewards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all rewards unlocked by current user

    Returns only the rewards the user has unlocked, ordered by unlock time (newest first)
    """
    reward_service = RewardService(db)
    user_rewards = reward_service.get_user_unlocked_rewards(current_user.id)

    return [
        UserRewardResponse(**ur.to_dict(include_reward_details=True))
        for ur in user_rewards
    ]


@router.get("/active-nickname", response_model=ActiveNicknameResponse)
def get_active_nickname(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get active nickname for current user

    Returns the nickname from the highest-level unlocked nickname reward
    Used by AI to address user in conversations
    """
    reward_service = RewardService(db)
    nickname = reward_service.get_active_nickname(current_user.id)

    return ActiveNicknameResponse(
        has_nickname=nickname is not None,
        nickname=nickname
    )


@router.get("/{reward_id}", response_model=RewardResponse)
def get_reward_details(
    reward_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific reward details

    Returns detailed information about a specific reward
    If the reward is unlocked, includes unlock and view status
    If locked, returns reward info without unlock details
    """
    reward_service = RewardService(db)

    # Get the reward
    reward = reward_service.get_reward_by_id(reward_id)
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reward {reward_id} not found"
        )

    # Check if user has unlocked it
    user_reward = reward_service.get_user_reward_by_id(current_user.id, reward_id)

    reward_dict = reward.to_dict()

    if user_reward:
        # Reward is unlocked
        reward_dict['is_unlocked'] = True
        reward_dict['unlocked_at'] = user_reward.unlocked_at.isoformat()
        reward_dict['is_viewed'] = user_reward.is_viewed
        reward_dict['is_new'] = user_reward.is_new
    else:
        # Reward is locked
        reward_dict['is_unlocked'] = False
        reward_dict['unlocked_at'] = None
        reward_dict['is_viewed'] = False
        reward_dict['is_new'] = False

    return RewardResponse(**reward_dict)


@router.put("/{reward_id}/view", response_model=MarkViewedResponse)
def mark_reward_as_viewed(
    reward_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a reward as viewed by user

    Updates the is_viewed flag and sets viewed_at timestamp
    Used when user opens the reward details screen
    """
    reward_service = RewardService(db)

    success = reward_service.mark_reward_as_viewed(current_user.id, reward_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reward {reward_id} not found or not unlocked for user"
        )

    return MarkViewedResponse(
        success=True,
        message="Reward marked as viewed"
    )


@router.get("/check-feature/{feature_name}", response_model=dict)
def check_feature_access(
    feature_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user has unlocked a specific feature

    Used for feature access control (e.g., video calls, voice messages, etc.)
    """
    reward_service = RewardService(db)
    has_access = reward_service.has_feature_unlocked(current_user.id, feature_name)

    return {
        'feature_name': feature_name,
        'has_access': has_access
    }
