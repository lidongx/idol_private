# Story 4.4: 用户标签系统与"关于我"页面

**Epic**: Epic 4 - 记忆系统与专属个性化
**Story ID**: 4-4-user-tag-system-about-me-page
**Status**: ✅ Done
**Implementation Date**: 2026-01-15

---

## 📋 Story Overview

### User Story
**作为** 用户
**我想要** 查看AI为我标注的个人标签和记忆
**以便** 我知道她记住了哪些关于我的事情

### Acceptance Criteria
- [x] 创建"关于我"页面展示用户档案
- [x] 按类型分组显示记忆（爱好、工作、家人、情感、目标）
- [x] 显示记忆统计信息
- [x] 显示用户标签（tags）
- [x] 支持删除记忆功能
- [x] Material Design 3风格
- [x] 下拉刷新功能

---

## 🎯 Implementation Summary

### Flutter Components

#### 1. Memory Model (`lib/features/memory/models/memory.dart`)

**Memory类：**
```dart
class Memory {
  final int id;
  final String content;
  final String? memoryType;  // hobby, work, family, feeling, goal, preference, event
  final String importance;   // high, medium, low
  final DateTime createdAt;
  final DateTime? lastMentionedAt;

  String get typeDisplayName;  // "爱好兴趣", "工作学习", etc.
  String get importanceColor;  // Color based on importance
}
```

**UserProfile类：**
```dart
class UserProfile {
  final Map<String, String> tags;
  final List<Memory> recentMemories;
  final MemoryStats stats;

  Map<String, List<Memory>> get memoriesByType;
}
```

**MemoryStats类：**
```dart
class MemoryStats {
  final int totalMemories;
  final int hobbyCount;
  final int workCount;
  final int familyCount;
  final int feelingCount;
  final int goalCount;
}
```

#### 2. Memory Service (`lib/features/memory/services/memory_service.dart`)

**核心方法：**
- `getMyMemories()` - 获取用户记忆（支持过滤）
- `getMyTags()` - 获取用户标签
- `deleteMemory()` - 删除记忆
- `getMyProfile()` - 获取完整用户档案

#### 3. Memory Widgets (`lib/features/memory/widgets/memory_widgets.dart`)

**MemoryCard：**
- 记忆卡片组件
- 显示内容、类型、重要性、创建时间
- 支持点击和删除操作

**MemorySection：**
- 按类型分组的记忆区域
- 显示区域标题和图标
- "查看全部"按钮（可选）

**MemoryStatsCard：**
- 记忆统计卡片
- 显示总数和各类型数量

#### 4. About Me Page (`lib/features/memory/pages/about_me_page.dart`)

**功能：**
- 精美的页头（渐变背景）
- 记忆统计卡片
- 按类型分组的记忆展示
- 下拉刷新
- 删除确认对话框
- 空状态提示

---

## 📁 Files Created

### Flutter
1. `lib/features/memory/models/memory.dart` (149 lines)
2. `lib/features/memory/services/memory_service.dart` (156 lines)
3. `lib/features/memory/widgets/memory_widgets.dart` (361 lines)
4. `lib/features/memory/pages/about_me_page.dart` (315 lines)

---

## 🎨 UI Design

### Page Layout

```
┌─────────────────────────────────┐
│  AppBar: 关于我                  │
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │ 🧑 她眼中的你                │ │
│ │ 这是林雪晴对你的了解和记忆    │ │
│ │                              │ │
│ │ [标签chip] [标签chip]        │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 🧠 记忆统计                  │ │
│ │ 总记忆数: 15                 │ │
│ │ [爱好:5] [工作:3] [家人:2]   │ │
│ └─────────────────────────────┘ │
│                                 │
│ 🏀 爱好兴趣         [查看全部]   │
│ ┌─────────────────────────────┐ │
│ │ [爱好] 用户喜欢打篮球    [×] │ │
│ │ 📅 3天前 ⭐ 一般            │ │
│ └─────────────────────────────┘ │
│                                 │
│ 💼 工作学习         [查看全部]   │
│ ┌─────────────────────────────┐ │
│ │ [工作] 用户是软件工程师  [×] │ │
│ │ 📅 1周前 ⭐ 重要            │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

### Color Scheme

**Importance Colors:**
- High (重要): 🔴 Red #F44336
- Medium (一般): 🟠 Orange #FF9800
- Low (次要): 🟢 Green #4CAF50

**Memory Type Icons:**
- 爱好兴趣: 🏀 `Icons.sports_basketball`
- 工作学习: 💼 `Icons.work_outline`
- 家人朋友: 👥 `Icons.people_outline`
- 情感状态: ❤️ `Icons.favorite_outline`
- 目标计划: 🚩 `Icons.flag_outlined`
- 个人偏好: 🎚️ `Icons.tune`
- 生活事件: 📅 `Icons.event_note`

---

## 🔧 Technical Details

### Memory Grouping Logic

```dart
Map<String, List<Memory>> get memoriesByType {
  final Map<String, List<Memory>> grouped = {};

  for (final memory in recentMemories) {
    final type = memory.memoryType ?? 'other';
    grouped.putIfAbsent(type, () => []);
    grouped[type]!.add(memory);
  }

  return grouped;
}
```

### Date Formatting

```dart
String _formatDate(DateTime date) {
  final difference = DateTime.now().difference(date);

  if (difference.inDays == 0) return '今天';
  if (difference.inDays == 1) return '昨天';
  if (difference.inDays < 7) return '${difference.inDays}天前';
  if (difference.inDays < 30) return '${(difference.inDays / 7).floor()}周前';
  return '${date.month}月${date.day}日';
}
```

### Delete Flow

```dart
1. User clicks delete button (×)
   ↓
