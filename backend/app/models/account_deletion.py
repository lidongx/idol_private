"""
Account Deletion Request Model
Story 8.4: 账号删除与数据清除
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.database import Base


class AccountDeletionRequest(Base):
    """
    Account deletion request with 7-day cooling-off period

    Status Flow:
    1. pending: Request submitted, 7-day cooling-off period
    2. cancelled: User cancelled during cooling-off period
    3. completed: Account and all data permanently deleted
    """
    __tablename__ = "account_deletion_requests"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")

    # Foreign keys
    user_id = Column(Integer, index=True, nullable=False, comment="用户ID")

    # Status
    status = Column(String(20), nullable=False, default='pending', comment="状态: pending, cancelled, completed")

    # Deletion details
    reason = Column(String(50), nullable=True, comment="删除原因")
    detailed_reason = Column(Text, nullable=True, comment="详细说明（可选）")

    # Scheduled deletion date (7 days after request)
    scheduled_deletion_at = Column(DateTime, nullable=False, comment="预定删除时间（7天后）")

    # Actual deletion date (when completed)
    completed_at = Column(DateTime, nullable=True, comment="实际删除时间")

    # Backup before deletion
    backup_created = Column(Boolean, default=False, comment="是否已创建备份")
    backup_filepath = Column(String(500), nullable=True, comment="备份文件路径")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # Deletion reason constants
    REASON_NO_LONGER_NEEDED = 'no_longer_needed'
    REASON_TOO_EXPENSIVE = 'too_expensive'
    REASON_PRIVACY_CONCERNS = 'privacy_concerns'
    REASON_TECHNICAL_ISSUES = 'technical_issues'
    REASON_OTHER = 'other'

    @property
    def days_until_deletion(self) -> int:
        """Get number of days until scheduled deletion"""
        if self.status != 'pending':
            return 0

        delta = self.scheduled_deletion_at - datetime.utcnow()
        days = delta.total_seconds() / 86400
        return max(0, int(days))

    @property
    def can_cancel(self) -> bool:
        """Check if request can be cancelled (still in cooling-off period)"""
        return self.status == 'pending' and datetime.utcnow() < self.scheduled_deletion_at

    @property
    def is_ready_for_deletion(self) -> bool:
        """Check if request is ready for permanent deletion"""
        return (
            self.status == 'pending' and
            datetime.utcnow() >= self.scheduled_deletion_at
        )

    @property
    def reason_display(self) -> str:
        """Get display name for deletion reason"""
        reason_names = {
            self.REASON_NO_LONGER_NEEDED: '不再需要',
            self.REASON_TOO_EXPENSIVE: '费用太高',
            self.REASON_PRIVACY_CONCERNS: '隐私担忧',
            self.REASON_TECHNICAL_ISSUES: '技术问题',
            self.REASON_OTHER: '其他原因',
        }
        return reason_names.get(self.reason, self.reason)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'reason': self.reason,
            'reason_display': self.reason_display,
            'detailed_reason': self.detailed_reason,
            'scheduled_deletion_at': self.scheduled_deletion_at.isoformat(),
            'days_until_deletion': self.days_until_deletion,
            'can_cancel': self.can_cancel,
            'backup_created': self.backup_created,
            'created_at': self.created_at.isoformat(),
        }
