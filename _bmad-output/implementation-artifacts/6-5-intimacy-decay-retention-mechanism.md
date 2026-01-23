# Story 6.5: 亲密度衰减与保持机制

Status: completed

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-19
> **⚠️ 重要说明:** 此功能为可选功能，建议根据用户反馈决定是否启用

## Story

As a **产品经理**,
I want **设计温和的亲密度衰减机制**,
So that **鼓励用户保持活跃但不过度惩罚**。

## Acceptance Criteria

### AC1: 衰减数据库表结构
- **Given** 需要追踪亲密度衰减事件
- **When** 设计衰减系统数据库
- **Then** 创建 `intimacy_decay_logs` 表存储衰减记录
- **And** 包含字段: conversation_id, decay_amount, reason, intimacy_exp_before, intimacy_exp_after
- **And** 在conversations表添加字段: decay_disabled, last_comeback_bonus_at

### AC2: 温和的衰减策略
- **Given** 用户超过7天未互动
- **When** 每日凌晨3点执行衰减检查
- **Then** 根据不活跃天数应用不同衰减:
  * 7-13天: -5 exp/天（温和衰减）
  * 14-29天: -7 exp/天（中度衰减）
  * 30天以上: -10 exp/天（加速衰减）
- **And** 经验值不会低于0（保底机制）
- **And** 等级永不降低（仅影响升级进度）

### AC3: 用户控制
- **Given** 用户希望关闭衰减
- **When** 调用toggle_decay API
- **Then** 设置conversations.decay_disabled = true
- **And** 该对话不再参与衰减检查
- **And** 可作为付费用户特权

### AC4: 回归激励
- **Given** 用户7天未登录后回归
- **When** 用户首次发送消息
- **Then** 可领取回归礼包+50 exp
- **And** 显示欢迎回来消息："好久不见！让我们重新建立默契吧~"
- **And** 每30天只能领取一次（防止滥用）

### AC5: 后台定时任务
- **Given** 需要自动执行衰减检查
- **When** 应用启动
- **Then** 启动后台定时任务（每日3:00 AM执行）
- **And** 查询所有7天以上未活跃的对话
- **And** 应用相应的衰减
- **And** 记录衰减日志

---

## Implementation Details

### Architecture Overview

```
Backend Architecture:
backend/
├── migrations/
│   ├── 022_create_intimacy_decay_logs_table.sql    # 衰减日志表
│   └── 023_add_decay_fields_to_conversations.sql   # conversations表新增字段
├── app/
│   ├── models/
│   │   └── intimacy_decay_log.py                   # 衰减日志模型
│   ├── services/
│   │   └── intimacy_service.py                     # [修改] 添加衰减方法
│   ├── tasks/
│   │   └── intimacy_decay_task.py                  # [新建] 后台定时任务
│   ├── routers/
│   │   └── intimacy.py                             # [修改] 添加衰减API端点
│   └── main.py                                      # [修改] 注册decay task
```

### Database Schema

```sql
-- intimacy_decay_logs: 衰减日志表
CREATE TABLE intimacy_decay_logs (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    decay_amount INTEGER NOT NULL,          -- 衰减量（负值，如-5）
    reason VARCHAR(100) NOT NULL,           -- 衰减原因
    intimacy_exp_before INTEGER NOT NULL,   -- 衰减前经验值
    intimacy_exp_after INTEGER NOT NULL,    -- 衰减后经验值
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- conversations表新增字段:
ALTER TABLE conversations ADD COLUMN decay_disabled BOOLEAN DEFAULT false;
ALTER TABLE conversations ADD COLUMN last_comeback_bonus_at TIMESTAMP;
```

### Decay Strategy

```
不活跃天数 → 衰减量（每日）:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 7-13天    →  -5 exp/天   温和衰减
 14-29天   →  -7 exp/天   中度衰减
 30天以上  →  -10 exp/天  加速衰减

保护机制:
- 当前经验值 < 衰减量 → 仅扣除至0，不会负数
- 等级永不降低
- 用户可关闭衰减（decay_disabled = true）
```

### Data Flow: Decay Check

