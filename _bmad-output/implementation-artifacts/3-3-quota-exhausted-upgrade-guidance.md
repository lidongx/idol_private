# Story 3.3: 配额耗尽后的升级引导

**Epic**: Epic 3 - Freemium边界与消息计量
**Story ID**: 3-3-quota-exhausted-upgrade-guidance
**Status**: ✅ Done
**Implementation Date**: 2026-01-15

---

## 📋 Story Overview

### User Story
**作为** 免费用户
**我想要** 在配额用完后看到友好的升级提示
**以便** 我了解升级会员的好处并可以选择升级

### Acceptance Criteria
- [x] 用户尝试发送第21条消息时被拦截
- [x] 弹出升级引导弹窗，包含标题、文案、对比表格
- [x] 提供"升级会员"和"明天再聊"两个按钮
- [x] 配额耗尽后输入框显示禁用状态
- [x] 占位符显示"今日额度已用完，明天继续~"
- [x] 提供便捷的工具类和Mixin简化集成

---

## 🎯 Implementation Summary

### Backend
后端配额检查已在Story 3.1实现：
- `QuotaExceededException` 返回 HTTP 429 状态码
- 错误消息："今天的免费额度用完啦~升级会员解锁无限对话"

### Flutter Components

#### 1. QuotaExhaustedDialog
升级引导弹窗组件 (`lib/features/quota/widgets/quota_exhausted_dialog.dart`)

**特性：**
- 圆形插图（心形图标）
- 标题："今天的免费额度用完啦~"
- 描述文案："明天继续免费陪你，或现在升级解锁无限对话"
- 功能对比表格（每日消息、专属内容、亲密度加速）
- 两个按钮：
  - 次要按钮："明天再聊"（OutlinedButton）
  - 主要按钮："升级会员"（FilledButton）

**使用方式：**
```dart
QuotaExhaustedDialog.show(
  context,
  onUpgrade: () {
    Navigator.pushNamed(context, '/subscription');
  },
);
```

#### 2. QuotaExhaustedInputBar
配额耗尽状态的输入栏 (`lib/features/quota/widgets/quota_exhausted_dialog.dart`)

**特性：**
- 禁用状态的输入框
- 占位符："今日额度已用完，明天继续~"
- 升级按钮（带图标）

**使用方式：**
```dart
if (quota.isExhausted)
  QuotaExhaustedInputBar(
    onUpgrade: () => Navigator.pushNamed(context, '/subscription'),
  )
else
  NormalInputBar()
```

#### 3. QuotaUtils
配额工具类 (`lib/features/quota/utils/quota_utils.dart`)

**方法：**
- `isQuotaExceeded(error)`: 检查错误是否为配额耗尽
- `handleQuotaExceeded(context, error)`: 自动处理配额错误并显示弹窗
- `getQuotaExceededMessage(error)`: 提取错误消息

#### 4. QuotaHandlerMixin
配额处理Mixin (`lib/features/quota/utils/quota_utils.dart`)

**方法：**
- `sendMessageWithQuotaCheck()`: 发送消息时自动检查配额

**使用方式：**
```dart
class _ConversationPageState extends State<ConversationPage>
    with QuotaHandlerMixin {

  Future<void> _handleSendMessage(String text) async {
    final success = await sendMessageWithQuotaCheck(
      sendMessage: () async {
        await conversationService.sendMessage(text);
        setState(() {
          quota = quota?.decrementRemaining();
        });
      },
      onQuotaExceeded: () {
        Navigator.pushNamed(context, '/subscription');
      },
    );
  }
}
```

---

## 📁 Files Created

### Flutter
1. `lib/features/quota/widgets/quota_exhausted_dialog.dart` (360 lines)
   - QuotaExhaustedDialog: 升级引导弹窗
   - QuotaExhaustedInputBar: 耗尽状态输入栏
2. `lib/features/quota/utils/quota_utils.dart` (92 lines)
   - QuotaUtils: 工具函数
   - QuotaHandlerMixin: 对话页面Mixin
3. `lib/features/quota/INTEGRATION_EXAMPLE.md` (集成示例文档)

---

## 🎨 UI Design

### Dialog Layout
```
┌─────────────────────────────┐
│     [Heart Icon Circle]     │
│                             │
│  今天的免费额度用完啦~        │
│  明天继续免费陪你，           │
│  或现在升级解锁无限对话        │
│                             │
│  ┌───────────────────────┐  │
│  │ 功能 │ 免费 │ 会员    │  │
│  ├───────────────────────┤  │
│  │每日消息│20条│ 无限    │  │
│  │专属内容│ ✗  │  ✓     │  │
│  │亲密度  │ ✗  │  ✓     │  │
│  └───────────────────────┘  │
│                             │
│ [明天再聊] [升级会员]        │
└─────────────────────────────┘
```

### Exhausted Input Bar
```
┌───────────────────────────────────────┐
│ [今日额度已用完，明天继续~] [💎 升级]   │
└───────────────────────────────────────┘
```

---

## 🔄 Integration Patterns

### Pattern 1: QuotaHandlerMixin (推荐)
```dart
class _ConversationPageState extends State<ConversationPage>
    with QuotaHandlerMixin {

  Future<void> _sendMessage(String text) async {
    await sendMessageWithQuotaCheck(
      sendMessage: () => _actualSendMessage(text),
      onQuotaExceeded: _navigateToSubscription,
    );
  }
}
```

### Pattern 2: Manual Error Handling
```dart
try {
  await conversationService.sendMessage(text);
} catch (e) {
  QuotaUtils.handleQuotaExceeded(context, e);
}
```

### Pattern 3: Proactive Check
```dart
if (quota.isExhausted) {
  QuotaExhaustedDialog.show(context, onUpgrade: ...);
  return;
}
```

---

## 🎭 Feature Comparison Table

| 功能 | 免费 | 会员 |
|------|------|------|
| 每日消息 | 20条 | 无限 |
| 专属内容 | ❌ | ✅ |
| 亲密度加速 | ❌ | ✅ |

---

## ✅ Testing Checklist

- [x] 第21条消息被拦截
- [x] 弹窗正确显示标题和文案
- [x] 对比表格正确渲染
- [x] "明天再聊"按钮关闭弹窗
- [x] "升级会员"按钮触发回调
- [x] 配额耗尽后输入框禁用
- [x] QuotaHandlerMixin正确处理配额错误
- [x] 无限用户不显示配额相关UI

---

## 🔗 Related Stories

- **Story 3.1**: 消息配额数据模型与计量逻辑 ✅
- **Story 3.2**: 前端配额显示与实时更新 ✅
- **Story 3.4**: 订阅页面基础版 (Next)

---

## 📝 Technical Notes

1. **Deferred Navigation**: 订阅页面导航代码已预留，待Story 3.4实现后启用
2. **Error Handling**: 自动识别HTTP 429和QuotaExceededException
3. **Material Design 3**: 使用MD3组件（FilledButton、OutlinedButton、Dialog）
4. **Immutability**: Quota模型保持不可变，使用copyWith()和decrementRemaining()
5. **Testing**: 提供测试用配额对象和SQL命令

---

## 🎓 Best Practices

1. ✅ 使用 QuotaHandlerMixin 简化集成
2. ✅ 本地更新配额（decrementRemaining）+ 定期API刷新
3. ✅ 配额耗尽时显示禁用输入栏而非隐藏
4. ✅ 友好文案避免生硬拦截
5. ✅ 无限用户完全隐藏配额UI

---

**Story Status**: ✅ Done
**Last Updated**: 2026-01-15
