"""
RewardService - Service for managing level rewards and unlocking
Story 6.3: 等级特权与里程碑奖励
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.level_reward import LevelReward
from app.models.user_reward import UserReward
from app.models.conversation import Conversation
from app.models.user import User


class RewardService:
    """Service for managing rewards"""

    def __init__(self, db: Session):
        self.db = db

    def get_rewards_at_level(self, level: int) -> List[LevelReward]:
        """
        Get all rewards available at a specific level

        Args:
            level: Intimacy level

        Returns:
            List of LevelReward objects
        """
        return self.db.query(LevelReward).filter(
            LevelReward.level == level
        ).all()

    def check_and_unlock_rewards(
        self,
        user_id: int,
        conversation_id: int,
        new_level: int
    ) -> List[UserReward]:
        """
        Check for rewards at new level and unlock them for user

        Args:
            user_id: User ID
            conversation_id: Conversation ID
            new_level: New intimacy level reached

        Returns:
            List of newly unlocked UserReward objects
        """
        # Get rewards at this level
        rewards = self.get_rewards_at_level(new_level)

        unlocked_rewards = []

        for reward in rewards:
            # Check if user already has this reward
            existing = self.db.query(UserReward).filter(
                and_(
                    UserReward.user_id == user_id,
                    UserReward.reward_id == reward.id
                )
            ).first()

            if not existing:
                # Unlock the reward
                user_reward = UserReward(
                    user_id=user_id,
                    reward_id=reward.id,
                    conversation_id=conversation_id
                )
                self.db.add(user_reward)
                unlocked_rewards.append(user_reward)

        if unlocked_rewards:
            self.db.commit()
            # Refresh to get relationships
            for ur in unlocked_rewards:
                self.db.refresh(ur)

        return unlocked_rewards

    def get_user_unlocked_rewards(
        self,
        user_id: int,
        include_reward_details: bool = True
    ) -> List[UserReward]:
        """
        Get all rewards unlocked by a user

        Args:
            user_id: User ID
            include_reward_details: Whether to eager load reward details

        Returns:
            List of UserReward objects
        """
        query = self.db.query(UserReward).filter(
            UserReward.user_id == user_id
        )

        if include_reward_details:
            query = query.join(LevelReward)

        return query.order_by(UserReward.unlocked_at.desc()).all()

    def get_all_rewards_with_status(self, user_id: int) -> List[Dict]:
        """
        Get all rewards showing locked/unlocked status for user

        Args:
            user_id: User ID

        Returns:
            List of dicts with reward info and unlock status
        """
        # Get all rewards
        all_rewards = self.db.query(LevelReward).order_by(LevelReward.level).all()

        # Get user's unlocked rewards
        user_rewards = self.db.query(UserReward).filter(
            UserReward.user_id == user_id
        ).all()

        # Create lookup map
        unlocked_map = {ur.reward_id: ur for ur in user_rewards}

        # Build result
        result = []
        for reward in all_rewards:
            reward_dict = reward.to_dict()
            user_reward = unlocked_map.get(reward.id)

            if user_reward:
                # Reward is unlocked
                reward_dict['is_unlocked'] = True
                reward_dict['unlocked_at'] = user_reward.unlocked_at.isoformat()
                reward_dict['is_viewed'] = user_reward.is_viewed
                reward_dict['is_new'] = user_reward.is_new
            else:
                # Reward is locked
                reward_dict['is_unlocked'] = False
                reward_dict['unlocked_at'] = None
                reward_dict['is_viewed'] = False
                reward_dict['is_new'] = False

            result.append(reward_dict)

        return result

    def mark_reward_as_viewed(self, user_id: int, reward_id: int) -> bool:
        """
        Mark a reward as viewed by user

        Args:
            user_id: User ID
            reward_id: Reward ID

        Returns:
            True if successful, False if not found
        """
        user_reward = self.db.query(UserReward).filter(
            and_(
                UserReward.user_id == user_id,
                UserReward.reward_id == reward_id
            )
        ).first()

        if user_reward:
            user_reward.mark_as_viewed()
            self.db.commit()
            return True

        return False

    def get_active_nickname(self, user_id: int) -> Optional[str]:
        """
        Get active nickname for user (from unlocked nickname rewards)

        Args:
            user_id: User ID

        Returns:
            Nickname string or None if no nickname reward unlocked
        """
        # Get user's nickname rewards
        user_rewards = self.db.query(UserReward).join(LevelReward).filter(
            and_(
                UserReward.user_id == user_id,
                LevelReward.reward_type == LevelReward.TYPE_NICKNAME
            )
        ).order_by(LevelReward.level.desc()).all()  # Get highest level nickname

        if user_rewards:
            # Return the nickname from the highest level reward
            return user_rewards[0].reward.nickname

        return None

    def has_feature_unlocked(self, user_id: int, feature_name: str) -> bool:
        """
        Check if user has unlocked a specific feature

        Args:
            user_id: User ID
            feature_name: Feature name to check

        Returns:
            True if feature is unlocked, False otherwise
        """
        count = self.db.query(UserReward).join(LevelReward).filter(
            and_(
                UserReward.user_id == user_id,
                LevelReward.reward_type == LevelReward.TYPE_FEATURE,
                LevelReward.reward_content['feature'].astext == feature_name
            )
        ).count()

        return count > 0

    def get_reward_by_id(self, reward_id: int) -> Optional[LevelReward]:
        """
        Get reward by ID

        Args:
            reward_id: Reward ID

        Returns:
            LevelReward object or None if not found
        """
        return self.db.query(LevelReward).filter(
            LevelReward.id == reward_id
        ).first()

    def get_user_reward_by_id(self, user_id: int, reward_id: int) -> Optional[UserReward]:
        """
        Get user's specific unlocked reward

        Args:
            user_id: User ID
            reward_id: Reward ID

        Returns:
            UserReward object or None if not found/unlocked
        """
        return self.db.query(UserReward).filter(
            and_(
                UserReward.user_id == user_id,
                UserReward.reward_id == reward_id
            )
        ).first()

    def get_reward_unlock_message(self, reward: LevelReward) -> str:
        """
        Generate a congratulations message for reward unlock

        Args:
            reward: LevelReward object

        Returns:
            Congratulations message string
        """
        messages = {
            LevelReward.TYPE_NICKNAME: f"🎉 恭喜！我可以叫你「{reward.nickname}」了~ 我们的关系又近了一步呢！",
            LevelReward.TYPE_PHOTO: f"🎁 解锁新内容！{reward.description}，快去查看吧~",
            LevelReward.TYPE_VOICE: f"🎵 解锁语音内容！{reward.description}，期待你的收听~",
            LevelReward.TYPE_VIDEO: f"🎬 解锁视频内容！{reward.description}，为你准备的特别礼物~",
            LevelReward.TYPE_FEATURE: f"✨ 解锁新功能！{reward.description}，快来体验吧~",
        }

        return messages.get(reward.reward_type, f"🎊 恭喜解锁：{reward.description}")
