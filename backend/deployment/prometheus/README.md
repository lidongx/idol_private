# Prometheus监控部署指南

Story 10.2: 监控告警增强 (Monitoring Alert Enhancement)

## 概述

本目录包含Prometheus监控栈的配置文件，用于监控idol_private应用的性能和业务指标。

## 组件

1. **Prometheus**: 指标收集和存储
2. **AlertManager**: 告警路由和分发
3. **Grafana**: 可视化仪表盘（可选）

## 快速开始

### 1. 配置钉钉/飞书Webhook

在后端`.env`文件中添加：

```env
# 钉钉Webhook
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN
DINGTALK_WEBHOOK_SECRET=YOUR_SECRET  # 可选，如果启用了签名验证

# 飞书Webhook
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID
```

### 2. 启动Prometheus栈

```bash
cd backend/deployment/prometheus
docker-compose up -d
```

### 3. 验证服务

- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093
- **Grafana**: http://localhost:3000 (admin/admin)
- **Backend Metrics**: http://localhost:8000/metrics

### 4. 测试告警

发送测试告警到钉钉/飞书：

```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/test-alert?title=测试告警&message=这是一条测试消息&severity=info"
```

## 配置说明

### prometheus.yml

定义了抓取目标和告警规则文件路径。

**主要配置**:
- `scrape_interval: 15s` - 每15秒抓取一次指标
- `scrape_configs` - 定义抓取目标（backend, postgres, redis等）

### alert_rules.yml

定义了告警规则和阈值。

**主要告警**:
- HTTP错误率 > 5%
- 7日留存率 < 35%
- 30日留存率 < 25%
- API响应时间 > 2秒
- AI API失败率 > 10%
- 数据库查询 > 1秒
- 缓存命中率 < 60%

### alertmanager.yml

定义了告警路由和接收器。

**告警流程**:
1. Prometheus检测到告警触发
2. 发送到AlertManager
3. AlertManager通过Webhook发送到后端
4. 后端通过AlertService发送到钉钉/飞书

## 业务指标

### 用户指标
- `total_users` - 总用户数
- `daily_active_users` - 日活跃用户
- `monthly_active_users` - 月活跃用户
- `user_registrations_total` - 注册总数

### 订阅指标
- `active_subscriptions` - 活跃订阅数
- `monthly_recurring_revenue` - 月度经常性收入(MRR)
- `payment_conversion_rate` - 付费转化率
- `subscription_events_total{event_type}` - 订阅事件

### 留存指标
- `retention_7d_rate` - 7日留存率
- `retention_30d_rate` - 30日留存率

### HTTP指标
- `http_requests_total{method, endpoint, status}` - 请求总数
- `http_request_duration_seconds{method, endpoint}` - 请求时长
- `http_errors_total{method, endpoint, status}` - 错误总数

### AI API指标
- `ai_api_calls_total{provider, status}` - AI调用总数
- `ai_api_duration_seconds{provider}` - AI响应时长
- `ai_tokens_used_total{provider, token_type}` - Token使用量

### 消息指标
- `messages_total{sender_type}` - 消息总数
- `message_processing_duration_seconds{message_type}` - 处理时长

### 系统指标
- `db_query_duration_seconds{query_type}` - 数据库查询时长
- `cache_operations_total{operation, result}` - 缓存操作
- `background_task_duration_seconds{task_name}` - 后台任务时长
- `background_task_errors_total{task_name}` - 后台任务错误

## 告警模板

后端提供了预定义的告警模板：

### 1. 系统错误告警
```python
from app.services.alert_service import AlertService, AlertTemplates

alert_service = AlertService()
title, message, severity = AlertTemplates.system_error(
    error_message="Database connection failed",
    component="PostgreSQL"
)
alert_service.send_alert(title, message, severity)
```

### 2. 高错误率告警
```python
title, message, severity = AlertTemplates.high_error_rate(
    error_rate=8.5,
    threshold=5.0
)
alert_service.send_alert(title, message, severity)
```

### 3. 低留存率告警
```python
title, message, severity = AlertTemplates.low_retention(
    retention_rate=32.5,
    metric_name="7日留存率",
    threshold=35.0
)
alert_service.send_alert(title, message, severity)
```

### 4. 每日数据摘要
```python
title, message, severity = AlertTemplates.daily_summary(
    dau=150,
    new_users=20,
    messages=2500,
    errors=10,
    revenue=500.0
)
alert_service.send_alert(title, message, severity)
```

## Grafana仪表盘

### 访问Grafana
1. 打开 http://localhost:3000
2. 登录 (admin/admin)
3. 添加Prometheus数据源：http://prometheus:9090

### 导入仪表盘

创建新仪表盘，添加以下面板：

**用户增长面板**:
```promql
# DAU趋势
daily_active_users

# 新用户趋势
rate(user_registrations_total[1d])
```

**留存率面板**:
```promql
# 7日留存
retention_7d_rate

# 30日留存
retention_30d_rate
```

**API性能面板**:
```promql
# P95响应时间
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 错误率
(sum(rate(http_errors_total[5m])) / sum(rate(http_requests_total[5m]))) * 100
```

**AI API面板**:
```promql
# AI调用成功率
(sum(rate(ai_api_calls_total{status="success"}[5m])) / sum(rate(ai_api_calls_total[5m]))) * 100

# AI Token使用量
rate(ai_tokens_used_total[1h])
```

## 故障排查

### Prometheus无法抓取指标

检查后端是否启动：
```bash
curl http://localhost:8000/metrics
```

检查Prometheus targets状态：
1. 打开 http://localhost:9090/targets
2. 查看backend target状态

### AlertManager未收到告警

检查Prometheus告警状态：
1. 打开 http://localhost:9090/alerts
2. 查看告警是否触发

检查AlertManager配置：
```bash
docker logs idol_alertmanager
```

### 未收到钉钉/飞书通知

检查webhook配置：
```bash
# 查看环境变量
docker exec idol_backend env | grep DINGTALK
docker exec idol_backend env | grep FEISHU

# 查看后端日志
docker logs idol_backend | grep AlertService
```

测试webhook：
```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/test-alert"
```

## 生产环境建议

1. **数据持久化**: 确保volumes正确配置
2. **访问控制**: 配置BasicAuth或OAuth
3. **HTTPS**: 使用反向代理(Nginx)配置SSL
4. **数据备份**: 定期备份Prometheus数据目录
5. **告警降噪**: 调整`repeat_interval`和`group_interval`
6. **告警分级**: 为不同严重级别配置不同的接收者
7. **监控Prometheus**: 监控Prometheus自身的健康状态

## 参考资料

- [Prometheus文档](https://prometheus.io/docs/)
- [AlertManager文档](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Grafana文档](https://grafana.com/docs/)
- [钉钉机器人文档](https://open.dingtalk.com/document/robots/custom-robot-access)
- [飞书机器人文档](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN)
