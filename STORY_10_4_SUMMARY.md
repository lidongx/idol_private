# Story 10.4: A/B测试框架实现总结

## 概述

实现了完整的A/B测试实验框架，支持实验配置、用户分组、事件追踪和统计分析。

## 实现内容

### 1. 数据库模型

**文件**: `backend/app/models/experiment.py` (150行)

**三个核心表**:

1. **Experiment (实验配置表)**:
   - 实验基本信息：name, description, hypothesis
   - 状态管理：draft, running, paused, completed, archived
   - 分组配置：variants_config (JSON)
   - 指标配置：metrics_config (JSON)
   - 流量控制：traffic_allocation (0-100%)
   - 结果记录：winning_variant, confidence_level

2. **ExperimentAssignment (用户分组表)**:
   - 记录用户被分配到哪个变体
   - 支持hash和random两种分配方式
   - 支持用户排除机制
   - 唯一索引确保一个用户只分配一次

3. **ExperimentEvent (事件追踪表)**:
   - 记录实验中的用户行为事件
   - 支持事件值（如收入）
   - 支持自定义metadata (JSON)
   - 按experiment_id + variant + event_type索引

### 2. 迁移脚本

**文件**: `backend/migrations/011_create_experiment_tables.sql` (160行)

**功能**:
- 创建3个表和9个索引
- 插入2个示例实验配置
- 添加表和字段注释

### 3. 实验服务

**文件**: `backend/app/services/experiment_service.py` (350行)

**核心功能**:

#### 用户分组
```python
def assign_variant(experiment_name: str, user_id: int, method: str) -> str
```
- 基于hash的确定性分配（同一用户总是分配到同一变体）
- 支持流量控制（如只让50%用户参与实验）
- 防止重复分配

#### 分组算法
- **Hash方法**: MD5(experiment_name:user_id) % 100
  - 确定性：同一用户总是相同变体
  - 均匀分布：用户均匀分配到各变体
- **Random方法**: 随机分配
  - 适用于需要完全随机的场景

#### 事件追踪
```python
def track_event(experiment_name, user_id, event_type, event_value, metadata) -> bool
```
- 记录用户在实验中的行为
- 关联用户所在变体
- 支持事件值和元数据

#### 统计分析
```python
def get_experiment_stats(experiment_name) -> Dict
def calculate_conversion_rate(experiment_name, conversion_event) -> Dict
def calculate_statistical_significance(...) -> Dict
```

**统计显著性检验 (Z-test)**:
- 计算p-value判断结果是否显著
- 计算lift（提升幅度）
- 默认显著性水平α=0.05

### 4. API端点

**文件**: `backend/app/routers/experiment.py` (280行)

**8个API端点**:

1. `GET /api/v1/experiments/list` - 实验列表
2. `GET /api/v1/experiments/{name}` - 实验详情
3. `POST /api/v1/experiments/{name}/assign` - 分配用户到变体
4. `POST /api/v1/experiments/{name}/track` - 追踪事件
5. `GET /api/v1/experiments/{name}/stats` - 基础统计
6. `GET /api/v1/experiments/{name}/conversion-rate` - 转化率
7. `POST /api/v1/experiments/calculate-significance` - 显著性检验（通用工具）
8. `GET /api/v1/experiments/{name}/analysis` - 完整分析报告

### 5. 前端实验管理页面

**文件**: `lib/features/experiment/pages/experiment_list_page.dart` (400行)

**功能**:
- 实验列表展示
- 按状态筛选（全部/草稿/运行中/已暂停/已完成）
- 实验详情查看（Bottom Sheet）
- 状态徽章和信息展示
- 下拉刷新功能

### 6. Main.py集成

**更新文件**: `backend/app/main.py`

**改动**:
- 导入experiment router
- 注册`/api/v1/experiments`端点

## 使用示例

### 1. 创建实验

实验已通过迁移脚本预设，也可通过SQL插入：