```
Daily Decay Check (3:00 AM):
1. Background task wakes up at 3:00 AM
2. Query conversations:
   - last_message_at < 7 days ago
   - decay_disabled = false
   - intimacy_exp > 0
3. For each inactive conversation:
   - Calculate days_inactive = now - last_message_at
   - Determine decay_amount based on days_inactive
   - Apply decay: exp -= min(decay_amount, current_exp)
   - Create IntimacyDecayLog record
4. Sleep until next day

Decay Amount Calculation:
if days_inactive >= 30:
    decay = 10 exp, reason = 'inactive_30days'
elif days_inactive >= 14:
    decay = 7 exp, reason = 'inactive_14days'
else:  # 7-13 days
    decay = 5 exp, reason = 'inactive_7days'
```

### Data Flow: Comeback Bonus

```
User Returns After 7+ Days:
1. User sends message after long inactivity
2. Frontend calls POST /intimacy/conversations/{id}/comeback-bonus
3. Backend checks:
   - Is user actually inactive? (days_inactive >= 7)
   - Has user claimed bonus recently? (< 30 days ago)
4. If eligible:
   - Add +50 exp bonus
   - Update last_comeback_bonus_at = now
   - Return welcome message
5. Frontend shows celebration:
   - "欢迎回来！这是给你的回归礼包~"
   - Display +50 exp animation
```

---

## Files Created/Modified

### 新建文件 (2个)

#### Database Migrations
1. **backend/migrations/022_create_intimacy_decay_logs_table.sql** (24 lines)
   - 创建intimacy_decay_logs表
   - 2个索引: conversation_id, created_at DESC

2. **backend/migrations/023_add_decay_fields_to_conversations.sql** (14 lines)
   - conversations表添加decay_disabled字段
   - conversations表添加last_comeback_bonus_at字段
   - 2个索引: decay_disabled, last_message_at

#### Models
3. **backend/app/models/intimacy_decay_log.py** (71 lines)
   - IntimacyDecayLog模型，追踪衰减事件
   - 3种衰减原因常量
   - reason_display_name属性（中文显示名）
   - to_dict()方法用于API响应

#### Tasks
4. **backend/app/tasks/intimacy_decay_task.py** (114 lines)
   - 后台定时任务，每日3:00 AM执行
   - start_intimacy_decay_task()启动任务
   - stop_intimacy_decay_task()停止任务
   - _decay_check_loop()主循环

### 修改文件 (3个)

5. **backend/app/services/intimacy_service.py**
   - 添加 apply_intimacy_decay() - 应用衰减
   - 添加 check_and_apply_decay() - 批量检查并应用
   - 添加 toggle_decay() - 开启/关闭衰减
   - 添加 give_comeback_bonus() - 发放回归礼包
   - 添加 get_decay_history() - 获取衰减历史

6. **backend/app/routers/intimacy.py**
   - 添加 GET /api/v1/intimacy/conversations/{id}/decay-history
   - 添加 PUT /api/v1/intimacy/conversations/{id}/toggle-decay
   - 添加 POST /api/v1/intimacy/conversations/{id}/comeback-bonus

7. **backend/app/main.py**
   - lifespan函数中添加start_intimacy_decay_task()
   - shutdown时添加stop_intimacy_decay_task()

---

## API Endpoints

### GET /api/v1/intimacy/conversations/{conversation_id}/decay-history
获取亲密度衰减历史

**Response:**
```json
{
  "conversation_id": 1,
  "history": [
    {
      "id": 1,
      "conversation_id": 1,
      "decay_amount": -5,
      "reason": "inactive_7days",
      "reason_display": "7天未互动",
      "intimacy_exp_before": 250,
      "intimacy_exp_after": 245,
      "created_at": "2026-01-19T03:00:00",
      "days_since_decay": 1
    }
  ],
  "total_count": 1
}
```

### PUT /api/v1/intimacy/conversations/{conversation_id}/toggle-decay
开启/关闭亲密度衰减

**Request Body:**
```json
{
  "disabled": true
}
```

**Response:**
```json
{
  "conversation_id": 1,
  "decay_disabled": true,
  "message": "Decay disabled successfully"
}
```

**Use Cases:**
- 免费用户: 衰减默认开启，无法关闭
- 付费用户: 可以关闭衰减作为特权
- 运营活动: 临时关闭所有用户的衰减

### POST /api/v1/intimacy/conversations/{conversation_id}/comeback-bonus
领取回归礼包

**Response (成功):**
```json
{
  "success": true,
  "message": "欢迎回来！这是给你的回归礼包~",
  "exp_added": 50,
  "old_level": 5,
  "new_level": 5,
  "level_up": false,
  "is_comeback_bonus": true
}
```

**Response (太早):**
```json
{
  "success": false,
  "reason": "too_soon",
  "message": "Comeback bonus available in 15 days",
  "days_until_available": 15
}
```

**Response (未不活跃):**
```json
{
  "success": false,
  "reason": "not_inactive",
  "message": "User was not inactive long enough for comeback bonus"
}
```

---

## Business Logic Highlights

### 温和衰减策略
```python
# 根据不活跃天数决定衰减量
days_inactive = (now - conversation.last_message_at).days

if days_inactive >= 30:
    decay_amount = 10  # 一个月以上，加速衰减
    reason = 'inactive_30days'
elif days_inactive >= 14:
    decay_amount = 7   # 两周以上，中度衰减
else:  # 7-13 days
    decay_amount = 5   # 一周以上，温和衰减
    reason = 'inactive_7days'

# 应用衰减（不会低于0）
actual_decay = min(decay_amount, conversation.intimacy_exp)
conversation.intimacy_exp -= actual_decay
```

### 防止滥用回归礼包
```python
# 检查上次领取时间（30天冷却）
if last_comeback_bonus_at:
    days_since = (now - last_comeback_bonus_at).days
    if days_since < 30:
        return {
            'success': False,
            'reason': 'too_soon',
            'days_until_available': 30 - days_since
        }

# 检查是否真的不活跃（7天以上）
days_inactive = (now - last_message_at).days
if days_inactive < 7:
    return {
        'success': False,
        'reason': 'not_inactive'
    }
```

### 衰减日志追踪
```python
# 记录每次衰减，用于用户查询和数据分析
log = IntimacyDecayLog(
    conversation_id=conv_id,
    decay_amount=-5,  # 负值表示减少
    reason='inactive_7days',
    intimacy_exp_before=250,
    intimacy_exp_after=245
)
```

---

## Background Task Details

### 任务配置
- **执行时间:** 每日3:00 AM（低流量时段）
- **执行频率:** 每天1次
- **超时设置:** 无超时（自动执行）
- **错误处理:** 捕获异常，继续运行

### 任务流程
```
1. 每分钟检查当前时间
2. 如果是3:00 - 3:05之间：
   - 创建数据库会话
   - 查询所有需要衰减的对话
   - 批量应用衰减
   - 记录日志
   - 关闭数据库会话
   - 睡眠6分钟（避免重复执行）
3. 否则：睡眠1分钟
```

### 性能考虑
- 使用批量查询减少数据库访问
- 仅查询需要衰减的对话（过滤条件）
- 后台线程执行，不影响主应用
- 日志记录前5个衰减详情（避免日志过多）

---

## Testing Notes

### 测试场景1: 首次衰减
1. 用户7天未登录
2. 后台任务执行（或手动触发）
3. 验证经验值减少5 exp
4. 验证intimacy_decay_logs有记录
5. 验证reason = 'inactive_7days'

### 测试场景2: 多级衰减
1. 用户8天未登录：-5 exp/天
2. 用户15天未登录：-7 exp/天
3. 用户31天未登录：-10 exp/天
4. 验证衰减量根据天数正确调整

### 测试场景3: 保底机制
1. 用户当前经验值为3 exp
2. 应衰减5 exp
3. 验证仅减少3 exp，经验值变为0
4. 验证不会出现负数

### 测试场景4: 等级不降低
1. 用户Level 5, 经验值5 exp
2. 连续衰减至经验值0
3. 验证等级仍为Level 5
4. 验证不会降级到Level 4

### 测试场景5: 关闭衰减
1. 用户调用toggle-decay API（disabled=true）
2. 7天后后台任务执行
3. 验证该对话未被衰减
4. 验证decay_disabled = true

### 测试场景6: 回归礼包
1. 用户10天未登录
2. 用户回归并发送消息
3. 调用comeback-bonus API
4. 验证获得+50 exp
5. 验证last_comeback_bonus_at已更新
6. 立即再次调用 → 失败（too_soon）
7. 30天后再次调用 → 成功

---

## Integration Points

### 与Story 6.1集成（亲密度系统）
- 衰减直接操作conversations表的intimacy_exp字段
- 使用IntimacyLog的reason字段区分衰减原因
- 回归礼包调用add_intimacy_exp()方法

### 与Story 6.3集成（奖励系统）
- 关闭衰减可作为Level奖励或付费特权
- RewardService.has_feature_unlocked('no_decay')

### 与推送通知系统集成（未实现）
- 第5天未登录：推送"好久没见，想你了~"
- 第7天未登录：推送"再不来看我，亲密度要下降啦~"
- 需要Firebase Cloud Messaging (FCM)

### 与订阅系统集成（未实现）
- 付费用户可永久关闭衰减
- SubscriptionService.has_premium() → toggle_decay(disabled=true)

---

## Operational Considerations

### 功能开关
**重要:** 此功能具有争议性，建议通过配置开关控制：

```python
# config.py
DECAY_ENABLED = os.getenv('DECAY_ENABLED', 'false').lower() == 'true'

# 在decay task中检查
if not settings.DECAY_ENABLED:
    print("[Decay Task] Decay is disabled globally")
    return
```

### A/B测试建议
- **对照组:** 衰减关闭，观察自然留存率
- **实验组:** 衰减开启，观察激励效果
- **指标监控:**
  * 7日留存率
  * 14日留存率
  * 30日留存率
  * 回归率（用户重新活跃比例）
  * 用户投诉率

### 运营策略
**温和启用路径:**
1. **第1-2周:** 仅记录日志，不实际扣减经验（观察数据）
2. **第3-4周:** 小范围A/B测试（10%用户）
3. **第5-6周:** 扩大至50%用户
4. **第7周+:** 根据数据决定是否全量

**风险缓解:**
- 提前告知用户衰减机制（透明度）
- 提供关闭选项（用户控制感）
- 回归礼包补偿（正向激励）
- 监控用户反馈，随时调整

---

## Lessons Learned

### 设计决策
✅ **温和策略** - 7天才开始衰减，避免过早惩罚
✅ **渐进衰减** - 根据不活跃天数分级衰减（5/7/10 exp）
✅ **保底机制** - 经验值不会负数，等级不会降低
✅ **用户控制** - 允许关闭衰减，尊重用户选择
✅ **回归激励** - 提供回归礼包，正向鼓励
✅ **可配置性** - 通过环境变量控制全局开关

### 潜在风险
⚠️ **用户流失** - 衰减可能导致用户感到惩罚而离开
⚠️ **负面情绪** - "我的努力被抹杀了"的挫败感
⚠️ **竞品对比** - 其他产品无衰减，用户可能流失至竞品

### 替代方案
如果衰减效果不佳，可考虑：
- **软性提醒:** 仅推送通知，不扣经验
- **冻结机制:** 7天后经验值冻结，不增不减
- **每日奖励:** 连续登录奖励（正向激励），而非衰减（负向惩罚）

---

## Status

**✅ Story 6.5 完成 (2026-01-19)**

Backend Implementation: ✅ 完成
- Database Migrations: ✅
- Models: ✅
- Service Logic: ✅
- Background Task: ✅
- API Endpoints: ✅

Configuration: ⚠️ 建议
- 默认关闭，通过环境变量控制: ⏳
- A/B测试框架: ⏳
- 推送通知集成: ⏳

Frontend Implementation: ⏳ 待开发（不在6.5范围）
- Decay History UI: ⏳
- Toggle Decay Settings: ⏳
- Comeback Bonus Modal: ⏳

Documentation: ✅ 完成

---

## Recommendations

### MVP阶段建议
1. **默认关闭衰减功能**（DECAY_ENABLED=false）
2. 仅实现回归礼包功能（正向激励）
3. 收集1-2周用户行为数据
4. 根据自然留存率决定是否启用衰减

### 后续优化方向
1. **推送通知系统** - 第5天、第7天提醒
2. **数据分析看板** - 监控衰减影响
3. **个性化衰减** - 根据用户活跃度调整衰减速率
4. **衰减补偿** - 用户回归后可花费道具恢复经验

### Epic 6总结
**Epic 6: 亲密度养成与里程碑庆祝 - 全部完成 ✅**

5个Story全部实现：
- ✅ 6.1: 亲密度等级系统与经验值计算
- ✅ 6.2: 前端亲密度展示与升级动画
- ✅ 6.3: 等级特权与里程碑奖励
- ✅ 6.4: 成就系统与每日互动奖励
- ✅ 6.5: 亲密度衰减与保持机制

**下一步:** Epic 7 - 订阅支付完善 or Epic 8 - 跨设备同步
