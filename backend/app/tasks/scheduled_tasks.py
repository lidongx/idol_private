"""
Scheduled Tasks for Subscription Management
Story 7.5: 订阅激活与权限管理
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List

from app.database import SessionLocal
from app.models.user import User
from app.models.subscription_log import SubscriptionLog


def check_expired_subscriptions():
    """
    Check for expired subscriptions and downgrade users to free tier

    This task should run daily (e.g., at 00:00 UTC) to:
    1. Find all premium users with expired subscriptions
    2. Downgrade them to free tier
    3. Record expiry in subscription logs

    Returns:
        Number of users downgraded
    """
    db: Session = SessionLocal()

    try:
        # Find all premium users with expired subscriptions
        now = datetime.utcnow()
        expired_users: List[User] = db.query(User).filter(
            and_(
                User.subscription_tier == 'premium',
                User.subscription_expires_at.isnot(None),
                User.subscription_expires_at < now
            )
        ).all()

        downgraded_count = 0

        for user in expired_users:
            # Downgrade user to free tier
            old_expires_at = user.subscription_expires_at
            user.subscription_tier = 'free'
            user.subscription_expires_at = None

            # Record subscription log
            subscription_log = SubscriptionLog(
                user_id=user.id,
                action=SubscriptionLog.ACTION_EXPIRE,
                plan_id=None,
                order_id=None,
                expires_at=old_expires_at,
                notes=f"Subscription expired on {old_expires_at.isoformat()}"
            )
            db.add(subscription_log)

            downgraded_count += 1

        # Commit all changes
        db.commit()

        print(f"[Subscription Expiry Check] Downgraded {downgraded_count} users to free tier")
        return downgraded_count

    except Exception as e:
        db.rollback()
        print(f"[Subscription Expiry Check] Error: {str(e)}")
        raise

    finally:
        db.close()


def send_renewal_reminders():
    """
    Send renewal reminders to users whose subscriptions will expire soon

    This task should run daily to:
    1. Find premium users whose subscriptions expire in 3 days
    2. Send reminder notifications

    Returns:
        Number of reminders sent
    """
    db: Session = SessionLocal()

    try:
        from datetime import timedelta

        # Find users expiring in 3 days
        now = datetime.utcnow()
        reminder_date = now + timedelta(days=3)

        users_to_remind: List[User] = db.query(User).filter(
            and_(
                User.subscription_tier == 'premium',
                User.subscription_expires_at.isnot(None),
                User.subscription_expires_at >= now,
                User.subscription_expires_at <= reminder_date
            )
        ).all()

        reminder_count = 0

        for user in users_to_remind:
            # TODO: Implement notification sending
            # For now, just log the reminder
            days_remaining = (user.subscription_expires_at - now).days

            # Record subscription log for reminder
            subscription_log = SubscriptionLog(
                user_id=user.id,
                action='reminder',  # Not a standard action, but useful for tracking
                plan_id=None,
                order_id=None,
                expires_at=user.subscription_expires_at,
                notes=f"Renewal reminder sent - {days_remaining} days remaining"
            )
            db.add(subscription_log)

            reminder_count += 1

        # Commit all changes
        db.commit()

        print(f"[Renewal Reminder] Sent {reminder_count} renewal reminders")
        return reminder_count

    except Exception as e:
        db.rollback()
        print(f"[Renewal Reminder] Error: {str(e)}")
        raise

    finally:
        db.close()
