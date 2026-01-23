"""
Operations Statistics Service
Story 10.1: 运营数据仪表盘 (Operations Data Dashboard)

Provides aggregated statistics for operations team:
- DAU/MAU (Daily/Monthly Active Users)
- New user registrations
- Retention rates (7-day, 30-day)
- Payment conversion rate
- Subscription renewal rate
- Average session duration
- Message volume
- AI API call volume
- Intimacy level distribution
- Error rates
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func, and_, distinct
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.subscription import Subscription, SubscriptionPlan
from app.models.intimacy_level import IntimacyLevel


class OperationsStatsService:
    """Service for calculating operations metrics"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== User Metrics ====================

    def get_dau(self, date: Optional[datetime] = None) -> int:
        """
        Get Daily Active Users

        Active = sent at least one message that day
        """
        if date is None:
            date = datetime.utcnow()

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        dau = self.db.query(distinct(Message.user_id)).filter(
            and_(
                Message.created_at >= start_of_day,
                Message.created_at < end_of_day,
            )
        ).count()

        return dau

    def get_mau(self, month: Optional[datetime] = None) -> int:
        """
        Get Monthly Active Users

        Active = sent at least one message in the last 30 days
        """
        if month is None:
            month = datetime.utcnow()

        thirty_days_ago = month - timedelta(days=30)

        mau = self.db.query(distinct(Message.user_id)).filter(
            Message.created_at >= thirty_days_ago
        ).count()

        return mau

    def get_new_users(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """Get new user registrations in a time period"""
        if start_date is None:
            start_date = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        if end_date is None:
            end_date = start_date + timedelta(days=1)

        new_users = self.db.query(User).filter(
            and_(
                User.created_at >= start_date,
                User.created_at < end_date,
            )
        ).count()

        return new_users

    def get_total_users(self) -> int:
        """Get total registered users"""
        return self.db.query(User).count()

    # ==================== Retention Metrics ====================

    def get_retention_rate(
        self,
        cohort_date: datetime,
        retention_days: int,
    ) -> float:
        """
        Calculate retention rate for a cohort

        Args:
            cohort_date: Date when users signed up
            retention_days: Number of days after signup (e.g., 7, 30)

        Returns:
            Retention rate as percentage (0.0 - 100.0)
        """
        # Get users who signed up on cohort_date
        start_of_day = cohort_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        cohort_users = self.db.query(User.id).filter(
            and_(
                User.created_at >= start_of_day,
                User.created_at < end_of_day,
            )
        ).all()

        if not cohort_users:
            return 0.0

        cohort_user_ids = [user.id for user in cohort_users]
        cohort_size = len(cohort_user_ids)

        # Check how many were active on retention day
        retention_date = start_of_day + timedelta(days=retention_days)
        retention_date_end = retention_date + timedelta(days=1)

        retained_users = self.db.query(distinct(Message.user_id)).filter(
            and_(
                Message.user_id.in_(cohort_user_ids),
                Message.created_at >= retention_date,
                Message.created_at < retention_date_end,
            )
        ).count()

        return (retained_users / cohort_size) * 100 if cohort_size > 0 else 0.0

    # ==================== Payment Metrics ====================

    def get_paying_users_count(self) -> int:
        """Get count of users with active subscriptions"""
        return self.db.query(distinct(Subscription.user_id)).filter(
            and_(
                Subscription.is_active == True,  # noqa: E712
                Subscription.expires_at > datetime.utcnow(),
            )
        ).count()

    def get_payment_conversion_rate(self) -> float:
        """
        Get payment conversion rate

        Returns:
            Conversion rate as percentage (0.0 - 100.0)
        """
        total_users = self.get_total_users()
        if total_users == 0:
            return 0.0

        paying_users = self.get_paying_users_count()
        return (paying_users / total_users) * 100

    def get_subscription_renewal_rate(self, days: int = 30) -> float:
        """
        Calculate subscription renewal rate in the last N days

        Args:
            days: Number of days to look back

        Returns:
            Renewal rate as percentage (0.0 - 100.0)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Subscriptions that expired in the period
        expired_subscriptions = self.db.query(Subscription).filter(
            and_(
                Subscription.expires_at >= cutoff_date,
                Subscription.expires_at < datetime.utcnow(),
            )
        ).all()

        if not expired_subscriptions:
            return 0.0

        # Check how many renewed (have a new active subscription)
        renewed_count = 0
        for sub in expired_subscriptions:
            has_renewed = self.db.query(Subscription).filter(
                and_(
                    Subscription.user_id == sub.user_id,
                    Subscription.is_active == True,  # noqa: E712
                    Subscription.created_at > sub.expires_at,
                )
            ).first()

            if has_renewed:
                renewed_count += 1

        total_expired = len(expired_subscriptions)
        return (renewed_count / total_expired) * 100 if total_expired > 0 else 0.0

    def get_mrr(self) -> float:
        """
        Get Monthly Recurring Revenue (MRR)

        Returns:
            MRR in yuan (CNY)
        """
        # Get all active subscriptions
        active_subscriptions = self.db.query(Subscription).filter(
            and_(
                Subscription.is_active == True,  # noqa: E712
                Subscription.expires_at > datetime.utcnow(),
            )
        ).all()

        mrr = 0.0
        for sub in active_subscriptions:
            # Get plan details
            plan = self.db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == sub.plan_id
            ).first()

            if plan:
                # Normalize to monthly revenue
                if plan.duration_days == 30:
                    mrr += plan.price
                elif plan.duration_days == 90:
                    mrr += plan.price / 3
                elif plan.duration_days == 365:
                    mrr += plan.price / 12

        return round(mrr, 2)

    # ==================== Engagement Metrics ====================

    def get_total_messages(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """Get total messages sent in a time period"""
        query = self.db.query(Message)

        if start_date:
            query = query.filter(Message.created_at >= start_date)
        if end_date:
            query = query.filter(Message.created_at < end_date)

        return query.count()

    def get_average_session_duration(self, days: int = 7) -> float:
        """
        Calculate average session duration in the last N days

        Returns:
            Average duration in minutes
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get all conversations in the period
        conversations = self.db.query(Conversation).filter(
            Conversation.updated_at >= cutoff_date
        ).all()

        if not conversations:
            return 0.0

        total_duration = 0
        for conv in conversations:
            if conv.created_at and conv.updated_at:
                duration = (conv.updated_at - conv.created_at).total_seconds() / 60
                total_duration += duration

        return round(total_duration / len(conversations), 2)

    def get_messages_per_user(self, days: int = 7) -> float:
        """
        Calculate average messages per user in the last N days

        Returns:
            Average messages per user
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        total_messages = self.get_total_messages(
            start_date=cutoff_date,
            end_date=datetime.utcnow(),
        )

        active_users = self.db.query(distinct(Message.user_id)).filter(
            Message.created_at >= cutoff_date
        ).count()

        if active_users == 0:
            return 0.0

        return round(total_messages / active_users, 2)

    # ==================== Intimacy Distribution ====================

    def get_intimacy_distribution(self) -> Dict[int, int]:
        """
        Get distribution of users across intimacy levels

        Returns:
            Dict mapping level -> user count
        """
        distribution = {}

        # Get all intimacy levels
        intimacy_records = self.db.query(
            IntimacyLevel.current_level,
            func.count(IntimacyLevel.user_id).label('count')
        ).group_by(IntimacyLevel.current_level).all()

        for level, count in intimacy_records:
            distribution[level] = count

        return distribution

    # ==================== System Metrics ====================

    def get_ai_api_call_count(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """
        Get count of AI API calls in a time period

        Approximated by counting AI-sent messages
        """
        query = self.db.query(Message).filter(
            Message.sender_type == 'idol'
        )

        if start_date:
            query = query.filter(Message.created_at >= start_date)
        if end_date:
            query = query.filter(Message.created_at < end_date)

        return query.count()

    # ==================== Dashboard Summary ====================

    def get_dashboard_summary(self) -> Dict:
        """
        Get comprehensive dashboard summary

        Returns all key metrics for the operations dashboard
        """
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)
        seven_days_ago = today - timedelta(days=7)
        thirty_days_ago = today - timedelta(days=30)

        # Calculate retention rates for recent cohorts
        # Use cohort from 7 days ago to calculate 7-day retention
        cohort_7d = today - timedelta(days=7)
        retention_7d = self.get_retention_rate(cohort_7d, 7)

        # Use cohort from 30 days ago to calculate 30-day retention
        cohort_30d = today - timedelta(days=30)
        retention_30d = self.get_retention_rate(cohort_30d, 30)

        return {
            # User metrics
            'total_users': self.get_total_users(),
            'dau': self.get_dau(today),
            'mau': self.get_mau(today),
            'new_users_today': self.get_new_users(
                start_date=today.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=today,
            ),
            'new_users_7d': self.get_new_users(
                start_date=seven_days_ago,
                end_date=today,
            ),
            'new_users_30d': self.get_new_users(
                start_date=thirty_days_ago,
                end_date=today,
            ),

            # Retention
            'retention_7d': round(retention_7d, 2),
            'retention_30d': round(retention_30d, 2),

            # Payment metrics
            'paying_users': self.get_paying_users_count(),
            'payment_conversion_rate': round(self.get_payment_conversion_rate(), 2),
            'subscription_renewal_rate': round(self.get_subscription_renewal_rate(30), 2),
            'mrr': self.get_mrr(),

            # Engagement metrics
            'total_messages_today': self.get_total_messages(
                start_date=today.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=today,
            ),
            'total_messages_7d': self.get_total_messages(
                start_date=seven_days_ago,
                end_date=today,
            ),
            'average_session_duration_minutes': self.get_average_session_duration(7),
            'messages_per_user_7d': self.get_messages_per_user(7),

            # System metrics
            'ai_api_calls_today': self.get_ai_api_call_count(
                start_date=today.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=today,
            ),
            'ai_api_calls_7d': self.get_ai_api_call_count(
                start_date=seven_days_ago,
                end_date=today,
            ),

            # Intimacy distribution
            'intimacy_distribution': self.get_intimacy_distribution(),

            # Metadata
            'generated_at': today.isoformat(),
        }

    def get_historical_data(
        self,
        metric: str,
        days: int = 30,
    ) -> List[Dict]:
        """
        Get historical data for a specific metric

        Args:
            metric: Metric name ('dau', 'new_users', 'messages', etc.)
            days: Number of days to look back

        Returns:
            List of {date, value} dictionaries
        """
        today = datetime.utcnow()
        data = []

        for i in range(days, 0, -1):
            date = today - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)

            if metric == 'dau':
                value = self.get_dau(date)
            elif metric == 'new_users':
                value = self.get_new_users(date_start, date_end)
            elif metric == 'messages':
                value = self.get_total_messages(date_start, date_end)
            elif metric == 'ai_calls':
                value = self.get_ai_api_call_count(date_start, date_end)
            else:
                value = 0

            data.append({
                'date': date_start.strftime('%Y-%m-%d'),
                'value': value,
            })

        return data
