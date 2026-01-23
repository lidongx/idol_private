"""
SubscriptionLog model for tracking subscription changes
Story 7.5: 订阅激活与权限管理
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SubscriptionLog(Base):
    """
    SubscriptionLog model for tracking subscription lifecycle events

    Actions:
    - activate: User first activates subscription
    - renew: Subscription renewed (auto-renew or manual)
    - cancel: User cancels subscription (remains active until expiry)
    - expire: Subscription expired
    - upgrade: User upgrades to higher tier
    - downgrade: User downgrades to lower tier
    - refund: Subscription refunded
    """
    __tablename__ = "subscription_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey('subscription_plans.id'), nullable=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscription_logs")
    plan = relationship("SubscriptionPlan")
    order = relationship("Order")

    # Action constants
    ACTION_ACTIVATE = 'activate'
    ACTION_RENEW = 'renew'
    ACTION_CANCEL = 'cancel'
    ACTION_EXPIRE = 'expire'
    ACTION_UPGRADE = 'upgrade'
    ACTION_DOWNGRADE = 'downgrade'
    ACTION_REFUND = 'refund'

    @property
    def action_display(self) -> str:
        """Get display name for action"""
        action_names = {
            self.ACTION_ACTIVATE: '激活订阅',
            self.ACTION_RENEW: '续费',
            self.ACTION_CANCEL: '取消订阅',
            self.ACTION_EXPIRE: '订阅过期',
            self.ACTION_UPGRADE: '升级套餐',
            self.ACTION_DOWNGRADE: '降级套餐',
            self.ACTION_REFUND: '退款',
        }
        return action_names.get(self.action, self.action)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'action_display': self.action_display,
            'plan_id': self.plan_id,
            'order_id': self.order_id,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<SubscriptionLog(id={self.id}, user_id={self.user_id}, action={self.action})>"
