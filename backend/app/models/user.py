"""
User SQLAlchemy Model
"""
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """User model for authentication and subscription management"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(11), unique=True, nullable=False, index=True, comment="用户手机号")
    password_hash = Column(String(255), nullable=False, comment="bcrypt密码哈希")
    subscription_tier = Column(String(20), default="free", nullable=False, comment="订阅等级: free/basic/premium")
    subscription_expires_at = Column(TIMESTAMP, nullable=True, comment="订阅过期时间")
    onboarding_completed = Column(Boolean, default=False, nullable=False, index=True, comment="是否完成引导流程")
    last_active_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, comment="最后活跃时间")
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # Relationships
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    memory_tags = relationship("MemoryTag", back_populates="user", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="user", cascade="all, delete-orphan")
    proactive_mentions = relationship("ProactiveMention", back_populates="user", cascade="all, delete-orphan")
    moment_likes = relationship("IdolMomentLike", back_populates="user", cascade="all, delete-orphan")
    daily_rituals = relationship("DailyRitual", back_populates="user", cascade="all, delete-orphan")
    reverse_care_logs = relationship("ReverseCare", back_populates="user", cascade="all, delete-orphan")
    special_events = relationship("UserSpecialEvent", back_populates="user", cascade="all, delete-orphan")
    subscription_logs = relationship("SubscriptionLog", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("UserDevice", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone}, tier={self.subscription_tier})>"
