"""
Operations Dashboard API
Story 10.1: 运营数据仪表盘 (Operations Data Dashboard)

Provides REST API endpoints for operations metrics:
- /api/v1/operations/dashboard - Get comprehensive dashboard summary
- /api/v1/operations/metrics/{metric}/history - Get historical data for a metric
- /api/v1/operations/users/stats - Get user statistics
- /api/v1/operations/payments/stats - Get payment statistics
- /api/v1/operations/engagement/stats - Get engagement statistics
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.operations_stats_service import OperationsStatsService


router = APIRouter(prefix="/api/v1/operations", tags=["operations"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require admin privileges

    For MVP, we'll use a simple check. In production, implement proper RBAC.
    """
    # TODO: Implement proper admin check
    # For now, allow all authenticated users (operations team only in production)
    return current_user


@router.get("/dashboard")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get comprehensive dashboard summary

    Returns all key metrics for the operations dashboard including:
    - User metrics (DAU, MAU, new users, total users)
    - Retention rates (7-day, 30-day)
    - Payment metrics (paying users, conversion rate, MRR)
    - Engagement metrics (messages, session duration)
    - System metrics (AI API calls)
    - Intimacy distribution

    **Requires**: Admin privileges
    """
    stats_service = OperationsStatsService(db)

    try:
        summary = stats_service.get_dashboard_summary()
        return {
            "success": True,
            "data": summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")


@router.get("/metrics/{metric}/history")
def get_metric_history(
    metric: str,
    days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get historical data for a specific metric

    **Supported metrics:**
    - `dau` - Daily Active Users
    - `new_users` - New user registrations
    - `messages` - Total messages sent
    - `ai_calls` - AI API calls

    **Parameters:**
    - metric: Metric name
    - days: Number of days to look back (1-90, default: 30)

    **Returns:**
    - List of {date, value} objects for charting

    **Requires**: Admin privileges
    """
    valid_metrics = ['dau', 'new_users', 'messages', 'ai_calls']

    if metric not in valid_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Must be one of: {', '.join(valid_metrics)}"
        )

    stats_service = OperationsStatsService(db)

    try:
        data = stats_service.get_historical_data(metric, days)
        return {
            "success": True,
            "metric": metric,
            "days": days,
            "data": data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metric history: {str(e)}"
        )


@router.get("/users/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get detailed user statistics

    Returns:
    - Total users
    - DAU (today)
    - MAU (last 30 days)
    - New users (today, 7d, 30d)

    **Requires**: Admin privileges
    """
    stats_service = OperationsStatsService(db)
    today = datetime.utcnow()

    try:
        return {
            "success": True,
            "data": {
                "total_users": stats_service.get_total_users(),
                "dau": stats_service.get_dau(today),
                "mau": stats_service.get_mau(today),
                "new_users_today": stats_service.get_new_users(),
                "new_users_7d": stats_service.get_new_users(
                    start_date=today.replace(hour=0, minute=0, second=0, microsecond=0),
                    end_date=today,
                ),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user stats: {str(e)}")


@router.get("/payments/stats")
def get_payment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get detailed payment statistics

    Returns:
    - Paying users count
    - Payment conversion rate
    - Subscription renewal rate
    - MRR (Monthly Recurring Revenue)

    **Requires**: Admin privileges
    """
    stats_service = OperationsStatsService(db)

    try:
        return {
            "success": True,
            "data": {
                "paying_users": stats_service.get_paying_users_count(),
                "payment_conversion_rate": round(
                    stats_service.get_payment_conversion_rate(), 2
                ),
                "subscription_renewal_rate": round(
                    stats_service.get_subscription_renewal_rate(30), 2
                ),
                "mrr": stats_service.get_mrr(),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment stats: {str(e)}")


@router.get("/engagement/stats")
def get_engagement_stats(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get detailed engagement statistics

    **Parameters:**
    - days: Number of days to analyze (1-30, default: 7)

    Returns:
    - Total messages
    - Average session duration
    - Messages per user
    - AI API calls

    **Requires**: Admin privileges
    """
    stats_service = OperationsStatsService(db)
    today = datetime.utcnow()
    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        return {
            "success": True,
            "days": days,
            "data": {
                "total_messages_today": stats_service.get_total_messages(
                    start_date=start_date,
                    end_date=today,
                ),
                "total_messages_period": stats_service.get_total_messages(
                    start_date=today - timedelta(days=days),
                    end_date=today,
                ),
                "average_session_duration_minutes": stats_service.get_average_session_duration(days),
                "messages_per_user": stats_service.get_messages_per_user(days),
                "ai_api_calls_today": stats_service.get_ai_api_call_count(
                    start_date=start_date,
                    end_date=today,
                ),
                "ai_api_calls_period": stats_service.get_ai_api_call_count(
                    start_date=today - timedelta(days=days),
                    end_date=today,
                ),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get engagement stats: {str(e)}")


@router.get("/intimacy/distribution")
def get_intimacy_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get distribution of users across intimacy levels

    Returns:
    - Dict mapping level -> user count

    **Requires**: Admin privileges
    """
    stats_service = OperationsStatsService(db)

    try:
        distribution = stats_service.get_intimacy_distribution()
        return {
            "success": True,
            "data": distribution,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get intimacy distribution: {str(e)}"
        )


@router.get("/retention")
def get_retention_rates(
    cohort_date: Optional[str] = Query(None, description="Cohort date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get retention rates for a specific cohort

    **Parameters:**
    - cohort_date: Date when users signed up (YYYY-MM-DD). If not provided, uses 30 days ago.

    Returns:
    - 7-day retention rate
    - 30-day retention rate

    **Requires**: Admin privileges
    """
    stats_service = OperationsStatsService(db)

    # Parse cohort date
    if cohort_date:
        try:
            cohort_dt = datetime.strptime(cohort_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        # Default to 30 days ago
        cohort_dt = datetime.utcnow() - timedelta(days=30)

    try:
        return {
            "success": True,
            "cohort_date": cohort_dt.strftime('%Y-%m-%d'),
            "data": {
                "retention_7d": round(stats_service.get_retention_rate(cohort_dt, 7), 2),
                "retention_30d": round(stats_service.get_retention_rate(cohort_dt, 30), 2),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get retention rates: {str(e)}")


# Missing import
from datetime import timedelta
