"""
Metrics Update Background Task
Story 10.2: 监控告警增强 (Monitoring Alert Enhancement)

Periodically updates Prometheus business metrics from database
"""

import threading
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.metrics import (
    update_user_metrics,
    update_subscription_metrics,
    update_retention_metrics,
    update_intimacy_distribution,
    update_cost_metrics,
)
from app.services.operations_stats_service import OperationsStatsService
from app.services.cost_tracker import CostTracker


# Global task control
_metrics_update_thread = None
_metrics_update_stop_event = threading.Event()


def _metrics_update_worker(interval_seconds: int = 60):
    """
    Background worker to update metrics

    Args:
        interval_seconds: Update interval in seconds (default: 60)
    """
    print(f"[Metrics Update Task] Started (interval: {interval_seconds}s)")

    while not _metrics_update_stop_event.is_set():
        try:
            # Create database session
            db = SessionLocal()

            try:
                # Initialize stats service
                stats_service = OperationsStatsService(db)
                today = datetime.utcnow()

                # Update user metrics
                total_users = stats_service.get_total_users()
                dau = stats_service.get_dau(today)
                mau = stats_service.get_mau(today)
                update_user_metrics(total_users, dau, mau)

                # Update subscription metrics
                active_subs = stats_service.get_paying_users_count()
                mrr = stats_service.get_mrr()
                conversion = stats_service.get_payment_conversion_rate()
                update_subscription_metrics(active_subs, mrr, conversion)

                # Update retention metrics (use recent cohort)
                cohort_7d = today - timedelta(days=7)
                cohort_30d = today - timedelta(days=30)
                retention_7d = stats_service.get_retention_rate(cohort_7d, 7)
                retention_30d = stats_service.get_retention_rate(cohort_30d, 30)
                update_retention_metrics(retention_7d, retention_30d)

                # Update intimacy distribution
                distribution = stats_service.get_intimacy_distribution()
                update_intimacy_distribution(distribution)

                # Update cost metrics (Story 10.3)
                cost_tracker = CostTracker(db)
                today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
                daily_costs_by_provider = cost_tracker.get_cost_by_provider(start_date=today_start)
                daily_cost_dict = {item['provider']: item['total_cost_usd'] for item in daily_costs_by_provider}
                budget_status = cost_tracker.check_budget(budget_type='global')
                update_cost_metrics(daily_cost_dict, budget_status)

                print(
                    f"[Metrics Update Task] Updated metrics: "
                    f"users={total_users}, dau={dau}, mau={mau}, "
                    f"active_subs={active_subs}, mrr={mrr:.2f}, "
                    f"retention_7d={retention_7d:.1f}%, retention_30d={retention_30d:.1f}%, "
                    f"daily_cost=${budget_status.get('daily_cost_usd', 0):.4f}"
                )

            except Exception as e:
                print(f"[Metrics Update Task] Error updating metrics: {e}")
            finally:
                db.close()

        except Exception as e:
            print(f"[Metrics Update Task] Fatal error: {e}")

        # Wait for interval or stop event
        _metrics_update_stop_event.wait(interval_seconds)

    print("[Metrics Update Task] Stopped")


def start_metrics_update_task(interval_seconds: int = 60):
    """
    Start metrics update background task

    Args:
        interval_seconds: Update interval in seconds (default: 60)
    """
    global _metrics_update_thread

    if _metrics_update_thread is not None and _metrics_update_thread.is_alive():
        print("[Metrics Update Task] Already running")
        return

    _metrics_update_stop_event.clear()
    _metrics_update_thread = threading.Thread(
        target=_metrics_update_worker,
        args=(interval_seconds,),
        daemon=True,
    )
    _metrics_update_thread.start()


def stop_metrics_update_task():
    """Stop metrics update background task"""
    global _metrics_update_thread

    if _metrics_update_thread is None or not _metrics_update_thread.is_alive():
        print("[Metrics Update Task] Not running")
        return

    print("[Metrics Update Task] Stopping...")
    _metrics_update_stop_event.set()

    # Wait for thread to finish (with timeout)
    _metrics_update_thread.join(timeout=5)

    if _metrics_update_thread.is_alive():
        print("[Metrics Update Task] Warning: Thread did not stop gracefully")
    else:
        print("[Metrics Update Task] Stopped successfully")

    _metrics_update_thread = None
