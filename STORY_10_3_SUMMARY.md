# Story 10.3: 成本监控与优化实现总结

## 概述

实现了完整的AI成本追踪和预算监控系统，包括成本记录、预算管理、告警通知等功能。

## 实现内容

### 1. 数据库模型与迁移

**文件**: `backend/app/models/ai_cost.py`
- `AICostLog`: AI调用成本记录表
  - 记录provider、model、tokens、cost等信息
  - 支持按时间、provider、用户查询
- `CostBudget`: 成本预算配置表
  - 支持全局、provider、用户三种预算维度
  - 可配置每日/每月限额和告警阈值

**迁移**: `backend/migrations/010_create_ai_cost_tables.sql`
- 创建ai_cost_logs表（15个字段，5个索引）
- 创建cost_budgets表（9个字段，2个索引）
- 插入默认预算配置（全局$10/day, $200/month）

### 2. 成本追踪服务

**文件**: `backend/app/services/cost_tracker.py` (350行)

**核心功能**:
- `calculate_cost()`: 根据provider和tokens计算成本
- `log_ai_call()`: 记录AI调用和成本
- `get_cost_summary()`: 成本汇总统计
- `get_cost_by_provider()`: 按provider分组统计
- `get_daily_cost_trend()`: 每日成本趋势
- `check_budget()`: 检查预算使用情况
- `get_top_users_by_cost()`: 成本最高用户

**定价表**:
- Ollama: $0（本地部署）
- Deepseek: $0.14/1M input, $0.28/1M output
- Claude 3.5 Sonnet: $3/1M input, $15/1M output
- Claude 3 Haiku: $0.25/1M input, $1.25/1M output

### 3. 成本API端点

**文件**: `backend/app/routers/cost.py` (200行)

**API端点**:
- `GET /api/v1/cost/summary` - 成本汇总
- `GET /api/v1/cost/by-provider` - 按provider分组
- `GET /api/v1/cost/daily-trend` - 每日趋势
- `GET /api/v1/cost/budget-status` - 预算状态
- `GET /api/v1/cost/top-users` - TOP用户
- `GET /api/v1/cost/today` - 今日快照
- `GET /api/v1/cost/month` - 本月快照

### 4. Prometheus Metrics集成

**更新文件**: `backend/app/core/metrics.py`

**新增指标**:
- `ai_cost_total_usd`: 累计成本（Counter）
- `ai_daily_cost_usd`: 每日成本（Gauge）
- `budget_usage_percentage`: 预算使用率（Gauge）

**更新函数**:
- `record_ai_call()`: 添加cost_usd参数
- `update_cost_metrics()`: 更新成本metrics

### 5. 预算监控任务

**文件**: `backend/app/tasks/budget_monitor_task.py` (180行)

**功能**:
- 每5分钟检查一次预算
- 检查全局和各provider预算
- 超过warning/critical阈值时发送告警
- 支持每日和每月预算监控

**启动**: 在`backend/app/main.py`中注册
```python
start_budget_monitor_task(interval_seconds=300)
```

### 6. 告警模板

**更新文件**: `backend/app/services/alert_service.py`

**新增模板**:
- `budget_exceeded()`: 预算超限告警
  - 支持warning/critical两种级别
  - 显示使用率、当前成本、预算限额
  - 提供优化建议
- `cost_anomaly()`: 成本异常增长告警
  - 检测成本突增情况
  - 显示增长幅度和可能原因

### 7. Metrics更新任务集成

**更新文件**: `backend/app/tasks/metrics_update_task.py`

**新增逻辑**:
```python
cost_tracker = CostTracker(db)
daily_costs_by_provider = cost_tracker.get_cost_by_provider(start_date=today_start)
budget_status = cost_tracker.check_budget(budget_type='global')
update_cost_metrics(daily_cost_dict, budget_status)
```

### 8. 前端成本监控页面

**文件**: `lib/features/cost/pages/cost_monitoring_page.dart` (400行)

**功能模块**:
- 今日成本卡片: 显示总成本、调用次数、成功率
- 预算状态卡片: 进度条显示预算使用情况
- Provider成本卡片: 按provider分组展示
- 本月汇总卡片: 月度成本和预算使用率
- 下拉刷新功能

## 技术架构

### 成本追踪流程
```
AI API调用
    ↓
CostTracker.log_ai_call()
    ↓
写入ai_cost_logs表
    ↓
Prometheus Metrics更新
```

### 预算监控流程
```
Budget Monitor Task (每5分钟)
    ↓
CostTracker.check_budget()
    ↓
计算使用率
    ↓
超过阈值 → AlertService发送告警
```

### Metrics更新流程
```
Metrics Update Task (每60秒)
    ↓
查询今日成本
    ↓
更新Prometheus Gauges
    ↓
Prometheus抓取/metrics端点
```

## 使用示例

### 1. 记录AI调用成本
```python
from app.services.cost_tracker import CostTracker

tracker = CostTracker(db)
tracker.log_ai_call(
    provider='deepseek',
    model='deepseek-chat',
    input_tokens=1000,
    output_tokens=500,
    latency_ms=1200,
    user_id=123,
    request_type='chat',
    success=True
)
```

