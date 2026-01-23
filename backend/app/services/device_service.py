"""
DeviceService - Service for managing user devices
Story 8.1: 多设备登录与设备管理
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import uuid

from app.models.user_device import UserDevice


class DeviceService:
    """Service for managing user devices and multi-device login"""

    # Maximum number of devices allowed per user
    MAX_DEVICES_PER_USER = 5

    def __init__(self, db: Session):
        self.db = db

    def register_device(
        self,
        user_id: int,
        device_id: str = None,
        device_name: str = None,
        device_type: str = None,
        device_model: str = None,
        os_version: str = None,
        app_version: str = None,
        ip_address: str = None
    ) -> UserDevice:
        """
        Register or update a device for a user

        Args:
            user_id: User ID
            device_id: Unique device identifier (UUID), auto-generated if not provided
            device_name: User-friendly device name
            device_type: Device type (ios, android, web)
            device_model: Device model
            os_version: OS version
            app_version: App version
            ip_address: IP address

        Returns:
            UserDevice object

        Raises:
            ValueError: If device limit exceeded
        """
        # Generate device_id if not provided
        if not device_id:
            device_id = str(uuid.uuid4())

        # Check if device already exists
        existing_device = self.db.query(UserDevice).filter(
            and_(
                UserDevice.user_id == user_id,
                UserDevice.device_id == device_id
            )
        ).first()

        if existing_device:
            # Update existing device
            existing_device.device_name = device_name or existing_device.device_name
            existing_device.device_type = device_type or existing_device.device_type
            existing_device.device_model = device_model or existing_device.device_model
            existing_device.os_version = os_version or existing_device.os_version
            existing_device.app_version = app_version or existing_device.app_version
            existing_device.last_login_at = datetime.utcnow()
            existing_device.last_ip_address = ip_address
            existing_device.is_active = True
            existing_device.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(existing_device)
            return existing_device

        # Check device limit
        active_devices = self.get_user_devices(user_id, active_only=True)
        if len(active_devices) >= self.MAX_DEVICES_PER_USER:
            raise ValueError(
                f"Device limit exceeded. Maximum {self.MAX_DEVICES_PER_USER} devices allowed per user. "
                f"Please remove an old device first."
            )

        # Create new device
        device = UserDevice(
            user_id=user_id,
            device_id=device_id,
            device_name=device_name or f"{device_type} device",
            device_type=device_type or UserDevice.TYPE_WEB,
            device_model=device_model,
            os_version=os_version,
            app_version=app_version,
            is_active=True,
            last_login_at=datetime.utcnow(),
            last_ip_address=ip_address
        )

        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)

        return device

    def get_user_devices(
        self,
        user_id: int,
        active_only: bool = True
    ) -> List[UserDevice]:
        """
        Get all devices for a user

        Args:
            user_id: User ID
            active_only: Whether to return only active devices

        Returns:
            List of UserDevice objects ordered by last login time
        """
        query = self.db.query(UserDevice).filter(UserDevice.user_id == user_id)

        if active_only:
            query = query.filter(UserDevice.is_active == True)

        return query.order_by(UserDevice.last_login_at.desc()).all()

    def get_device_by_id(self, device_db_id: int) -> Optional[UserDevice]:
        """
        Get device by database ID

        Args:
            device_db_id: Device database ID

        Returns:
            UserDevice object or None
        """
        return self.db.query(UserDevice).filter(UserDevice.id == device_db_id).first()

    def get_device_by_device_id(
        self,
        user_id: int,
        device_id: str
    ) -> Optional[UserDevice]:
        """
        Get device by device UUID

        Args:
            user_id: User ID
            device_id: Device UUID

        Returns:
            UserDevice object or None
        """
        return self.db.query(UserDevice).filter(
            and_(
                UserDevice.user_id == user_id,
                UserDevice.device_id == device_id
            )
        ).first()

    def remove_device(
        self,
        user_id: int,
        device_db_id: int
    ) -> Dict:
        """
        Remove (deactivate) a device

        Args:
            user_id: User ID
            device_db_id: Device database ID

        Returns:
            Result dictionary

        Raises:
            ValueError: If device not found or doesn't belong to user
        """
        device = self.get_device_by_id(device_db_id)

        if not device:
            raise ValueError(f"Device {device_db_id} not found")

        if device.user_id != user_id:
            raise ValueError("Device does not belong to user")

        # Mark device as inactive instead of deleting
        device.is_active = False
        device.updated_at = datetime.utcnow()

        self.db.commit()

        return {
            'success': True,
            'message': 'Device removed successfully',
            'device_id': device_db_id
        }

    def update_device_login(
        self,
        user_id: int,
        device_id: str,
        ip_address: str = None
    ) -> Optional[UserDevice]:
        """
        Update device last login time

        Args:
            user_id: User ID
            device_id: Device UUID
            ip_address: IP address (optional)

        Returns:
            Updated UserDevice object or None if not found
        """
        device = self.get_device_by_device_id(user_id, device_id)

        if not device:
            return None

        device.last_login_at = datetime.utcnow()
        if ip_address:
            device.last_ip_address = ip_address
        device.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(device)

        return device

    def get_device_stats(self, user_id: int) -> Dict:
        """
        Get device statistics for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary with device statistics
        """
        all_devices = self.get_user_devices(user_id, active_only=False)
        active_devices = [d for d in all_devices if d.is_active]

        device_types = {}
        for device in active_devices:
            device_type = device.device_type
            device_types[device_type] = device_types.get(device_type, 0) + 1

        return {
            'total_devices': len(all_devices),
            'active_devices': len(active_devices),
            'inactive_devices': len(all_devices) - len(active_devices),
            'device_types': device_types,
            'max_devices': self.MAX_DEVICES_PER_USER,
            'can_add_device': len(active_devices) < self.MAX_DEVICES_PER_USER
        }
