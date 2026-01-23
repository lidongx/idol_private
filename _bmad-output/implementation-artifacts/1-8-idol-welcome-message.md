# Story 1.8: 偶像主动欢迎消息

Status: completed

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-13

## Story

As a **新用户**,
I want **收到偶像的第一条欢迎消息**,
So that **我感受到"她在等我"的温暖，愿意开始对话**。

## Acceptance Criteria

### AC1: 数据库表创建
- **Given** 数据库基础设施已就绪
- **When** 运行数据库迁移脚本
- **Then** 创建conversations表，包含以下字段：
  - `id`: 主键（自增）
  - `user_id`: 关联用户ID（外键）
  - `idol_id`: 关联偶像ID（外键）
  - `intimacy_level`: 亲密度等级（1-100，默认1）
  - `intimacy_exp`: 亲密度经验值（默认0）
  - `created_at`: 创建时间
  - `last_message_at`: 最后消息时间
  - 唯一约束: (user_id, idol_id)
- **And** 创建messages表，包含以下字段：
  - `id`: 主键（自增）
  - `conversation_id`: 关联对话ID（外键）
  - `sender_type`: 发送者类型（'user' 或 'idol'）
  - `content`: 消息内容
  - `emotion`: 情绪标签（可选）
  - `timestamp`: 发送时间
  - `status`: 消息状态（'sent', 'delivered', 'read'）
- **And** 创建索引以优化查询性能

### AC2: SQLAlchemy ORM模型
- **Given** 数据库表已创建
- **When** 定义Conversation和Message模型类
- **Then** 创建 `backend/app/models/conversation.py`
- **And** 创建 `backend/app/models/message.py`
- **And** 建立关系映射（Conversation.messages）
- **And** 提供`__repr__`方法用于调试

### AC3: Pydantic API Schemas
- **Given** 需要定义API请求和响应格式
- **When** 创建Pydantic schemas
- **Then** 创建 `backend/app/schemas/conversation.py` 包含：
  - `ConversationCreate`: 创建对话请求
  - `ConversationResponse`: 对话响应
  - `ConversationWithWelcomeMessage`: 对话 + 欢迎消息
  - `MessageResponse`: 消息响应
  - `SendMessageRequest`: 发送消息请求
  - `ErrorResponse`: 错误响应

### AC4: 欢迎消息生成逻辑
- **Given** 用户创建新对话
- **When** 系统生成欢迎消息
- **Then** 根据时间段返回不同消息：
  - 早上（6:00-12:00）："早上好呀~我是雪晴，很高兴遇见你。今天想聊些什么呢？"
  - 下午（12:00-18:00）："下午好~我是雪晴，你的专属陪伴者。有什么想和我分享的吗？"
  - 晚上（18:00-24:00）："晚上好呀~我是雪晴。今天过得怎么样？来和我聊聊吧~"
  - 深夜（0:00-6:00）："这么晚还没睡呀？我是雪晴，陪你聊聊天吧~"
- **And** 欢迎消息不计入亲密度经验值
- **And** 不消耗免费用户的每日消息配额

### AC5: 后端API端点
- **Given** 用户已登录（JWT token有效）
- **When** 调用创建对话API
- **Then** 创建 `POST /api/v1/conversations` 端点
- **And** 验证JWT认证
- **And** 验证偶像存在且激活
- **And** 检查对话是否已存在（返回409）
- **And** 创建对话记录
- **And** 生成并保存欢迎消息
- **And** 返回对话信息和欢迎消息

### AC6: Flutter数据模型
- **Given** 前端需要处理对话和消息数据
- **When** 创建Flutter数据模型
- **Then** 创建 `lib/features/conversation/models/conversation.dart`
- **And** 创建 `lib/features/conversation/models/message.dart`
- **And** 实现`fromJson`和`toJson`方法
- **And** 实现`copyWith`、`==`和`hashCode`

### AC7: Flutter ConversationService
- **Given** 前端需要调用对话API
- **When** 创建ConversationService
- **Then** 创建 `lib/features/conversation/services/conversation_service.dart`
- **And** 实现`createConversation()`方法
- **And** 实现`getConversation()`方法
- **And** 处理JWT认证和错误响应

---

## Implementation Details

### Architecture Overview

