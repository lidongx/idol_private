"""
Message Quota Service
Handles daily message quota tracking and enforcement for freemium model
"""
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User
from app.models.message_quota import MessageQuota
from app.core.exceptions import QuotaExceededException


# Quota limits
FREE_USER_DAILY_LIMIT = 20
PREMIUM_USER_QUOTA = -1  # Unlimited


class QuotaService:
    """Service for managing message quotas"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_quota_limit(self, user: User) -> int:
        """
        Get quota limit based on user subscription tier

        Args:
            user: User instance

        Returns:
            Quota limit (-1 for unlimited, positive number for free tier)
        """
        if user.subscription_tier == 'premium':
            # Check if premium subscription is still valid
            if user.subscription_expires_at:
                if user.subscription_expires_at > datetime.now():
                    return PREMIUM_USER_QUOTA
                # Expired premium, revert to free
                return FREE_USER_DAILY_LIMIT
            # Premium without expiry (lifetime)
            return PREMIUM_USER_QUOTA

        # Free user
        return FREE_USER_DAILY_LIMIT

    def get_or_create_daily_quota(self, user_id: int, target_date: date = None) -> MessageQuota:
        """
        Get or create daily quota record for user

        Args:
            user_id: User ID
            target_date: Target date (defaults to today in UTC+8)

        Returns:
            MessageQuota instance
        """
        if target_date is None:
            # Use UTC+8 timezone (Beijing Time)
            utc_now = datetime.utcnow()
            beijing_now = utc_now + timedelta(hours=8)
            target_date = beijing_now.date()

        # Try to get existing quota
        quota = self.db.query(MessageQuota).filter(
            and_(
                MessageQuota.user_id == user_id,
                MessageQuota.date == target_date
            )
        ).first()

        if quota:
            return quota

        # Create new quota record
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        quota_limit = self.get_user_quota_limit(user)

        quota = MessageQuota(
            user_id=user_id,
            date=target_date,
            messages_sent=0,
            quota_limit=quota_limit
        )
        self.db.add(quota)
        self.db.commit()
        self.db.refresh(quota)

        return quota

    def check_and_increment_quota(self, user_id: int) -> MessageQuota:
        """
        Check if user has remaining quota and increment counter

        Args:
            user_id: User ID

        Returns:
            Updated MessageQuota instance

        Raises:
            QuotaExceededException: If user has no remaining quota
        """
        # Get or create today's quota
        quota = self.get_or_create_daily_quota(user_id)

        # Check if quota is exhausted
        if quota.is_exhausted:
            raise QuotaExceededException(
                message="今天的免费额度用完啦~升级会员解锁无限对话"
            )

        # Increment message count
        quota.messages_sent += 1
        self.db.commit()
        self.db.refresh(quota)

        return quota

    def get_quota_info(self, user_id: int, target_date: date = None) -> dict:
        """
        Get quota information for user

        Args:
            user_id: User ID
            target_date: Target date (defaults to today)

        Returns:
            Dict with quota info:
            {
                "date": "2026-01-14",
                "messages_sent": 5,
                "quota_limit": 20,
                "remaining": 15,
                "is_unlimited": False
            }
        """
        quota = self.get_or_create_daily_quota(user_id, target_date)

        return {
            "date": quota.date.isoformat(),
            "messages_sent": quota.messages_sent,
            "quota_limit": quota.quota_limit,
            "remaining": quota.remaining,
            "is_unlimited": quota.is_unlimited
        }

    def reset_daily_quotas(self, target_date: date = None):
        """
        Reset all quotas for a specific date (maintenance task)

        This is typically run as a daily cleanup job to remove old quota records.
        New quota records are created automatically when users send messages.

        Args:
            target_date: Date to reset (defaults to yesterday)
        """
        if target_date is None:
            # Default to yesterday
            utc_now = datetime.utcnow()
            beijing_now = utc_now + timedelta(hours=8)
            target_date = (beijing_now - timedelta(days=1)).date()

        # Delete old quota records (older than 30 days for analytics)
        cutoff_date = target_date - timedelta(days=30)
        self.db.query(MessageQuota).filter(
            MessageQuota.date < cutoff_date
        ).delete()
        self.db.commit()

    def get_quota_stats(self, user_id: int, days: int = 7) -> list:
        """
        Get quota usage statistics for past N days

        Args:
            user_id: User ID
            days: Number of days to retrieve

        Returns:
            List of daily quota info dictionaries
        """
        # Calculate date range
        utc_now = datetime.utcnow()
        beijing_now = utc_now + timedelta(hours=8)
        end_date = beijing_now.date()
        start_date = end_date - timedelta(days=days - 1)

        # Query quotas
        quotas = self.db.query(MessageQuota).filter(
            and_(
                MessageQuota.user_id == user_id,
                MessageQuota.date >= start_date,
                MessageQuota.date <= end_date
            )
        ).order_by(MessageQuota.date.desc()).all()

        return [
            {
                "date": q.date.isoformat(),
                "messages_sent": q.messages_sent,
                "quota_limit": q.quota_limit,
                "remaining": q.remaining,
            }
            for q in quotas
        ]
