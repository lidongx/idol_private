"""
Automatic Backup Task
Story 8.3: 云端备份与数据导出
Runs daily at 2:00 AM UTC to backup all user data
"""
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import SessionLocal
from app.models.user import User
from app.services.backup_service import BackupService


# Global scheduler instance
_backup_scheduler = None


def backup_all_users():
    """
    Backup data for all users
    Runs daily at 4:00 AM UTC
    """
    print(f"[Backup Task] Starting daily backup at {datetime.utcnow().isoformat()}")

    db = SessionLocal()
    try:
        # Get all active users
        users = db.query(User).all()
        print(f"[Backup Task] Found {len(users)} users to backup")

        backup_service = BackupService(db)
        success_count = 0
        error_count = 0

        for user in users:
            try:
                # Save backup to file
                filepath = backup_service.save_backup_to_file(
                    user_id=user.id,
                    backup_dir="backups/daily"
                )
                success_count += 1
                print(f"[Backup Task] ✓ User {user.id} backed up successfully")

            except Exception as e:
                error_count += 1
                print(f"[Backup Task] ✗ Error backing up user {user.id}: {e}")

        print(f"[Backup Task] Backup completed: {success_count} successful, {error_count} errors")

    except Exception as e:
        print(f"[Backup Task] Fatal error during backup: {e}")

    finally:
        db.close()


def start_backup_task():
    """
    Start the automatic backup task
    Scheduled to run daily at 4:00 AM UTC
    """
    global _backup_scheduler

    if _backup_scheduler is not None:
        print("[Backup Task] Backup task already running")
        return

    _backup_scheduler = BackgroundScheduler()

    # Schedule daily backup at 4:00 AM UTC
    _backup_scheduler.add_job(
        func=backup_all_users,
        trigger=CronTrigger(hour=4, minute=0),
        id='daily_backup',
        name='Daily User Data Backup',
        replace_existing=True
    )

    _backup_scheduler.start()
    print("[Backup Task] Daily backup task started (runs at 4:00 AM UTC)")


def stop_backup_task():
    """Stop the automatic backup task"""
    global _backup_scheduler

    if _backup_scheduler is not None:
        _backup_scheduler.shutdown()
        _backup_scheduler = None
        print("[Backup Task] Backup task stopped")


def run_backup_now():
    """
    Manually trigger backup immediately (for testing)
    """
    print("[Backup Task] Manual backup triggered")
    backup_all_users()
