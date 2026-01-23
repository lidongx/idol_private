"""
ReverseCare model for tracking idol's proactive care actions
Story 5.4: 反向陪伴机制
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base


class ReverseCare(Base):
    """
    ReverseCare model for tracking when idol proactively reaches out to users

    Tracks three types of care scenarios:
    1. inactive_3days - User hasn't logged in for 3+ days
    2. late_night - User active during late night hours (1:00-3:00 AM)
    3. low_mood_3days - User shows low mood for 3+ consecutive days
    """
    __tablename__ = "reverse_care_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    idol_id = Column(Integer, ForeignKey("idols.id", ondelete="CASCADE"), nullable=False)
    care_type = Column(String(50), nullable=False)
    message_content = Column(Text, nullable=True)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    was_responded = Column(Boolean, default=False)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="reverse_care_logs")
    idol = relationship("Idol")

    # Care types
    INACTIVE_3DAYS = 'inactive_3days'
    LATE_NIGHT = 'late_night'
    LOW_MOOD_3DAYS = 'low_mood_3days'

    @property
    def care_display_name(self) -> str:
        """Get display name for care type"""
        names = {
            self.INACTIVE_3DAYS: '久未登录关心',
            self.LATE_NIGHT: '深夜关心',
            self.LOW_MOOD_3DAYS: '情绪关心',
        }
        return names.get(self.care_type, self.care_type)

    @property
    def is_recent(self) -> bool:
        """Check if care action was triggered recently (within 7 days)"""
        if not self.triggered_at:
            return False
        days_passed = (datetime.utcnow() - self.triggered_at).days
        return days_passed < 7

    def mark_as_responded(self):
        """Mark this care message as responded by user"""
        self.was_responded = True
        self.responded_at = datetime.utcnow()

    def __repr__(self):
        return f"<ReverseCare(id={self.id}, user_id={self.user_id}, type={self.care_type}, responded={self.was_responded})>"
