"""
Task Scheduler Configuration
Story 7.5: 订阅激活与权限管理
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from app.tasks.scheduled_tasks import check_expired_subscriptions, send_renewal_reminders


# Global scheduler instance
scheduler = BackgroundScheduler()


def start_scheduler():
    """
    Start the background scheduler with all scheduled tasks
    """
    # Task 1: Check expired subscriptions daily at 00:00 UTC
    scheduler.add_job(
        func=check_expired_subscriptions,
        trigger=CronTrigger(hour=0, minute=0),  # Daily at 00:00 UTC
        id='check_expired_subscriptions',
        name='Check and downgrade expired subscriptions',
        replace_existing=True
    )

    # Task 2: Send renewal reminders daily at 10:00 UTC
    scheduler.add_job(
        func=send_renewal_reminders,
        trigger=CronTrigger(hour=10, minute=0),  # Daily at 10:00 UTC
        id='send_renewal_reminders',
        name='Send subscription renewal reminders',
        replace_existing=True
    )

    # Start the scheduler
    scheduler.start()
    print(f"[Scheduler] Started at {datetime.utcnow().isoformat()}")
    print("[Scheduler] Scheduled tasks:")
    print("  - check_expired_subscriptions: Daily at 00:00 UTC")
    print("  - send_renewal_reminders: Daily at 10:00 UTC")


def stop_scheduler():
    """
    Stop the background scheduler
    """
    if scheduler.running:
        scheduler.shutdown()
        print(f"[Scheduler] Stopped at {datetime.utcnow().isoformat()}")


def run_task_now(task_name: str):
    """
    Manually trigger a scheduled task for testing

    Args:
        task_name: Name of the task ('check_expired_subscriptions' or 'send_renewal_reminders')
    """
    if task_name == 'check_expired_subscriptions':
        return check_expired_subscriptions()
    elif task_name == 'send_renewal_reminders':
        return send_renewal_reminders()
    else:
        raise ValueError(f"Unknown task: {task_name}")
