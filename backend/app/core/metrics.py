"""
Prometheus Metrics
Story 10.2: 监控告警增强 (Monitoring Alert Enhancement)

Custom business metrics for Prometheus monitoring:
- User metrics (total_users, active_users_gauge)
- Request metrics (http_requests_total, http_request_duration_seconds)
- Business metrics (subscription_active_count, message_count_total)
- System metrics (ai_api_calls_total, error_count_total)
"""

from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from typing import Dict
import time


# ==================== HTTP Metrics ====================

# HTTP request counter
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# HTTP request duration histogram
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# HTTP error counter
http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status']
)


# ==================== User Metrics ====================

# Total registered users (gauge)
total_users_gauge = Gauge(
    'total_users',
    'Total number of registered users'
)

# Daily active users (gauge)
daily_active_users_gauge = Gauge(
    'daily_active_users',
    'Number of daily active users (last 24 hours)'
)

# Monthly active users (gauge)
monthly_active_users_gauge = Gauge(
    'monthly_active_users',
    'Number of monthly active users (last 30 days)'
)

# New user registrations counter
user_registrations_total = Counter(
    'user_registrations_total',
    'Total user registrations'
)


# ==================== Subscription Metrics ====================

# Active subscriptions gauge
active_subscriptions_gauge = Gauge(
    'active_subscriptions',
    'Number of active subscriptions'
)

# Subscription revenue gauge (MRR)
monthly_recurring_revenue_gauge = Gauge(
    'monthly_recurring_revenue',
    'Monthly recurring revenue in yuan'
)

# Payment conversion rate gauge
payment_conversion_rate_gauge = Gauge(
    'payment_conversion_rate',
    'Payment conversion rate as percentage'
)

# Subscription events counter
subscription_events_total = Counter(
    'subscription_events_total',
    'Total subscription events',
    ['event_type']  # created, renewed, canceled, expired
)


# ==================== Message Metrics ====================

# Total messages counter
messages_total = Counter(
    'messages_total',
    'Total messages sent',
    ['sender_type']  # user, idol
)

# Message processing duration
message_processing_duration_seconds = Histogram(
    'message_processing_duration_seconds',
    'Message processing duration in seconds',
    ['message_type']  # text, voice, image
)


# ==================== AI API Metrics ====================

# AI API calls counter
ai_api_calls_total = Counter(
    'ai_api_calls_total',
    'Total AI API calls',
    ['provider', 'status']  # provider: openai/anthropic, status: success/error
)

# AI API response duration
ai_api_duration_seconds = Histogram(
    'ai_api_duration_seconds',
    'AI API response duration in seconds',
    ['provider']
)

# AI token usage counter
ai_tokens_used_total = Counter(
    'ai_tokens_used_total',
    'Total AI tokens used',
    ['provider', 'token_type']  # token_type: prompt/completion
)

# AI cost counter (Story 10.3)
ai_cost_total_usd = Counter(
    'ai_cost_total_usd',
    'Total AI cost in USD',
    ['provider']
)

# AI cost gauge (current daily cost)
ai_daily_cost_usd = Gauge(
    'ai_daily_cost_usd',
    'Daily AI cost in USD',
    ['provider']
)

# Budget usage percentage gauge
budget_usage_percentage = Gauge(
    'budget_usage_percentage',
    'Budget usage percentage',
    ['budget_type', 'target_id', 'period']  # period: daily/monthly
)


# ==================== Intimacy Metrics ====================

# Intimacy level distribution
intimacy_level_gauge = Gauge(
    'intimacy_level_users',
    'Number of users at each intimacy level',
    ['level']
)

# Intimacy level up events
intimacy_levelup_total = Counter(
    'intimacy_levelup_total',
    'Total intimacy level up events',
    ['from_level', 'to_level']
)


# ==================== System Metrics ====================

# Database query duration
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

# Cache hit/miss counter
cache_operations_total = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'result']  # operation: get/set, result: hit/miss/error
)

# Background task duration
background_task_duration_seconds = Histogram(
    'background_task_duration_seconds',
    'Background task duration in seconds',
    ['task_name']
)

# Background task errors
background_task_errors_total = Counter(
    'background_task_errors_total',
    'Total background task errors',
    ['task_name']
)


# ==================== Business KPI Metrics ====================

# 7-day retention rate
retention_7d_gauge = Gauge(
    'retention_7d_rate',
    '7-day retention rate as percentage'
)

# 30-day retention rate
retention_30d_gauge = Gauge(
    'retention_30d_rate',
    '30-day retention rate as percentage'
)

