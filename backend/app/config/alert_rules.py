"""
Alert Rules Configuration
Story 10.2: 监控告警增强 (Monitoring Alert Enhancement)

Defines alert thresholds and rules
"""

# ==================== Threshold Configuration ====================

# Error rate threshold (percentage)
ERROR_RATE_THRESHOLD = 5.0  # Alert if > 5% of requests result in errors

# Retention thresholds (percentage)
RETENTION_7D_THRESHOLD = 35.0  # Alert if 7-day retention < 35%
RETENTION_30D_THRESHOLD = 25.0  # Alert if 30-day retention < 25%

# API response time threshold (seconds)
API_RESPONSE_THRESHOLD = 2.0  # Alert if average response time > 2s

# AI cost threshold (yuan per day)
AI_DAILY_COST_THRESHOLD = 1000.0  # Alert if daily AI cost > ¥1000

# Database connection retry threshold
DB_CONNECTION_RETRY_THRESHOLD = 3  # Alert after 3 failed connection attempts

# Subscription expiry warning (days)
SUBSCRIPTION_EXPIRY_WARNING_DAYS = 7  # Alert for subscriptions expiring within 7 days

# DAU drop threshold (percentage)
DAU_DROP_THRESHOLD = 20.0  # Alert if DAU drops > 20% from previous day

# Payment conversion rate threshold (percentage)
PAYMENT_CONVERSION_THRESHOLD = 8.0  # Alert if conversion rate < 8%

# Background task failure threshold
BACKGROUND_TASK_FAILURE_THRESHOLD = 3  # Alert after 3 consecutive failures


# ==================== Alert Schedule Configuration ====================

# When to send daily summary (UTC time)
DAILY_SUMMARY_HOUR = 2  # Send at 2:00 AM UTC (10:00 AM Beijing Time)

# Alert cooldown period (seconds)
# Prevents alert spam by not sending same alert type within this period
ALERT_COOLDOWN_PERIOD = 3600  # 1 hour


# ==================== Alert Routing Configuration ====================

# Which platforms to use for each severity
ALERT_ROUTING = {
    'info': ['dingtalk'],  # Info alerts only to DingTalk
    'warning': ['dingtalk', 'feishu'],  # Warnings to both platforms
    'error': ['dingtalk', 'feishu'],  # Errors to both platforms
    'critical': ['dingtalk', 'feishu'],  # Critical to both platforms with @ all
}

# Whether to @ all for critical alerts
AT_ALL_ON_CRITICAL = True

# Phone numbers to @ for critical alerts (DingTalk)
# Format: ['13800138000', '13900139000']
CRITICAL_ALERT_MOBILES = []


# ==================== Prometheus AlertManager Rules (YAML) ====================

# These rules should be configured in Prometheus AlertManager
# Example: /etc/prometheus/alert_rules.yml

PROMETHEUS_ALERT_RULES_YAML = """
groups:
  - name: idol_private_alerts
    interval: 30s
    rules:

      # HTTP Error Rate Alert
      - alert: HighHttpErrorRate
        expr: |
          (
            sum(rate(http_errors_total[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) * 100 > 5
        for: 5m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "High HTTP error rate detected"
          description: "Error rate is {{ $value | humanize }}% (threshold: 5%)"

      # Low Retention Alert
      - alert: LowRetention7d
        expr: retention_7d_rate < 35
        for: 1h
        labels:
          severity: warning
          component: business
        annotations:
          summary: "7-day retention rate is low"
          description: "7-day retention is {{ $value | humanize }}% (threshold: 35%)"

      - alert: LowRetention30d
        expr: retention_30d_rate < 25
        for: 1h
        labels:
          severity: warning
          component: business
        annotations:
          summary: "30-day retention rate is low"
          description: "30-day retention is {{ $value | humanize }}% (threshold: 25%)"

      # API Response Time Alert
      - alert: SlowApiResponse
        expr: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 2
        for: 5m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "API response time is slow"
          description: "P95 response time is {{ $value | humanize }}s (threshold: 2s)"

      # Database Query Performance
      - alert: SlowDatabaseQueries
        expr: |
          histogram_quantile(0.95,
            rate(db_query_duration_seconds_bucket[5m])
          ) > 1
        for: 5m
        labels:
          severity: warning
          component: database
        annotations:
          summary: "Database queries are slow"
          description: "P95 query time is {{ $value | humanize }}s (threshold: 1s)"

      # AI API Call Failures
      - alert: HighAiApiFailureRate
        expr: |
          (
            sum(rate(ai_api_calls_total{status="error"}[5m]))
            /
            sum(rate(ai_api_calls_total[5m]))
          ) * 100 > 10
        for: 5m
        labels:
          severity: error
          component: ai
        annotations:
          summary: "High AI API failure rate"
          description: "AI API failure rate is {{ $value | humanize }}% (threshold: 10%)"

      # Background Task Failures
      - alert: BackgroundTaskFailures
        expr: rate(background_task_errors_total[10m]) > 0.1
        for: 5m
        labels:
          severity: error
          component: background_tasks
        annotations:
          summary: "Background tasks are failing"
          description: "Background task failure rate: {{ $value | humanize }}/s"

      # DAU Drop Alert
      - alert: DauDropped
        expr: |
          (
            (daily_active_users - daily_active_users offset 1d)
            /
            (daily_active_users offset 1d)
          ) * 100 < -20
        for: 1h
        labels:
          severity: warning
          component: business
        annotations:
          summary: "DAU has dropped significantly"
          description: "DAU dropped {{ $value | humanize }}% from yesterday"

      # Low Payment Conversion
      - alert: LowPaymentConversion
        expr: payment_conversion_rate < 8
        for: 6h
        labels:
          severity: warning
          component: business
        annotations:
          summary: "Payment conversion rate is low"
          description: "Conversion rate is {{ $value | humanize }}% (threshold: 8%)"

      # System Resource Alerts
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 / 1024 > 2
        for: 5m
        labels:
          severity: warning
          component: system
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is {{ $value | humanize }}GB (threshold: 2GB)"

      # Cache Performance
      - alert: LowCacheHitRate
        expr: |
          (
            sum(rate(cache_operations_total{result="hit"}[5m]))
            /
            sum(rate(cache_operations_total{operation="get"}[5m]))
          ) * 100 < 60
        for: 10m
        labels:
          severity: warning
          component: cache
        annotations:
          summary: "Cache hit rate is low"
          description: "Cache hit rate is {{ $value | humanize }}% (threshold: 60%)"
"""


# ==================== Webhook Receiver Configuration ====================

# Webhook endpoint that receives alerts from Prometheus AlertManager
# AlertManager should be configured to send alerts to:
# http://<backend-host>:8000/api/v1/webhooks/alertmanager

ALERTMANAGER_WEBHOOK_CONFIG = """
# /etc/alertmanager/alertmanager.yml

global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'idol-private-webhook'

receivers:
  - name: 'idol-private-webhook'
    webhook_configs:
      - url: 'http://backend:8000/api/v1/webhooks/alertmanager'
        send_resolved: true
"""
