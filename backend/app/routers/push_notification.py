"""
Push Notification API Router
Story 9.3: 推送通知集成（Firebase Cloud Messaging）

Endpoints for managing push notifications and device tokens.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict

from app.database import get_db
from app.services.push_notification_service import PushNotificationService, NotificationTemplates
from app.routers.auth import get_current_user
from app.models.user import User


router = APIRouter()


# ==================== Request/Response Models ====================

class RegisterDeviceTokenRequest(BaseModel):
    """Register device token request"""
    device_id: str
    fcm_token: str
    device_name: Optional[str] = None


class UnregisterDeviceTokenRequest(BaseModel):
    """Unregister device token request"""
    device_id: str


class SendNotificationRequest(BaseModel):
    """Send notification request (admin/testing only)"""
    title: str
    body: str
    data: Optional[Dict] = None


class NotificationResponse(BaseModel):
    """Notification response"""
    success: bool
    message: str
    sent_count: Optional[int] = None
    failed_count: Optional[int] = None


# ==================== API Endpoints ====================

@router.post("/push/register", response_model=NotificationResponse)
def register_device_token(
    request: RegisterDeviceTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register FCM device token

    Body:
    - device_id: Unique device identifier
    - fcm_token: Firebase Cloud Messaging token
    - device_name: Device name (optional)

    Returns:
        NotificationResponse: Registration result
    """
    service = PushNotificationService(db)

    try:
        success = service.register_device_token(
            user_id=current_user.id,
            device_id=request.device_id,
            fcm_token=request.fcm_token
        )

        if success:
            return NotificationResponse(
                success=True,
                message="设备令牌注册成功"
            )
        else:
            raise HTTPException(status_code=500, detail="设备令牌注册失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.post("/push/unregister", response_model=NotificationResponse)
def unregister_device_token(
    request: UnregisterDeviceTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unregister FCM device token

    Body:
    - device_id: Unique device identifier

    Returns:
        NotificationResponse: Unregistration result
    """
    service = PushNotificationService(db)

    try:
        success = service.unregister_device_token(
            user_id=current_user.id,
            device_id=request.device_id
        )

        if success:
            return NotificationResponse(
                success=True,
                message="设备令牌注销成功"
            )
        else:
            raise HTTPException(status_code=500, detail="设备令牌注销失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注销失败: {str(e)}")


@router.post("/push/test", response_model=NotificationResponse)
def send_test_notification(
    request: SendNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send test notification to current user's devices

    Body:
    - title: Notification title
    - body: Notification body
    - data: Additional data payload (optional)

    Returns:
        NotificationResponse: Send result

    Note: This is for testing purposes. In production, notifications
    should be triggered by events (new message, subscription expiring, etc.)
    """
    service = PushNotificationService(db)

    try:
        result = service.send_notification_to_user(
            user_id=current_user.id,
            title=request.title,
            body=request.body,
            data=request.data
        )

        return NotificationResponse(
            success=True,
            message="测试通知发送完成",
            sent_count=result['sent'],
            failed_count=result['failed']
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")


# ==================== Helper Functions for Internal Use ====================

def send_idol_message_notification(
    db: Session,
    user_id: int,
    idol_name: str,
    message_preview: str
):
    """
    Send notification for new idol message

    Called internally when idol sends a message to user.

    Args:
        db: Database session
        user_id: User ID
        idol_name: Name of the idol
        message_preview: Preview of the message
    """
    service = PushNotificationService(db)
    notification = NotificationTemplates.idol_message(idol_name, message_preview)

    result = service.send_notification_to_user(
        user_id=user_id,
        title=notification['title'],
        body=notification['body'],
        data=notification.get('data')
    )

    return result


def send_intimacy_level_up_notification(
    db: Session,
    user_id: int,
    idol_name: str,
    new_level: int
):
    """
    Send notification for intimacy level up

    Called internally when intimacy level increases.

    Args:
        db: Database session
        user_id: User ID
        idol_name: Name of the idol
        new_level: New intimacy level
    """
    service = PushNotificationService(db)
    notification = NotificationTemplates.intimacy_level_up(idol_name, new_level)

    result = service.send_notification_to_user(
        user_id=user_id,
        title=notification['title'],
        body=notification['body'],
        data=notification.get('data')
    )

    return result


def send_subscription_expiring_notification(
    db: Session,
    user_id: int,
    days_remaining: int
):
    """
    Send notification for subscription expiring soon

    Called internally by subscription reminder task.

    Args:
        db: Database session
        user_id: User ID
        days_remaining: Days until subscription expires
    """
    service = PushNotificationService(db)
    notification = NotificationTemplates.subscription_expiring(days_remaining)

    result = service.send_notification_to_user(
        user_id=user_id,
        title=notification['title'],
        body=notification['body'],
        data=notification.get('data')
    )

    return result


def send_subscription_expired_notification(
    db: Session,
    user_id: int
):
    """
    Send notification for subscription expired

    Called internally when subscription expires.

    Args:
        db: Database session
        user_id: User ID
    """
    service = PushNotificationService(db)
    notification = NotificationTemplates.subscription_expired()

    result = service.send_notification_to_user(
        user_id=user_id,
        title=notification['title'],
        body=notification['body'],
        data=notification.get('data')
    )

    return result


def send_milestone_reminder_notification(
    db: Session,
    user_id: int,
    milestone_name: str,
    date: str
):
    """
    Send notification for milestone reminder

    Called internally by milestone check task.

    Args:
        db: Database session
        user_id: User ID
        milestone_name: Name of the milestone
        date: Milestone date
    """
    service = PushNotificationService(db)
    notification = NotificationTemplates.milestone_reminder(milestone_name, date)

    result = service.send_notification_to_user(
        user_id=user_id,
        title=notification['title'],
        body=notification['body'],
        data=notification.get('data')
    )

    return result


def send_achievement_unlocked_notification(
    db: Session,
    user_id: int,
    achievement_name: str
):
    """
    Send notification for achievement unlocked

    Called internally when user unlocks achievement.

    Args:
        db: Database session
        user_id: User ID
        achievement_name: Name of the achievement
    """
    service = PushNotificationService(db)
    notification = NotificationTemplates.achievement_unlocked(achievement_name)

    result = service.send_notification_to_user(
        user_id=user_id,
        title=notification['title'],
        body=notification['body'],
        data=notification.get('data')
    )

    return result
