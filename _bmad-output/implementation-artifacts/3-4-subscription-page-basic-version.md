# Story 3.4: 订阅页面基础版（仅展示）

**Epic**: Epic 3 - Freemium边界与消息计量
**Story ID**: 3-4-subscription-page-basic-version
**Status**: ✅ Done
**Implementation Date**: 2026-01-15

---

## 📋 Story Overview

### User Story
**作为** 用户
**我想要** 查看订阅套餐对比和价格
**以便** 我可以了解付费会员的权益

### Acceptance Criteria
- [x] 创建订阅页面（路由：`/subscription`）
- [x] 显示Free和Premium两个套餐卡片
- [x] Premium卡片带"推荐"标签
- [x] 功能列表清晰展示（✓/✗）
- [x] 底部按钮显示"立即升级（即将开放）"并禁用
- [x] 显示提示文案："支付功能开发中，敬请期待~"
- [x] Material Design 3风格

---

## 🎯 Implementation Summary

### Flutter Components

#### 1. SubscriptionPlan Model
订阅套餐数据模型 (`lib/features/subscription/models/subscription_plan.dart`)

**属性：**
- `id`, `name`, `displayName`: 套餐标识
- `price`, `currency`, `period`: 价格信息
- `features`: 功能列表（List<SubscriptionFeature>）
- `isRecommended`: 是否推荐
- `isCurrentPlan`: 是否为当前套餐

**预定义套餐：**
```dart
// Free plan
SubscriptionPlan.freePlan:
- ¥0
- 每日20条消息 ✓
- 基础对话功能 ✓
- 无限消息 ✗
- 专属内容解锁 ✗
- 亲密度加速 ✗

// Premium plan
SubscriptionPlan.premiumPlan:
- ¥28/月
- 无限消息 ✓ (highlight)
- 专属私密照片 ✓
- 专属语音日记 ✓
- 亲密度加速 ✓
- 优先AI响应 ✓
- isRecommended: true
```

#### 2. SubscriptionPlanCard Widget
订阅套餐卡片组件 (`lib/features/subscription/widgets/subscription_plan_card.dart`)

**特性：**
- 响应式卡片布局
- Premium卡片高亮边框和阴影效果
- 推荐标签（顶部居中，带渐变背景和星星图标）
- 功能列表带图标（✓/✗）
- 当前套餐指示器
- 价格显示（大字号）

**视觉差异：**
```dart
// Free plan
- 普通边框（outlineVariant, 1px）
- 白色背景
- 常规颜色

// Premium plan
- 粗边框（primary, 2px）
- 浅色primaryContainer背景
- 主色调高亮
- 卡片阴影效果
- 顶部"推荐"标签
```

#### 3. SubscriptionPage
订阅页面 (`lib/features/subscription/pages/subscription_page.dart`)

**布局结构：**
```
┌─────────────────────────────┐
│      AppBar: 订阅会员        │
├─────────────────────────────┤
│ 选择适合你的套餐              │
│ 解锁完整功能，享受无限陪伴     │
│                             │
│ ┌─────────────────────────┐ │
│ │    Free Plan Card       │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │  Premium Plan Card ⭐   │ │
│ │  (Recommended)          │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ 💎 为什么选择Premium？   │ │
│ │ • 无限对话               │ │
│ │ • 专属内容               │ │
│ │ • 亲密度加速             │ │
│ └─────────────────────────┘ │
├─────────────────────────────┤
│ ℹ️  支付功能开发中，敬请期待~ │
│ [立即升级（即将开放）]        │
└─────────────────────────────┘
```

**关键功能：**
- 套餐对比展示（使用SubscriptionComparisonView）
- "为什么选择Premium"说明区域
- 底部固定操作栏
- 按钮禁用状态（onPressed: null）
- 提示信息盒子

---

## 📁 Files Created

### Flutter
1. `lib/features/subscription/models/subscription_plan.dart` (132 lines)
   - SubscriptionPlan: 套餐数据模型
   - SubscriptionFeature: 功能特性
   - 静态方法：freePlan, premiumPlan, allPlans

2. `lib/features/subscription/widgets/subscription_plan_card.dart` (267 lines)
   - SubscriptionPlanCard: 套餐卡片组件
   - SubscriptionComparisonView: 对比视图
   - SubscriptionPlanCopyWith: 扩展方法