```
Backend Architecture:
backend/
├── migrations/
│   └── 004_create_conversations_messages_tables.sql  # Database tables
├── app/
│   ├── models/
│   │   ├── conversation.py                           # Conversation ORM model
│   │   └── message.py                                # Message ORM model
│   ├── schemas/
│   │   └── conversation.py                           # Pydantic schemas
│   ├── services/
│   │   └── welcome_service.py                        # Welcome message logic
│   ├── routers/
│   │   └── conversation.py                           # Conversation API endpoints
│   └── main.py                                       # Register conversation router

Frontend Architecture:
lib/
├── features/
│   └── conversation/
│       ├── models/
│       │   ├── conversation.dart                     # Conversation data model
│       │   └── message.dart                          # Message data model
│       └── services/
│           └── conversation_service.dart              # Conversation API service
```

### Data Flow

```
User Flow:
1. User completes onboarding (Story 1.7)
2. User navigates to Idol Intro Page (Story 1.6)
3. User clicks "开始对话" button
4. Frontend calls ConversationService.createConversation(idolId)
5. Backend creates conversation record
6. Backend generates time-based welcome message
7. Backend saves message to database
8. Backend returns conversation + welcome message
9. Frontend navigates to Chat Page (Epic 2)
10. Chat Page displays welcome message with typing animation
```

---

## Files Created

### Backend

1. **backend/migrations/004_create_conversations_messages_tables.sql** (42 lines)
   - Creates `conversations` table with intimacy tracking
   - Creates `messages` table with sender_type and emotion
   - Creates indexes for performance optimization
   - Adds constraints (unique user_idol pair, check constraints)

2. **backend/app/models/conversation.py** (31 lines)
   - Conversation ORM model
   - Relationship to Message model
   - Unique constraint on (user_id, idol_id)

3. **backend/app/models/message.py** (27 lines)
   - Message ORM model
   - Relationship to Conversation model
   - Sender type ('user' or 'idol')

4. **backend/app/models/__init__.py** (Updated)
   - Added Conversation and Message imports

5. **backend/app/schemas/conversation.py** (92 lines)
   - MessageBase, MessageResponse
   - ConversationCreate, ConversationResponse
   - ConversationWithWelcomeMessage
   - SendMessageRequest, SendMessageResponse
   - ErrorResponse

6. **backend/app/services/welcome_service.py** (30 lines)
   - `get_welcome_message(hour)` function
   - Time-based message selection (4 time periods)

7. **backend/app/routers/conversation.py** (162 lines)
   - POST /api/v1/conversations (create conversation)
   - GET /api/v1/conversations/{id} (get conversation details)
   - JWT authentication required
   - Comprehensive error handling

8. **backend/app/main.py** (Updated)
   - Registered conversation router with /api/v1 prefix

### Frontend

1. **lib/features/conversation/models/message.dart** (89 lines)
   - Message data model
   - `isFromUser` and `isFromIdol` getters
   - Full JSON serialization and equality

2. **lib/features/conversation/models/conversation.dart** (80 lines)
   - Conversation data model
   - Intimacy level and experience fields
   - Full JSON serialization and equality

3. **lib/features/conversation/services/conversation_service.dart** (104 lines)
   - `createConversation(idolId)` method
   - `getConversation(conversationId)` method
   - JWT authentication integration
   - Error handling and response parsing

---

## API Endpoints

### POST /api/v1/conversations

**Authentication:** Required (JWT Bearer token)

**Request:**
```json
{
  "idol_id": 1
}
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 123,
  "idol_id": 1,
  "intimacy_level": 1,
  "intimacy_exp": 0,
  "created_at": "2026-01-13T10:00:00Z",
  "last_message_at": "2026-01-13T10:00:00Z",
  "welcome_message": {
    "id": 1,
    "conversation_id": 1,
    "sender_type": "idol",
    "content": "早上好呀~我是雪晴，很高兴遇见你。今天想聊些什么呢？",
    "emotion": "happy",
    "timestamp": "2026-01-13T10:00:00Z",
    "status": "delivered"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Idol not found or inactive
- `401 Unauthorized`: Invalid or missing JWT token
- `409 Conflict`: Conversation already exists
- `500 Internal Server Error`: Database error

### GET /api/v1/conversations/{conversation_id}

**Authentication:** Required (JWT Bearer token)

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 123,
  "idol_id": 1,
  "intimacy_level": 1,
  "intimacy_exp": 0,
  "created_at": "2026-01-13T10:00:00Z",
  "last_message_at": "2026-01-13T10:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing JWT token
- `404 Not Found`: Conversation not found or not owned by user

---

## Database Schema Changes

### Migration: 004_create_conversations_messages_tables

**Conversations Table:**
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    idol_id INTEGER NOT NULL REFERENCES idols(id) ON DELETE CASCADE,
    intimacy_level INTEGER DEFAULT 1 CHECK (intimacy_level >= 1 AND intimacy_level <= 100),
    intimacy_exp INTEGER DEFAULT 0 CHECK (intimacy_exp >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_idol UNIQUE(user_id, idol_id)
);
```

