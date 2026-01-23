"""
IntimacyLog model for tracking intimacy exp changes
Story 6.1: 亲密度等级系统与经验值计算
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class IntimacyLog(Base):
    """
    IntimacyLog model for tracking intimacy experience changes

    Reasons for exp change:
    - send_message: User sends a text message (+5 exp)
    - send_voice: User sends a voice message (+8 exp)
    - send_image: User sends an image (+8 exp)
    - morning_greeting: Complete morning greeting ritual (+10 exp)
    - night_greeting: Complete night greeting ritual (+10 exp)
    - check_fortune: Check daily fortune (+5 exp)
    - like_moment: Like idol's moment (+3 exp, max 5/day)
    - login_streak_7: 7-day login streak (+50 exp)
    """
    __tablename__ = "intimacy_logs"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    exp_change = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False)
    new_level = Column(Integer, nullable=False)
    new_exp = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", backref="intimacy_logs")

    # Exp change reasons
    REASON_SEND_MESSAGE = 'send_message'
    REASON_SEND_VOICE = 'send_voice'
    REASON_SEND_IMAGE = 'send_image'
    REASON_MORNING_GREETING = 'morning_greeting'
    REASON_NIGHT_GREETING = 'night_greeting'
    REASON_CHECK_FORTUNE = 'check_fortune'
    REASON_LIKE_MOMENT = 'like_moment'
    REASON_LOGIN_STREAK_7 = 'login_streak_7'
    REASON_LEVEL_UP = 'level_up'

    @property
    def reason_display_name(self) -> str:
        """Get display name for reason"""
        names = {
            self.REASON_SEND_MESSAGE: '发送消息',
            self.REASON_SEND_VOICE: '发送语音',
            self.REASON_SEND_IMAGE: '发送图片',
            self.REASON_MORNING_GREETING: '早安问候',
            self.REASON_NIGHT_GREETING: '晚安问候',
            self.REASON_CHECK_FORTUNE: '查看运势',
            self.REASON_LIKE_MOMENT: '朋友圈点赞',
            self.REASON_LOGIN_STREAK_7: '连续登录7天',
            self.REASON_LEVEL_UP: '等级提升',
        }
        return names.get(self.reason, self.reason)

    def __repr__(self):
        return f"<IntimacyLog(id={self.id}, conversation_id={self.conversation_id}, exp_change={self.exp_change}, reason={self.reason})>"
