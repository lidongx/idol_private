"""
User Preferences Service
Story 9.2: 个性化设置

Manages user preferences including theme, font size, notifications, etc.
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime

from app.models.user_preferences import UserPreferences


class PreferencesService:
    """
    User Preferences Service

    Handles all operations related to user preferences.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_preferences(self, user_id: int) -> Dict:
        """
        Get user preferences

        If preferences don't exist, create them with default values.

        Args:
            user_id: User ID

        Returns:
            dict: User preferences
        """
        preferences = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()

        if not preferences:
            # Create default preferences
            preferences = self.create_default_preferences(user_id)

        return preferences.to_dict()

    def create_default_preferences(self, user_id: int) -> UserPreferences:
        """
        Create default preferences for a new user

        Args:
            user_id: User ID

        Returns:
            UserPreferences: Created preferences object
        """
        default_prefs = UserPreferences.get_default_preferences()

        preferences = UserPreferences(
            user_id=user_id,
            **default_prefs
        )

        self.db.add(preferences)
        self.db.commit()
        self.db.refresh(preferences)

        return preferences

    def update_preferences(
        self,
        user_id: int,
        updates: Dict
    ) -> Dict:
        """
        Update user preferences

        Args:
            user_id: User ID
            updates: Dictionary of fields to update

        Returns:
            dict: Updated preferences

        Raises:
            ValueError: If preferences not found or invalid values
        """
        preferences = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()

        if not preferences:
            raise ValueError(f"Preferences not found for user {user_id}")

        # Validate and update fields
        if "theme_mode" in updates:
            if updates["theme_mode"] not in [
                UserPreferences.THEME_LIGHT,
                UserPreferences.THEME_DARK,
                UserPreferences.THEME_AUTO
            ]:
                raise ValueError(f"Invalid theme_mode: {updates['theme_mode']}")
            preferences.theme_mode = updates["theme_mode"]

        if "font_size" in updates:
            if updates["font_size"] not in [
                UserPreferences.FONT_SMALL,
                UserPreferences.FONT_MEDIUM,
                UserPreferences.FONT_LARGE
            ]:
                raise ValueError(f"Invalid font_size: {updates['font_size']}")
            preferences.font_size = updates["font_size"]

        if "notifications_enabled" in updates:
            preferences.notifications_enabled = bool(updates["notifications_enabled"])

        if "message_sound_enabled" in updates:
            preferences.message_sound_enabled = bool(updates["message_sound_enabled"])

        if "typing_sound_enabled" in updates:
            preferences.typing_sound_enabled = bool(updates["typing_sound_enabled"])

        if "language" in updates:
            if updates["language"] not in [
                UserPreferences.LANG_ZH_CN,
                UserPreferences.LANG_EN_US
            ]:
                raise ValueError(f"Invalid language: {updates['language']}")
            preferences.language = updates["language"]

        if "show_online_status" in updates:
            preferences.show_online_status = bool(updates["show_online_status"])

        if "send_on_enter" in updates:
            preferences.send_on_enter = bool(updates["send_on_enter"])

        if "show_typing_indicator" in updates:
            preferences.show_typing_indicator = bool(updates["show_typing_indicator"])

        # Update timestamp
        preferences.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(preferences)

        return preferences.to_dict()

    def update_theme(self, user_id: int, theme_mode: str) -> Dict:
        """
        Update theme mode

        Args:
            user_id: User ID
            theme_mode: Theme mode (light, dark, auto)

        Returns:
            dict: Updated preferences
        """
        return self.update_preferences(user_id, {"theme_mode": theme_mode})

    def update_font_size(self, user_id: int, font_size: str) -> Dict:
        """
        Update font size

        Args:
            user_id: User ID
            font_size: Font size (small, medium, large)

        Returns:
            dict: Updated preferences
        """
        return self.update_preferences(user_id, {"font_size": font_size})

    def toggle_notifications(self, user_id: int, enabled: bool) -> Dict:
        """
        Toggle push notifications

        Args:
            user_id: User ID
            enabled: Whether to enable notifications

        Returns:
            dict: Updated preferences
        """
        return self.update_preferences(user_id, {"notifications_enabled": enabled})

    def toggle_message_sound(self, user_id: int, enabled: bool) -> Dict:
        """
        Toggle message notification sound

        Args:
            user_id: User ID
            enabled: Whether to enable sound

        Returns:
            dict: Updated preferences
        """
        return self.update_preferences(user_id, {"message_sound_enabled": enabled})

    def reset_to_defaults(self, user_id: int) -> Dict:
        """
        Reset preferences to default values

        Args:
            user_id: User ID

        Returns:
            dict: Reset preferences
        """
        preferences = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()

        if not preferences:
            raise ValueError(f"Preferences not found for user {user_id}")

        # Reset to defaults
        default_prefs = UserPreferences.get_default_preferences()
        for key, value in default_prefs.items():
            setattr(preferences, key, value)

        preferences.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(preferences)

        return preferences.to_dict()

    def delete_preferences(self, user_id: int) -> bool:
        """
        Delete user preferences

        Args:
            user_id: User ID

        Returns:
            bool: True if deleted, False if not found
        """
        preferences = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()

        if not preferences:
            return False

        self.db.delete(preferences)
        self.db.commit()

        return True
