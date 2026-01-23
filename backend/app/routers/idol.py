"""
Idol API Router
Handles idol listing and details endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.idol import (
    IdolListResponse,
    IdolListItem,
    IdolDetailResponse,
    IdolResponse,
    ErrorResponse,
)
from app.models.idol import Idol
from app.services.idol_state_service import IdolStateService
from app.tasks.idol_state_update_task import run_idol_state_update_now
from app.services.idol_moment_service import IdolMomentService
from app.core.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter()


@router.get(
    "/idols",
    response_model=IdolListResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="获取所有活跃偶像列表",
    description="返回所有is_active=true的偶像，用于用户选择"
)
async def get_idols(db: Session = Depends(get_db)):
    """
    Get all active idols

    Returns a list of active idols with basic information.
    - Filters by is_active=true
    - Returns id, name, avatar_url, description, and hobbies as list
    - MVP: Returns only one idol (林雪晴)
    """
    try:
        # Query active idols
        idols = db.query(Idol).filter(Idol.is_active == True).all()

        # Transform to list items
        idol_items = []
        for idol in idols:
            # Parse hobbies from comma-separated string to list
            hobbies_list = []
            if idol.hobbies:
                hobbies_list = [h.strip() for h in idol.hobbies.split('、')]

            idol_item = IdolListItem(
                id=idol.id,
                name=idol.name,
                avatar_url=idol.avatar_url,
                description=idol.description,
                hobbies_list=hobbies_list,
            )
            idol_items.append(idol_item)

        return IdolListResponse(idols=idol_items)

    except Exception as e:
        print(f"Error fetching idols: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取偶像列表失败，请稍后重试"
        )


@router.get(
    "/idols/{idol_id}",
    response_model=IdolDetailResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Idol not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="获取偶像详细信息",
    description="根据ID获取单个偶像的完整信息"
)
async def get_idol_by_id(idol_id: int, db: Session = Depends(get_db)):
    """
    Get idol by ID

    Returns detailed information about a specific idol.
    - Returns 404 if idol not found or is_active=false
    - Excludes personality_prompt for security
    """
    try:
        # Query idol by ID
        idol = db.query(Idol).filter(
            Idol.id == idol_id,
            Idol.is_active == True
        ).first()

        if not idol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该偶像不存在或已下线"
            )

        # Convert to response model
        idol_response = IdolResponse(
            id=idol.id,
            name=idol.name,
            avatar_url=idol.avatar_url,
            description=idol.description,
            hobbies=idol.hobbies,
            background_story=idol.background_story,
            is_active=idol.is_active,
            created_at=idol.created_at,
        )

        return IdolDetailResponse(idol=idol_response)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching idol {idol_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取偶像信息失败，请稍后重试"
        )


@router.get(
    "/idols/{idol_id}/state",
    responses={
        404: {"model": ErrorResponse, "description": "Idol not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="获取偶像当前状态",
    description="获取偶像的实时状态（活动状态、心情、能量等级）"
)
async def get_idol_state(idol_id: int, db: Session = Depends(get_db)):
    """
    Get idol's current state (Story 5.1)

    Returns idol's current life state including:
    - Status (working, resting, active, sleeping, etc.)
    - Mood (happy, calm, tired, excited, etc.)
    - Energy level (0-100)
    - Status message
    - Availability for conversation
    """
    try:
        # Verify idol exists and is active
        idol = db.query(Idol).filter(
            Idol.id == idol_id,
            Idol.is_active == True
        ).first()

        if not idol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该偶像不存在或已下线"
            )

        # Get idol state
        idol_state_service = IdolStateService(db)
        state_info = idol_state_service.get_state_display_info(idol_id)

        # Initialize state if doesn't exist
        if not state_info:
            idol_state_service.initialize_idol_state(idol_id)
            state_info = idol_state_service.get_state_display_info(idol_id)

        return state_info

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching idol state for {idol_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取偶像状态失败，请稍后重试"
        )


@router.post(
    "/idols/state/update-all",
    summary="手动更新所有偶像状态（测试用）",
    description="手动触发偶像状态更新任务，正常情况下由后台任务每小时自动执行"
)
async def trigger_state_update():
    """
    Manually trigger idol state update for all idols (testing/admin)

    In production, this is automatically done by the hourly background task.
    """
    try:
        result = run_idol_state_update_now()
        return result

    except Exception as e:
        print(f"Error triggering idol state update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新偶像状态失败"
        )


# Pydantic schemas for moments
class CreateMomentRequest(BaseModel):
    """Request schema for creating a moment"""
    content: str = Field(..., max_length=300, description="Moment content, max 300 characters")
    image_url: str | None = Field(None, description="Optional image URL")


class LikeMomentResponse(BaseModel):
    """Response schema for like/unlike action"""
    action: str = Field(..., description="'liked' or 'unliked'")
    likes_count: int = Field(..., description="Current like count")


@router.get(
    "/idols/{idol_id}/moments",
    summary="获取偶像朋友圈列表",
    description="获取偶像的朋友圈动态列表，支持分页"
)
async def get_idol_moments(
    idol_id: int,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get idol moments list (Story 5.2)

    Returns list of moments with:
    - Moment content and image
    - Like count
    - Posted time (relative)
    - User's like status
    """
    try:
        # Verify idol exists and is active
        idol = db.query(Idol).filter(
            Idol.id == idol_id,
            Idol.is_active == True
        ).first()

        if not idol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该偶像不存在或已下线"
            )

        # Get moments with like status
        moment_service = IdolMomentService(db)
        moments = moment_service.get_moments_with_like_status(
            idol_id=idol_id,
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )

        return {
            'idol_id': idol_id,
            'idol_name': idol.name,
            'idol_avatar': idol.avatar_url,
            'moments': moments,
            'total': moment_service.get_moment_count(idol_id),
            'limit': limit,
            'offset': offset
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching idol moments for {idol_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取朋友圈失败，请稍后重试"
        )


@router.post(
    "/idols/moments/{moment_id}/like",
    response_model=LikeMomentResponse,
    summary="点赞/取消点赞朋友圈",
    description="点赞或取消点赞偶像朋友圈动态"
)
async def like_moment(
    moment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Like or unlike a moment (Story 5.2)

    - If not liked: add like
    - If already liked: remove like (unlike)
    - Returns action taken and current like count
    """
    try:
        moment_service = IdolMomentService(db)

        # Like/unlike the moment
        result = moment_service.like_moment(moment_id, current_user.id)

        return LikeMomentResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error liking moment {moment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="操作失败，请稍后重试"
        )


@router.post(
    "/idols/{idol_id}/moments",
    summary="发布朋友圈（管理员/测试用）",
    description="创建新的朋友圈动态，用于测试或运营发布"
)
async def create_moment(
    idol_id: int,
    request: CreateMomentRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new moment (admin/testing)

    In production, this should be protected with admin auth.
    For MVP, used for testing and manual content publishing.
    """
    try:
        # Verify idol exists
        idol = db.query(Idol).filter(
            Idol.id == idol_id,
            Idol.is_active == True
        ).first()

        if not idol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该偶像不存在或已下线"
            )

        # Create moment
        moment_service = IdolMomentService(db)
        moment = moment_service.create_moment(
            idol_id=idol_id,
            content=request.content,
            image_url=request.image_url
        )

        return {
            'id': moment.id,
            'idol_id': moment.idol_id,
            'content': moment.content,
            'image_url': moment.image_url,
            'likes_count': moment.likes_count,
            'posted_at': moment.posted_at.isoformat() if moment.posted_at else None,
            'message': '朋友圈发布成功'
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating moment for idol {idol_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发布失败，请稍后重试"
        )


@router.get(
    "/idols/{idol_id}/moments/stats",
    summary="获取朋友圈统计",
    description="获取偶像朋友圈的统计信息"
)
async def get_moment_stats(
    idol_id: int,
    db: Session = Depends(get_db)
):
    """
    Get moment statistics for an idol

    Returns:
    - Total moments count
    - Total likes count
    - Average likes per moment
    """
    try:
        # Verify idol exists
        idol = db.query(Idol).filter(
            Idol.id == idol_id,
            Idol.is_active == True
        ).first()

        if not idol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该偶像不存在或已下线"
            )

        moment_service = IdolMomentService(db)
        stats = moment_service.get_moment_stats(idol_id)

        return {
            'idol_id': idol_id,
            'idol_name': idol.name,
            **stats
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching moment stats for idol {idol_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )
