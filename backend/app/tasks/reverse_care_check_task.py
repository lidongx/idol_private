"""
Reverse Care Check Background Task
Story 5.4: 反向陪伴机制

Runs daily at 10:00 AM to check for users needing care
"""
import threading
import time
import schedule
from datetime import datetime
from app.database import SessionLocal
from app.services.reverse_care_service import ReverseCareService

# Global task control
_task_thread = None
_stop_event = threading.Event()


def run_reverse_care_check():
    """
    Main function that checks for users needing reverse care

    This function:
    1. Checks for inactive users (3+ days no login)
    2. Checks for low mood users (3+ days of sad/anxious messages)
    3. Sends appropriate care messages
    """
    print(f"[{datetime.now()}] Starting reverse care check...")

    db = SessionLocal()
    try:
        service = ReverseCareService(db)

        # Process all care checks
        results = service.process_all_care_checks()

        print(f"[{datetime.now()}] Reverse care check completed:")
        print(f"  - Inactive users checked: {results['inactive_users_checked']}")
        print(f"  - Inactive care messages sent: {results['inactive_care_sent']}")
        print(f"  - Low mood users checked: {results['low_mood_users_checked']}")
        print(f"  - Low mood care messages sent: {results['low_mood_care_sent']}")

        if results['errors']:
            print(f"  - Errors encountered: {len(results['errors'])}")
            for error in results['errors']:
                print(f"    * {error}")

    except Exception as e:
        print(f"[{datetime.now()}] Error in reverse care check: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def schedule_reverse_care_check(run_time: str = "10:00"):
    """
    Schedule the reverse care check to run daily at specified time

    Args:
        run_time: Time to run check in HH:MM format (default: "10:00")
    """
    schedule.every().day.at(run_time).do(run_reverse_care_check)
    print(f"[{datetime.now()}] Reverse care check scheduled for daily {run_time}")


def run_scheduler():
    """
    Background thread function that runs the scheduler
    """
    print(f"[{datetime.now()}] Reverse care check task thread started")

    while not _stop_event.is_set():
        schedule.run_pending()
        time.sleep(60)  # Check every minute

    print(f"[{datetime.now()}] Reverse care check task thread stopped")


def start_reverse_care_check_task(run_time: str = "10:00"):
    """
    Start the reverse care check background task

    Args:
        run_time: Time to run check in HH:MM format (default: "10:00" - 10:00 AM)

    Example:
        start_reverse_care_check_task("10:00")  # Run daily at 10:00 AM
    """
    global _task_thread

    if _task_thread is not None and _task_thread.is_alive():
        print(f"[{datetime.now()}] Reverse care check task already running")
        return

    # Clear stop event
    _stop_event.clear()

    # Schedule the task
    schedule_reverse_care_check(run_time)

    # Start background thread
    _task_thread = threading.Thread(target=run_scheduler, daemon=True)
    _task_thread.start()

    print(f"[{datetime.now()}] Reverse care check task started successfully")


def stop_reverse_care_check_task():
    """
    Stop the reverse care check background task
    """
    global _task_thread

    if _task_thread is None or not _task_thread.is_alive():
        print(f"[{datetime.now()}] Reverse care check task not running")
        return

    print(f"[{datetime.now()}] Stopping reverse care check task...")

    # Signal thread to stop
    _stop_event.set()

    # Wait for thread to finish (with timeout)
    _task_thread.join(timeout=5)

    # Clear schedule
    schedule.clear()

    _task_thread = None

    print(f"[{datetime.now()}] Reverse care check task stopped successfully")


def get_task_status():
    """
    Get the current status of the reverse care check task

    Returns:
        dict: Task status information
    """
    is_running = _task_thread is not None and _task_thread.is_alive()

    return {
        'task_name': 'reverse_care_check',
        'is_running': is_running,
        'scheduled_jobs': len(schedule.jobs),
        'next_run': str(schedule.next_run()) if schedule.jobs else None
    }


# For manual testing
if __name__ == "__main__":
    print("Starting reverse care check task (manual test)...")
    start_reverse_care_check_task("10:00")

    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping task...")
        stop_reverse_care_check_task()
        print("Done")
