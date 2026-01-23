"""
DailyRitual model for daily routine tracking
Story 5.3: 每日仪式（早安/运势/晚安）
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class DailyRitual(Base):
    """
    DailyRitual model for tracking daily rituals

    Tracks three types of daily rituals:
    1. morning_greeting - Morning greeting (7:00-9:00)
    2. fortune - Daily fortune check (anytime)
    3. night_greeting - Night greeting (22:00-24:00)
    """
    __tablename__ = "daily_rituals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    idol_id = Column(Integer, ForeignKey("idols.id", ondelete="CASCADE"), nullable=False)
    ritual_type = Column(String(50), nullable=False)
    ritual_date = Column(Date, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    fortune_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="daily_rituals")
    idol = relationship("Idol")

    # Unique constraint: one ritual of each type per user per day
    __table_args__ = (
        UniqueConstraint('user_id', 'ritual_type', 'ritual_date', name='uq_user_ritual_type_date'),
    )

    # Ritual types
    MORNING_GREETING = 'morning_greeting'
    FORTUNE = 'fortune'
    NIGHT_GREETING = 'night_greeting'

    @property
    def ritual_display_name(self) -> str:
        """Get display name for ritual type"""
        names = {
            self.MORNING_GREETING: '早安问候',
            self.FORTUNE: '每日运势',
            self.NIGHT_GREETING: '晚安问候',
        }
        return names.get(self.ritual_type, self.ritual_type)

    @property
    def is_today(self) -> bool:
        """Check if ritual was completed today"""
        return self.ritual_date == date.today()

    @staticmethod
    def get_ritual_exp_reward(ritual_type: str) -> int:
        """
        Get experience points reward for ritual type

        Args:
            ritual_type: Ritual type

        Returns:
            Experience points
        """
        rewards = {
            DailyRitual.MORNING_GREETING: 10,
            DailyRitual.FORTUNE: 5,
            DailyRitual.NIGHT_GREETING: 10,
        }
        return rewards.get(ritual_type, 0)

    def __repr__(self):
        return f"<DailyRitual(id={self.id}, user_id={self.user_id}, type={self.ritual_type}, date={self.ritual_date})>"
