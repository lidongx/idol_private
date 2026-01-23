"""
RefundRequest model for handling subscription refunds
Story 7.6: 订阅管理与退款处理
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class RefundRequest(Base):
    """
    RefundRequest model for tracking refund applications

    Statuses:
    - pending: Awaiting review
    - approved: Refund approved and processed
    - rejected: Refund request denied
    """
    __tablename__ = "refund_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    reason = Column(String(200), nullable=False)
    detailed_reason = Column(Text, nullable=True)  # Optional detailed explanation
    status = Column(String(20), default='pending', nullable=False, index=True)
    admin_notes = Column(Text, nullable=True)  # Internal notes for admin review
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
    order = relationship("Order")

    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    # Common refund reasons
    REASON_NOT_SATISFIED = 'not_satisfied'
    REASON_TECHNICAL_ISSUE = 'technical_issue'
    REASON_ACCIDENTAL_PURCHASE = 'accidental_purchase'
    REASON_BILLING_ERROR = 'billing_error'
    REASON_OTHER = 'other'

    @property
    def status_display(self) -> str:
        """Get display name for status"""
        status_names = {
            self.STATUS_PENDING: '待审核',
            self.STATUS_APPROVED: '已通过',
            self.STATUS_REJECTED: '已拒绝',
        }
        return status_names.get(self.status, self.status)

    @property
    def reason_display(self) -> str:
        """Get display name for reason"""
        reason_names = {
            self.REASON_NOT_SATISFIED: '不满意服务',
            self.REASON_TECHNICAL_ISSUE: '技术问题',
            self.REASON_ACCIDENTAL_PURCHASE: '误购',
            self.REASON_BILLING_ERROR: '扣费错误',
            self.REASON_OTHER: '其他原因',
        }
        return reason_names.get(self.reason, self.reason)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'reason': self.reason,
            'reason_display': self.reason_display,
            'detailed_reason': self.detailed_reason,
            'status': self.status,
            'status_display': self.status_display,
            'admin_notes': self.admin_notes,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<RefundRequest(id={self.id}, order_id={self.order_id}, status={self.status})>"