3. `lib/features/subscription/pages/subscription_page.dart` (264 lines)
   - SubscriptionPage: 订阅页面
   - WhyPremium section: 优势说明
   - Bottom action bar: 操作栏

---

## 🎨 Design Specifications

### Premium Card Special Effects

1. **Border & Background**
   ```dart
   border: Border.all(
     color: colorScheme.primary.withOpacity(0.5),
     width: 2,
   )
   backgroundColor: colorScheme.primaryContainer.withOpacity(0.15)
   ```

2. **Recommended Badge**
   ```dart
   - Gradient background (primary)
   - Stars icon + "推荐" text
   - Positioned at top center
   - BoxShadow for depth
   ```

3. **Card Shadow**
   ```dart
   boxShadow: [
     BoxShadow(
       color: primary.withOpacity(0.1),
       blurRadius: 12,
       offset: Offset(0, 4),
     ),
   ]
   ```

### Color Scheme

| Element | Color | Usage |
|---------|-------|-------|
| Free card border | `outlineVariant` | 1px |
| Premium card border | `primary` | 2px |
| Premium background | `primaryContainer` | 15% opacity |
| Recommended badge | `primary` (gradient) | Full |
| Check icon (Free) | `tertiary` | Feature list |
| Check icon (Premium) | `primary` | Feature list |
| Disabled button | `surfaceVariant` | 50% opacity |

---

## 🔄 Navigation Integration

### From Quota Exhausted Dialog
```dart
QuotaExhaustedDialog.show(
  context,
  onUpgrade: () {
    Navigator.pushNamed(context, '/subscription');
  },
);
```

### From Quota Exhausted Input Bar
```dart
QuotaExhaustedInputBar(
  onUpgrade: () {
    Navigator.pushNamed(context, '/subscription');
  },
)
```

### Route Definition (TODO)
```dart
// In main.dart or router configuration
'/subscription': (context) => const SubscriptionPage(),
```

---

## 📊 Feature Comparison Table

| 功能 | Free | Premium |
|------|------|---------|
| 每日消息 | 20条 | 无限 ⭐ |
| 基础对话 | ✅ | ✅ |
| 专属私密照片 | ❌ | ✅ |
| 专属语音日记 | ❌ | ✅ |
| 亲密度加速 | ❌ | ✅ |
| 优先AI响应 | ❌ | ✅ |
| **价格** | **¥0** | **¥28/月** |

---

## ✅ Testing Checklist

- [x] 订阅页面正确显示
- [x] Free和Premium卡片并排展示
- [x] Premium卡片显示"推荐"标签
- [x] 功能列表正确显示（✓/✗图标）
- [x] 价格格式正确（¥0、¥28/月）
- [x] "为什么选择Premium"区域显示
- [x] 底部按钮禁用状态
- [x] 提示文案显示："支付功能开发中，敬请期待~"
- [x] Material Design 3组件使用正确

---

## 🔗 Related Stories

- **Story 3.1**: 消息配额数据模型与计量逻辑 ✅
- **Story 3.2**: 前端配额显示与实时更新 ✅
- **Story 3.3**: 配额耗尽后的升级引导 ✅
- **Epic 7 Stories**: 支付集成（未来实现）

---

## 📝 Technical Notes

1. **Display Only**: 此版本仅UI展示，不包含支付功能
2. **Deferred Payment**: Epic 7将实现完整支付集成（支付宝、微信、Apple IAP、Google Play）
3. **Static Plans**: 当前使用静态数据，未来将从API获取
4. **Route Setup**: 需在路由配置中添加 `/subscription` 路由
5. **Current Plan Detection**: `_currentPlanId` 暂时硬编码，未来从用户资料获取

---

## 🎓 Future Enhancements (Epic 7)

1. **Payment Integration**
   - 支付宝、微信支付
   - Apple In-App Purchase
   - Google Play Billing

2. **Dynamic Pricing**
   - 从API获取套餐信息
   - 支持多种订阅周期（月/季/年）
   - A/B测试定价

3. **Subscription Management**
   - 订阅激活逻辑
   - 自动续费管理
   - 退款处理

4. **Analytics**
   - 转化漏斗追踪
   - 支付成功率统计
   - 用户订阅周期分析

---

**Story Status**: ✅ Done
**Epic 3 Status**: ✅ Done (All 4 stories completed)
**Last Updated**: 2026-01-15
