"""
LevelReward model for milestone rewards
Story 6.3: 等级特权与里程碑奖励
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class LevelReward(Base):
    """
    LevelReward model for milestone reward configuration

    Reward types:
    - nickname: AI uses special nickname for user
    - photo: Unlock special photo content
    - voice: Unlock voice message content
    - video: Unlock video content
    - feature: Unlock special feature access
    """
    __tablename__ = "level_rewards"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, unique=True, nullable=False, index=True)
    reward_type = Column(String(50), nullable=False, index=True)
    reward_content = Column(JSONB, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_rewards = relationship("UserReward", back_populates="reward", cascade="all, delete-orphan")

    # Reward type constants
    TYPE_NICKNAME = 'nickname'
    TYPE_PHOTO = 'photo'
    TYPE_VOICE = 'voice'
    TYPE_VIDEO = 'video'
    TYPE_FEATURE = 'feature'

    @property
    def reward_type_display(self) -> str:
        """Get display name for reward type"""
        type_names = {
            self.TYPE_NICKNAME: '专属昵称',
            self.TYPE_PHOTO: '专属照片',
            self.TYPE_VOICE: '语音消息',
            self.TYPE_VIDEO: '视频内容',
            self.TYPE_FEATURE: '特殊功能',
        }
        return type_names.get(self.reward_type, self.reward_type)

    def get_content_value(self, key: str):
        """Get specific value from reward_content JSON"""
        return self.reward_content.get(key)

    @property
    def nickname(self) -> str:
        """Get nickname if reward type is nickname"""
        if self.reward_type == self.TYPE_NICKNAME:
            return self.reward_content.get('nickname', '')
        return ''

    @property
    def photo_url(self) -> str:
        """Get photo URL if reward type is photo"""
        if self.reward_type == self.TYPE_PHOTO:
            return self.reward_content.get('photo_url', '')
        return ''

    @property
    def voice_url(self) -> str:
        """Get voice URL if reward type is voice"""
        if self.reward_type == self.TYPE_VOICE:
            return self.reward_content.get('voice_url', '')
        return ''

    @property
    def video_url(self) -> str:
        """Get video URL if reward type is video"""
        if self.reward_type == self.TYPE_VIDEO:
            return self.reward_content.get('video_url', '')
        return ''

    @property
    def feature_name(self) -> str:
        """Get feature name if reward type is feature"""
        if self.reward_type == self.TYPE_FEATURE:
            return self.reward_content.get('feature', '')
        return ''

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'level': self.level,
            'reward_type': self.reward_type,
            'reward_type_display': self.reward_type_display,
            'reward_content': self.reward_content,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<LevelReward(id={self.id}, level={self.level}, type={self.reward_type})>"
