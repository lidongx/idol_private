"""
Order model for subscription purchases
Story 7.1: 订阅套餐数据模型与定价策略
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    """
    Order model for subscription purchase orders

    Order status flow:
    pending -> paid (success)
    pending -> failed (payment failed)
    pending -> cancelled (user cancelled)
    paid -> refunded (refund processed)
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50))
    status = Column(String(20), default='pending', index=True)
    paid_at = Column(DateTime, nullable=True, index=True)
    expires_at = Column(DateTime, nullable=True)
    transaction_id = Column(String(100))
    refund_reason = Column(Text)
    refunded_at = Column(DateTime, nullable=True)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="orders")
    plan = relationship("SubscriptionPlan", back_populates="orders")

    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'

    # Payment method constants
    PAYMENT_ALIPAY = 'alipay'
    PAYMENT_WECHAT = 'wechat'
    PAYMENT_APPLE_IAP = 'apple_iap'
    PAYMENT_GOOGLE_PLAY = 'google_play'

    @property
    def status_display(self) -> str:
        """Get display name for order status"""
        status_names = {
            self.STATUS_PENDING: '待支付',
            self.STATUS_PAID: '已支付',
            self.STATUS_FAILED: '支付失败',
            self.STATUS_CANCELLED: '已取消',
            self.STATUS_REFUNDED: '已退款',
        }
        return status_names.get(self.status, self.status)

    @property
    def payment_method_display(self) -> str:
        """Get display name for payment method"""
        method_names = {
            self.PAYMENT_ALIPAY: '支付宝',
            self.PAYMENT_WECHAT: '微信支付',
            self.PAYMENT_APPLE_IAP: 'Apple内购',
            self.PAYMENT_GOOGLE_PLAY: 'Google Play',
        }
        return method_names.get(self.payment_method, self.payment_method or '未知')

    @property
    def is_paid(self) -> bool:
        """Check if order is paid"""
        return self.status == self.STATUS_PAID

    @property
    def is_pending(self) -> bool:
        """Check if order is pending payment"""
        return self.status == self.STATUS_PENDING

    @property
    def is_active(self) -> bool:
        """Check if subscription is still active"""
        if not self.is_paid:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    @property
    def days_until_expiry(self) -> int:
        """Calculate days until subscription expires"""
        if not self.expires_at:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    def mark_as_paid(self, transaction_id: str = None):
        """Mark order as paid"""
        self.status = self.STATUS_PAID
        self.paid_at = datetime.utcnow()
        if transaction_id:
            self.transaction_id = transaction_id

        # Calculate expiry date
        if self.plan and self.plan.duration_days > 0:
            from datetime import timedelta
            self.expires_at = datetime.utcnow() + timedelta(days=self.plan.duration_days)

    def mark_as_failed(self, reason: str = None):
        """Mark order as failed"""
        self.status = self.STATUS_FAILED
        if reason and self.metadata:
            self.metadata['failure_reason'] = reason
        elif reason:
            self.metadata = {'failure_reason': reason}

    def mark_as_cancelled(self):
        """Mark order as cancelled"""
        self.status = self.STATUS_CANCELLED

    def mark_as_refunded(self, reason: str = None):
        """Mark order as refunded"""
        self.status = self.STATUS_REFUNDED
        self.refunded_at = datetime.utcnow()
        if reason:
            self.refund_reason = reason

    def to_dict(self, include_plan_details: bool = True):
        """Convert to dictionary for API responses"""
        result = {
            'id': self.id,
            'order_no': self.order_no,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'payment_method_display': self.payment_method_display,
            'status': self.status,
            'status_display': self.status_display,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'transaction_id': self.transaction_id,
            'is_active': self.is_active,
            'days_until_expiry': self.days_until_expiry,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

        if include_plan_details and self.plan:
            result['plan'] = self.plan.to_dict()

        if self.refunded_at:
            result['refunded_at'] = self.refunded_at.isoformat()
            result['refund_reason'] = self.refund_reason

        return result

    def __repr__(self):
        return f"<Order(id={self.id}, order_no={self.order_no}, status={self.status}, amount={self.amount})>"
