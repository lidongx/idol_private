"""
Intimacy Decay Background Task
Story 6.5: 亲密度衰减与保持机制

Runs daily to check and apply intimacy decay for inactive users
"""
import threading
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.intimacy_service import IntimacyService

# Task state
_decay_task_thread = None
_decay_task_running = False


def _decay_check_loop(check_hour: int = 3):
    """
    Background loop that checks for decay daily at specified hour

    Args:
        check_hour: Hour of day to run check (0-23), default 3 AM
    """
    global _decay_task_running

    print(f"[Decay Task] Started. Will run daily at {check_hour}:00")

    while _decay_task_running:
        try:
            current_time = datetime.now()

            # Check if it's time to run (at specified hour)
            if current_time.hour == check_hour and current_time.minute < 5:
                print(f"[Decay Task] Running decay check at {current_time.isoformat()}")

                db = SessionLocal()
                try:
                    intimacy_service = IntimacyService(db)
                    results = intimacy_service.check_and_apply_decay()

                    if results:
                        total_decay = sum(r.get('decay_applied', 0) for r in results)
                        print(f"[Decay Task] Applied decay to {len(results)} conversations, total exp lost: {total_decay}")

                        # Log some details
                        for r in results[:5]:  # Log first 5
                            print(f"  - Conversation {r['conversation_id']}: -{r['decay_applied']} exp (inactive {r['days_inactive']} days)")
                    else:
                        print("[Decay Task] No conversations needed decay")

                except Exception as e:
                    print(f"[Decay Task] Error during decay check: {e}")
                finally:
                    db.close()

                # Sleep for 6 minutes to avoid running multiple times in same hour
                time.sleep(360)

            # Sleep for 1 minute before checking again
            time.sleep(60)

        except Exception as e:
            print(f"[Decay Task] Unexpected error in loop: {e}")
            time.sleep(60)


def start_intimacy_decay_task(check_hour: int = 3):
    """
    Start the intimacy decay background task

    Args:
        check_hour: Hour of day to run check (0-23), default 3 AM (low traffic time)
    """
    global _decay_task_thread, _decay_task_running

    if _decay_task_running:
        print("[Decay Task] Already running")
        return

    _decay_task_running = True
    _decay_task_thread = threading.Thread(
        target=_decay_check_loop,
        args=(check_hour,),
        daemon=True
    )
    _decay_task_thread.start()
    print(f"[Decay Task] Background task started (check hour: {check_hour}:00)")


def stop_intimacy_decay_task():
    """Stop the intimacy decay background task"""
    global _decay_task_running

    if not _decay_task_running:
        print("[Decay Task] Not running")
        return

    print("[Decay Task] Stopping...")
    _decay_task_running = False

    # Wait for thread to finish
    if _decay_task_thread:
        _decay_task_thread.join(timeout=5)

    print("[Decay Task] Stopped")


def is_decay_task_running() -> bool:
    """Check if decay task is running"""
    return _decay_task_running
