"""
User Preferences API Router
Story 9.2: 个性化设置

Endpoints for managing user preferences.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.services.preferences_service import PreferencesService
from app.routers.auth import get_current_user
from app.models.user import User


router = APIRouter()


# ==================== Request/Response Models ====================

class PreferencesResponse(BaseModel):
    """User preferences response"""
    id: int
    user_id: int
    theme_mode: str
    font_size: str
    notifications_enabled: bool
    message_sound_enabled: bool
    typing_sound_enabled: bool
    language: str
    show_online_status: bool
    send_on_enter: bool
    show_typing_indicator: bool
    created_at: str
    updated_at: str


class UpdatePreferencesRequest(BaseModel):
    """Update preferences request"""
    theme_mode: Optional[str] = None
    font_size: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    message_sound_enabled: Optional[bool] = None
    typing_sound_enabled: Optional[bool] = None
    language: Optional[str] = None
    show_online_status: Optional[bool] = None
    send_on_enter: Optional[bool] = None
    show_typing_indicator: Optional[bool] = None


class UpdateThemeRequest(BaseModel):
    """Update theme request"""
    theme_mode: str  # "light", "dark", "auto"


class UpdateFontSizeRequest(BaseModel):
    """Update font size request"""
    font_size: str  # "small", "medium", "large"


class ToggleNotificationsRequest(BaseModel):
    """Toggle notifications request"""
    enabled: bool


class ToggleSoundRequest(BaseModel):
    """Toggle sound request"""
    enabled: bool


# ==================== API Endpoints ====================

@router.get("/preferences", response_model=PreferencesResponse)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user preferences

    If preferences don't exist, they will be created with default values.

    Returns:
        PreferencesResponse: User preferences
    """
    service = PreferencesService(db)

    try:
        preferences = service.get_preferences(current_user.id)
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取偏好设置失败: {str(e)}")


@router.put("/preferences", response_model=PreferencesResponse)
def update_preferences(
    request: UpdatePreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user preferences

    Body:
    - theme_mode: Theme mode (light, dark, auto) - optional
    - font_size: Font size (small, medium, large) - optional
    - notifications_enabled: Enable/disable notifications - optional
    - message_sound_enabled: Enable/disable message sounds - optional
    - typing_sound_enabled: Enable/disable typing sounds - optional
    - language: Language code (zh_CN, en_US) - optional
    - show_online_status: Show online status - optional
    - send_on_enter: Send message on Enter key - optional
    - show_typing_indicator: Show typing indicator - optional

    Returns:
        PreferencesResponse: Updated preferences
    """
    service = PreferencesService(db)

    try:
        # Convert request to dict, excluding None values
        updates = request.model_dump(exclude_none=True)

        if not updates:
            raise HTTPException(status_code=400, detail="没有提供需要更新的字段")

        preferences = service.update_preferences(current_user.id, updates)
        return preferences
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新偏好设置失败: {str(e)}")


@router.put("/preferences/theme", response_model=PreferencesResponse)
def update_theme(
    request: UpdateThemeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update theme mode

    Body:
    - theme_mode: "light", "dark", or "auto"

    Returns:
        PreferencesResponse: Updated preferences
    """
    service = PreferencesService(db)

    try:
        preferences = service.update_theme(current_user.id, request.theme_mode)
        return preferences
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新主题失败: {str(e)}")


@router.put("/preferences/font-size", response_model=PreferencesResponse)
def update_font_size(
    request: UpdateFontSizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update font size

    Body:
    - font_size: "small", "medium", or "large"

    Returns:
        PreferencesResponse: Updated preferences
    """
    service = PreferencesService(db)

    try:
        preferences = service.update_font_size(current_user.id, request.font_size)
        return preferences
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新字体大小失败: {str(e)}")


@router.put("/preferences/notifications", response_model=PreferencesResponse)
def toggle_notifications(
    request: ToggleNotificationsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle push notifications

    Body:
    - enabled: true to enable, false to disable

    Returns:
        PreferencesResponse: Updated preferences
    """
    service = PreferencesService(db)

    try:
        preferences = service.toggle_notifications(current_user.id, request.enabled)
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新通知设置失败: {str(e)}")


@router.put("/preferences/message-sound", response_model=PreferencesResponse)
def toggle_message_sound(
    request: ToggleSoundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle message notification sound

    Body:
    - enabled: true to enable, false to disable

    Returns:
        PreferencesResponse: Updated preferences
    """
    service = PreferencesService(db)

    try:
        preferences = service.toggle_message_sound(current_user.id, request.enabled)
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新消息提示音失败: {str(e)}")


@router.post("/preferences/reset", response_model=PreferencesResponse)
def reset_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset preferences to default values

    Returns:
        PreferencesResponse: Reset preferences
    """
    service = PreferencesService(db)

    try:
        preferences = service.reset_to_defaults(current_user.id)
        return preferences
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置偏好设置失败: {str(e)}")
