"""
Account Deletion Task
Story 8.4: 账号删除与数据清除
Runs daily at 5:00 AM UTC to process expired deletion requests
"""
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import SessionLocal
from app.services.account_deletion_service import AccountDeletionService


# Global scheduler instance
_deletion_scheduler = None


def process_pending_deletions():
    """
    Process all pending deletion requests that have passed cooling-off period
    Runs daily at 5:00 AM UTC
    """
    print(f"[Deletion Task] Starting deletion processing at {datetime.utcnow().isoformat()}")

    db = SessionLocal()
    try:
        deletion_service = AccountDeletionService(db)

        # Get all pending deletions ready for execution
        pending_deletions = deletion_service.get_pending_deletions()

        if not pending_deletions:
            print("[Deletion Task] No pending deletions to process")
            return

        print(f"[Deletion Task] Found {len(pending_deletions)} accounts ready for deletion")

        success_count = 0
        error_count = 0

        for deletion_request in pending_deletions:
            try:
                # Execute permanent deletion
                result = deletion_service.permanently_delete_account(
                    user_id=deletion_request.user_id,
                    deletion_request_id=deletion_request.id
                )

                success_count += 1
                print(f"[Deletion Task] ✓ Successfully deleted user {deletion_request.user_id}")

            except Exception as e:
                error_count += 1
                print(f"[Deletion Task] ✗ Error deleting user {deletion_request.user_id}: {e}")

        print(f"[Deletion Task] Deletion processing completed: {success_count} successful, {error_count} errors")

    except Exception as e:
        print(f"[Deletion Task] Fatal error during deletion processing: {e}")

    finally:
        db.close()


def start_deletion_task():
    """
    Start the automatic deletion task
    Scheduled to run daily at 5:00 AM UTC
    """
    global _deletion_scheduler

    if _deletion_scheduler is not None:
        print("[Deletion Task] Deletion task already running")
        return

    _deletion_scheduler = BackgroundScheduler()

    # Schedule daily deletion processing at 5:00 AM UTC
    _deletion_scheduler.add_job(
        func=process_pending_deletions,
        trigger=CronTrigger(hour=5, minute=0),
        id='daily_account_deletion',
        name='Daily Account Deletion Processing',
        replace_existing=True
    )

    _deletion_scheduler.start()
    print("[Deletion Task] Daily deletion task started (runs at 5:00 AM UTC)")


def stop_deletion_task():
    """Stop the automatic deletion task"""
    global _deletion_scheduler

    if _deletion_scheduler is not None:
        _deletion_scheduler.shutdown()
        _deletion_scheduler = None
        print("[Deletion Task] Deletion task stopped")


def run_deletion_now():
    """
    Manually trigger deletion processing immediately (for testing)
    """
    print("[Deletion Task] Manual deletion processing triggered")
    process_pending_deletions()
