"""
UserDevice model for multi-device management
Story 8.1: 多设备登录与设备管理
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class UserDevice(Base):
    """
    UserDevice model for tracking user login devices

    Supports up to 5 devices per user for multi-device sync
    """
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    device_id = Column(String(255), nullable=False, index=True)  # Unique device identifier (UUID)
    device_name = Column(String(100), nullable=False)  # User-friendly name (e.g., "iPhone 15 Pro")
    device_type = Column(String(50), nullable=False)  # 'ios', 'android', 'web'
    device_model = Column(String(100), nullable=True)  # Device model (e.g., "iPhone 15 Pro")
    os_version = Column(String(50), nullable=True)  # OS version (e.g., "iOS 17.2")
    app_version = Column(String(50), nullable=True)  # App version
    is_active = Column(Boolean, default=True, nullable=False)  # Whether device is active
    last_login_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="devices")

    # Device type constants
    TYPE_IOS = 'ios'
    TYPE_ANDROID = 'android'
    TYPE_WEB = 'web'

    @property
    def is_current_device(self) -> bool:
        """Check if this is the current active device (last login within 5 minutes)"""
        if not self.last_login_at:
            return False
        delta = datetime.utcnow() - self.last_login_at
        return delta.total_seconds() < 300  # 5 minutes

    @property
    def last_seen_display(self) -> str:
        """Get display string for last login time"""
        if not self.last_login_at:
            return "Never"

        delta = datetime.utcnow() - self.last_login_at
        seconds = delta.total_seconds()

        if seconds < 60:
            return "刚刚"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}分钟前"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}小时前"
        else:
            days = int(seconds / 86400)
            if days == 1:
                return "昨天"
            elif days < 7:
                return f"{days}天前"
            else:
                return self.last_login_at.strftime("%Y-%m-%d")

    @property
    def device_icon(self) -> str:
        """Get icon name for device type"""
        if self.device_type == self.TYPE_IOS:
            return "phone_iphone"
        elif self.device_type == self.TYPE_ANDROID:
            return "phone_android"
        elif self.device_type == self.TYPE_WEB:
            return "computer"
        else:
            return "devices"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'device_model': self.device_model,
            'os_version': self.os_version,
            'app_version': self.app_version,
            'is_active': self.is_active,
            'is_current_device': self.is_current_device,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'last_seen_display': self.last_seen_display,
            'last_ip_address': self.last_ip_address,
            'device_icon': self.device_icon,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<UserDevice(id={self.id}, user_id={self.user_id}, device_name={self.device_name})>"
