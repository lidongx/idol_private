"""
SpecialEvent models for surprise events and easter eggs
Story 5.5: 特殊事件与互动彩蛋
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class SpecialEvent(Base):
    """
    SpecialEvent model for event templates/configurations

    Event types:
    - random: Random events (5% probability)
    - holiday: Holiday-based events (Valentine's Day, Christmas, etc.)
    - achievement: Achievement-based events (100 messages, 30-day streak, etc.)
    - weather: Weather-based events (rainy day, snowy day, etc.)
    """
    __tablename__ = "special_events"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(100), unique=True, nullable=False)
    event_type = Column(String(50), nullable=False)
    trigger_condition = Column(JSONB, nullable=True)
    content_template = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    reward_exp = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_events = relationship("UserSpecialEvent", back_populates="event")

    # Event types
    TYPE_RANDOM = 'random'
    TYPE_HOLIDAY = 'holiday'
    TYPE_ACHIEVEMENT = 'achievement'
    TYPE_WEATHER = 'weather'

    @property
    def type_display_name(self) -> str:
        """Get display name for event type"""
        names = {
            self.TYPE_RANDOM: '随机事件',
            self.TYPE_HOLIDAY: '节日事件',
            self.TYPE_ACHIEVEMENT: '成就事件',
            self.TYPE_WEATHER: '天气事件',
        }
        return names.get(self.event_type, self.event_type)

    def __repr__(self):
        return f"<SpecialEvent(id={self.id}, name={self.event_name}, type={self.event_type})>"


class UserSpecialEvent(Base):
    """
    UserSpecialEvent model for tracking user event history
    """
    __tablename__ = "user_special_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    idol_id = Column(Integer, ForeignKey("idols.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("special_events.id", ondelete="CASCADE"), nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    event_content = Column(Text, nullable=True)
    exp_awarded = Column(Integer, default=0)
    was_interacted = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="special_events")
    idol = relationship("Idol")
    event = relationship("SpecialEvent", back_populates="user_events")

    @property
    def is_recent(self) -> bool:
        """Check if event was triggered recently (within 24 hours)"""
        if not self.triggered_at:
            return False
        hours_passed = (datetime.utcnow() - self.triggered_at).total_seconds() / 3600
        return hours_passed < 24

    def mark_as_interacted(self):
        """Mark this event as interacted by user"""
        self.was_interacted = True

    def __repr__(self):
        return f"<UserSpecialEvent(id={self.id}, user_id={self.user_id}, event={self.event.event_name if self.event else 'N/A'})>"
