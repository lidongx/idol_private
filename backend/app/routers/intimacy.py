"""
Intimacy API Router
Story 6.1: 亲密度等级系统与经验值计算
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.services.intimacy_service import IntimacyService


router = APIRouter(prefix="/api/v1/intimacy", tags=["intimacy"])


# Pydantic schemas
class IntimacyInfoResponse(BaseModel):
    """Intimacy info response schema"""
    conversation_id: int
    current_level: int
    current_exp: int
    required_exp_for_next: int
    progress_percentage: float
    level_title: str
    total_exp_earned: int


class IntimacyHistoryItem(BaseModel):
    """Intimacy history item schema"""
    id: int
    exp_change: int
    reason: str
    reason_display: str
    new_level: int
    new_exp: int
    created_at: str


class IntimacyHistoryResponse(BaseModel):
    """Intimacy history response schema"""
    conversation_id: int
    history: List[IntimacyHistoryItem]
    total_count: int


class IntimacyStatsResponse(BaseModel):
    """Intimacy stats response schema"""
    conversation_id: int
    total_exp_gained: int
    exp_by_reason: Dict[str, int]
    level_ups: int
    days_active: int


@router.get(
    "/conversations/{conversation_id}",
    response_model=IntimacyInfoResponse,
    summary="获取亲密度信息",
    description="获取指定对话的亲密度等级、经验值和进度信息"
)
def get_intimacy_info(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get intimacy information for a conversation

    Returns:
    - Current level and exp
    - Progress percentage to next level
    - Level title (e.g., "新朋友", "恋人")
    - Total exp earned
    """
    try:
        intimacy_service = IntimacyService(db)
        info = intimacy_service.get_intimacy_info(conversation_id)

        return IntimacyInfoResponse(**info)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error fetching intimacy info for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取亲密度信息失败"
        )


@router.get(
    "/conversations/{conversation_id}/history",
    response_model=IntimacyHistoryResponse,
    summary="获取亲密度历史记录",
    description="获取亲密度经验值变化历史，支持分页"
)
def get_intimacy_history(
    conversation_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get intimacy exp change history

    Query params:
    - limit: Number of records to retrieve (default: 50, max: 100)

    Returns list of intimacy log records showing:
    - Exp changes
    - Reasons for changes
    - Level and exp after each change
    """
    try:
        # Limit max page size
        limit = min(limit, 100)

        intimacy_service = IntimacyService(db)
        history = intimacy_service.get_intimacy_history(conversation_id, limit)

        return IntimacyHistoryResponse(
            conversation_id=conversation_id,
            history=[IntimacyHistoryItem(**item) for item in history],
            total_count=len(history)
        )

    except Exception as e:
        print(f"Error fetching intimacy history for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取亲密度历史失败"
        )


@router.get(
    "/conversations/{conversation_id}/stats",
    response_model=IntimacyStatsResponse,
    summary="获取亲密度统计信息",
    description="获取亲密度的统计数据（总经验值、不同来源的经验值分布、升级次数等）"
)
def get_intimacy_stats(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get intimacy statistics

    Returns:
    - Total exp gained
    - Exp breakdown by reason (messages, rituals, likes, etc.)
    - Number of level ups
    - Days active
    """
    try:
        intimacy_service = IntimacyService(db)
        stats = intimacy_service.get_intimacy_stats(conversation_id)

        return IntimacyStatsResponse(**stats)

    except Exception as e:
        print(f"Error fetching intimacy stats for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取亲密度统计失败"
        )


# Story 6.5: 亲密度衰减与保持机制

class DecayHistoryItem(BaseModel):
    """Decay history item schema"""
    id: int
    conversation_id: int
    decay_amount: int
    reason: str
    reason_display: str
    intimacy_exp_before: int
    intimacy_exp_after: int
    created_at: str
    days_since_decay: int


class DecayHistoryResponse(BaseModel):
    """Decay history response schema"""
    conversation_id: int
    history: List[DecayHistoryItem]
    total_count: int


class ToggleDecayRequest(BaseModel):
    """Toggle decay request schema"""
    disabled: bool


class ToggleDecayResponse(BaseModel):
    """Toggle decay response schema"""
    conversation_id: int
    decay_disabled: bool
    message: str


class ComebackBonusResponse(BaseModel):
    """Comeback bonus response schema"""
    success: bool
    message: str
    exp_added: Optional[int] = None
    old_level: Optional[int] = None
    new_level: Optional[int] = None
    level_up: Optional[bool] = None
    reason: Optional[str] = None
    days_until_available: Optional[int] = None


@router.get(
    "/conversations/{conversation_id}/decay-history",
    response_model=DecayHistoryResponse,
    summary="获取亲密度衰减历史",
    description="获取对话的亲密度衰减记录"
)
def get_decay_history(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get intimacy decay history for a conversation

    Returns list of decay events showing:
    - When decay occurred
    - How much exp was lost
    - Reason for decay
    - Exp before and after
    """
    try:
        intimacy_service = IntimacyService(db)
        history = intimacy_service.get_decay_history(conversation_id)

        return DecayHistoryResponse(
            conversation_id=conversation_id,
            history=[DecayHistoryItem(**item) for item in history],
            total_count=len(history)
        )

    except Exception as e:
        print(f"Error fetching decay history for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取衰减历史失败"
        )


@router.put(
    "/conversations/{conversation_id}/toggle-decay",
    response_model=ToggleDecayResponse,
    summary="开启/关闭亲密度衰减",
    description="用户可以选择开启或关闭亲密度衰减（付费用户功能）"
)
def toggle_decay(
    conversation_id: int,
    request: ToggleDecayRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enable or disable intimacy decay for a conversation

    This can be used as a premium feature:
    - Free users: decay enabled by default
    - Premium users: can disable decay

    Body:
    - disabled: true to disable decay, false to enable
    """
    try:
        intimacy_service = IntimacyService(db)
        result = intimacy_service.toggle_decay(conversation_id, request.disabled)

        return ToggleDecayResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error toggling decay for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="切换衰减状态失败"
        )


@router.post(
    "/conversations/{conversation_id}/comeback-bonus",
    response_model=ComebackBonusResponse,
    summary="领取回归礼包",
    description="用户长时间未登录后回归，可以领取回归礼包（+50 exp）"
)
def claim_comeback_bonus(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Claim comeback bonus after being inactive

    Requirements:
    - User must have been inactive for 7+ days
    - Can only claim once every 30 days

    Returns:
    - +50 exp bonus
    - Welcome back message
    """
    try:
        intimacy_service = IntimacyService(db)
        result = intimacy_service.give_comeback_bonus(conversation_id)

        return ComebackBonusResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error giving comeback bonus for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="领取回归礼包失败"
        )
