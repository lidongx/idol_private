"""
AchievementService - Service for managing achievement system
Story 6.4: 成就系统与每日互动奖励
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from datetime import datetime, timedelta

from app.models.achievement import Achievement
from app.models.user_achievement import UserAchievement
from app.models.message import Message
from app.models.conversation import Conversation
from app.models.daily_ritual import DailyRitual
from app.models.idol_moment import IdolMomentLike


class AchievementService:
    """Service for managing achievements and user progress"""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user_achievement(
        self,
        user_id: int,
        achievement_id: int
    ) -> UserAchievement:
        """
        Get existing user achievement or create new one

        Args:
            user_id: User ID
            achievement_id: Achievement ID

        Returns:
            UserAchievement object
        """
        user_achievement = self.db.query(UserAchievement).filter(
            and_(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id
            )
        ).first()

        if not user_achievement:
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement_id,
                progress=0
            )
            self.db.add(user_achievement)
            self.db.flush()

        return user_achievement

    def check_and_unlock_achievement(
        self,
        user_id: int,
        achievement_type: str,
        current_value: int
    ) -> List[UserAchievement]:
        """
        Check achievements of given type and unlock if conditions are met

        Args:
            user_id: User ID
            achievement_type: Type of achievement to check
            current_value: Current progress value

        Returns:
            List of newly unlocked UserAchievement objects
        """
        # Get all achievements of this type
        achievements = self.db.query(Achievement).filter(
            Achievement.achievement_type == achievement_type
        ).all()

        newly_unlocked = []

        for achievement in achievements:
            # Get or create user achievement record
            user_achievement = self.get_or_create_user_achievement(user_id, achievement.id)

            # Skip if already unlocked
            if user_achievement.is_unlocked:
                continue

            # Update progress
            user_achievement.progress = current_value

            # Check if condition is met
            if current_value >= achievement.condition_value:
                user_achievement.unlock()
                newly_unlocked.append(user_achievement)

        if newly_unlocked:
            self.db.commit()
            # Refresh to get relationships
            for ua in newly_unlocked:
                self.db.refresh(ua)

        return newly_unlocked

    def check_message_achievements(self, user_id: int) -> List[UserAchievement]:
        """
        Check and unlock message count achievements

        Args:
            user_id: User ID

        Returns:
            List of newly unlocked achievements
        """
        # Count total messages sent by user
        message_count = self.db.query(func.count(Message.id)).join(
            Conversation, Message.conversation_id == Conversation.id
        ).filter(
            and_(
                Message.sender_type == 'user',
                Conversation.user_id == user_id
            )
        ).scalar() or 0

        return self.check_and_unlock_achievement(
            user_id,
            Achievement.TYPE_MESSAGE_COUNT,
            message_count
        )

    def check_level_achievements(self, user_id: int, current_level: int) -> List[UserAchievement]:
        """
        Check and unlock level achievements

        Args:
            user_id: User ID
            current_level: Current intimacy level

        Returns:
            List of newly unlocked achievements
        """
        return self.check_and_unlock_achievement(
            user_id,
            Achievement.TYPE_LEVEL,
            current_level
        )

    def check_ritual_achievements(self, user_id: int) -> List[UserAchievement]:
        """
        Check and unlock ritual count achievements (morning + night)

        Args:
            user_id: User ID

        Returns:
            List of newly unlocked achievements
        """
        # Count total rituals completed
        ritual_count = self.db.query(func.count(DailyRitual.id)).filter(
            and_(
                DailyRitual.user_id == user_id,
                or_(
                    DailyRitual.ritual_type == 'morning',
                    DailyRitual.ritual_type == 'night'
                )
            )
        ).scalar() or 0

        return self.check_and_unlock_achievement(
            user_id,
            Achievement.TYPE_RITUAL_COUNT,
            ritual_count
        )

    def check_fortune_achievements(self, user_id: int) -> List[UserAchievement]:
        """
        Check and unlock fortune check achievements

        Args:
            user_id: User ID

        Returns:
            List of newly unlocked achievements
        """
        # Count fortune checks from daily rituals
        fortune_count = self.db.query(func.count(DailyRitual.id)).filter(
            and_(
                DailyRitual.user_id == user_id,
                DailyRitual.ritual_type == DailyRitual.FORTUNE
            )
        ).scalar() or 0

        return self.check_and_unlock_achievement(
            user_id,
            Achievement.TYPE_FORTUNE_COUNT,
            fortune_count
        )

    def check_moment_like_achievements(self, user_id: int) -> List[UserAchievement]:
        """
        Check and unlock moment like achievements

        Args:
            user_id: User ID

        Returns:
            List of newly unlocked achievements
        """
        # Count moment likes
        like_count = self.db.query(func.count(IdolMomentLike.id)).filter(
            IdolMomentLike.user_id == user_id
        ).scalar() or 0

        return self.check_and_unlock_achievement(
            user_id,
            Achievement.TYPE_MOMENT_LIKE,
            like_count
        )

    def check_login_streak_achievements(self, user_id: int, streak_days: int) -> List[UserAchievement]:
        """
        Check and unlock login streak achievements

        Args:
            user_id: User ID
            streak_days: Current login streak in days

        Returns:
            List of newly unlocked achievements
        """
        return self.check_and_unlock_achievement(
            user_id,
            Achievement.TYPE_LOGIN_STREAK,
            streak_days
        )

    def check_all_achievements(self, user_id: int) -> List[UserAchievement]:
        """
        Check all achievement types for a user

        Args:
            user_id: User ID

        Returns:
            List of all newly unlocked achievements
        """
        all_unlocked = []

        # Check message achievements
        all_unlocked.extend(self.check_message_achievements(user_id))

        # Check ritual achievements
        all_unlocked.extend(self.check_ritual_achievements(user_id))

        # Check fortune achievements
        all_unlocked.extend(self.check_fortune_achievements(user_id))

        # Check moment like achievements
        all_unlocked.extend(self.check_moment_like_achievements(user_id))

        # Note: Level and login streak achievements should be checked
        # in their respective contexts (level up, login)

        return all_unlocked

    def get_user_achievements(
        self,
        user_id: int,
        include_locked: bool = True
    ) -> List[Dict]:
        """
        Get all achievements with user progress

        Args:
            user_id: User ID
            include_locked: Whether to include locked achievements

        Returns:
            List of dicts with achievement info and progress
        """
        # Get all achievements
        achievements = self.db.query(Achievement).order_by(Achievement.achievement_type, Achievement.condition_value).all()

        result = []

        for achievement in achievements:
            # Get user progress for this achievement
            user_achievement = self.db.query(UserAchievement).filter(
                and_(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == achievement.id
                )
            ).first()

            achievement_dict = achievement.to_dict()

            if user_achievement:
                # Achievement is being tracked
                achievement_dict['progress'] = user_achievement.progress
                achievement_dict['is_unlocked'] = user_achievement.is_unlocked
                achievement_dict['unlocked_at'] = user_achievement.unlocked_at.isoformat() if user_achievement.unlocked_at else None
                achievement_dict['is_viewed'] = user_achievement.is_viewed
                achievement_dict['is_new'] = user_achievement.is_new
                achievement_dict['completion_percentage'] = user_achievement.completion_percentage
            else:
                # Achievement not yet tracked
                achievement_dict['progress'] = 0
                achievement_dict['is_unlocked'] = False
                achievement_dict['unlocked_at'] = None
                achievement_dict['is_viewed'] = False
                achievement_dict['is_new'] = False
                achievement_dict['completion_percentage'] = 0.0

            # Include in result if unlocked or include_locked is True
            if achievement_dict['is_unlocked'] or include_locked:
                result.append(achievement_dict)

        return result

    def get_new_achievements(self, user_id: int) -> List[UserAchievement]:
        """
        Get newly unlocked achievements that user hasn't viewed yet

        Args:
            user_id: User ID

        Returns:
            List of new UserAchievement objects
        """
        return self.db.query(UserAchievement).filter(
            and_(
                UserAchievement.user_id == user_id,
                UserAchievement.unlocked_at.isnot(None),
                UserAchievement.is_viewed == False
            )
        ).order_by(UserAchievement.unlocked_at.desc()).all()

    def mark_achievement_as_viewed(self, user_id: int, achievement_id: int) -> bool:
        """
        Mark an achievement as viewed by user

        Args:
            user_id: User ID
            achievement_id: Achievement ID

        Returns:
            True if successful, False if not found
        """
        user_achievement = self.db.query(UserAchievement).filter(
            and_(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id
            )
        ).first()

        if user_achievement and user_achievement.is_unlocked:
            user_achievement.mark_as_viewed()
            self.db.commit()
            return True

        return False

    def get_achievement_unlock_message(self, achievement: Achievement) -> str:
        """
        Generate congratulations message for achievement unlock

        Args:
            achievement: Achievement object

        Returns:
            Congratulations message string
        """
        return f"🎉 成就达成：{achievement.achievement_name}！\n{achievement.description}\n获得经验值奖励：+{achievement.reward_exp} exp"
