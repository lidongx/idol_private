# Story 1.3: 密码重置流程

Status: completed

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-13

## Story

As a **注册用户**,
I want **在忘记密码时能够通过手机验证码重置密码**,
so that **我可以重新获得账号访问权限，无需联系客服**。

## Acceptance Criteria

### AC1: 发送密码重置验证码
- **Given** 用户在登录页面点击"忘记密码"
- **When** 用户输入已注册的手机号并点击"发送验证码"
- **Then** 系统发送6位验证码到手机（MVP阶段控制台输出）
- **And** 验证码有效期10分钟
- **And** 按钮变为倒计时状态（60秒）
- **And** 显示验证码输入框

**Edge Cases:**
- 未注册手机号 → 提示"该手机号未注册，请先注册"
- 60秒内重复发送 → 禁用按钮，显示倒计时
- 验证码发送失败 → 显示错误提示，允许重试

### AC2: 验证码校验并进入重置页面
- **Given** 用户已收到验证码
- **When** 用户输入6位验证码并点击"下一步"
- **Then** 跳转到设置新密码页面
- **And** 显示当前操作的手机号

**Edge Cases:**
- 验证码输入不足6位 → 前端提示"请输入6位验证码"
- 验证码为空 → 表单验证失败

### AC3: 设置新密码并自动登录
- **Given** 用户在重置密码页面
- **When** 用户输入新密码和确认密码，满足强度要求，点击"确认重置"
- **Then** 系统更新数据库密码（bcrypt哈希）
- **And** 自动登录（返回JWT token）
- **And** 显示"密码重置成功！已自动登录"
- **And** 跳转到登录页面（清空导航栈）

**密码强度要求:**
- 至少8位
- 包含字母（大小写均可）
- 包含数字

**Edge Cases:**
- 两次密码输入不一致 → 提示"两次输入的密码不一致"
- 密码不符合强度要求 → 表单验证失败，显示具体规则
- 验证码错误或已过期（后端校验）→ 提示"验证码错误或已过期"
- 手机号未注册（后端校验）→ 提示"该手机号未注册"
- 后端错误 → 提示"密码重置失败，请稍后重试"

---

## Implementation Details

### Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌────────────┐
│  LoginScreen    │         │ ForgotPassword   │         │   Reset    │
│                 │ "忘记   │   Screen         │  验证码  │  Password  │
│ [忘记密码？]   │─────────→│                  │─────────→│  Screen    │
│                 │         │ • 输入手机号     │         │            │
└─────────────────┘         │ • 发送验证码     │         │ • 设置新   │
                            │ • 60s倒计时      │         │   密码     │
                            │ • 输入验证码     │         │ • 自动登录 │
                            └──────────────────┘         └────────────┘
                                     │                           │
                                     ▼                           ▼
                            ┌──────────────────┐         ┌────────────┐
                            │  AuthService     │         │  Redis     │
                            │                  │         │            │
                            │ • sendForgot     │────────→│ pwd:reset: │
                            │   PasswordCode() │         │  {phone}   │
                            │ • resetPassword()│         │ (10 min)   │
                            └──────────────────┘         └────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Backend API     │
                            │                  │
                            │ POST /forgot-    │
                            │   password       │
                            │ POST /reset-     │
                            │   password       │
                            └──────────────────┘
```

### Backend Implementation

#### 1. API Endpoints

**POST /api/v1/auth/forgot-password**

Request:
```json
{
  "phone": "13800138000"
}
```

Response (200 OK):
```json
{
  "message": "重置密码验证码已发送",
  "expires_in": 600
}
```

Error Responses:
- 400: 手机号未注册
- 400: 验证码发送过于频繁（60秒限制）
- 500: 验证码存储失败或发送失败

**POST /api/v1/auth/reset-password**

Request:
```json
{
  "phone": "13800138000",
  "verification_code": "123456",
  "new_password": "NewPass123"
}
```

Response (200 OK) - 自动登录:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": 1,
    "phone": "13800138000",
    "subscription_tier": "free"
  }
}
```

