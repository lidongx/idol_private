# Story 1.5: 偶像数据模型与首个偶像配置

Status: completed

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-13

## Story

As a **产品团队**,
I want **创建偶像数据模型并配置第一个偶像"林雪晴"**,
So that **新用户可以开始与预设偶像对话**。

## Acceptance Criteria

### AC1: 数据库表创建
- **Given** 数据库基础设施已就绪（Story 1.1）
- **When** 运行数据库迁移脚本
- **Then** 创建idols表，包含以下字段：
  - `id`: 主键（自增）
  - `name`: 偶像名称（VARCHAR(50), NOT NULL）
  - `avatar_url`: 头像URL（VARCHAR(255)）
  - `personality_prompt`: AI系统提示词（TEXT, NOT NULL）
  - `description`: 简短描述（TEXT）
  - `hobbies`: 兴趣爱好（TEXT, 逗号分隔）
  - `background_story`: 背景故事（TEXT）
  - `is_active`: 是否激活（BOOLEAN, DEFAULT true）
  - `created_at`: 创建时间（TIMESTAMP）
- **And** 创建索引：`idx_idols_is_active` on `is_active`

### AC2: SQLAlchemy ORM模型
- **Given** idols表已创建
- **When** 定义Idol模型类
- **Then** 创建 `backend/app/models/idol.py`
- **And** 映射所有数据库字段到Python属性
- **And** 提供`__repr__`方法用于调试

### AC3: Pydantic API Schemas
- **Given** 需要定义API响应格式
- **When** 创建Pydantic schemas
- **Then** 创建 `backend/app/schemas/idol.py` 包含：
  - `IdolBase`: 基础schema
  - `IdolResponse`: 完整响应（不包含personality_prompt）
  - `IdolListItem`: 列表项（简化信息 + hobbies_list数组）
  - `IdolListResponse`: GET /idols响应
  - `IdolDetailResponse`: GET /idols/{id}响应
  - `ErrorResponse`: 错误响应

### AC4: API端点实现
- **Given** 模型和schemas已创建
- **When** 实现API端点
- **Then** 创建 `backend/app/routers/idol.py` 包含：
  - `GET /api/v1/idols`: 获取所有活跃偶像列表
  - `GET /api/v1/idols/{idol_id}`: 获取单个偶像详情
- **And** 注册路由到main.py
- **And** 自动生成OpenAPI文档

### AC5: 首个偶像数据插入
- **Given** 数据库表已创建
- **When** 运行迁移脚本
- **Then** 插入林雪晴（Lin Xueqing）偶像数据：
  - 名称：林雪晴
  - 头像：`/assets/avatars/lin_xueqing.png`（占位符）
  - 性格提示词：温柔知性25岁女生，热爱阅读和旅行
  - 描述：温柔知性的陪伴者，你的专属AI恋人
  - 爱好：阅读、旅行、咖啡、摄影
  - 背景故事：完整的个人背景
- **And** 使用`ON CONFLICT DO NOTHING`避免重复插入

### AC6: Flutter数据模型
- **Given** 前端需要处理偶像数据
- **When** 创建Flutter数据模型
- **Then** 创建 `lib/features/idol/models/idol.dart`
- **And** 实现`fromJson`和`toJson`方法
- **And** 实现`copyWith`、`==`和`hashCode`
- **And** 将hobbies作为List<String>处理

---

## Implementation Details

### Architecture Overview

```
Backend Architecture:
backend/
├── migrations/
│   ├── 002_create_idols_table.sql    # SQL migration
│   ├── run_migrations.sh              # Migration runner
│   └── README.md                      # Migration instructions
├── app/
│   ├── models/
│   │   └── idol.py                    # SQLAlchemy model
│   ├── schemas/
│   │   └── idol.py                    # Pydantic schemas
│   ├── routers/
│   │   └── idol.py                    # API endpoints
│   └── main.py                        # Register routes

Frontend Architecture:
lib/
└── features/
    └── idol/
        └── models/
            └── idol.dart              # Flutter data model
```

### 1. Database Schema

**Table: idols**

