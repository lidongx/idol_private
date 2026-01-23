"""
Account Deletion API router
Story 8.4: 账号删除与数据清除
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.account_deletion_service import AccountDeletionService


router = APIRouter(prefix="/account", tags=["account"])


# Request models
class CreateDeletionRequestBody(BaseModel):
    """Request model for creating deletion request"""
    reason: Optional[str] = None
    detailed_reason: Optional[str] = None


# Response models
class DeletionRequestResponse(BaseModel):
    """Response model for deletion request"""
    id: int
    user_id: int
    status: str
    reason: Optional[str]
    reason_display: str
    detailed_reason: Optional[str]
    scheduled_deletion_at: str
    days_until_deletion: int
    can_cancel: bool
    backup_created: bool
    created_at: str


class DeletionStatusResponse(BaseModel):
    """Response model for deletion status"""
    has_pending_request: bool
    deletion_request: Optional[DeletionRequestResponse]


@router.get(
    "/deletion/status",
    response_model=DeletionStatusResponse,
    summary="获取删除请求状态",
    description="检查当前用户是否有待处理的删除请求"
)
def get_deletion_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get deletion request status for current user

    Returns:
    - has_pending_request: Whether user has pending deletion request
    - deletion_request: Deletion request details (if exists)
    """
    deletion_service = AccountDeletionService(db)

    deletion_request = deletion_service.get_deletion_request(current_user.id)

    if deletion_request:
        return DeletionStatusResponse(
            has_pending_request=True,
            deletion_request=DeletionRequestResponse(**deletion_request.to_dict())
        )
    else:
        return DeletionStatusResponse(
            has_pending_request=False,
            deletion_request=None
        )


@router.post(
    "/deletion/request",
    response_model=DeletionRequestResponse,
    summary="申请删除账号",
    description="提交账号删除请求（7天冷静期）"
)
def create_deletion_request(
    body: CreateDeletionRequestBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create account deletion request with 7-day cooling-off period

    Body:
    - reason: Deletion reason (optional)
    - detailed_reason: Detailed explanation (optional)

    Returns:
    - Deletion request details
    - scheduled_deletion_at: When account will be permanently deleted
    - days_until_deletion: Countdown in days

    Note:
    - 7-day cooling-off period before permanent deletion
    - Can cancel anytime during cooling-off period
    - Final backup created before deletion
    """
    deletion_service = AccountDeletionService(db)

    try:
        deletion_request = deletion_service.create_deletion_request(
            user_id=current_user.id,
            reason=body.reason,
            detailed_reason=body.detailed_reason
        )

        return DeletionRequestResponse(**deletion_request.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error creating deletion request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建删除请求失败"
        )


@router.post(
    "/deletion/cancel",
    summary="取消删除请求",
    description="取消待处理的账号删除请求（仅冷静期内有效）"
)
def cancel_deletion_request(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel pending deletion request (only during cooling-off period)

    Returns:
    - Success message

    Note:
    - Can only cancel during 7-day cooling-off period
    - After cooling-off period expires, deletion is irreversible
    """
    deletion_service = AccountDeletionService(db)

    try:
        result = deletion_service.cancel_deletion_request(current_user.id)
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error cancelling deletion request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取消删除请求失败"
        )


@router.delete(
    "/delete",
    summary="立即删除账号（测试用）",
    description="⚠️ 危险操作：立即删除账号和所有数据（测试用，生产环境应移除）"
)
def immediate_delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ⚠️ DANGEROUS: Immediately delete account without cooling-off period

    This endpoint is for testing only and should be removed in production.

    In production, users must:
    1. Create deletion request (7-day cooling-off period)
    2. Wait for automatic deletion after 7 days

    Returns:
    - Deletion summary
    """
    deletion_service = AccountDeletionService(db)

    try:
        # Check if there's a pending request
        deletion_request = deletion_service.get_deletion_request(current_user.id)

        if not deletion_request:
            # Create immediate deletion request (for testing)
            deletion_request = deletion_service.create_deletion_request(
                user_id=current_user.id,
                reason='immediate_test_deletion'
            )

            # Override scheduled time to now (for testing)
            from datetime import datetime
            deletion_request.scheduled_deletion_at = datetime.utcnow()
            db.commit()
            db.refresh(deletion_request)

        # Execute deletion
        result = deletion_service.permanently_delete_account(
            user_id=current_user.id,
            deletion_request_id=deletion_request.id
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error deleting account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除账号失败"
        )
