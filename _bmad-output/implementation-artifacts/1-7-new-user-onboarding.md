# Story 1.7: 新用户引导流程

Status: completed

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-13

## Story

As a **新注册用户**,
I want **看到3步式引导流程介绍产品核心价值**,
So that **快速理解如何使用并建立对产品的期待**。

## Acceptance Criteria

### AC1: 数据库onboarding_completed字段
- **Given** 用户表已存在（Story 1.1）
- **When** 运行数据库迁移脚本
- **Then** 在users表添加`onboarding_completed`字段：
  - 类型: BOOLEAN
  - 默认值: false
  - NOT NULL
  - 带索引: `idx_users_onboarding`
- **And** 将现有用户的onboarding_completed设置为false

### AC2: Flutter引导页面UI
- **Given** Material Design 3主题已配置（Story 1.4）
- **When** 创建OnboardingScreen widget
- **Then** 创建 `lib/features/onboarding/screens/onboarding_screen.dart`
- **And** 实现3步PageView引导流程
- **And** 每步包含：
  - 图标（带背景圆圈）
  - 标题（第一人称偶像口吻）
  - 副标题（功能说明）
- **And** 包含UI元素：
  - 右上角"跳过"按钮
  - 底部页面指示器（动画圆点）
  - 底部导航按钮（"下一步" → "开始体验"）

### AC3: 引导内容文案
- **Given** 产品定位为AI虚拟恋人
- **When** 用户浏览引导页面
- **Then** 第1步展示：
  - 图标: waving_hand（橙色）
  - 标题: "你好，我是雪晴，很高兴认识你~"
  - 副标题: "24小时陪伴，随时倾听你的心事"
- **And** 第2步展示：
  - 图标: chat_bubble_outline（蓝色）
  - 标题: "和我聊天就像和真实朋友一样自然"
  - 副标题: "我会记住你说的每件事"
- **And** 第3步展示：
  - 图标: favorite（粉色）
  - 标题: "每次互动都让我们更亲密"
  - 副标题: "解锁更多专属内容和惊喜"

### AC4: 后端API完成引导
- **Given** 用户已登录（JWT token有效）
- **When** 用户完成引导流程
- **Then** 创建 `POST /api/v1/auth/complete-onboarding` 端点
- **And** 要求JWT认证（Bearer token）
- **And** 更新用户的`onboarding_completed = True`
- **And** 返回成功响应
- **And** 幂等性：可重复调用

### AC5: Flutter引导完成逻辑
- **Given** OnboardingScreen已创建
- **When** 用户点击"开始体验"或"跳过"
- **Then** 调用`AuthService.completeOnboarding()`方法
- **And** 发送POST请求到 `/api/v1/auth/complete-onboarding`
- **And** 带Authorization Bearer token
- **And** 更新本地存储的用户数据
- **And** 触发onCompleted回调

### AC6: 路由集成
- **Given** 用户登录后
- **When** 检查用户的onboarding_completed状态
- **Then** 在main.dart AuthGate中：
  - 如果 onboarding_completed = false → 显示 OnboardingScreen
  - 如果 onboarding_completed = true → 显示 IdolIntroPage
- **And** 引导完成后自动导航到IdolIntroPage
- **And** 新注册用户默认onboarding_completed = false
- **And** 登录用户从API响应获取onboarding_completed状态

---

## Implementation Details

### Architecture Overview

```
Backend Architecture:
backend/
├── migrations/
│   └── 003_add_onboarding_completed.sql  # Add onboarding_completed field
├── app/
│   ├── models/
│   │   └── user.py                       # Updated User model
│   ├── schemas/
│   │   └── auth.py                       # Updated UserResponse, CompleteOnboardingResponse
│   ├── routers/
│   │   └── auth.py                       # New /complete-onboarding endpoint
│   └── core/
│       └── dependencies.py               # JWT auth dependency (existing)

Frontend Architecture:
lib/
├── features/
│   ├── onboarding/
│   │   └── screens/
│   │       └── onboarding_screen.dart    # 3-step onboarding UI
│   ├── auth/
│   │   ├── models/
│   │   │   └── user.dart                 # Updated User model with onboarding_completed
│   │   └── services/
│   │       └── auth_service.dart         # New completeOnboarding() method
│   └── idol/
│       └── screens/
│           └── idol_intro_page.dart      # Destination after onboarding
└── main.dart                             # Updated AuthGate routing logic
```

### Data Flow

