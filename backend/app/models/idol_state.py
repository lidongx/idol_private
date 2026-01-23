"""
IdolState model for idol life rhythm system
Story 5.1: 偶像状态系统与生活节奏引擎
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class IdolState(Base):
    """
    IdolState model for tracking idol's current life state

    Represents the "living" aspect of the idol - their current activity,
    mood, and energy level that changes throughout the day.
    """
    __tablename__ = "idol_states"

    id = Column(Integer, primary_key=True, index=True)
    idol_id = Column(Integer, ForeignKey("idols.id", ondelete="CASCADE"), nullable=False, unique=True)
    current_status = Column(String(50), nullable=False)
    current_mood = Column(String(50), nullable=False)
    energy_level = Column(Integer, default=80, nullable=False)
    status_message = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    idol = relationship("Idol", back_populates="state")

    # Constraints
    __table_args__ = (
        CheckConstraint('energy_level >= 0 AND energy_level <= 100', name='check_energy_level_range'),
        UniqueConstraint('idol_id', name='uq_idol_id'),
    )

    # Status types
    STATUS_WORKING = 'working'
    STATUS_RESTING = 'resting'
    STATUS_ACTIVE = 'active'
    STATUS_BUSY = 'busy'
    STATUS_SLEEPING = 'sleeping'
    STATUS_WAKING_UP = 'waking_up'
    STATUS_PREPARING_SLEEP = 'preparing_sleep'

    # Mood types
    MOOD_HAPPY = 'happy'
    MOOD_CALM = 'calm'
    MOOD_TIRED = 'tired'
    MOOD_EXCITED = 'excited'
    MOOD_THOUGHTFUL = 'thoughtful'
    MOOD_FOCUSED = 'focused'
    MOOD_RELAXED = 'relaxed'
    MOOD_SLEEPY = 'sleepy'

    @property
    def status_display_name(self) -> str:
        """Get Chinese display name for status"""
        status_names = {
            self.STATUS_WORKING: '工作中',
            self.STATUS_RESTING: '休息中',
            self.STATUS_ACTIVE: '活跃中',
            self.STATUS_BUSY: '忙碌中',
            self.STATUS_SLEEPING: '睡眠中',
            self.STATUS_WAKING_UP: '刚醒来',
            self.STATUS_PREPARING_SLEEP: '准备睡觉',
        }
        return status_names.get(self.current_status, self.current_status)

    @property
    def mood_display_name(self) -> str:
        """Get Chinese display name for mood"""
        mood_names = {
            self.MOOD_HAPPY: '心情不错~',
            self.MOOD_CALM: '平静',
            self.MOOD_TIRED: '有点累',
            self.MOOD_EXCITED: '兴奋',
            self.MOOD_THOUGHTFUL: '若有所思',
            self.MOOD_FOCUSED: '专注',
            self.MOOD_RELAXED: '放松',
            self.MOOD_SLEEPY: '困了',
        }
        return mood_names.get(self.current_mood, self.current_mood)

    @property
    def energy_display(self) -> str:
        """Get energy level display text"""
        if self.energy_level >= 80:
            return '精力充沛'
        elif self.energy_level >= 60:
            return '状态良好'
        elif self.energy_level >= 40:
            return '有点疲惫'
        elif self.energy_level >= 20:
            return '比较累'
        else:
            return '需要休息'

    @property
    def is_available(self) -> bool:
        """Check if idol is available for conversation"""
        unavailable_statuses = [self.STATUS_SLEEPING, self.STATUS_BUSY]
        return self.current_status not in unavailable_statuses

    @property
    def is_sleeping(self) -> bool:
        """Check if idol is sleeping"""
        return self.current_status == self.STATUS_SLEEPING

    def update_state(self, status: str = None, mood: str = None, energy: int = None, message: str = None):
        """
        Update idol state

        Args:
            status: New status (optional)
            mood: New mood (optional)
            energy: New energy level (optional)
            message: New status message (optional)
        """
        if status is not None:
            self.current_status = status
        if mood is not None:
            self.current_mood = mood
        if energy is not None:
            # Ensure energy is within 0-100
            self.energy_level = max(0, min(100, energy))
        if message is not None:
            self.status_message = message

        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<IdolState(idol_id={self.idol_id}, status={self.current_status}, mood={self.current_mood}, energy={self.energy_level})>"