2. Show confirmation dialog
   ↓
3. If confirmed:
   ├─ Call API: DELETE /users/me/memories/{id}
   ├─ Remove from local state
   └─ Show success SnackBar
```

---

## ✅ Testing Checklist

- [x] Page loads successfully
- [x] Memories grouped by type correctly
- [x] Statistics calculated accurately
- [x] Tags displayed correctly
- [x] Delete confirmation dialog shows
- [x] Delete removes memory from UI
- [x] Pull-to-refresh works
- [x] Empty state displays correctly
- [x] Error state displays with retry button

---

## 🎓 Usage Examples

### Example 1: User with Hobbies

**Data:**
```json
{
  "tags": {"name": "张三", "job": "软件工程师"},
  "recent_memories": [
    {
      "id": 1,
      "content": "用户喜欢打篮球",
      "memory_type": "hobby",
      "importance": "medium",
      "created_at": "2026-01-10T10:00:00Z"
    },
    {
      "id": 2,
      "content": "用户是软件工程师，在字节跳动工作",
      "memory_type": "work",
      "importance": "high",
      "created_at": "2026-01-12T14:00:00Z"
    }
  ]
}
```

**Display:**
```
她眼中的你
这是林雪晴对你的了解和记忆

[name: 张三] [job: 软件工程师]

📊 记忆统计
总记忆数: 2
[爱好: 1] [工作: 1]

🏀 爱好兴趣
┌──────────────────────────┐
│ [爱好] 用户喜欢打篮球 [×] │
│ 📅 5天前 ⭐ 一般         │
└──────────────────────────┘

💼 工作学习
┌────────────────────────────────────┐
│ [工作] 用户是软件工程师，在... [×] │
│ 📅 3天前 ⭐ 重要                  │
└────────────────────────────────────┘
```

### Example 2: Empty State

**Display:**
```
她眼中的你
这是林雪晴对你的了解和记忆

📊 记忆统计
总记忆数: 0

🧠
暂时还没有记忆
多和她聊聊天，让她更了解你吧
```

---

## 🔗 Integration

### Navigation

```dart
// From profile menu or settings
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => const AboutMePage(),
  ),
);
```

### Router Configuration (Future)

```dart
'/about-me': (context) => const AboutMePage(),
```

---

## 📊 API Integration

**Existing Endpoints (Story 4.2):**
- `GET /users/me/memories` ✓
- `GET /users/me/tags` ✓
- `DELETE /users/me/memories/{id}` ✓

**Future Enhancement:**
```
GET /users/me/profile
Response: {
  "tags": {...},
  "recent_memories": [...],
  "stats": {...}
}
```

---

## 🚀 Future Enhancements

1. **Memory Details Dialog**
   - Click memory card → show full details
   - Display source conversation snippet
   - Show when it was last mentioned

2. **Tag Editing**
   - Edit tag values directly
   - Add new tags manually

3. **Memory Search**
   - Search bar to filter memories
   - Filter by type, importance, date

4. **Export Memories**
   - Export as JSON or text file
   - Share functionality

5. **Memory Timeline**
   - Visual timeline of memories
   - Group by date/month

6. **Memory Insights**
   - Most mentioned topics
   - Memory growth over time

---

## 📝 Technical Notes

1. **Data Loading**: Combined calls for MVP, should be single endpoint in production
2. **Local State**: Deletes update local state immediately for better UX
3. **Refresh Strategy**: Pull-to-refresh reloads all data
4. **Grouping**: Client-side grouping by memory type
5. **Empty State**: Encourages user engagement

---

**Story Status**: ✅ Done
**Last Updated**: 2026-01-15