# Average session duration
average_session_duration_seconds_gauge = Gauge(
    'average_session_duration_seconds',
    'Average session duration in seconds'
)


# ==================== Metric Update Functions ====================

def update_user_metrics(total: int, dau: int, mau: int):
    """Update user-related metrics"""
    total_users_gauge.set(total)
    daily_active_users_gauge.set(dau)
    monthly_active_users_gauge.set(mau)


def update_subscription_metrics(
    active_count: int,
    mrr: float,
    conversion_rate: float,
):
    """Update subscription-related metrics"""
    active_subscriptions_gauge.set(active_count)
    monthly_recurring_revenue_gauge.set(mrr)
    payment_conversion_rate_gauge.set(conversion_rate)


def update_retention_metrics(retention_7d: float, retention_30d: float):
    """Update retention metrics"""
    retention_7d_gauge.set(retention_7d)
    retention_30d_gauge.set(retention_30d)


def update_intimacy_distribution(distribution: Dict[int, int]):
    """Update intimacy level distribution"""
    for level, count in distribution.items():
        intimacy_level_gauge.labels(level=str(level)).set(count)


def record_http_request(method: str, endpoint: str, status: int, duration: float):
    """Record HTTP request metrics"""
    http_requests_total.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

    if status >= 400:
        http_errors_total.labels(method=method, endpoint=endpoint, status=str(status)).inc()


def record_message(sender_type: str, duration: float = 0, message_type: str = 'text'):
    """Record message metrics"""
    messages_total.labels(sender_type=sender_type).inc()
    if duration > 0:
        message_processing_duration_seconds.labels(message_type=message_type).observe(duration)


def record_ai_call(provider: str, status: str, duration: float, prompt_tokens: int = 0, completion_tokens: int = 0, cost_usd: float = 0.0):
    """Record AI API call metrics"""
    ai_api_calls_total.labels(provider=provider, status=status).inc()
    ai_api_duration_seconds.labels(provider=provider).observe(duration)

    if prompt_tokens > 0:
        ai_tokens_used_total.labels(provider=provider, token_type='prompt').inc(prompt_tokens)
    if completion_tokens > 0:
        ai_tokens_used_total.labels(provider=provider, token_type='completion').inc(completion_tokens)

    # Record cost (Story 10.3)
    if cost_usd > 0:
        ai_cost_total_usd.labels(provider=provider).inc(cost_usd)


def record_subscription_event(event_type: str):
    """Record subscription event"""
    subscription_events_total.labels(event_type=event_type).inc()


def record_intimacy_levelup(from_level: int, to_level: int):
    """Record intimacy level up event"""
    intimacy_levelup_total.labels(from_level=str(from_level), to_level=str(to_level)).inc()


def record_db_query(query_type: str, duration: float):
    """Record database query metrics"""
    db_query_duration_seconds.labels(query_type=query_type).observe(duration)


def record_cache_operation(operation: str, result: str):
    """Record cache operation"""
    cache_operations_total.labels(operation=operation, result=result).inc()


def record_background_task(task_name: str, duration: float, error: bool = False):
    """Record background task metrics"""
    background_task_duration_seconds.labels(task_name=task_name).observe(duration)
    if error:
        background_task_errors_total.labels(task_name=task_name).inc()


def update_cost_metrics(daily_cost_by_provider: dict, budget_usage: dict):
    """
    Update cost and budget metrics (Story 10.3)

    Args:
        daily_cost_by_provider: Dict of {provider: daily_cost_usd}
        budget_usage: Dict with budget usage data
    """
    # Update daily cost by provider
    for provider, cost in daily_cost_by_provider.items():
        ai_daily_cost_usd.labels(provider=provider).set(cost)

    # Update budget usage percentages
    if budget_usage.get('has_budget'):
        budget_type = budget_usage.get('budget_type', 'global')
        target_id = budget_usage.get('target_id') or 'all'

        if 'daily_usage_pct' in budget_usage:
            budget_usage_percentage.labels(
                budget_type=budget_type,
                target_id=target_id,
                period='daily'
            ).set(budget_usage['daily_usage_pct'])

        if 'monthly_usage_pct' in budget_usage:
            budget_usage_percentage.labels(
                budget_type=budget_type,
                target_id=target_id,
                period='monthly'
            ).set(budget_usage['monthly_usage_pct'])


# ==================== Metrics Export ====================

def get_metrics() -> bytes:
    """
    Get Prometheus metrics in text format

    Returns:
        Metrics in Prometheus text format
    """
    return generate_latest()


def get_content_type() -> str:
    """
    Get Prometheus metrics content type

    Returns:
        Content type string
    """
    return CONTENT_TYPE_LATEST
