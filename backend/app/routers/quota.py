"""
Quota API Router
Handles message quota queries and statistics
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.quota import QuotaResponse
from app.services.quota_service import QuotaService

router = APIRouter()


@router.get(
    "/users/me/quota",
    response_model=QuotaResponse,
    summary="获取当前用户配额",
    description="获取当前用户今日消息配额信息"
)
async def get_my_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's message quota

    - Requires JWT authentication
    - Returns today's quota information
    - Includes remaining messages count
    """
    quota_service = QuotaService(db)
    quota_info = quota_service.get_quota_info(current_user.id)

    return QuotaResponse(**quota_info)
