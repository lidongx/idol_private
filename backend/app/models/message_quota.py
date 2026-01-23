"""
MessageQuota SQLAlchemy Model
Tracks daily message usage for freemium model
"""
from sqlalchemy import Column, Integer, Date, ForeignKey, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class MessageQuota(Base):
    """
    Message quota tracking model

    Tracks daily message usage per user for freemium limits:
    - Free users: 20 messages per day (quota_limit = 20)
    - Premium users: Unlimited messages (quota_limit = -1)
    """

    __tablename__ = "message_quotas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联用户ID"
    )
    date = Column(
        Date,
        nullable=False,
        index=True,
        comment="配额日期（UTC+8时区）"
    )
    messages_sent = Column(
        Integer,
        default=0,
        nullable=False,
        comment="已发送消息数"
    )
    quota_limit = Column(
        Integer,
        nullable=False,
        comment="每日限额（-1表示无限制）"
    )
    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='unique_user_date_quota'),
    )

    def __repr__(self):
        return f"<MessageQuota(user_id={self.user_id}, date={self.date}, sent={self.messages_sent}/{self.quota_limit})>"

    @property
    def remaining(self) -> int:
        """
        Calculate remaining messages

        Returns:
            Remaining messages count (-1 for unlimited)
        """
        if self.quota_limit == -1:
            return -1  # Unlimited
        return max(0, self.quota_limit - self.messages_sent)

    @property
    def is_exhausted(self) -> bool:
        """
        Check if quota is exhausted

        Returns:
            True if no messages remaining, False otherwise
        """
        if self.quota_limit == -1:
            return False  # Unlimited never exhausted
        return self.messages_sent >= self.quota_limit

    @property
    def is_unlimited(self) -> bool:
        """
        Check if quota is unlimited

        Returns:
            True if quota_limit is -1
        """
        return self.quota_limit == -1
