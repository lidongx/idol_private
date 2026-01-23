"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown
    """
    # Startup: Start background tasks
    from app.tasks.memory_extraction_task import start_memory_extraction_task
    from app.tasks.milestone_check_task import start_milestone_check_task
    from app.tasks.idol_state_update_task import start_idol_state_update_task
    from app.tasks.reverse_care_check_task import start_reverse_care_check_task
    from app.tasks.intimacy_decay_task import start_intimacy_decay_task
    from app.tasks.backup_task import start_backup_task
    from app.tasks.account_deletion_task import start_deletion_task
    from app.tasks.metrics_update_task import start_metrics_update_task
    from app.tasks import start_scheduler

    # Start memory extraction task (runs every 5 minutes)
    start_memory_extraction_task(interval_minutes=5, idle_minutes=5)

    # Start milestone check task (runs daily at 2:00 AM)
    start_milestone_check_task()

    # Start idol state update task (runs every hour)
    start_idol_state_update_task(interval_minutes=60)

    # Start reverse care check task (runs daily at 10:00 AM)
    start_reverse_care_check_task("10:00")

    # Start intimacy decay task (runs daily at 3:00 AM)
    start_intimacy_decay_task(check_hour=3)

    # Start backup task (runs daily at 4:00 AM)
    start_backup_task()

    # Start account deletion task (runs daily at 5:00 AM)
    start_deletion_task()

    # Start subscription scheduler (expiry check at 00:00, renewal reminders at 10:00)
    start_scheduler()

    # Start metrics update task (updates Prometheus business metrics every 60s)
    start_metrics_update_task(interval_seconds=60)

    # Start budget monitor task (checks AI cost budgets every 5 minutes) - Story 10.3
    from app.tasks.budget_monitor_task import start_budget_monitor_task
    start_budget_monitor_task(interval_seconds=300)

    yield

    # Shutdown: Stop background tasks
    from app.tasks.memory_extraction_task import stop_memory_extraction_task
    from app.tasks.milestone_check_task import stop_milestone_check_task
    from app.tasks.idol_state_update_task import stop_idol_state_update_task
    from app.tasks.reverse_care_check_task import stop_reverse_care_check_task
    from app.tasks.intimacy_decay_task import stop_intimacy_decay_task
    from app.tasks.backup_task import stop_backup_task
    from app.tasks.account_deletion_task import stop_deletion_task
    from app.tasks.metrics_update_task import stop_metrics_update_task
    from app.tasks.budget_monitor_task import stop_budget_monitor_task
    from app.tasks import stop_scheduler

    stop_memory_extraction_task()
    stop_milestone_check_task()
    stop_idol_state_update_task()
    stop_reverse_care_check_task()
    stop_intimacy_decay_task()
    stop_backup_task()
    stop_deletion_task()
    stop_metrics_update_task()
    stop_budget_monitor_task()
    stop_scheduler()


# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Virtual Idol Companion Application API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure middlewares
# Story 9.1: Performance optimization middleware
from app.middleware.performance_middleware import PerformanceMiddleware, set_performance_middleware

# Add performance tracking middleware
performance_middleware = PerformanceMiddleware(app)
app.add_middleware(PerformanceMiddleware)
set_performance_middleware(performance_middleware)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP stage: allow all, PRODUCTION: restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {"status": "ok"}


@app.get("/")
async def root():
    """
    Root endpoint with basic information
    """
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


# Register routers
from app.routers import auth, idol, conversation, memory, milestone, ritual, special_event, intimacy, reward, achievement, subscription, payment, device, sse, backup, account_deletion, performance, preferences, push_notification, operations, metrics, webhooks, cost, experiment
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(idol.router, prefix="/api/v1", tags=["偶像"])
app.include_router(conversation.router, prefix="/api/v1", tags=["对话"])
app.include_router(memory.router, prefix="/api/v1", tags=["记忆"])
app.include_router(milestone.router, prefix="/api/v1", tags=["纪念日"])
app.include_router(ritual.router, prefix="/api/v1", tags=["每日仪式"])
app.include_router(special_event.router, prefix="/api/v1", tags=["特殊事件"])
app.include_router(intimacy.router, tags=["亲密度"])
app.include_router(reward.router, prefix="/api/v1", tags=["奖励"])
app.include_router(achievement.router, prefix="/api/v1", tags=["成就"])
app.include_router(subscription.router, prefix="/api/v1", tags=["订阅"])
app.include_router(payment.router, prefix="/api/v1", tags=["支付"])
app.include_router(device.router, prefix="/api/v1", tags=["设备"])
app.include_router(sse.router, prefix="/api/v1", tags=["实时同步"])
app.include_router(backup.router, prefix="/api/v1", tags=["数据备份"])
app.include_router(account_deletion.router, prefix="/api/v1", tags=["账号管理"])
app.include_router(performance.router, prefix="/api/v1/performance", tags=["性能监控"])
app.include_router(preferences.router, prefix="/api/v1", tags=["用户设置"])
app.include_router(push_notification.router, prefix="/api/v1", tags=["推送通知"])
app.include_router(operations.router, tags=["运营监控"])
app.include_router(metrics.router)
app.include_router(webhooks.router)
app.include_router(cost.router, tags=["成本监控"])
app.include_router(experiment.router, tags=["A/B测试"])
