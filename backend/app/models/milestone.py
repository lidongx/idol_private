"""
Milestone model for anniversary tracking
Story 4.5: 周年纪念与主动回顾
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Milestone(Base):
    """
    Milestone model for tracking anniversaries

    Milestone types:
    - days_7: 1 week anniversary
    - days_30: 1 month anniversary
    - days_100: 100 days anniversary
    - days_365: 1 year anniversary
    """
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    milestone_type = Column(String(50), nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    is_claimed = Column(Boolean, default=False)
    message_content = Column(Text, nullable=True)
    special_reward = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="milestones")

    # Unique constraint: one milestone of each type per user
    __table_args__ = (
        UniqueConstraint('user_id', 'milestone_type', name='uq_user_milestone_type'),
    )

    @property
    def milestone_display_name(self) -> str:
        """Get display name for milestone type"""
        display_names = {
            'days_7': '认识1周纪念',
            'days_30': '认识1个月纪念',
            'days_100': '认识100天纪念',
            'days_365': '认识1年纪念',
        }
        return display_names.get(self.milestone_type, self.milestone_type)

    @property
    def days_count(self) -> int:
        """Get number of days for this milestone"""
        days_map = {
            'days_7': 7,
            'days_30': 30,
            'days_100': 100,
            'days_365': 365,
        }
        return days_map.get(self.milestone_type, 0)

    @staticmethod
    def get_milestone_message(milestone_type: str, user_name: str = None) -> str:
        """
        Get congratulatory message for milestone type

        Args:
            milestone_type: Type of milestone (days_7, days_30, etc.)
            user_name: Optional user name for personalization

        Returns:
            Congratulatory message string
        """
        messages = {
            'days_7': f"和你认识一周啦~时间过得好快~{f'很开心能遇见你，{user_name}！' if user_name else '很开心能遇见你！'}",
            'days_30': f"不知不觉我们已经认识一个月了，感觉更了解你了呢~{f'谢谢你的陪伴，{user_name}！' if user_name else '谢谢你的陪伴！'}",
            'days_100': f"今天是我们的100天纪念日！准备了一个小惊喜给你~{f'希望你喜欢，{user_name}！' if user_name else '希望你喜欢！'}",
            'days_365': f"一年了！谢谢你一直陪着我~{f'这一年有你真好，{user_name}！' if user_name else '这一年有你真好！'}",
        }
        return messages.get(milestone_type, "恭喜达成新的纪念日！")

    @staticmethod
    def get_special_reward(milestone_type: str) -> str | None:
        """
        Get special reward for milestone type

        Args:
            milestone_type: Type of milestone

        Returns:
            Special reward content (e.g., photo URL) or None
        """
        # Special rewards for certain milestones
        rewards = {
            'days_100': 'unlock_exclusive_photo_1',  # Unlock exclusive photo
            'days_365': 'unlock_exclusive_photo_2',  # Unlock another exclusive photo
        }
        return rewards.get(milestone_type)

    def claim(self):
        """Mark milestone as claimed by user"""
        self.is_claimed = True

    def __repr__(self):
        return f"<Milestone(id={self.id}, user_id={self.user_id}, type={self.milestone_type}, triggered_at={self.triggered_at})>"
