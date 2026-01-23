"""
Background task for hourly idol state updates
Story 5.1: 偶像状态系统与生活节奏引擎

This task runs every hour to update idol states based on their daily schedule,
making them feel "alive" with changing moods and energy levels.
"""
import logging
import threading
import time
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.idol_state_service import IdolStateService

logger = logging.getLogger(__name__)


class IdolStateUpdateTask:
    """
    Background task for updating idol states hourly

    Runs every hour (at minute 0) to update all idol states based on
    their daily schedule configuration.
    """

    def __init__(self, interval_minutes: int = 60):
        """
        Initialize idol state update task

        Args:
            interval_minutes: How often to check (default: 60 minutes)
        """
        self.interval_minutes = interval_minutes
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def run_idol_state_update(self):
        """
        Run idol state update for all idols

        This is the main function that gets executed hourly.
        """
        current_time = datetime.now()
        logger.info(f"🎭 Starting hourly idol state update at {current_time.strftime('%H:%M')}...")

        db: Session = SessionLocal()
        try:
            idol_state_service = IdolStateService(db)
            updated_states = idol_state_service.update_all_idol_states()

            logger.info(f"✅ Idol state update completed:")
            logger.info(f"   - Idols updated: {len(updated_states)}")

            # Log each idol's new state
            for idol_state in updated_states:
                logger.info(
                    f"   🎭 Idol {idol_state.idol_id}: "
                    f"{idol_state.status_display_name} | "
                    f"{idol_state.mood_display_name} | "
                    f"Energy: {idol_state.energy_level}%"
                )

            return {
                'success': True,
                'idols_updated': len(updated_states),
                'timestamp': current_time.isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error during idol state update: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': current_time.isoformat()
            }

        finally:
            db.close()

    def _task_loop(self):
        """
        Main task loop - runs continuously and executes update every hour
        """
        logger.info(f"🚀 Idol state update task started. Will run every {self.interval_minutes} minutes")

        last_run_hour = None

        while self.running:
            try:
                now = datetime.now()
                current_hour = now.hour
                current_minute = now.minute

                # Run at the start of each hour (minute 0) or at interval
                should_run = False

                if self.interval_minutes == 60:
                    # Hourly mode: run at minute 0 of each hour
                    if current_minute == 0 and current_hour != last_run_hour:
                        should_run = True
                        last_run_hour = current_hour
                else:
                    # Custom interval mode: check if it's time
                    if last_run_hour is None or (now.minute % self.interval_minutes) == 0:
                        if last_run_hour != current_hour:
                            should_run = True
                            last_run_hour = current_hour

                if should_run:
                    logger.info(f"⏰ Idol state update time reached: {now.strftime('%Y-%m-%d %H:%M')}")
                    self.run_idol_state_update()

                # Sleep for 60 seconds before next check
                time.sleep(60)

            except Exception as e:
                logger.error(f"❌ Error in idol state update task loop: {e}", exc_info=True)
                # Sleep for 5 minutes before retrying
                time.sleep(300)

        logger.info("🛑 Idol state update task stopped.")

    def start(self):
        """
        Start the background task in a daemon thread
        """
        if self.running:
            logger.warning("⚠️ Idol state update task is already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._task_loop, daemon=True)
        self.thread.start()
        logger.info("✅ Idol state update task thread started")

    def stop(self):
        """
        Stop the background task
        """
        if not self.running:
            logger.warning("⚠️ Idol state update task is not running")
            return

        self.running = False
        logger.info("🛑 Stopping idol state update task...")

        # Wait for thread to finish (with timeout)
        if self.thread:
            self.thread.join(timeout=10)

        logger.info("✅ Idol state update task stopped")

    def run_now(self):
        """
        Manually trigger idol state update immediately (for testing)

        Returns:
            Result dictionary from update
        """
        logger.info("🔧 Manual idol state update triggered")
        return self.run_idol_state_update()


# Global task instance
_idol_state_task: Optional[IdolStateUpdateTask] = None


def start_idol_state_update_task(interval_minutes: int = 60):
    """
    Start the global idol state update task

    Args:
        interval_minutes: Update interval in minutes (default: 60 = hourly)

    Usage:
        # In main.py or app startup
        from app.tasks.idol_state_update_task import start_idol_state_update_task
        start_idol_state_update_task()  # Run every hour
    """
    global _idol_state_task

    if _idol_state_task is not None and _idol_state_task.running:
        logger.warning("⚠️ Idol state update task is already running globally")
        return

    _idol_state_task = IdolStateUpdateTask(interval_minutes=interval_minutes)
    _idol_state_task.start()
    logger.info(f"✅ Global idol state update task started (interval: {interval_minutes} min)")


def stop_idol_state_update_task():
    """
    Stop the global idol state update task
    """
    global _idol_state_task

    if _idol_state_task is None:
        logger.warning("⚠️ No global idol state update task to stop")
        return

    _idol_state_task.stop()
    _idol_state_task = None
    logger.info("✅ Global idol state update task stopped")


def get_idol_state_task() -> Optional[IdolStateUpdateTask]:
    """
    Get the global idol state update task instance

    Returns:
        IdolStateUpdateTask instance or None
    """
    return _idol_state_task


def run_idol_state_update_now():
    """
    Manually trigger idol state update immediately (for testing/debugging)

    Returns:
        Result dictionary from update
    """
    global _idol_state_task

    if _idol_state_task is None:
        # Create temporary task instance
        temp_task = IdolStateUpdateTask()
        return temp_task.run_now()

    return _idol_state_task.run_now()
