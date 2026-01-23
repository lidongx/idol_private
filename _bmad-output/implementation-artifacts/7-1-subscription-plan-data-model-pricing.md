# Story 7.1: 订阅套餐数据模型与定价策略

Status: completed

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-19

## Story

As a **产品经理**,
I want **定义清晰的订阅套餐和定价**,
So that **用户可以选择适合自己的付费方案**。

## Acceptance Criteria

### AC1: 订阅套餐数据表
- **Given** 需要存储订阅套餐配置
- **When** 设计订阅数据模型
- **Then** 创建 `subscription_plans` 表
- **And** 包含字段: plan_name, plan_type, price_cny, duration_days, features (JSONB)
- **And** 插入3个初始套餐: 免费版、月度会员、年度会员

### AC2: 订单数据表
- **Given** 需要追踪用户购买记录
- **When** 设计订单数据模型
- **Then** 创建 `orders` 表
- **And** 包含字段: order_no, user_id, plan_id, amount, payment_method, status, paid_at, expires_at
- **And** 支持5种订单状态: pending, paid, failed, cancelled, refunded

### AC3: 订阅API端点
- **Given** 前端需要获取套餐信息和管理订单
- **When** 创建订阅API
- **Then** 实现GET /api/v1/subscriptions/plans获取套餐列表
- **And** 实现POST /api/v1/subscriptions/orders创建订单
- **And** 实现GET /api/v1/subscriptions/orders获取订单列表
- **And** 实现GET /api/v1/subscriptions/active获取当前激活订阅

---

## Implementation Details

### Database Schema

