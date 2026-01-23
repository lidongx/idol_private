"""
UserReward model for tracking unlocked rewards
Story 6.3: 等级特权与里程碑奖励
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class UserReward(Base):
    """
    UserReward model for tracking which rewards each user has unlocked

    Tracks:
    - Which user unlocked which reward
    - When it was unlocked
    - Whether user has viewed the reward details
    - Which conversation triggered the unlock
    """
    __tablename__ = "user_rewards"
    __table_args__ = (
        UniqueConstraint('user_id', 'reward_id', name='uq_user_reward'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reward_id = Column(Integer, ForeignKey("level_rewards.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    unlocked_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_viewed = Column(Boolean, default=False, index=True)
    viewed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="rewards")
    reward = relationship("LevelReward", back_populates="user_rewards")
    conversation = relationship("Conversation", backref="rewards_unlocked")

    def mark_as_viewed(self):
        """Mark reward as viewed"""
        if not self.is_viewed:
            self.is_viewed = True
            self.viewed_at = datetime.utcnow()

    @property
    def is_new(self) -> bool:
        """Check if reward is newly unlocked (not yet viewed)"""
        return not self.is_viewed

    @property
    def days_since_unlock(self) -> int:
        """Calculate days since unlock"""
        if self.unlocked_at:
            delta = datetime.utcnow() - self.unlocked_at
            return delta.days
        return 0

    def to_dict(self, include_reward_details: bool = True):
        """Convert to dictionary for API responses"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'reward_id': self.reward_id,
            'conversation_id': self.conversation_id,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'is_viewed': self.is_viewed,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'is_new': self.is_new,
            'days_since_unlock': self.days_since_unlock,
        }

        if include_reward_details and self.reward:
            result['reward'] = self.reward.to_dict()

        return result

    def __repr__(self):
        return f"<UserReward(id={self.id}, user_id={self.user_id}, reward_id={self.reward_id}, viewed={self.is_viewed})>"
