"""
SubscriptionPlan model for subscription packages
Story 7.1: 订阅套餐数据模型与定价策略
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class SubscriptionPlan(Base):
    """
    SubscriptionPlan model for subscription package configuration

    Plan types:
    - free: Free plan (default for all users)
    - monthly: Monthly subscription
    - yearly: Yearly subscription (with discount)
    """
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String(50), nullable=False)
    plan_type = Column(String(20), nullable=False, index=True)
    price_cny = Column(Numeric(10, 2), nullable=False)
    duration_days = Column(Integer, nullable=False)
    features = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    sort_order = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="plan")

    # Plan type constants
    TYPE_FREE = 'free'
    TYPE_MONTHLY = 'monthly'
    TYPE_YEARLY = 'yearly'

    @property
    def plan_type_display(self) -> str:
        """Get display name for plan type"""
        type_names = {
            self.TYPE_FREE: '免费版',
            self.TYPE_MONTHLY: '月度会员',
            self.TYPE_YEARLY: '年度会员',
        }
        return type_names.get(self.plan_type, self.plan_type)

    @property
    def price_display(self) -> str:
        """Get formatted price display"""
        if self.price_cny == 0:
            return '免费'
        return f'¥{self.price_cny}'

    @property
    def duration_display(self) -> str:
        """Get formatted duration display"""
        if self.duration_days == 0:
            return '永久'
        elif self.duration_days == 30:
            return '1个月'
        elif self.duration_days == 365:
            return '1年'
        else:
            return f'{self.duration_days}天'

    def get_feature(self, feature_key: str, default=None):
        """Get specific feature value from features JSON"""
        if self.features and isinstance(self.features, dict):
            return self.features.get(feature_key, default)
        return default

    @property
    def messages_per_day(self) -> int:
        """Get daily message limit (-1 means unlimited)"""
        return self.get_feature('messages_per_day', 20)

    @property
    def has_exclusive_content(self) -> bool:
        """Check if plan has exclusive content access"""
        return self.get_feature('exclusive_content', False)

    @property
    def has_priority_response(self) -> bool:
        """Check if plan has priority AI response"""
        return self.get_feature('priority_response', False)

    @property
    def has_no_ads(self) -> bool:
        """Check if plan has ad-free experience"""
        return self.get_feature('no_ads', False)

    @property
    def intimacy_decay_disabled(self) -> bool:
        """Check if intimacy decay is disabled"""
        return self.get_feature('intimacy_decay_disabled', False)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'plan_name': self.plan_name,
            'plan_type': self.plan_type,
            'plan_type_display': self.plan_type_display,
            'price_cny': float(self.price_cny),
            'price_display': self.price_display,
            'duration_days': self.duration_days,
            'duration_display': self.duration_display,
            'features': self.features,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<SubscriptionPlan(id={self.id}, name={self.plan_name}, type={self.plan_type}, price={self.price_cny})>"