### 2. 检查预算状态
```python
# 检查全局预算
global_budget = tracker.check_budget(budget_type='global')
print(f"Daily usage: {global_budget['daily_usage_pct']:.1f}%")

# 检查provider预算
deepseek_budget = tracker.check_budget(
    budget_type='provider',
    target_id='deepseek'
)
```

### 3. 获取成本报告
```python
from datetime import datetime, timedelta

# 今日成本
today = datetime.utcnow().replace(hour=0, minute=0, second=0)
today_cost = tracker.get_cost_summary(start_date=today)

# 按provider分组
by_provider = tracker.get_cost_by_provider(start_date=today)

# TOP 10用户
top_users = tracker.get_top_users_by_cost(limit=10)
```

### 4. API调用示例
```bash
# 获取今日成本快照
curl http://localhost:8000/api/v1/cost/today

# 获取预算状态
curl http://localhost:8000/api/v1/cost/budget-status?budget_type=global

# 获取30天趋势
curl http://localhost:8000/api/v1/cost/daily-trend?days=30

# 按provider分组
curl http://localhost:8000/api/v1/cost/by-provider
```

## 配置说明

### 默认预算配置

在迁移脚本中预设了以下预算：

- **全局预算**: $10/day, $200/month
- **Deepseek**: $5/day, $100/month
- **Claude**: $8/day, $150/month
- **Ollama**: $0（本地部署）

### 告警阈值

- **Warning阈值**: 80%
- **Critical阈值**: 95%

### 监控频率

- **Metrics更新**: 每60秒
- **预算检查**: 每300秒（5分钟）

## 成本优化建议

### 1. 选择合适的模型
- 简单任务使用Deepseek或Claude Haiku
- 复杂任务才使用Claude 3.5 Sonnet
- 本地部署任务优先使用Ollama

### 2. 控制token使用
- 限制prompt长度
- 优化system prompt
- 使用token限制参数

### 3. 缓存优化
- 相似请求使用缓存
- 减少重复AI调用

### 4. 预算管理
- 设置合理的预算限额
- 配置告警通知
- 定期审查成本报告

## 监控指标

### Prometheus Metrics
- `ai_cost_total_usd{provider}`: 累计成本
- `ai_daily_cost_usd{provider}`: 每日成本
- `budget_usage_percentage{budget_type,target_id,period}`: 预算使用率

### 告警规则建议

可在`alert_rules.yml`中添加：
```yaml
- alert: HighAICostDaily
  expr: budget_usage_percentage{period="daily"} > 90
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Daily AI cost budget exceeded 90%"

- alert: AICostBudgetCritical
  expr: budget_usage_percentage{period="daily"} >= 100
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Daily AI cost budget fully exhausted"
```

## 文件清单

### Backend文件 (8个)
1. `backend/app/models/ai_cost.py` (120行)
2. `backend/migrations/010_create_ai_cost_tables.sql` (120行)
3. `backend/app/services/cost_tracker.py` (350行)
4. `backend/app/routers/cost.py` (200行)
5. `backend/app/tasks/budget_monitor_task.py` (180行)
6. `backend/app/core/metrics.py` (更新: +25行)
7. `backend/app/services/alert_service.py` (更新: +60行)
8. `backend/app/tasks/metrics_update_task.py` (更新: +10行)

### Frontend文件 (1个)
9. `lib/features/cost/pages/cost_monitoring_page.dart` (400行)

### 配置文件
10. `backend/app/main.py` (更新: 注册cost router和budget monitor task)

**总计**: 约1,465行新代码

## 测试建议

### 单元测试
```python
def test_calculate_cost():
    tracker = CostTracker(db)
    input_cost, output_cost, total = tracker.calculate_cost(
        'deepseek', 'deepseek-chat', 1000000, 500000
    )
    assert input_cost == 0.14
    assert output_cost == 0.14
    assert total == 0.28

def test_budget_check():
    # Create test budget
    # Log some costs
    # Check budget status
    # Assert alert level
```

### 集成测试
```python
def test_cost_tracking_flow():
    # 1. Record AI call
    # 2. Verify ai_cost_logs entry
    # 3. Query cost summary
    # 4. Check budget status
    # 5. Verify metrics updated
```

## 后续优化

1. **成本预测**: 基于历史数据预测未来成本
2. **异常检测**: 自动检测成本异常模式
3. **成本归因**: 按功能模块归因成本
4. **优化建议**: AI自动生成成本优化建议
5. **报表导出**: 支持CSV/PDF成本报表导出

## 总结

Story 10.3成功实现了完整的AI成本监控系统，包括：

✅ **成本追踪**: 记录每次AI调用的详细成本
✅ **预算管理**: 多维度预算配置和监控
✅ **实时告警**: 预算超限自动发送通知
✅ **数据可视化**: 前端监控页面和Prometheus metrics
✅ **API接口**: 7个成本查询API端点
✅ **后台任务**: 自动预算监控和metrics更新

系统为运营团队提供了全面的成本可见性和管控能力。