Error Responses:
- 400: 验证码错误或已过期
- 400: 手机号未注册
- 400: 密码强度不符合要求（Pydantic验证）
- 500: 数据库更新失败

#### 2. Redis Key Pattern

**密码重置验证码:**
```
Key:    pwd:reset:{phone}
Value:  123456 (6-digit code)
TTL:    600 seconds (10 minutes)
```

**发送频率限制:**
```
Key:    sms:ratelimit:{phone}
Value:  "1"
TTL:    60 seconds
```

**与注册验证码的区别:**
- 注册验证码: `sms:verify:{phone}` (5分钟)
- 密码重置验证码: `pwd:reset:{phone}` (10分钟)
- 不同的Redis key避免冲突

#### 3. SMS Service Functions

新增函数 in `backend/app/services/sms_service.py`:

```python
def store_password_reset_code(phone: str, code: str, ttl: int = 600) -> bool:
    """Store password reset verification code in Redis"""

def verify_password_reset_code(phone: str, input_code: str) -> bool:
    """Verify password reset code from Redis (one-time use)"""
```

**一次性使用机制:**
- 验证成功后自动删除Redis中的验证码
- 防止重放攻击

#### 4. Security Considerations

**密码哈希:**
- 使用bcrypt (rounds=12)
- 与注册时相同的`hash_password()`函数
- 更新数据库中的`password_hash`字段

**自动登录机制:**
- 重置成功后立即生成JWT token
- Token有效期7天
- 用户体验优化：避免重置后再次输入密码

**验证码安全:**
- 10分钟过期时间
- 一次性使用（验证后删除）
- 60秒发送频率限制

### Frontend Implementation

#### 1. Screen Flow

**Step 1: ForgotPasswordScreen**
- 路径: `lib/features/auth/screens/forgot_password_screen.dart`
- 功能:
  - 输入手机号（11位，中国手机号验证）
  - 发送验证码按钮 + 60秒倒计时
  - 验证码输入框（发送后显示）
  - 重新发送验证码
  - "下一步"按钮（输入验证码后）

**Step 2: ResetPasswordScreen**
- 路径: `lib/features/auth/screens/reset_password_screen.dart`
- 功能:
  - 显示当前操作的手机号
  - 新密码输入（密码强度验证）
  - 确认密码输入（一致性校验）
  - 密码可见性切换
  - "确认重置"按钮

**Navigation:**
```dart
// LoginScreen → ForgotPasswordScreen
Navigator.push(context, MaterialPageRoute(
  builder: (context) => const ForgotPasswordScreen()
));

// ForgotPasswordScreen → ResetPasswordScreen
Navigator.push(context, MaterialPageRoute(
  builder: (context) => ResetPasswordScreen(
    phone: phone,
    verificationCode: code,
  )
));

// ResetPasswordScreen → 返回登录（清空导航栈）
Navigator.of(context).popUntil((route) => route.isFirst);
```

#### 2. AuthService Methods

新增方法 in `lib/features/auth/services/auth_service.dart`:

```dart
/// Send forgot password verification code
Future<bool> sendForgotPasswordCode(String phone) async {
  final response = await http.post(
    Uri.parse('$_baseUrl/forgot-password'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'phone': phone}),
  );
  // Handle response...
}

/// Reset password with verification code
/// Returns login response with token and user info (auto-login)
Future<Map<String, dynamic>> resetPassword({
  required String phone,
  required String verificationCode,
  required String newPassword,
}) async {
  final response = await http.post(
    Uri.parse('$_baseUrl/reset-password'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'phone': phone,
      'verification_code': verificationCode,
      'new_password': newPassword,
    }),
  );
  // Save token, return data...
}
```

#### 3. UI/UX Highlights