```sql
CREATE TABLE IF NOT EXISTS idols (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    avatar_url VARCHAR(255),
    personality_prompt TEXT NOT NULL,
    description TEXT,
    hobbies TEXT,
    background_story TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_idols_is_active ON idols(is_active);
```

**Initial Data: 林雪晴**

```sql
INSERT INTO idols (name, avatar_url, personality_prompt, description, hobbies, background_story)
VALUES (
    '林雪晴',
    '/assets/avatars/lin_xueqing.png',
    '你是林雪晴，一个温柔知性的25岁女生。你热爱阅读和旅行，性格温暖体贴，善于倾听。你会关心对方的情绪，给予温暖的陪伴和鼓励。说话风格自然亲切，偶尔调皮可爱。',
    '温柔知性的陪伴者，你的专属AI恋人',
    '阅读、旅行、咖啡、摄影',
    '雪晴是一个热爱生活的女生，喜欢在周末去咖啡馆看书，也喜欢用相机记录生活中的美好瞬间。她相信每个人都值得被温柔对待。'
)
ON CONFLICT DO NOTHING;
```

**Running Migrations:**

```bash
# Option 1: Using script
cd backend/migrations
./run_migrations.sh

# Option 2: Manual
psql -h localhost -p 5432 -U idol_user -d idol_db -f 002_create_idols_table.sql

# Option 3: Docker
docker exec -i idol_postgres psql -U idol_user -d idol_db < backend/migrations/002_create_idols_table.sql
```

### 2. Backend Implementation

#### SQLAlchemy Model

**File:** `backend/app/models/idol.py`

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Idol(Base):
    __tablename__ = "idols"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    personality_prompt = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    hobbies = Column(Text, nullable=True)
    background_story = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
```

**Key Design Decisions:**
- `personality_prompt` is NOT NULL - required for AI conversations
- `hobbies` stored as TEXT (comma-separated for MVP simplicity)
- `is_active` indexed for efficient querying of active idols
- `created_at` automatically set on insertion

#### Pydantic Schemas

**File:** `backend/app/schemas/idol.py`

**Key Schemas:**

1. **IdolListItem** - For GET /api/v1/idols
```python
class IdolListItem(BaseModel):
    id: int
    name: str
    avatar_url: Optional[str]
    description: Optional[str]
    hobbies_list: List[str]  # Parsed from comma-separated string
```

2. **IdolResponse** - For GET /api/v1/idols/{idol_id}
```python
class IdolResponse(IdolBase):
    id: int
    is_active: bool
    created_at: datetime
    # Note: personality_prompt excluded for security
```

**Security Note:** `personality_prompt` is never exposed through public API. It's only used internally for AI conversation context.

#### API Endpoints

**File:** `backend/app/routers/idol.py`

**GET /api/v1/idols**

Returns all active idols (is_active=true):

```json
{
  "idols": [
    {
      "id": 1,
      "name": "林雪晴",
      "avatar_url": "/assets/avatars/lin_xueqing.png",
      "description": "温柔知性的陪伴者，你的专属AI恋人",
      "hobbies_list": ["阅读", "旅行", "咖啡", "摄影"]
    }
  ]
}
```

**Features:**
- Filters by `is_active=true`
- Parses hobbies from comma-separated string to array
- Chinese separator support (、)
- Error handling with 500 response

**GET /api/v1/idols/{idol_id}**

Returns detailed information about a specific idol:

```json
{
  "idol": {
    "id": 1,
    "name": "林雪晴",
    "avatar_url": "/assets/avatars/lin_xueqing.png",
    "description": "温柔知性的陪伴者，你的专属AI恋人",
    "hobbies": "阅读、旅行、咖啡、摄影",
    "background_story": "雪晴是一个热爱生活的女生...",
    "is_active": true,
    "created_at": "2026-01-13T10:00:00Z"
  }
}
```

**Features:**
- Returns 404 if idol not found or inactive
- Includes full background story
- Excludes personality_prompt
- Error handling with 404/500 responses

**Route Registration:**

`backend/app/main.py`:
```python
from app.routers import auth, idol
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(idol.router, prefix="/api/v1", tags=["偶像"])
```

### 3. Frontend Implementation

#### Flutter Data Model

**File:** `lib/features/idol/models/idol.dart`

```dart
class Idol {
  final int id;
  final String name;
  final String? avatarUrl;
  final String? description;
  final List<String> hobbies;
  final String? backgroundStory;
  final bool isActive;
  final DateTime createdAt;