```sql
-- subscription_plans: 订阅套餐配置表
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(50) NOT NULL,
    plan_type VARCHAR(20) NOT NULL,        -- 'free', 'monthly', 'yearly'
    price_cny DECIMAL(10, 2) NOT NULL,
    duration_days INTEGER NOT NULL,
    features JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0
);

-- orders: 订单表
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    plan_id INTEGER NOT NULL REFERENCES subscription_plans(id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Initial Subscription Plans

| 套餐名称 | 类型 | 价格 | 时长 | 每日消息 | 特权 |
|---------|------|------|------|---------|------|
| 免费版 | free | ¥0 | 永久 | 20条/天 | 基础功能 |
| 月度会员 | monthly | ¥28 | 30天 | 无限制 | 全部功能 + 无广告 + 无衰减 |
| 年度会员 | yearly | ¥268 | 365天 | 无限制 | 全部功能 + 额外500经验 + 优惠20% |

**定价策略:**
- 月度会员: ¥28/月
- 年度会员: ¥268/年 (原价¥336，优惠20%)
- 年度会员额外福利: 订阅时赠送500经验值

---

## Files Created/Modified

### 新建文件 (6个)

#### Database Migrations
1. **backend/migrations/024_create_subscription_plans_table.sql** (79 lines)
   - 创建subscription_plans表
   - 插入3个初始套餐数据

2. **backend/migrations/025_create_orders_table.sql** (44 lines)
   - 创建orders表
   - 5个索引: user_id, status, order_no, created_at, paid_at

#### Models
3. **backend/app/models/subscription_plan.py** (129 lines)
   - SubscriptionPlan模型，3种套餐类型
   - 属性方法: messages_per_day, has_exclusive_content等
   - to_dict()方法用于API响应

4. **backend/app/models/order.py** (169 lines)
   - Order模型，5种订单状态
   - 方法: mark_as_paid(), mark_as_failed(), mark_as_cancelled(), mark_as_refunded()
   - 属性: is_active, days_until_expiry

#### Services
5. **backend/app/services/subscription_service.py** (289 lines)
   - SubscriptionService业务逻辑服务
   - 核心方法:
     * generate_order_no(): 生成唯一订单号
     * create_order(): 创建订单
     * get_active_subscription(): 获取激活订阅
     * check_user_has_feature(): 检查用户功能权限
     * get_user_message_limit(): 获取消息配额

#### Routers
6. **backend/app/routers/subscription.py** (401 lines)
   - 8个API端点:
     * GET /api/v1/subscriptions/plans - 套餐列表
     * GET /api/v1/subscriptions/plans/{id} - 套餐详情
     * POST /api/v1/subscriptions/orders - 创建订单
     * GET /api/v1/subscriptions/orders - 订单列表
     * GET /api/v1/subscriptions/orders/{order_no} - 订单详情
     * GET /api/v1/subscriptions/active - 当前激活订阅
     * GET /api/v1/subscriptions/stats - 订阅统计
     * DELETE /api/v1/subscriptions/orders/{order_no} - 取消订单

### 修改文件 (1个)

7. **backend/app/main.py**
   - 添加import: subscription
   - 注册路由: app.include_router(subscription.router, prefix="/api/v1", tags=["订阅"])

---

## API Endpoints

### GET /api/v1/subscriptions/plans
获取订阅套餐列表

**Response:**
```json
[
  {
    "id": 1,
    "plan_name": "免费版",
    "plan_type": "free",
    "plan_type_display": "免费版",
    "price_cny": 0.0,
    "price_display": "免费",
    "duration_days": 0,
    "duration_display": "永久",
    "features": {
      "messages_per_day": 20,
      "voice_messages": false,
      "exclusive_content": false
    },
    "is_active": true,
    "sort_order": 1
  },
  {
    "id": 2,
    "plan_name": "月度会员",
    "plan_type": "monthly",
    "price_cny": 28.0,
    "price_display": "¥28",
    "duration_days": 30,
    "duration_display": "1个月",
    "features": {
      "messages_per_day": -1,
      "exclusive_content": true,
      "intimacy_decay_disabled": true
    }
  },
  {
    "id": 3,
    "plan_name": "年度会员",
    "plan_type": "yearly",
    "price_cny": 268.0,
    "features": {
      "discount": "优惠20%（原价336元）",
      "bonus_exp": 500
    }
  }
]
```

### POST /api/v1/subscriptions/orders
创建订单

**Request Body:**
```json
{
  "plan_id": 2,
  "payment_method": "alipay"
}
```

**Response:**
```json
{
  "success": true,
  "order": {
    "id": 1,
    "order_no": "IDL20260119123456ABCD",
    "user_id": 1,
    "plan_id": 2,
    "amount": 28.0,
    "payment_method": "alipay",
    "status": "pending",
    "status_display": "待支付",
    "created_at": "2026-01-19T12:34:56"
  },
  "message": "订单创建成功，请继续完成支付"
}
```

### GET /api/v1/subscriptions/active
获取当前激活的订阅

**Response (有订阅):**
```json
{
  "id": 1,
  "order_no": "IDL20260119123456ABCD",
  "status": "paid",
  "expires_at": "2026-02-18T12:34:56",
  "is_active": true,
  "days_until_expiry": 30,
  "plan": {
    "plan_name": "月度会员",
    "features": {...}
  }
}
```

**Response (无订阅):**
```json
null
```

### GET /api/v1/subscriptions/stats
获取订阅统计

**Response:**
```json
{
  "has_active_subscription": true,
  "total_orders": 3,
  "total_spent": 324.0,
  "pending_orders": 0,
  "active_subscription": {
    "plan_name": "年度会员",
    "expires_at": "2027-01-19T12:34:56",
    "days_remaining": 365,
    "features": {...}
  }
}
```

---

## Business Logic Highlights

### 订单号生成
```python
def generate_order_no() -> str:
    """
    Format: IDL + YYYYMMDDHHMMSS + 4-digit random
    Example: IDL20260119123456ABCD
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = secrets.token_hex(2).upper()
    return f"IDL{timestamp}{random_suffix}"
```

### 激活订阅判断
```python
@property
def is_active(self) -> bool:
    if not self.is_paid:
        return False
    if self.expires_at and datetime.utcnow() > self.expires_at:
        return False  # 已过期
    return True
```

### 用户功能权限检查
```python
def check_user_has_feature(user_id, feature_key):
    active_sub = get_active_subscription(user_id)
    if active_sub:
        return active_sub.plan.get_feature(feature_key)
    else:
        # 返回免费版的功能
        free_plan = get_plan_by_type('free')
        return free_plan.get_feature(feature_key)
```

---

## Integration Points

### 与Epic 3集成（消息配额）
- QuotaService可以调用SubscriptionService.get_user_message_limit()
- 付费用户配额为-1（无限制）

### 与Story 6.5集成（亲密度衰减）
- 付费用户feature: intimacy_decay_disabled = true
- IntimacyService可以调用check_user_has_feature()

### 与Story 6.3集成（奖励系统）
- 年度会员订阅时赠送500经验值
- 可在订单支付成功后调用intimacy_service.add_intimacy_exp()

---

## Next Steps

### Story 7.2: 支付宝与微信支付集成
- 集成支付宝SDK（沙箱环境测试）
- 集成微信支付Native（扫码支付）
- 处理支付回调
- 订单状态更新

### Story 7.3: Apple IAP集成
- 集成Apple StoreKit
- Receipt验证
- 自动续费处理

### Story 7.4: Google Play Billing集成
- 集成Google Play Billing Library
- Purchase验证
- 订阅管理

---

## MVP Implementation Notes

**当前完成内容:**
- ✅ 数据模型和表结构
- ✅ 订单创建和查询
- ✅ 功能权限检查
- ✅ API端点

**未实现（需Story 7.2-7.4）:**
- ⏳ 实际支付流程
- ⏳ 支付回调处理
- ⏳ 订单状态自动更新
- ⏳ 退款处理

**测试建议:**
- 可以手动创建订单测试API
- 手动调用mark_as_paid()模拟支付成功
- 验证功能权限检查逻辑

---

## Status

**✅ Story 7.1 完成 (2026-01-19)**

Backend Implementation: ✅ 完成
- Database Migrations: ✅
- Models: ✅
- Services: ✅
- API Endpoints: ✅

Payment Integration: ⏳ Story 7.2-7.4
- Alipay: ⏳
- WeChat Pay: ⏳
- Apple IAP: ⏳
- Google Play: ⏳

Frontend Implementation: ⏳ 待开发（不在7.1范围）
- Subscription Page: ⏳
- Payment Flow UI: ⏳
- Order Management: ⏳

Documentation: ✅ 完成