**Material Design 3:**
- Icon: `Icons.lock_reset` (ForgotPassword), `Icons.vpn_key` (ResetPassword)
- Color: Orange theme for password reset
- Form validation with real-time feedback

**User Feedback:**
- ✅ 验证码已发送提示（SnackBar）
- ✅ 倒计时显示（60s, 59s, 58s...）
- ✅ 密码重置成功提示 + 自动登录说明
- ❌ 详细的错误提示（验证码错误、密码不一致等）

**State Management:**
- Riverpod `authLoadingProvider` for loading states
- Riverpod `userProvider` for user info after auto-login
- Local state for countdown timer

---

## Files Modified/Created

### Backend Files

**Modified:**
1. `backend/app/routers/auth.py`
   - Added `POST /forgot-password` endpoint (lines 229-287)
   - Added `POST /reset-password` endpoint (lines 290-362)

2. `backend/app/services/sms_service.py`
   - Added `store_password_reset_code()` function (lines 148-166)
   - Added `verify_password_reset_code()` function (lines 169-195)

3. `backend/app/schemas/auth.py`
   - Added `ForgotPasswordRequest` schema (lines 97-107)
   - Added `ResetPasswordRequest` schema (lines 110-142)

### Frontend Files

**Created:**
1. `lib/features/auth/screens/forgot_password_screen.dart` (268 lines)
   - Complete verification code flow
   - 60-second countdown timer
   - Phone input → Code input → Next button

2. `lib/features/auth/screens/reset_password_screen.dart` (224 lines)
   - New password + confirm password inputs
   - Password strength validation
   - Auto-login after successful reset

**Modified:**
3. `lib/features/auth/services/auth_service.dart`
   - Added `sendForgotPasswordCode()` method (lines 118-142)
   - Added `resetPassword()` method (lines 144-183)

4. `lib/features/auth/screens/login_screen.dart`
   - Added import for ForgotPasswordScreen (line 7)
   - Updated `_navigateToForgotPassword()` to actual navigation (lines 101-107)

---

## Implementation Success Criteria

**Story完成标准:**
- ✅ 所有Acceptance Criteria通过验证
- ✅ Backend API endpoints implemented and tested
- ✅ Redis verification code storage with 10-minute TTL
- ✅ Frontend screens created with complete UI/UX
- ✅ AuthService methods integrated with backend APIs
- ✅ Login screen links to ForgotPasswordScreen
- ✅ Password validation matches backend requirements
- ✅ Auto-login after successful password reset
- ✅ Error handling for all edge cases
- ✅ Countdown timer and rate limiting working correctly

**Technical Validation:**
- ✅ Redis keys: `pwd:reset:{phone}` (10 min) vs `sms:verify:{phone}` (5 min)
- ✅ Password hashing with bcrypt (rounds=12)
- ✅ JWT token generation and secure storage
- ✅ Form validation with RegExp for phone and password
- ✅ One-time verification code usage (deleted after verification)
- ✅ 60-second rate limiting for resend

**Definition of Done:**
- All backend endpoints return correct responses
- Frontend flow tested: Login → Forgot → Code → Reset → Auto-login
- No critical bugs or edge cases unhandled
- Code follows architecture standards (Riverpod, Material Design 3)
- Documentation updated (this file)

---

## Testing Guide

### Manual Testing Steps

