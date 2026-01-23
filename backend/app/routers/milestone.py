"""
Milestone API router
Story 4.5: 周年纪念与主动回顾
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.milestone import Milestone
from app.services.milestone_service import MilestoneService
from app.tasks.milestone_check_task import run_milestone_check_now


router = APIRouter(
    prefix="/milestones",
    tags=["milestones"]
)


# Pydantic schemas

class MilestoneResponse(BaseModel):
    """Milestone response schema"""
    id: int
    milestone_type: str
    milestone_name: str
    message_content: str | None
    special_reward: str | None
    triggered_at: datetime
    is_claimed: bool
    days_count: int

    class Config:
        from_attributes = True

    @staticmethod
    def from_milestone(milestone: Milestone) -> "MilestoneResponse":
        """Convert Milestone model to response schema"""
        return MilestoneResponse(
            id=milestone.id,
            milestone_type=milestone.milestone_type,
            milestone_name=milestone.milestone_display_name,
            message_content=milestone.message_content,
            special_reward=milestone.special_reward,
            triggered_at=milestone.triggered_at,
            is_claimed=milestone.is_claimed,
            days_count=milestone.days_count,
        )


class NextMilestoneResponse(BaseModel):
    """Next milestone info response schema"""
    milestone_type: str
    milestone_name: str
    required_days: int
    current_days: int
    days_remaining: int


class ClaimMilestoneRequest(BaseModel):
    """Request to claim a milestone"""
    milestone_id: int = Field(..., description="Milestone ID to claim")


class MilestoneCheckResponse(BaseModel):
    """Response for milestone check operation"""
    users_checked: int
    milestones_created: int
    milestone_details: List[dict]


# API endpoints

@router.get("/me", response_model=List[MilestoneResponse])
def get_my_milestones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all milestones for current user

    Returns:
        List of user's milestones
    """
    milestone_service = MilestoneService(db)
    milestones = milestone_service.get_user_milestones(current_user.id)

    return [MilestoneResponse.from_milestone(m) for m in milestones]


@router.get("/me/unclaimed", response_model=List[MilestoneResponse])
def get_my_unclaimed_milestones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get unclaimed milestones for current user

    Returns:
        List of unclaimed milestones
    """
    milestone_service = MilestoneService(db)
    milestones = milestone_service.get_unclaimed_milestones(current_user.id)

    return [MilestoneResponse.from_milestone(m) for m in milestones]


@router.get("/me/next", response_model=NextMilestoneResponse | None)
def get_next_milestone(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about the next milestone user will reach

    Returns:
        Next milestone info or null if all milestones reached
    """
    milestone_service = MilestoneService(db)
    next_milestone = milestone_service.get_next_milestone_info(current_user.id)

    if next_milestone:
        return NextMilestoneResponse(**next_milestone)

    return None


@router.post("/me/claim")
def claim_milestone(
    request: ClaimMilestoneRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a milestone as claimed (user has viewed the celebration)

    Args:
        request: Milestone ID to claim

    Returns:
        Success message
    """
    milestone_service = MilestoneService(db)

    # Get milestone
    milestone = db.query(Milestone).filter(Milestone.id == request.milestone_id).first()

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    # Verify ownership
    if milestone.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to claim this milestone"
        )

    # Claim milestone
    milestone_service.claim_milestone(request.milestone_id)

    return {"message": "Milestone claimed successfully"}


@router.post("/check", response_model=MilestoneCheckResponse)
def check_milestones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually check and create milestones for current user

    This is primarily for testing. In production, milestones are checked
    automatically by the daily background task at 2:00 AM.

    Returns:
        List of newly created milestones
    """
    milestone_service = MilestoneService(db)
    newly_created = milestone_service.check_and_create_milestones_for_user(current_user.id)

    milestone_details = []
    for milestone in newly_created:
        milestone_details.append({
            'user_id': current_user.id,
            'milestone_type': milestone.milestone_type,
            'milestone_name': milestone.milestone_display_name,
            'message': milestone.message_content,
            'special_reward': milestone.special_reward,
        })

    return MilestoneCheckResponse(
        users_checked=1,
        milestones_created=len(newly_created),
        milestone_details=milestone_details
    )


@router.post("/check-all", response_model=MilestoneCheckResponse)
def check_all_milestones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger milestone check for ALL users (admin/testing only)

    This endpoint simulates the daily background task that runs at 2:00 AM.

    Note: In production, this should be protected with admin authentication.

    Returns:
        Statistics about the milestone check operation
    """
    # TODO: Add admin authentication check
    # For MVP, we allow any authenticated user to trigger this for testing

    result = run_milestone_check_now()

    return MilestoneCheckResponse(**result)


@router.get("/me/stats")
def get_milestone_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get milestone statistics for current user

    Returns:
        Dictionary with milestone stats
    """
    milestone_service = MilestoneService(db)

    # Get days since first conversation
    days_since = milestone_service.calculate_days_since_first_conversation(current_user.id)

    if days_since is None:
        return {
            'days_since_first_conversation': 0,
            'total_milestones': 0,
            'unclaimed_milestones': 0,
            'next_milestone': None
        }

    # Get milestone counts
    all_milestones = milestone_service.get_user_milestones(current_user.id)
    unclaimed_milestones = milestone_service.get_unclaimed_milestones(current_user.id)
    next_milestone = milestone_service.get_next_milestone_info(current_user.id)

    return {
        'days_since_first_conversation': days_since,
        'total_milestones': len(all_milestones),
        'unclaimed_milestones': len(unclaimed_milestones),
        'next_milestone': next_milestone
    }