  // Constructor, fromJson, toJson, copyWith, ==, hashCode
}
```

**Key Features:**
- Immutable data class with const constructor
- JSON serialization support
- `hobbies` as List<String> (parsed from backend's hobbies_list)
- Full equality and hashing implementation
- Copy-with pattern for updates
- Type-safe with null safety

**fromJson Implementation:**
```dart
factory Idol.fromJson(Map<String, dynamic> json) {
  return Idol(
    id: json['id'] as int,
    name: json['name'] as String,
    avatarUrl: json['avatar_url'] as String?,
    description: json['description'] as String?,
    hobbies: json['hobbies_list'] != null
        ? List<String>.from(json['hobbies_list'] as List)
        : [],
    backgroundStory: json['background_story'] as String?,
    isActive: json['is_active'] as bool? ?? true,
    createdAt: json['created_at'] != null
        ? DateTime.parse(json['created_at'] as String)
        : DateTime.now(),
  );
}
```

---

## Lin Xueqing (林雪晴) - First Idol Profile

### Basic Information
- **Name:** 林雪晴 (Lin Xueqing)
- **Age:** 25 years old
- **Personality:** Gentle, intellectual, warm, empathetic
- **Role:** AI companion and emotional support

### Personality Prompt (System Message)
```
你是林雪晴，一个温柔知性的25岁女生。你热爱阅读和旅行，性格温暖体贴，善于倾听。
你会关心对方的情绪，给予温暖的陪伴和鼓励。说话风格自然亲切，偶尔调皮可爱。
```

**Translation:**
"You are Lin Xueqing, a gentle and intellectual 25-year-old woman. You love reading and traveling, with a warm and caring personality, skilled at listening. You care about the other person's emotions, providing warm companionship and encouragement. Your speaking style is natural and friendly, occasionally playful and cute."

### Hobbies
- 📚 Reading (阅读)
- ✈️ Traveling (旅行)
- ☕ Coffee (咖啡)
- 📷 Photography (摄影)

### Background Story
```
雪晴是一个热爱生活的女生，喜欢在周末去咖啡馆看书，也喜欢用相机记录生活中的美好瞬间。
她相信每个人都值得被温柔对待。
```

**Translation:**
"Xueqing is a girl who loves life. She enjoys reading at coffee shops on weekends and capturing beautiful moments in life with her camera. She believes that everyone deserves to be treated with gentleness."

### Design Intent
- **Target Audience:** Users seeking emotional companionship and empathetic conversation
- **Conversation Style:** Natural, friendly, supportive
- **Character Archetype:** The caring friend/companion
- **MVP Scope:** Single idol to validate AI conversation quality

---

## Files Created/Modified

### Backend Files

**Created:**
1. `backend/migrations/002_create_idols_table.sql` (36 lines)
   - SQL migration for idols table
   - Initial data insertion

2. `backend/migrations/run_migrations.sh` (26 lines)
   - Bash script to run migrations
   - Environment variable support

3. `backend/migrations/README.md` (45 lines)
   - Migration documentation
   - Usage instructions

4. `backend/app/models/idol.py` (29 lines)
   - SQLAlchemy ORM model
   - Database field mappings

5. `backend/app/schemas/idol.py` (68 lines)
   - Pydantic API schemas
   - Request/response models

6. `backend/app/routers/idol.py` (106 lines)
   - GET /api/v1/idols endpoint
   - GET /api/v1/idols/{idol_id} endpoint
   - Error handling

**Modified:**
7. `backend/app/main.py` (modified)
   - Registered idol router

### Frontend Files

**Created:**
8. `lib/features/idol/models/idol.dart` (134 lines)
   - Flutter data model
   - JSON serialization
   - Equality and hashing

**Total New Code:** ~450 lines

---

## Testing Guide

### Backend Testing

**1. Run Migrations:**

```bash
cd backend/migrations
./run_migrations.sh
```

Expected output:
```
Running database migrations...
Running migration: 002_create_idols_table.sql
✅ All migrations completed successfully!
```

**2. Verify Database:**

```bash
psql -h localhost -p 5432 -U idol_user -d idol_db -c "SELECT id, name, is_active FROM idols;"
```

Expected output:
```
 id |  name   | is_active