**Happy Path:**
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && flutter run`
3. Login screen → Click "忘记密码？"
4. Enter registered phone (e.g., 13800138000) → Click "发送验证码"
5. Check console for verification code (MVP stage)
6. Enter 6-digit code → Click "下一步"
7. Enter new password (e.g., "NewPass123") → Confirm password
8. Click "确认重置"
9. Verify: Success message + Auto-login + Redirect to login screen

**Edge Cases to Test:**
1. **Unregistered phone:**
   - Enter unregistered phone → Send code
   - Expected: "该手机号未注册，请先注册"

2. **Rate limiting:**
   - Send code → Wait < 60s → Try to resend
   - Expected: Button disabled with countdown

3. **Wrong verification code:**
   - Enter phone → Send code → Enter wrong code → Reset password
   - Expected: "验证码错误或已过期"

4. **Password mismatch:**
   - Enter different passwords in two fields
   - Expected: "两次输入的密码不一致"

5. **Weak password:**
   - Enter password < 8 chars or no letters/numbers
   - Expected: Form validation error with specific rule

6. **Expired verification code:**
   - Send code → Wait 10+ minutes → Reset password
   - Expected: "验证码错误或已过期"

### Backend Verification

```bash
# Send forgot password code
curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000"}'

# Check Redis
redis-cli GET "pwd:reset:13800138000"

# Reset password
curl -X POST http://localhost:8000/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "verification_code": "123456",
    "new_password": "NewPass123"
  }'

# Verify auto-login (token returned)
# Verify password updated in database
psql -U idol_user -d idol_db -c "SELECT phone, password_hash FROM users WHERE phone='13800138000';"
```

---

## References

**Architecture文档:**
- [Technology Stack - Backend] `_bmad-output/planning-artifacts/architecture.md` Lines 451-470
- [Security Requirements] `architecture.md` Lines 900-950
- [JWT Configuration] `architecture.md` Lines 920-935

**Epics文档:**
- [Story 1.3 Full Spec] `_bmad-output/planning-artifacts/epics.md` Lines 1900-2050
- [Epic 1 Overview] `epics.md` Lines 1631-1641

**PRD文档:**
- [FR8-FR9: 密码重置] `_bmad-output/planning-artifacts/prd.md` (密码管理功能需求)
- [NFR-S1-S4: 安全需求] `prd.md` (密码哈希、JWT安全)

**Related Stories:**
- [Story 1.1: 项目初始化与用户注册] `1-1-project-init-user-registration.md`
- [Story 1.2: 用户登录与JWT认证] (implementation artifact to be created)

---

## Dev Agent Record

### Agent Model Used
Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Implementation Timeline
- **Start:** 2026-01-13 (continuing from Story 1.2)
- **Completion:** 2026-01-13 (same day)
- **Total Duration:** ~1 day

### Key Implementation Decisions

1. **Separate Redis Keys for Different Verification Types:**
   - Registration: `sms:verify:{phone}` (300s)
   - Password Reset: `pwd:reset:{phone}` (600s)
   - Rationale: Avoid key conflicts, different TTL requirements

2. **Auto-Login After Reset:**
   - Backend returns full `LoginResponse` including JWT token
   - Frontend saves token to secure storage immediately
   - Updates `userProvider` with user info
   - UX benefit: User doesn't need to login again after reset

3. **Two-Step Frontend Flow:**
   - Step 1: Send code + verify code on same screen
   - Step 2: Set new password on separate screen
   - Rationale: Clear separation of concerns, better UX

4. **One-Time Verification Code:**
   - Code deleted from Redis after successful verification
   - Prevents replay attacks
   - User must request new code if verification fails

### Completion Notes

**What went well:**
- Clean integration with existing auth infrastructure
- Reused SMS service and security functions
- Consistent error handling with other auth endpoints
- Material Design 3 UI matches existing screens

**Implementation highlights:**
- All 3 Acceptance Criteria fully implemented
- 10+ edge cases handled with proper error messages
- Password validation consistent between frontend and backend
- Rate limiting and TTL correctly configured

**No blockers encountered during implementation**

---

## 🎯 Story 1.3 Status: ✅ COMPLETED

**Ready for testing and Story 1.4 implementation!**

开发工作已完成，密码重置功能已完全集成到应用中。用户现在可以通过手机验证码安全地重置密码，并在重置成功后自动登录。所有安全要求和用户体验优化均已实现。

**Next Story:** Story 1.4 - Material Design 3 主题与UI框架
