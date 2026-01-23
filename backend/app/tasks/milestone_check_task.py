"""
Background task for daily milestone checking
Story 4.5: 周年纪念与主动回顾

This task runs daily at 2:00 AM to check if any users have reached
anniversary milestones (7 days, 30 days, 100 days, 365 days).
"""
import logging
import threading
import time
from datetime import datetime, time as dt_time
from typing import Optional

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.milestone_service import MilestoneService

logger = logging.getLogger(__name__)


class MilestoneCheckTask:
    """
    Background task for checking user milestones daily

    Runs at 2:00 AM every day to check if users have reached anniversary milestones.
    """

    def __init__(self, check_time: dt_time = dt_time(2, 0)):
        """
        Initialize milestone check task

        Args:
            check_time: Time to run the check (default: 2:00 AM)
        """
        self.check_time = check_time
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def run_milestone_check(self):
        """
        Run milestone check for all users

        This is the main function that gets executed daily.
        """
        logger.info("🎉 Starting daily milestone check...")

        db: Session = SessionLocal()
        try:
            milestone_service = MilestoneService(db)
            result = milestone_service.check_all_users_milestones()

            logger.info(f"✅ Milestone check completed:")
            logger.info(f"   - Users checked: {result['users_checked']}")
            logger.info(f"   - Milestones created: {result['milestones_created']}")

            # Log each newly created milestone
            for milestone_detail in result['milestone_details']:
                logger.info(
                    f"   🎊 User {milestone_detail['user_id']}: "
                    f"{milestone_detail['milestone_name']} - "
                    f"{milestone_detail['message']}"
                )

            return result

        except Exception as e:
            logger.error(f"❌ Error during milestone check: {e}", exc_info=True)
            raise

        finally:
            db.close()

    def _task_loop(self):
        """
        Main task loop - runs continuously and executes check at scheduled time
        """
        logger.info(f"🚀 Milestone check task started. Will run daily at {self.check_time}")

        last_check_date = None

        while self.running:
            try:
                now = datetime.now()
                current_time = now.time()
                current_date = now.date()

                # Check if it's time to run AND we haven't run today yet
                if (
                    current_time.hour == self.check_time.hour
                    and current_time.minute == self.check_time.minute
                    and current_date != last_check_date
                ):
                    logger.info(f"⏰ Milestone check time reached: {now}")
                    self.run_milestone_check()
                    last_check_date = current_date

                # Sleep for 60 seconds before next check
                time.sleep(60)

            except Exception as e:
                logger.error(f"❌ Error in milestone task loop: {e}", exc_info=True)
                # Sleep for 5 minutes before retrying
                time.sleep(300)

        logger.info("🛑 Milestone check task stopped.")

    def start(self):
        """
        Start the background task in a daemon thread
        """
        if self.running:
            logger.warning("⚠️ Milestone check task is already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._task_loop, daemon=True)
        self.thread.start()
        logger.info("✅ Milestone check task thread started")

    def stop(self):
        """
        Stop the background task
        """
        if not self.running:
            logger.warning("⚠️ Milestone check task is not running")
            return

        self.running = False
        logger.info("🛑 Stopping milestone check task...")

        # Wait for thread to finish (with timeout)
        if self.thread:
            self.thread.join(timeout=10)

        logger.info("✅ Milestone check task stopped")

    def run_now(self):
        """
        Manually trigger milestone check immediately (for testing)

        Returns:
            Result dictionary from milestone check
        """
        logger.info("🔧 Manual milestone check triggered")
        return self.run_milestone_check()


# Global task instance
_milestone_task: Optional[MilestoneCheckTask] = None


def start_milestone_check_task(check_time: dt_time = dt_time(2, 0)):
    """
    Start the global milestone check task

    Args:
        check_time: Time to run the check (default: 2:00 AM)

    Usage:
        # In main.py or app startup
        from app.tasks.milestone_check_task import start_milestone_check_task
        start_milestone_check_task()
    """
    global _milestone_task

    if _milestone_task is not None and _milestone_task.running:
        logger.warning("⚠️ Milestone check task is already running globally")
        return

    _milestone_task = MilestoneCheckTask(check_time=check_time)
    _milestone_task.start()
    logger.info("✅ Global milestone check task started")


def stop_milestone_check_task():
    """
    Stop the global milestone check task
    """
    global _milestone_task

    if _milestone_task is None:
        logger.warning("⚠️ No global milestone check task to stop")
        return

    _milestone_task.stop()
    _milestone_task = None
    logger.info("✅ Global milestone check task stopped")


def get_milestone_task() -> Optional[MilestoneCheckTask]:
    """
    Get the global milestone check task instance

    Returns:
        MilestoneCheckTask instance or None
    """
    return _milestone_task


def run_milestone_check_now():
    """
    Manually trigger milestone check immediately (for testing/debugging)

    Returns:
        Result dictionary from milestone check
    """
    global _milestone_task

    if _milestone_task is None:
        # Create temporary task instance
        temp_task = MilestoneCheckTask()
        return temp_task.run_now()

    return _milestone_task.run_now()