**Messages Table:**
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('user', 'idol')),
    content TEXT NOT NULL,
    emotion VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'read'))
);
```

**Indexes:**
- `idx_conversations_user` on `conversations(user_id)`
- `idx_conversations_last_message` on `conversations(last_message_at DESC)`
- `idx_messages_conversation` on `messages(conversation_id)`
- `idx_messages_timestamp` on `messages(timestamp DESC)`

---

## Testing Notes

### Manual Testing Checklist

1. **Database Migration:**
   - [ ] Run migration successfully
   - [ ] Verify tables created
   - [ ] Verify indexes created
   - [ ] Verify constraints work (try duplicate user_idol pair)

2. **Welcome Message Generation:**
   - [ ] Test morning message (6:00-12:00)
   - [ ] Test afternoon message (12:00-18:00)
   - [ ] Test evening message (18:00-24:00)
   - [ ] Test late night message (0:00-6:00)

3. **API Endpoint - Create Conversation:**
   - [ ] Call without JWT token → 401
   - [ ] Call with invalid idol_id → 400
   - [ ] Call first time → 200 with conversation + welcome_message
   - [ ] Call second time (same idol) → 409
   - [ ] Verify message saved to database
   - [ ] Verify conversation saved with correct user_id and idol_id

4. **API Endpoint - Get Conversation:**
   - [ ] Call without JWT token → 401
   - [ ] Call with invalid conversation_id → 404
   - [ ] Call with another user's conversation_id → 404
   - [ ] Call with valid conversation_id → 200

5. **Flutter Integration:**
   - [ ] ConversationService.createConversation() returns data correctly
   - [ ] ConversationService.getConversation() returns data correctly
   - [ ] Error handling displays appropriate messages
   - [ ] JWT token automatically included in requests

---

## Technical Decisions

### 1. Time-Based Welcome Messages
**Decision:** Generate different welcome messages based on time of day
**Rationale:**
- Enhances realism and personal connection
- Shows idol is "aware" of user's context
- Simple implementation with clear time boundaries
- No AI generation needed for first message (faster, cheaper)

**Implementation:**
- 4 time periods: morning, afternoon, evening, late night
- Hard-coded messages in welcome_service.py
- Easy to localize or customize per idol in future

### 2. Unique Constraint on (user_id, idol_id)
**Decision:** One conversation per user-idol pair
**Rationale:**
- Simplifies data model for MVP
- All messages between user and idol in single conversation
- Matches mental model of "my relationship with 林雪晴"
- Can be relaxed in future if multi-conversation feature needed

### 3. Intimacy Tracking in Conversations Table
**Decision:** Store intimacy_level and intimacy_exp in conversations table
**Rationale:**
- Enables Epic 5 (Intimacy System) without schema migration
- Level and exp are conversation-specific metrics
- Efficient queries (no joins needed)
- Supports future features (unlock content at level X)

### 4. Emotion Field in Messages
**Decision:** Optional `emotion` field on messages
**Rationale:**
- Enables Epic 2.3 (Emotion Recognition)
- Supports UI enhancements (emoji reactions, tone-based styling)
- Nullable for MVP (not all messages have detected emotion)
- Simple string field (no complex emotion model needed)

### 5. Message Status Tracking
**Decision:** Add `status` field ('sent', 'delivered', 'read')
**Rationale:**
- Common messaging app pattern
- Enables read receipts feature
- Supports offline message queue (sent → delivered transition)
- Simple enum validation with CHECK constraint

### 6. Cascade Deletes
**Decision:** ON DELETE CASCADE for all foreign keys
**Rationale:**
- User deletion → conversations deleted → messages deleted
- Idol deactivation → conversations deleted (data cleanup)
- Simplifies data management
- Matches user expectation (delete account = delete all data)

---

## Dependencies

### Backend
- `fastapi`: Web framework
- `sqlalchemy`: ORM for database
- `pydantic`: Data validation
- `python-jose`: JWT token handling (from Story 1.2)

### Frontend
- `flutter_riverpod ^2.6.1`: State management
- `http ^1.2.2`: HTTP client
- `flutter_secure_storage ^9.2.2`: JWT token storage

---

## Performance Considerations

1. **Database Indexes:**
   - Conversation queries by user_id (frequent)
   - Message queries by conversation_id (frequent)
   - Last message timestamp for conversation list sorting

2. **Pagination Not Implemented (MVP):**
   - Single conversation, limited messages
   - Epic 2 will add message history pagination

3. **No Message Caching (Yet):**
   - Redis caching will be added in Epic 2 Story 2.2
   - Current: direct database queries

---

## Security Considerations

1. **JWT Authentication:** All conversation endpoints require valid JWT token
2. **User Ownership Validation:** Users can only access their own conversations
3. **Idol Existence Check:** Validates idol_id before creating conversation
4. **SQL Injection Protection:** SQLAlchemy ORM prevents injection attacks
5. **Input Validation:** Pydantic schemas validate all request data
6. **Cascade Deletes:** Data cleanup when user deletes account

---

## Limitations & Future Work

### Current Limitations (MVP):
1. **No Chat UI:** Full chat interface will be implemented in Epic 2
2. **No Message Sending:** User cannot send messages yet (Epic 2 Story 2.1)
3. **No AI Replies:** Only welcome message is generated (Epic 2)
4. **No Message History:** No pagination or history loading (Epic 2 Story 2.8)
5. **No Typing Animation:** Will be added in Epic 2
6. **Single Idol Only:** MVP hardcodes idol_id = 1

### Future Enhancements (Post-MVP):
1. **Multi-Conversation Support:** Allow multiple conversations per user-idol pair
2. **Message Search:** Full-text search across message history
3. **Message Reactions:** Like/love specific messages
4. **Voice Messages:** Audio message support (Epic 2.5)
5. **Image Messages:** Photo sharing (Epic 2.6)
6. **Message Editing:** Edit sent messages within 5 minutes
7. **Message Deletion:** Delete individual messages
8. **Conversation Archiving:** Hide old conversations

---

## Lessons Learned

1. **Time-Based Logic:** Simple time-based welcome messages effective for MVP
2. **Database Design:** Planning for future features (emotion, intimacy) saved migration effort
3. **Cascade Deletes:** Simplifies data lifecycle management significantly
4. **Unique Constraints:** Prevents duplicate conversations, simplifies business logic
5. **API Design:** Returning conversation + message together reduces round trips

---

## Related Stories

- **Depends on:**
  - Story 1.1: User registration (users table)
  - Story 1.2: JWT authentication (auth infrastructure)
  - Story 1.5: Idol data model (idols table)
  - Story 1.6: Idol introduction page (entry point)
  - Story 1.7: Onboarding (user funnel)

- **Enables:**
  - Story 2.1: Basic text conversation (builds on message infrastructure)
  - Story 2.2: Multi-turn context management (uses conversation history)
  - Story 2.8: Conversation history (loads messages)
  - Epic 5: Intimacy system (uses intimacy_level/exp fields)

---

## Acceptance Criteria Status

| AC | Status | Notes |
|----|--------|-------|
| AC1: 数据库表创建 | ✅ Done | conversations + messages tables with indexes |
| AC2: SQLAlchemy ORM模型 | ✅ Done | Conversation and Message models with relationships |
| AC3: Pydantic API Schemas | ✅ Done | Complete schemas for requests/responses |
| AC4: 欢迎消息生成逻辑 | ✅ Done | Time-based welcome messages (4 periods) |
| AC5: 后端API端点 | ✅ Done | POST /conversations, GET /conversations/{id} |
| AC6: Flutter数据模型 | ✅ Done | Conversation and Message models |
| AC7: Flutter ConversationService | ✅ Done | API service with createConversation() method |

---

**Story 1.8 Complete!** ✅

**Epic 1 Complete!** 🎉

All 8 stories in Epic 1 (First User Experience) have been successfully implemented. Users can now:
- Register and login ✅
- Reset forgotten passwords ✅
- Experience Material Design 3 UI ✅
- View idol information ✅
- Complete onboarding ✅
- Receive welcome message from idol ✅

**Next Step:** Epic 2 - AI Conversation Core (implement full chat functionality with AI replies)
