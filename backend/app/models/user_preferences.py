"""
User Preferences Model
Story 9.2: 个性化设置

Stores user preferences including:
- Theme (light/dark/auto)
- Font size (small/medium/large)
- Notification settings
- Sound settings
- Language
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class UserPreferences(Base):
    """
    User Preferences Model

    Stores personalized settings for each user.
    """
    __tablename__ = "user_preferences"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to users table
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Theme settings
    theme_mode = Column(
        String(20),
        nullable=False,
        default="auto",
        comment="Theme mode: light, dark, auto (follows system)"
    )

    # Font size settings
    font_size = Column(
        String(20),
        nullable=False,
        default="medium",
        comment="Font size: small, medium, large"
    )

    # Notification settings
    notifications_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether push notifications are enabled"
    )

    # Sound settings
    message_sound_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether message notification sound is enabled"
    )

    typing_sound_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether typing sound effects are enabled"
    )

    # Language settings
    language = Column(
        String(10),
        nullable=False,
        default="zh_CN",
        comment="Language code: zh_CN (Chinese), en_US (English)"
    )

    # Privacy settings
    show_online_status = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether to show online status to others"
    )

    # Chat settings
    send_on_enter = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether Enter key sends message (vs. Shift+Enter)"
    )

    show_typing_indicator = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether to show typing indicator to idol"
    )

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="preferences")

    # Constants for theme modes
    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    THEME_AUTO = "auto"

    # Constants for font sizes
    FONT_SMALL = "small"
    FONT_MEDIUM = "medium"
    FONT_LARGE = "large"

    # Constants for languages
    LANG_ZH_CN = "zh_CN"
    LANG_EN_US = "en_US"

    def to_dict(self) -> dict:
        """Convert preferences to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "theme_mode": self.theme_mode,
            "font_size": self.font_size,
            "notifications_enabled": self.notifications_enabled,
            "message_sound_enabled": self.message_sound_enabled,
            "typing_sound_enabled": self.typing_sound_enabled,
            "language": self.language,
            "show_online_status": self.show_online_status,
            "send_on_enter": self.send_on_enter,
            "show_typing_indicator": self.show_typing_indicator,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def get_default_preferences() -> dict:
        """Get default preference values"""
        return {
            "theme_mode": UserPreferences.THEME_AUTO,
            "font_size": UserPreferences.FONT_MEDIUM,
            "notifications_enabled": True,
            "message_sound_enabled": True,
            "typing_sound_enabled": False,
            "language": UserPreferences.LANG_ZH_CN,
            "show_online_status": True,
            "send_on_enter": True,
            "show_typing_indicator": True,
        }