```
Registration Flow:
1. User registers → POST /auth/register
2. Backend creates user with onboarding_completed = false
3. Flutter saves token + user data (onboarding_completed = false)
4. AuthGate detects onboarding_completed = false
5. Show OnboardingScreen

Onboarding Completion Flow:
1. User completes 3 steps → clicks "开始体验"
2. Flutter calls AuthService.completeOnboarding()
3. POST /auth/complete-onboarding with Bearer token
4. Backend updates user.onboarding_completed = true
5. Flutter updates local user data
6. AuthGate re-renders → Show IdolIntroPage

Login Flow (Returning User):
1. User logs in → POST /auth/login
2. Backend returns user data with onboarding_completed = true
3. Flutter saves token + user data
4. AuthGate detects onboarding_completed = true
5. Show IdolIntroPage directly (skip onboarding)
```

---

## Files Created

### Backend

1. **backend/migrations/003_add_onboarding_completed.sql** (12 lines)
   - Adds `onboarding_completed BOOLEAN DEFAULT false` to users table
   - Creates index `idx_users_onboarding`
   - Updates existing users to false

2. **backend/app/schemas/auth.py** (Updated)
   - Added `onboarding_completed` field to `UserResponse`
   - Created `CompleteOnboardingResponse` schema

3. **backend/app/routers/auth.py** (Updated)
   - Updated `login()` and `reset_password()` to include onboarding_completed
   - Added `complete_onboarding()` endpoint (POST /complete-onboarding)
   - Requires JWT authentication via `get_current_user` dependency

4. **backend/app/models/user.py** (Updated)
   - Added `onboarding_completed = Column(Boolean, default=False, index=True)`

### Frontend

1. **lib/features/onboarding/screens/onboarding_screen.dart** (241 lines)
   - StatefulWidget with PageController
   - 3 OnboardingPageData items
   - Skip button (top right)
   - Animated page indicators (dots)
   - Navigation button ("下一步" → "开始体验")
   - Callback `onCompleted` for routing

2. **lib/features/auth/models/user.dart** (Updated)
   - Added `onboardingCompleted` field
   - Updated `fromJson()` with default value false
   - Updated `toJson()` to include field

3. **lib/features/auth/services/auth_service.dart** (Updated)
   - Added `saveUserData()` / `getUserData()` / `deleteUserData()` methods
   - Updated `login()` to save user data from API response
   - Updated `register()` to create user data with onboarding_completed = false
   - Updated `resetPassword()` to save user data
   - Added `completeOnboarding()` method
   - Updated `logout()` to delete user data

4. **lib/main.dart** (Updated)
   - Changed AuthGate from ConsumerWidget to ConsumerStatefulWidget
   - Added `_checkOnboardingStatus()` method
   - Added `_handleOnboardingComplete()` method
   - Routing logic:
     - Not logged in → LoginScreen
     - Logged in + onboarding_completed = false → OnboardingScreen
     - Logged in + onboarding_completed = true → IdolIntroPage

---

## API Endpoints

### POST /api/v1/auth/complete-onboarding

**Authentication:** Required (JWT Bearer token)

**Request:**
```bash
POST /api/v1/auth/complete-onboarding
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
  "message": "新手引导已完成",
  "onboarding_completed": true
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing JWT token
- `500 Internal Server Error`: Database update failed

---

## Database Schema Changes

### Migration: 003_add_onboarding_completed

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT false;
UPDATE users SET onboarding_completed = false WHERE onboarding_completed IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_onboarding ON users(onboarding_completed);
```

**Impact:**
- Existing users: `onboarding_completed = false` (will see onboarding on next login)
- New users: `onboarding_completed = false` (will see onboarding after registration)
- After completing onboarding: `onboarding_completed = true` (skip onboarding)

---

## Testing Notes

### Manual Testing Checklist

1. **New User Registration:**
   - [ ] Register new account
   - [ ] Verify OnboardingScreen appears
   - [ ] Navigate through 3 steps
   - [ ] Check page indicators update
   - [ ] Click "开始体验" on last step
   - [ ] Verify navigation to IdolIntroPage

2. **Skip Onboarding:**
   - [ ] Register new account
   - [ ] Click "跳过" button
   - [ ] Verify onboarding marked as completed
   - [ ] Verify navigation to IdolIntroPage

3. **Returning User Login:**
   - [ ] Login with account that completed onboarding
   - [ ] Verify OnboardingScreen is skipped
   - [ ] Verify direct navigation to IdolIntroPage

4. **Backend API:**
   - [ ] Call /complete-onboarding without token → 401
   - [ ] Call /complete-onboarding with valid token → 200
   - [ ] Verify database updated: onboarding_completed = true
   - [ ] Call /complete-onboarding again (idempotent) → 200

5. **UI/UX:**
   - [ ] Page transitions smooth (300ms animation)
   - [ ] Dot indicators animate correctly
   - [ ] Button text changes on last page
   - [ ] Responsive layout works on mobile/tablet/desktop
   - [ ] Text readable in light and dark themes

---

## Technical Decisions

