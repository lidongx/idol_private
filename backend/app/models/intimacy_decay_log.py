"""
IntimacyDecayLog model for tracking intimacy decay events
Story 6.5: 亲密度衰减与保持机制
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class IntimacyDecayLog(Base):
    """
    IntimacyDecayLog model for tracking intimacy exp decay

    Tracks when and why intimacy exp decreases due to inactivity
    """
    __tablename__ = "intimacy_decay_logs"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    decay_amount = Column(Integer, nullable=False)  # Negative value (e.g., -5)
    reason = Column(String(100), nullable=False)
    intimacy_exp_before = Column(Integer, nullable=False)
    intimacy_exp_after = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    conversation = relationship("Conversation", backref="decay_logs")

    # Reason constants
    REASON_INACTIVE_7DAYS = 'inactive_7days'
    REASON_INACTIVE_14DAYS = 'inactive_14days'
    REASON_INACTIVE_30DAYS = 'inactive_30days'

    @property
    def reason_display_name(self) -> str:
        """Get display name for decay reason"""
        reason_names = {
            self.REASON_INACTIVE_7DAYS: '7天未互动',
            self.REASON_INACTIVE_14DAYS: '14天未互动',
            self.REASON_INACTIVE_30DAYS: '30天未互动',
        }
        return reason_names.get(self.reason, self.reason)

    @property
    def days_since_decay(self) -> int:
        """Calculate days since decay occurred"""
        if self.created_at:
            delta = datetime.utcnow() - self.created_at
            return delta.days
        return 0

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'decay_amount': self.decay_amount,
            'reason': self.reason,
            'reason_display': self.reason_display_name,
            'intimacy_exp_before': self.intimacy_exp_before,
            'intimacy_exp_after': self.intimacy_exp_after,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'days_since_decay': self.days_since_decay,
        }

    def __repr__(self):
        return f"<IntimacyDecayLog(id={self.id}, conversation_id={self.conversation_id}, decay_amount={self.decay_amount}, reason={self.reason})>"
