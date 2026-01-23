"""
ProactiveMention model for tracking AI proactive memory mentions
Story 4.6: 主动提及机制与记忆回顾
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class ProactiveMention(Base):
    """
    ProactiveMention model for tracking when AI proactively mentions memories

    This helps:
    1. Track which memories have been proactively mentioned
    2. Enforce daily limit (max 1 proactive mention per day)
    3. Avoid mentioning same memory too frequently
    4. Track user engagement with proactive mentions
    """
    __tablename__ = "proactive_mentions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    memory_id = Column(Integer, ForeignKey("memories.id", ondelete="CASCADE"), nullable=False)
    mention_date = Column(Date, nullable=False)
    proactive_message = Column(Text, nullable=False)
    was_replied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="proactive_mentions")
    memory = relationship("Memory", back_populates="proactive_mentions")

    # Unique constraint: don't mention same memory multiple times on same day
    __table_args__ = (
        UniqueConstraint('user_id', 'memory_id', 'mention_date', name='uq_user_memory_mention_date'),
    )

    def mark_replied(self):
        """Mark that user replied to this proactive mention"""
        self.was_replied = True

    @property
    def is_today(self) -> bool:
        """Check if this mention was sent today"""
        return self.mention_date == date.today()

    def __repr__(self):
        return f"<ProactiveMention(id={self.id}, user_id={self.user_id}, memory_id={self.memory_id}, date={self.mention_date})>"
