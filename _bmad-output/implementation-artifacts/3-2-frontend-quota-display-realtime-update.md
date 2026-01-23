# Story 3.2: 前端配额显示与实时更新

**Epic**: Epic 3 - Freemium边界与消息计量
**Story ID**: 3-2-frontend-quota-display-realtime-update
**Status**: ✅ Done
**Implementation Date**: 2026-01-15

---

## 📋 Story Overview

### User Story
**作为** 免费用户
**我想要** 清晰看到今日剩余消息数量
**以便** 合理规划对话并了解何时需要升级会员

### Acceptance Criteria
- [x] 创建Flutter配额数据模型（Quota）
- [x] 创建配额查询API（GET /users/me/quota）
- [x] 实现配额显示组件（QuotaIndicator）
- [x] 颜色分级警告（绿/橙/红）
- [x] 发送消息后本地更新配额
- [x] 无限用户不显示配额提示

---

## 🎯 Implementation Summary

### Backend API

**Quota Schema** (`backend/app/schemas/quota.py`):
```python
class QuotaResponse(BaseModel):
    date: str
    messages_sent: int
    quota_limit: int
    remaining: int
    is_unlimited: bool
```

**Quota Endpoint** (`backend/app/routers/quota.py`):
```python
@router.get("/users/me/quota", response_model=QuotaResponse)
async def get_my_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
)
```

### Flutter Models

**Quota** (`lib/features/quota/models/quota.dart`):
- Properties: `date`, `messagesSent`, `quotaLimit`, `remaining`, `isUnlimited`
- Helper properties: `isExhausted`, `usagePercentage`, `remainingPercentage`
- Methods: `decrementRemaining()` for local state updates

### Flutter Services

**QuotaService** (`lib/features/quota/services/quota_service.dart`):
```dart
Future<Quota> getMyQuota() async {
  final response = await http.get(
    Uri.parse('$_baseUrl/users/me/quota'),
    headers: {'Authorization': 'Bearer $token'},
  );
  return Quota.fromJson(jsonDecode(response.body));
}
```

### Flutter Widgets

**QuotaIndicator** (`lib/features/quota/widgets/quota_indicator.dart`):
Three variants implemented:
1. **QuotaIndicator**: Full-width banner with icon and text "今日剩余: X/20"
2. **QuotaBadge**: Compact badge showing remaining count
3. **QuotaProgressBar**: Visual progress bar with percentage

---

## 🎨 Color-Coded Warning Levels

| Remaining | Color | Background | Warning Level |
|-----------|-------|------------|---------------|
| > 10 | 🟢 Green (#4CAF50) | Green 10% opacity | Safe |
| 5-10 | 🟠 Orange (#FF9800) | Orange 10% opacity | Warning |
| < 5 | 🔴 Red (#F44336) | Red 10% opacity | Critical |

Implementation:
```dart
if (quota.remaining > 10) {
  backgroundColor = const Color(0xFF4CAF50).withOpacity(0.1);
  textColor = const Color(0xFF4CAF50);
} else if (quota.remaining >= 5) {
  backgroundColor = const Color(0xFFFF9800).withOpacity(0.1);
  textColor = const Color(0xFFFF9800);
} else {
  backgroundColor = const Color(0xFFF44336).withOpacity(0.1);
  textColor = const Color(0xFFF44336);
}
```

---

## 📁 Files Created

### Backend
1. `backend/app/schemas/quota.py` (26 lines)
2. `backend/app/routers/quota.py` (38 lines)

### Flutter
3. `lib/features/quota/models/quota.dart` (88 lines)
4. `lib/features/quota/services/quota_service.dart` (45 lines)
5. `lib/features/quota/widgets/quota_indicator.dart` (202 lines)

---

## 🔄 Real-time Update Strategy

1. **Initial Load**: Fetch quota on conversation page mount
2. **After Send**: Call `quota.decrementRemaining()` for instant UI update
3. **Periodic Refresh**: Refetch from API every 60 seconds
4. **Error Handling**: Show cached quota if API fails

---

## 📱 UI/UX Design

### QuotaIndicator Usage
```dart
// At top of conversation page
QuotaIndicator(
  quota: quotaState.quota,
  onTap: () => Navigator.push(...), // Navigate to subscription page
)
```

### QuotaBadge Usage
```dart
// In app bar or tight spaces
QuotaBadge(quota: quotaState.quota)
```

### QuotaProgressBar Usage
```dart
// In settings or profile page
QuotaProgressBar(
  quota: quotaState.quota,
  showLabel: true,
)
```

---

## ✅ Testing Checklist

- [x] API returns correct quota for free users (20 limit)
- [x] API returns unlimited for premium users (quota_limit = -1)
- [x] Widget hides for unlimited users
- [x] Color changes at thresholds (10 and 5)
- [x] decrementRemaining() updates state correctly
- [x] Quota exhausted state handled properly

---

**Story Status**: ✅ Done
**Last Updated**: 2026-01-15
