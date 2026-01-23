"""
Budget Monitoring Background Task
Story 10.3: 成本监控与优化 (Cost Monitoring & Optimization)

Periodically checks AI cost budgets and sends alerts when thresholds are exceeded
"""

import threading
import time
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.cost_tracker import CostTracker
from app.services.alert_service import AlertService, AlertTemplates


# Global variables for task control
_budget_monitor_thread = None
_budget_monitor_stop_event = threading.Event()


def _budget_monitor_worker(interval_seconds: int = 300):  # Check every 5 minutes
    """
    Budget monitoring worker thread

    Args:
        interval_seconds: Check interval in seconds (default: 300 = 5 minutes)
    """
    print(f"[Budget Monitor Task] Started with {interval_seconds}s interval")

    while not _budget_monitor_stop_event.is_set():
        try:
            # Get database session
            db = SessionLocal()

            try:
                # Initialize services
                cost_tracker = CostTracker(db)
                alert_service = AlertService()

                # Check global budget
                global_budget = cost_tracker.check_budget(budget_type='global')
                _check_and_alert(global_budget, alert_service, "全局")

                # Check provider budgets
                providers = ['deepseek', 'claude', 'ollama']
                for provider in providers:
                    provider_budget = cost_tracker.check_budget(
                        budget_type='provider',
                        target_id=provider
                    )
                    if provider_budget.get('has_budget'):
                        _check_and_alert(provider_budget, alert_service, f"Provider: {provider}")

                print(f"[Budget Monitor Task] Budget check completed")

            except Exception as e:
                print(f"[Budget Monitor Task] Error checking budgets: {e}")
            finally:
                db.close()

        except Exception as e:
            print(f"[Budget Monitor Task] Fatal error: {e}")

        # Wait for interval or stop event
        _budget_monitor_stop_event.wait(interval_seconds)

    print("[Budget Monitor Task] Stopped")


def _check_and_alert(budget_status: dict, alert_service: AlertService, target_desc: str):
    """
    Check budget status and send alerts if thresholds exceeded

    Args:
        budget_status: Budget status dict from CostTracker.check_budget()
        alert_service: AlertService instance
        target_desc: Description of the budget target (e.g., "全局", "Provider: deepseek")
    """
    if not budget_status.get('has_budget'):
        return

    alert_level = budget_status.get('alert_level')

    # Send alert if warning or critical
    if alert_level in ['warning', 'critical']:
        # Check daily budget
        daily_usage_pct = budget_status.get('daily_usage_pct', 0)
        daily_limit = budget_status.get('daily_limit_usd')
        daily_cost = budget_status.get('daily_cost_usd', 0)

        if daily_limit and daily_usage_pct >= budget_status.get('warning_threshold', 80):
            provider = budget_status.get('target_id') if budget_status.get('budget_type') == 'provider' else None

            title, message, severity = AlertTemplates.budget_exceeded(
                budget_type=budget_status.get('budget_type'),
                period='daily',
                usage_pct=daily_usage_pct,
                current_cost=daily_cost,
                limit=daily_limit,
                provider=provider
            )

            try:
                alert_service.send_alert(title, message, severity)
                print(f"[Budget Monitor] Alert sent: {target_desc} daily budget at {daily_usage_pct:.1f}%")
            except Exception as e:
                print(f"[Budget Monitor] Failed to send alert for {target_desc}: {e}")

        # Check monthly budget
        monthly_usage_pct = budget_status.get('monthly_usage_pct', 0)
        monthly_limit = budget_status.get('monthly_limit_usd')
        monthly_cost = budget_status.get('monthly_cost_usd', 0)

        if monthly_limit and monthly_usage_pct >= budget_status.get('warning_threshold', 80):
            provider = budget_status.get('target_id') if budget_status.get('budget_type') == 'provider' else None

            title, message, severity = AlertTemplates.budget_exceeded(
                budget_type=budget_status.get('budget_type'),
                period='monthly',
                usage_pct=monthly_usage_pct,
                current_cost=monthly_cost,
                limit=monthly_limit,
                provider=provider
            )

            try:
                alert_service.send_alert(title, message, severity)
                print(f"[Budget Monitor] Alert sent: {target_desc} monthly budget at {monthly_usage_pct:.1f}%")
            except Exception as e:
                print(f"[Budget Monitor] Failed to send alert for {target_desc}: {e}")


def start_budget_monitor_task(interval_seconds: int = 300):
    """
    Start budget monitoring background task

    Args:
        interval_seconds: Check interval in seconds (default: 300 = 5 minutes)
    """
    global _budget_monitor_thread

    if _budget_monitor_thread and _budget_monitor_thread.is_alive():
        print("[Budget Monitor Task] Already running")
        return

    _budget_monitor_stop_event.clear()
    _budget_monitor_thread = threading.Thread(
        target=_budget_monitor_worker,
        args=(interval_seconds,),
        daemon=True,
        name="BudgetMonitorThread"
    )
    _budget_monitor_thread.start()
    print(f"[Budget Monitor Task] Started successfully")


def stop_budget_monitor_task():
    """Stop budget monitoring background task"""
    global _budget_monitor_thread

    if not _budget_monitor_thread or not _budget_monitor_thread.is_alive():
        print("[Budget Monitor Task] Not running")
        return

    print("[Budget Monitor Task] Stopping...")
    _budget_monitor_stop_event.set()

    # Wait for thread to finish (max 10 seconds)
    _budget_monitor_thread.join(timeout=10)

    if _budget_monitor_thread.is_alive():
        print("[Budget Monitor Task] Warning: Thread did not stop gracefully")
    else:
        print("[Budget Monitor Task] Stopped successfully")

    _budget_monitor_thread = None