```sql
INSERT INTO experiments (
    name, description, hypothesis, status,
    experiment_type, variants_config, metrics_config
) VALUES (
    'new_ai_model_test',
    '测试新AI模型对响应质量的影响',
    '新模型能提升用户满意度15%',
    'draft',
    'algorithm',
    '[
        {"variant": "control", "ratio": 50},
        {"variant": "new_model", "ratio": 50}
    ]'::jsonb,
    '{
        "primary": "user_satisfaction",
        "secondary": ["response_time", "message_length"]
    }'::jsonb
);
```

### 2. 用户分组

```python
from app.services.experiment_service import ExperimentService

service = ExperimentService(db)

# 为用户分配变体
variant = service.assign_variant(
    experiment_name='message_recommendation_v2',
    user_id=123,
    method='hash'
)

print(f"User 123 assigned to: {variant}")  # control or treatment
```

### 3. 追踪事件

```python
# 用户点击推荐消息
service.track_event(
    experiment_name='message_recommendation_v2',
    user_id=123,
    event_type='recommendation_click',
    event_value=None
)

# 用户完成转化（如订阅）
service.track_event(
    experiment_name='subscription_pricing_test',
    user_id=456,
    event_type='subscription_conversion',
    event_value=30.0  # 订阅金额
)
```

### 4. 获取实验统计

```python
# 基础统计
stats = service.get_experiment_stats('message_recommendation_v2')

# 转化率
conversion = service.calculate_conversion_rate(
    experiment_name='message_recommendation_v2',
    conversion_event='recommendation_click'
)

# 显著性检验
significance = service.calculate_statistical_significance(
    control_conversions=45,
    control_total=500,
    treatment_conversions=62,
    treatment_total=500
)

if significance['is_significant']:
    print(f"实验有显著差异! p-value={significance['p_value']:.4f}")
    print(f"提升幅度: {significance['lift']:.1f}%")
```

### 5. API调用示例

```bash
# 分配用户到实验
curl -X POST http://localhost:8000/api/v1/experiments/message_recommendation_v2/assign \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123, "method": "hash"}'

# 追踪事件
curl -X POST http://localhost:8000/api/v1/experiments/message_recommendation_v2/track \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123, "event_type": "click", "event_value": 1.0}'

# 获取完整分析
curl http://localhost:8000/api/v1/experiments/message_recommendation_v2/analysis?conversion_event=click

# 计算显著性（独立工具）
curl -X POST http://localhost:8000/api/v1/experiments/calculate-significance \
  -H "Content-Type: application/json" \
  -d '{
    "control_conversions": 45,
    "control_total": 500,
    "treatment_conversions": 62,
    "treatment_total": 500
  }'
```

## 实验流程

### 典型A/B测试流程

```
1. 创建实验 (draft状态)
   ↓
2. 配置变体和指标
   ↓
3. 启动实验 (status → running)
   ↓
4. 用户访问时自动分组
   ↓
5. 追踪用户行为事件
   ↓
6. 达到最小样本量后分析
   ↓
7. 计算统计显著性
   ↓
8. 确定获胜变体
   ↓
9. 完成实验 (status → completed)
   ↓
10. 推广获胜变体到全量
```

### 分组逻辑流程图

```
用户访问
    ↓
检查是否已分配？
    ├─ 是 → 返回已分配变体
    └─ 否 ↓
检查流量分配
    ├─ 不在流量中 → 排除用户
    └─ 在流量中 ↓
计算hash/random值
    ↓
根据比例分配变体
    ↓
记录分配结果
    ↓
返回变体名称
```

## 技术特性

### 1. 确定性分组
- 基于MD5 hash确保同一用户总是分配到同一变体
- 避免用户体验不一致

### 2. 流量控制
- 支持0-100%流量分配
- 可以先小流量测试，再逐步扩大

### 3. 用户排除
- 支持排除某些用户（如VIP用户、测试账号）
- 记录排除原因

### 4. 多变体支持
- 不限于A/B，支持A/B/C/D等多变体
- 通过JSON配置灵活定义

### 5. 统计严谨性
- Z-test统计检验
- p-value和置信度计算
- lift计算

## 最佳实践

