"""
UserAchievement model for tracking user achievement progress
Story 6.4: 成就系统与每日互动奖励
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class UserAchievement(Base):
    """
    UserAchievement model for tracking user progress towards achievements

    Tracks:
    - Which achievements each user is working on
    - Current progress towards completion
    - Whether achievement has been unlocked
    - Whether user has viewed the unlock notification
    """
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    progress = Column(Integer, default=0)
    unlocked_at = Column(DateTime, nullable=True, index=True)
    is_viewed = Column(Boolean, default=False, index=True)
    viewed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    @property
    def is_unlocked(self) -> bool:
        """Check if achievement is unlocked"""
        return self.unlocked_at is not None

    @property
    def is_new(self) -> bool:
        """Check if achievement is newly unlocked (not yet viewed)"""
        return self.is_unlocked and not self.is_viewed

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        if not self.achievement:
            return 0.0
        if self.achievement.condition_value == 0:
            return 0.0
        percentage = (self.progress / self.achievement.condition_value) * 100
        return min(percentage, 100.0)

    @property
    def days_since_unlock(self) -> int:
        """Calculate days since unlock"""
        if self.unlocked_at:
            delta = datetime.utcnow() - self.unlocked_at
            return delta.days
        return 0

    def mark_as_viewed(self):
        """Mark achievement as viewed"""
        if not self.is_viewed:
            self.is_viewed = True
            self.viewed_at = datetime.utcnow()

    def unlock(self):
        """Unlock the achievement"""
        if not self.is_unlocked:
            self.unlocked_at = datetime.utcnow()

    def update_progress(self, new_progress: int) -> bool:
        """
        Update progress and check if should unlock

        Returns:
            True if achievement was unlocked, False otherwise
        """
        if self.is_unlocked:
            return False  # Already unlocked

        self.progress = new_progress

        # Check if condition is met
        if self.achievement and self.progress >= self.achievement.condition_value:
            self.unlock()
            return True

        return False

    def to_dict(self, include_achievement_details: bool = True):
        """Convert to dictionary for API responses"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'progress': self.progress,
            'is_unlocked': self.is_unlocked,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'is_viewed': self.is_viewed,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'is_new': self.is_new,
            'completion_percentage': self.completion_percentage,
            'days_since_unlock': self.days_since_unlock,
        }

        if include_achievement_details and self.achievement:
            result['achievement'] = self.achievement.to_dict()

        return result

    def __repr__(self):
        return f"<UserAchievement(id={self.id}, user_id={self.user_id}, achievement_id={self.achievement_id}, progress={self.progress}, unlocked={self.is_unlocked})>"
