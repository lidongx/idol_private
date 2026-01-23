"""
Device Management API router
Story 8.1: 多设备登录与设备管理
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.device_service import DeviceService
from app.routers.auth import get_current_user


router = APIRouter(prefix="/devices", tags=["devices"])


# Request models
class RegisterDeviceRequest(BaseModel):
    """Request model for registering device"""
    device_id: Optional[str] = None  # Auto-generated if not provided
    device_name: str
    device_type: str  # 'ios', 'android', 'web'
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None


# Response models
class DeviceResponse(BaseModel):
    """Response model for device"""
    id: int
    user_id: int
    device_id: str
    device_name: str
    device_type: str
    device_model: Optional[str]
    os_version: Optional[str]
    app_version: Optional[str]
    is_active: bool
    is_current_device: bool
    last_login_at: str
    last_seen_display: str
    last_ip_address: Optional[str]
    device_icon: str
    created_at: str

    class Config:
        from_attributes = True


class DeviceStatsResponse(BaseModel):
    """Response model for device statistics"""
    total_devices: int
    active_devices: int
    inactive_devices: int
    device_types: dict
    max_devices: int
    can_add_device: bool


class RemoveDeviceResponse(BaseModel):
    """Response model for remove device"""
    success: bool
    message: str
    device_id: int


@router.post(
    "/register",
    response_model=DeviceResponse,
    summary="注册设备",
    description="注册或更新用户设备"
)
def register_device(
    request: RegisterDeviceRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register or update a device for the current user

    Body:
    - device_id: Unique device identifier (auto-generated if not provided)
    - device_name: User-friendly device name (e.g., "iPhone 15 Pro")
    - device_type: Device type (ios, android, web)
    - device_model: Device model (optional)
    - os_version: OS version (optional)
    - app_version: App version (optional)

    Returns:
    - Created or updated device details

    Note: Maximum 5 devices per user. If limit exceeded, remove an old device first.
    """
    try:
        # Get client IP address
        ip_address = http_request.client.host if http_request.client else None

        device_service = DeviceService(db)
        device = device_service.register_device(
            user_id=current_user.id,
            device_id=request.device_id,
            device_name=request.device_name,
            device_type=request.device_type,
            device_model=request.device_model,
            os_version=request.os_version,
            app_version=request.app_version,
            ip_address=ip_address
        )

        return DeviceResponse(**device.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error registering device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册设备失败"
        )


@router.get(
    "",
    response_model=List[DeviceResponse],
    summary="获取设备列表",
    description="获取当前用户的所有设备"
)
def get_user_devices(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all devices for the current user

    Query params:
    - active_only: Whether to return only active devices (default: true)

    Returns:
    - List of devices ordered by last login time (newest first)
    """
    device_service = DeviceService(db)
    devices = device_service.get_user_devices(
        user_id=current_user.id,
        active_only=active_only
    )

    return [DeviceResponse(**device.to_dict()) for device in devices]


@router.get(
    "/stats",
    response_model=DeviceStatsResponse,
    summary="获取设备统计",
    description="获取用户的设备统计信息"
)
def get_device_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get device statistics for the current user

    Returns:
    - Total number of devices
    - Active vs inactive devices
    - Device types breakdown
    - Device limit information
    """
    device_service = DeviceService(db)
    stats = device_service.get_device_stats(current_user.id)

    return DeviceStatsResponse(**stats)


@router.delete(
    "/{device_id}",
    response_model=RemoveDeviceResponse,
    summary="移除设备",
    description="移除（停用）指定设备"
)
def remove_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove (deactivate) a device

    Path params:
    - device_id: Device database ID

    Returns:
    - Success status and message

    Note: Device is deactivated, not deleted, for audit purposes.
    """
    device_service = DeviceService(db)

    try:
        result = device_service.remove_device(
            user_id=current_user.id,
            device_db_id=device_id
        )

        return RemoveDeviceResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error removing device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="移除设备失败"
        )