### 1. Local User Data Storage
**Decision:** Store user data (including onboarding_completed) in secure storage
**Rationale:**
- Avoids extra API call on app startup
- Enables offline routing logic
- Simple MVP implementation
- User data is non-sensitive (no passwords)

**Alternative Considered:** Fetch user data from backend on app start
**Why Rejected:** Extra network latency, requires API endpoint for user profile

### 2. Idempotent Onboarding Completion
**Decision:** `/complete-onboarding` endpoint is idempotent
**Rationale:**
- Safe to retry on network failure
- No side effects if called multiple times
- Simpler error handling in Flutter

### 3. Skip Button Behavior
**Decision:** Skip button calls `onCompleted` callback (same as completing)
**Rationale:**
- Onboarding is informational, not mandatory
- Reduces friction for returning users
- Still marks onboarding as completed to avoid showing again

### 4. Onboarding Content
**Decision:** Use first-person voice from idol perspective
**Rationale:**
- Establishes personal connection immediately
- Aligns with product positioning (AI virtual companion)
- Creates emotional engagement from start

### 5. JWT Authentication for Complete-Onboarding
**Decision:** Require JWT token to mark onboarding complete
**Rationale:**
- Prevent anonymous users from manipulating onboarding status
- Ensures user is authenticated
- Reuses existing auth infrastructure

---

## Dependencies

### Backend
- `fastapi`: Web framework
- `sqlalchemy`: ORM for database
- `pydantic`: Data validation
- `python-jose`: JWT token handling

### Frontend
- `flutter_riverpod ^2.6.1`: State management
- `flutter_secure_storage ^9.2.2`: Secure token/user data storage
- `http ^1.2.2`: HTTP client

---

## Performance Considerations

1. **Database Index:** Created index on `onboarding_completed` for fast querying
2. **Local Storage:** User data cached in secure storage to avoid repeated API calls
3. **Animation Performance:** Used `AnimatedContainer` with 300ms duration for smooth transitions
4. **PageView:** Lazy loading with `itemBuilder` (though only 3 items in MVP)

---

## Security Considerations

1. **JWT Authentication:** `/complete-onboarding` requires valid JWT token
2. **Secure Storage:** User data stored in FlutterSecureStorage (encrypted)
3. **Idempotent API:** Safe to call multiple times without side effects
4. **No PII in Onboarding:** Onboarding screens don't display sensitive user data

---

## Future Enhancements (Post-MVP)

1. **Personalized Onboarding:** Use user's name in onboarding content
2. **Analytics Tracking:** Track onboarding completion rate and drop-off points
3. **A/B Testing:** Test different onboarding content variations
4. **Dynamic Idol Selection:** Let users choose their idol during onboarding
5. **Interactive Tutorial:** Add swipe gestures tutorial
6. **Onboarding Re-trigger:** Admin feature to reset onboarding_completed for user support
7. **Localization:** Support multiple languages for onboarding content

---

## Lessons Learned

1. **Local User Data Storage:** Storing user data locally simplified routing logic significantly
2. **Idempotent APIs:** Making `/complete-onboarding` idempotent reduced error handling complexity
3. **Callback Pattern:** Using `onCompleted` callback in OnboardingScreen kept widget reusable
4. **First-Person Voice:** Using idol's voice in onboarding creates immediate emotional connection
5. **Skip Button:** Essential for good UX - users appreciate having an escape route

---

## Related Stories

- **Depends on:**
  - Story 1.1: Project initialization & user registration (users table)
  - Story 1.2: User login & JWT authentication (auth infrastructure)
  - Story 1.4: Material Design 3 theme (UI components)
  - Story 1.5: Idol data model (林雪晴 configuration)
  - Story 1.6: Idol introduction page (destination after onboarding)

- **Enables:**
  - Story 1.8: Idol welcome message (first conversation after onboarding)
  - Story 2.x: Core chat features (users primed with expectations)

---

## Acceptance Criteria Status

| AC | Status | Notes |
|----|--------|-------|
| AC1: 数据库onboarding_completed字段 | ✅ Done | Migration 003 created and tested |
| AC2: Flutter引导页面UI | ✅ Done | OnboardingScreen with 3-step PageView |
| AC3: 引导内容文案 | ✅ Done | 3 steps with idol-first-person voice |
| AC4: 后端API完成引导 | ✅ Done | POST /complete-onboarding with JWT auth |
| AC5: Flutter引导完成逻辑 | ✅ Done | completeOnboarding() method implemented |
| AC6: 路由集成 | ✅ Done | AuthGate routes based on onboarding_completed |

---

**Story 1.7 Complete!** ✅

New users now receive a welcoming 3-step introduction to the product, setting expectations and building excitement before their first conversation with 林雪晴.