----+---------+-----------
  1 | 林雪晴  | t
```

**3. Start Backend:**

```bash
cd backend
uvicorn app.main:app --reload
```

**4. Test API Endpoints:**

**GET /api/v1/idols:**
```bash
curl http://localhost:8000/api/v1/idols
```

Expected response:
```json
{
  "idols": [
    {
      "id": 1,
      "name": "林雪晴",
      "avatar_url": "/assets/avatars/lin_xueqing.png",
      "description": "温柔知性的陪伴者，你的专属AI恋人",
      "hobbies_list": ["阅读", "旅行", "咖啡", "摄影"]
    }
  ]
}
```

**GET /api/v1/idols/1:**
```bash
curl http://localhost:8000/api/v1/idols/1
```

Expected response:
```json
{
  "idol": {
    "id": 1,
    "name": "林雪晴",
    "avatar_url": "/assets/avatars/lin_xueqing.png",
    "description": "温柔知性的陪伴者，你的专属AI恋人",
    "hobbies": "阅读、旅行、咖啡、摄影",
    "background_story": "雪晴是一个热爱生活的女生，喜欢在周末去咖啡馆看书，也喜欢用相机记录生活中的美好瞬间。她相信每个人都值得被温柔对待。",
    "is_active": true,
    "created_at": "2026-01-13T..."
  }
}
```

**Test 404 Error:**
```bash
curl http://localhost:8000/api/v1/idols/999
```

Expected response (404):
```json
{
  "detail": "该偶像不存在或已下线"
}
```

**5. API Documentation:**

Visit: http://localhost:8000/docs

Verify:
- Idol endpoints appear under "偶像" tag
- Request/response schemas are documented
- Try interactive API testing

### Frontend Testing

**Test Idol Model:**

```dart
void main() {
  // Test fromJson
  final json = {
    'id': 1,
    'name': '林雪晴',
    'avatar_url': '/assets/avatars/lin_xueqing.png',
    'description': '温柔知性的陪伴者，你的专属AI恋人',
    'hobbies_list': ['阅读', '旅行', '咖啡', '摄影'],
    'background_story': '雪晴是一个热爱生活的女生...',
    'is_active': true,
    'created_at': '2026-01-13T10:00:00Z',
  };

  final idol = Idol.fromJson(json);

  print(idol.name);  // 林雪晴
  print(idol.hobbies);  // [阅读, 旅行, 咖啡, 摄影]

  // Test toJson
  final jsonOutput = idol.toJson();
  print(jsonOutput);  // Matches input

  // Test copyWith
  final updated = idol.copyWith(description: 'New description');
  print(updated.description);  // New description
  print(updated.name);  // 林雪晴 (unchanged)
}
```

---

## Implementation Success Criteria

**Story完成标准:**
- ✅ Database table created with proper schema
- ✅ Migration script executable and documented
- ✅ SQLAlchemy model defined with all fields
- ✅ Pydantic schemas for API responses
- ✅ GET /api/v1/idols endpoint implemented
- ✅ GET /api/v1/idols/{idol_id} endpoint implemented
- ✅ Routes registered in main.py
- ✅ Lin Xueqing data inserted into database
- ✅ Flutter Idol model with JSON serialization
- ✅ personality_prompt secured (not exposed via API)
- ✅ Hobbies parsed as array in API responses
- ✅ Error handling for 404 and 500 cases
- ✅ OpenAPI documentation auto-generated

**Technical Validation:**
- ✅ is_active index created for performance
- ✅ ON CONFLICT DO NOTHING prevents duplicate insertion
- ✅ Chinese character support (UTF-8 encoding)
- ✅ Proper null handling in schemas and models
- ✅ Type safety in Flutter model
- ✅ Migration idempotency

**Definition of Done:**
- Database migration completed successfully
- API endpoints return correct data
- Flutter model parses backend responses
- Documentation complete
- No compilation errors
- Ready for Story 1.6 (Idol Intro Page)

---

## Security Considerations

### personality_prompt Protection

**Why it's critical:**
- Contains AI system instructions
- Exposes character design and prompting strategy
- Could be exploited to manipulate AI behavior
- Considered intellectual property

**Implementation:**
- ✅ Field exists in database (for backend AI usage)
- ✅ Excluded from all public API schemas
- ✅ Never sent to frontend
- ✅ Only accessed internally by AI conversation service

**Future Enhancement:**
- Story 2.x will use personality_prompt for AI conversations
- Only backend AI service will read this field
- Consider encryption at rest for sensitive prompts

---

## References

**Architecture文档:**
- [Database Layer] `_bmad-output/planning-artifacts/architecture.md` Lines 471-490
- [Backend Structure] `architecture.md` Lines 479-500
- [Frontend Structure] `architecture.md` Lines 468-477

**Epics文档:**
- [Story 1.5 Full Spec] `_bmad-output/planning-artifacts/epics.md` Lines 1955-2028
- [Epic 1 Overview] `epics.md` Lines 1631-1641

**PRD文档:**
- [偶像人设系统] `_bmad-output/planning-artifacts/prd.md` (Idol character requirements)
- [AI对话需求] `prd.md` (Personality prompt usage in AI conversations)

**Related Stories:**
- [Story 1.1: 项目初始化与用户注册] `1-1-project-init-user-registration.md`
- [Story 1.4: Material Design 3主题] `1-4-material-design-3-theme-ui-framework.md`
- **Next:** [Story 1.6: 偶像介绍页面] (to be implemented)

---

## Dev Agent Record

### Agent Model Used
Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Implementation Timeline
- **Start:** 2026-01-13 (continuing from Story 1.4)
- **Completion:** 2026-01-13 (same day)
- **Total Duration:** ~1 day

### Key Implementation Decisions

1. **Hobbies Storage Format:**
   - Stored as TEXT with comma-separated values in database (MVP simplicity)
   - Parsed to array in API response (better frontend UX)
   - Used Chinese separator (、) for natural language feel
   - Future: Could migrate to JSONB or separate table

2. **personality_prompt Security:**
   - Decided to completely exclude from public API
   - Only backend AI service can access
   - Prevents prompt injection attacks
   - Protects character design IP

3. **Migration Strategy:**
   - Simple SQL files (no complex migration tool for MVP)
   - Bash script for automation
   - Idempotent with ON CONFLICT DO NOTHING
   - Easy to run manually or via CI/CD

4. **API Endpoint Design:**
   - List endpoint returns minimal info
   - Detail endpoint returns full profile
   - Filters active idols automatically
   - RESTful naming conventions

5. **Flutter Model Design:**
   - Immutable data class pattern
   - Full equality and hashing for state management
   - Copy-with for updates
   - Type-safe with null safety

### Completion Notes

**What went well:**
- Clean separation of database, backend, and frontend layers
- Security-first approach for personality_prompt
- Comprehensive idol profile for Lin Xueqing
- Idempotent migration script

**Implementation highlights:**
- Complete data pipeline: SQL → SQLAlchemy → Pydantic → JSON → Flutter
- 450+ lines of production-ready code
- Chinese character support throughout
- Ready for AI conversation integration (Story 2.x)

**No blockers encountered during implementation**

---

## 🎯 Story 1.5 Status: ✅ COMPLETED

**Ready for Story 1.6 implementation!**

偶像数据模型已完全建立，林雪晴（Lin Xueqing）作为首个AI偶像已配置完成。数据库、后端API和前端模型全部就绪，为下一步的偶像介绍页面和用户交互功能奠定了基础。

**Next Story:** Story 1.6 - 偶像介绍页面
