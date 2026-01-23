"""
AI Cost Monitoring API
Story 10.3: 成本监控与优化 (Cost Monitoring & Optimization)
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.cost_tracker import CostTracker


router = APIRouter(prefix="/api/v1/cost", tags=["Cost Monitoring"])


@router.get("/summary")
def get_cost_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    db: Session = Depends(get_db)
):
    """
    获取成本汇总

    返回指定时间范围内的总成本、调用次数、成功率等指标
    """
    tracker = CostTracker(db)

    # 解析日期
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    summary = tracker.get_cost_summary(
        start_date=start_dt,
        end_date=end_dt,
        provider=provider
    )

    return {
        "status": "success",
        "data": summary,
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "provider": provider,
        }
    }


@router.get("/by-provider")
def get_cost_by_provider(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    按Provider分组的成本统计

    返回每个AI provider的成本、调用次数等
    """
    tracker = CostTracker(db)

    # 解析日期
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    cost_by_provider = tracker.get_cost_by_provider(
        start_date=start_dt,
        end_date=end_dt
    )

    return {
        "status": "success",
        "data": cost_by_provider,
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
        }
    }


@router.get("/daily-trend")
def get_daily_cost_trend(
    days: int = Query(30, description="Number of days", ge=1, le=365),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    db: Session = Depends(get_db)
):
    """
    获取每日成本趋势

    返回过去N天的每日成本数据
    """
    tracker = CostTracker(db)

    trend = tracker.get_daily_cost_trend(days=days, provider=provider)

    return {
        "status": "success",
        "data": trend,
        "filters": {
            "days": days,
            "provider": provider,
        }
    }


@router.get("/budget-status")
def get_budget_status(
    budget_type: str = Query("global", description="Budget type: global, provider, user"),
    target_id: Optional[str] = Query(None, description="Provider name or user ID"),
    db: Session = Depends(get_db)
):
    """
    检查预算使用情况

    返回当前预算使用百分比和告警状态
    """
    tracker = CostTracker(db)

    budget_status = tracker.check_budget(
        budget_type=budget_type,
        target_id=target_id
    )

    return {
        "status": "success",
        "data": budget_status
    }


@router.get("/top-users")
def get_top_users_by_cost(
    limit: int = Query(10, description="Number of users to return", ge=1, le=100),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    获取成本最高的用户

    返回成本消耗最高的TOP N用户
    """
    tracker = CostTracker(db)

    # 解析日期
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    top_users = tracker.get_top_users_by_cost(
        limit=limit,
        start_date=start_dt,
        end_date=end_dt
    )

    return {
        "status": "success",
        "data": top_users,
        "filters": {
            "limit": limit,
            "start_date": start_date,
            "end_date": end_date,
        }
    }


@router.get("/today")
def get_today_cost(db: Session = Depends(get_db)):
    """
    获取今日成本快照

    返回今日的成本汇总、预算状态、按provider分组的成本
    """
    tracker = CostTracker(db)

    # 今日开始时间
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # 今日成本汇总
    today_summary = tracker.get_cost_summary(start_date=today_start)

    # 全局预算状态
    budget_status = tracker.check_budget(budget_type='global')

    # 按provider分组
    by_provider = tracker.get_cost_by_provider(start_date=today_start)

    return {
        "status": "success",
        "data": {
            "summary": today_summary,
            "budget": budget_status,
            "by_provider": by_provider,
        }
    }


@router.get("/month")
def get_month_cost(db: Session = Depends(get_db)):
    """
    获取本月成本快照

    返回本月的成本汇总、预算状态、每日趋势
    """
    tracker = CostTracker(db)

    # 本月开始时间
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 本月成本汇总
    month_summary = tracker.get_cost_summary(start_date=month_start)

    # 全局预算状态
    budget_status = tracker.check_budget(budget_type='global')

    # 本月每日趋势
    days_in_month = (datetime.utcnow() - month_start).days + 1
    daily_trend = tracker.get_daily_cost_trend(days=days_in_month)

    return {
        "status": "success",
        "data": {
            "summary": month_summary,
            "budget": budget_status,
            "daily_trend": daily_trend,
        }
    }
