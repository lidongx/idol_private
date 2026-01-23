"""
Achievement model for achievement system
Story 6.4: 成就系统与每日互动奖励
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Achievement(Base):
    """
    Achievement model for achievement configuration

    Achievement types:
    - message_count: Based on total messages sent
    - login_streak: Based on consecutive login days
    - ritual_count: Based on morning/night ritual completions
    - fortune_count: Based on fortune check count
    - moment_like: Based on moment likes
    - level: Based on intimacy level reached
    """
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    achievement_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    achievement_type = Column(String(50), nullable=False, index=True)
    condition_value = Column(Integer, nullable=False)
    reward_exp = Column(Integer, default=0)
    icon_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

    # Achievement type constants
    TYPE_MESSAGE_COUNT = 'message_count'
    TYPE_LOGIN_STREAK = 'login_streak'
    TYPE_RITUAL_COUNT = 'ritual_count'
    TYPE_FORTUNE_COUNT = 'fortune_count'
    TYPE_MOMENT_LIKE = 'moment_like'
    TYPE_LEVEL = 'level'

    @property
    def achievement_type_display(self) -> str:
        """Get display name for achievement type"""
        type_names = {
            self.TYPE_MESSAGE_COUNT: '消息互动',
            self.TYPE_LOGIN_STREAK: '连续登录',
            self.TYPE_RITUAL_COUNT: '仪式完成',
            self.TYPE_FORTUNE_COUNT: '运势查询',
            self.TYPE_MOMENT_LIKE: '朋友圈互动',
            self.TYPE_LEVEL: '亲密度等级',
        }
        return type_names.get(self.achievement_type, self.achievement_type)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'achievement_name': self.achievement_name,
            'description': self.description,
            'achievement_type': self.achievement_type,
            'achievement_type_display': self.achievement_type_display,
            'condition_value': self.condition_value,
            'reward_exp': self.reward_exp,
            'icon_url': self.icon_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Achievement(id={self.id}, name={self.achievement_name}, type={self.achievement_type}, condition={self.condition_value})>"