### 1. 实验设计

**良好的假设**:
- ✅ "新推荐算法能提升10%的点击率"
- ❌ "新算法更好"

**选择指标**:
- Primary metric: 核心业务指标（如转化率）
- Secondary metrics: 辅助观察指标（如停留时长）

**最小样本量**:
- 建议每组至少1000个样本
- 根据效应量和显著性水平计算

### 2. 分组策略

**Hash vs Random**:
- Hash: 适合需要一致性的场景（如UI变化）
- Random: 适合单次行为测试

**流量分配**:
- 新功能：50/50
- 风险大的改动：90/10（90%对照组，10%实验组）
- 逐步放量：20% → 50% → 100%

### 3. 事件追踪

**关键事件**:
- page_view: 页面浏览
- click: 点击事件
- conversion: 转化事件（核心）
- retention: 留存事件

**事件命名**:
- 使用统一的命名规范
- 如: `{module}_{action}` (e.g., `subscription_purchase`)

### 4. 统计分析

**等待充分样本**:
- 不要过早下结论
- 达到最小样本量后再判断

**多重比较校正**:
- 如果测试多个指标，需要调整显著性水平
- 如Bonferroni校正: α_adjusted = α / n

**避免p-hacking**:
- 不要反复查看结果直到显著
- 预先设定实验时长和停止条件

## 扩展建议

### 短期优化

1. **实验管理界面**: 完善前端CRUD功能
2. **可视化**: 添加转化漏斗和趋势图表
3. **自动化**: 实验自动启动/停止
4. **告警**: 异常指标告警（如某个变体崩溃率飙升）

### 长期增强

1. **多层实验**: 支持同时运行多个不互斥的实验
2. **分层分流**: 按用户属性分层
3. **Bayesian A/B testing**: 贝叶斯统计方法
4. **多臂老虎机（MAB）**: 动态流量分配
5. **因果推断**: 反事实分析

## 文件清单

### Backend文件 (4个)
1. `backend/app/models/experiment.py` (150行)
2. `backend/migrations/011_create_experiment_tables.sql` (160行)
3. `backend/app/services/experiment_service.py` (350行)
4. `backend/app/routers/experiment.py` (280行)

### Frontend文件 (1个)
5. `lib/features/experiment/pages/experiment_list_page.dart` (400行)

### 配置文件
6. `backend/app/main.py` (更新: 注册experiment router)

**总计**: 约1,340行新代码

## 测试建议

### 单元测试

```python
def test_hash_assignment_deterministic():
    """测试hash分配的确定性"""
    service = ExperimentService(db)
    variant1 = service.assign_variant('test_exp', user_id=123, method='hash')
    variant2 = service.assign_variant('test_exp', user_id=123, method='hash')
    assert variant1 == variant2

def test_traffic_allocation():
    """测试流量分配"""
    # 创建50%流量的实验
    # 分配1000个用户
    # 验证约500个用户被分配，500个被排除
    pass

def test_statistical_significance():
    """测试统计检验"""
    service = ExperimentService(None)
    result = service.calculate_statistical_significance(
        control_conversions=50,
        control_total=1000,
        treatment_conversions=70,
        treatment_total=1000
    )
    # 验证p-value, z-score, lift计算正确
    assert result['is_significant'] == True
    assert result['lift'] > 0
```

### 集成测试

```python
def test_full_experiment_flow():
    # 1. 创建实验
    # 2. 分配用户
    # 3. 追踪事件
    # 4. 计算统计
    # 5. 验证结果
    pass
```

## 总结

Story 10.4成功实现了企业级A/B测试框架，包括：

✅ **实验管理**: 完整的实验生命周期管理
✅ **用户分组**: 确定性hash分组 + 流量控制
✅ **事件追踪**: 灵活的事件记录系统
✅ **统计分析**: 转化率计算 + 显著性检验
✅ **API接口**: 8个RESTful端点
✅ **前端界面**: 实验列表和详情页面

系统为产品团队提供了数据驱动决策的能力，可以科学地验证产品假设。
