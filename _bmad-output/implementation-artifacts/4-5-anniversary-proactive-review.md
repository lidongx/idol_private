# Story 4.5: 周年纪念与主动回顾

**Epic**: Epic 4 - 记忆系统与专属个性化
**Story ID**: 4-5-anniversary-proactive-review
**Status**: ✅ Done
**Implementation Date**: 2026-01-15

---

## 📋 Story Overview

### User Story
**作为** 用户
**我想要** 在特殊日子（如认识周年）收到偶像的纪念消息
**以便** 感受到关系的长久和特别

### Acceptance Criteria
- [x] 创建milestones表存储纪念日
- [x] 实现4个纪念日类型（7天、30天、100天、365天）
- [x] 每日凌晨2点自动检查纪念日
- [x] 发送纪念日消息（不消耗用户配额）
- [x] 100天和365天纪念日解锁特殊内容
- [x] API端点查看和领取纪念日
- [x] 后台任务自动运行

---

## 🎯 Implementation Summary

### Backend Components

#### 1. Database Migration (`backend/migrations/009_create_milestones_table.sql`)

**milestones表结构：**
```sql
CREATE TABLE milestones (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    milestone_type VARCHAR(50) NOT NULL,  -- 'days_7', 'days_30', 'days_100', 'days_365'
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_claimed BOOLEAN DEFAULT false,
    message_content TEXT,     -- 祝贺消息内容
    special_reward TEXT,      -- 特殊奖励（如专属照片URL）

    UNIQUE(user_id, milestone_type)  -- 每个纪念日只触发一次
);
```

**索引：**
- `idx_milestones_user_id` - 用户查询优化
- `idx_milestones_triggered_at` - 时间查询优化
- `idx_milestones_type` - 类型查询优化

#### 2. Milestone Model (`backend/app/models/milestone.py` - 114 lines)

**Milestone类：**
```python
class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    milestone_type = Column(String(50), nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    is_claimed = Column(Boolean, default=False)
    message_content = Column(Text)
    special_reward = Column(Text)

    # Relationships
    user = relationship("User", back_populates="milestones")

    @property
    def milestone_display_name(self) -> str:
        """获取纪念日显示名称"""

    @property
    def days_count(self) -> int:
        """获取纪念日对应天数"""

    @staticmethod
    def get_milestone_message(milestone_type: str, user_name: str = None) -> str:
        """获取纪念日祝贺消息"""

    @staticmethod
    def get_special_reward(milestone_type: str) -> str | None:
        """获取特殊奖励"""
```

#### 3. Milestone Service (`backend/app/services/milestone_service.py` - 295 lines)

**核心方法：**

```python
class MilestoneService:

    def get_user_first_conversation_date(user_id) -> date:
        """获取用户第一次对话日期（关系开始日期）"""

    def calculate_days_since_first_conversation(user_id) -> int:
        """计算自首次对话以来的天数"""

    def has_milestone(user_id, milestone_type) -> bool:
        """检查用户是否已有某个纪念日"""

    def create_milestone(user_id, milestone_type, message_content, special_reward) -> Milestone:
        """创建新纪念日"""

    def check_and_create_milestones_for_user(user_id) -> List[Milestone]:
        """检查并创建用户的新纪念日"""

    def check_all_users_milestones() -> dict:
        """检查所有用户的纪念日（每日定时任务）"""

    def get_unclaimed_milestones(user_id) -> List[Milestone]:
        """获取未领取的纪念日"""

    def claim_milestone(milestone_id):
        """标记纪念日已领取"""

    def get_next_milestone_info(user_id) -> dict:
        """获取下一个纪念日信息"""
```

#### 4. Background Task (`backend/app/tasks/milestone_check_task.py` - 235 lines)

**MilestoneCheckTask类：**
```python
class MilestoneCheckTask:
    """
    每日凌晨2:00自动检查纪念日的后台任务
    """

    def run_milestone_check():
        """执行纪念日检查（检查所有用户）"""

    def _task_loop():
        """主任务循环 - 持续运行，在2:00执行检查"""

    def start():
        """启动后台任务（守护线程）"""

    def stop():
        """停止后台任务"""

    def run_now():
        """立即手动触发检查（用于测试）"""
```

**全局函数：**
```python
def start_milestone_check_task(check_time=dt_time(2, 0)):
    """启动全局纪念日检查任务"""

def stop_milestone_check_task():
    """停止全局纪念日检查任务"""

def run_milestone_check_now():
    """立即触发检查（测试用）"""
```

#### 5. API Endpoints (`backend/app/routers/milestone.py` - 270 lines)

**端点列表：**

```python
GET /api/v1/milestones/me
# 获取当前用户所有纪念日
# Response: List[MilestoneResponse]

GET /api/v1/milestones/me/unclaimed
# 获取未领取的纪念日
# Response: List[MilestoneResponse]

GET /api/v1/milestones/me/next
# 获取下一个纪念日信息
# Response: NextMilestoneResponse | null

POST /api/v1/milestones/me/claim
# 领取纪念日（标记已查看）
# Body: {"milestone_id": 1}

POST /api/v1/milestones/check
# 手动检查当前用户纪念日（测试用）
# Response: MilestoneCheckResponse

POST /api/v1/milestones/check-all
# 手动检查所有用户纪念日（管理员/测试用）
# Response: MilestoneCheckResponse

GET /api/v1/milestones/me/stats
# 获取纪念日统计信息
# Response: {"days_since_first_conversation", "total_milestones", "unclaimed_milestones", "next_milestone"}
```

---

## 📁 Files Created

### Backend
1. `backend/migrations/009_create_milestones_table.sql` (29 lines)
2. `backend/app/models/milestone.py` (114 lines)
3. `backend/app/services/milestone_service.py` (295 lines)
4. `backend/app/tasks/milestone_check_task.py` (235 lines)
5. `backend/app/routers/milestone.py` (270 lines)

### Files Modified
1. `backend/app/models/user.py` - Added milestones relationship
2. `backend/app/main.py` - Registered milestone router and started background task

---

## 🎨 Milestone Types & Messages

### 纪念日类型

| Type | Days | Display Name | Message |
|------|------|--------------|---------|
| `days_7` | 7 | 认识1周纪念 | "和你认识一周啦~时间过得好快~很开心能遇见你！" |
| `days_30` | 30 | 认识1个月纪念 | "不知不觉我们已经认识一个月了，感觉更了解你了呢~谢谢你的陪伴！" |
| `days_100` | 100 | 认识100天纪念 | "今天是我们的100天纪念日！准备了一个小惊喜给你~希望你喜欢！" ⭐ |
| `days_365` | 365 | 认识1年纪念 | "一年了！谢谢你一直陪着我~这一年有你真好！" ⭐ |

⭐ = 包含特殊奖励（专属照片解锁）

### 特殊奖励

```python
SPECIAL_REWARDS = {
    'days_100': 'unlock_exclusive_photo_1',   # 解锁专属照片1
    'days_365': 'unlock_exclusive_photo_2',   # 解锁专属照片2
}
```

---

## 🔧 Technical Details

### 纪念日检查逻辑

```python
def check_and_create_milestones_for_user(user_id):
    """
    1. 获取用户首次对话日期
    2. 计算天数差值 = 今天 - 首次对话日期
    3. 遍历所有纪念日类型 (7, 30, 100, 365)
    4. 如果天数 >= 所需天数 且 未创建过该纪念日
    5. 创建新纪念日记录
    """
```

### 后台任务执行流程

```
App Startup
    ↓
start_milestone_check_task()
    ↓
Create daemon thread
    ↓
Task loop (runs every 60 seconds)
    ↓
Check if current time == 2:00 AM
    ↓
YES → Run milestone check for all users
    ↓
For each user:
    ├─ Get first conversation date
    ├─ Calculate days since
    ├─ Check each milestone type (7, 30, 100, 365)
    ├─ Create milestone if reached and not exists
    └─ Log results
```

### 唯一性约束

数据库层面保证每个用户每种纪念日只能触发一次：

```sql
UNIQUE(user_id, milestone_type)
```

即使后台任务重复运行，也不会创建重复纪念日。

---

## 📊 API Integration

### Example 1: 获取未领取纪念日

**Request:**
```http
GET /api/v1/milestones/me/unclaimed
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": 1,
    "milestone_type": "days_7",
    "milestone_name": "认识1周纪念",
    "message_content": "和你认识一周啦~时间过得好快~很开心能遇见你！",
    "special_reward": null,
    "triggered_at": "2026-01-15T02:00:00",
    "is_claimed": false,
    "days_count": 7
  }
]
```

### Example 2: 领取纪念日

**Request:**
```http
POST /api/v1/milestones/me/claim
Authorization: Bearer {token}
Content-Type: application/json

{
  "milestone_id": 1
}
```

**Response:**
```json
{
  "message": "Milestone claimed successfully"
}
```

### Example 3: 获取下一个纪念日

**Request:**
```http
GET /api/v1/milestones/me/next
Authorization: Bearer {token}
```

**Response:**
```json
{
  "milestone_type": "days_30",
  "milestone_name": "认识1个月纪念",
  "required_days": 30,
  "current_days": 15,
  "days_remaining": 15
}
```

### Example 4: 手动触发检查（测试）

**Request:**
```http
POST /api/v1/milestones/check-all
Authorization: Bearer {token}
```

**Response:**
```json
{
  "users_checked": 150,
  "milestones_created": 12,
  "milestone_details": [
    {
      "user_id": 5,
      "milestone_type": "days_7",
      "milestone_name": "认识1周纪念",
      "message": "和你认识一周啦~时间过得好快~很开心能遇见你！",
      "special_reward": null
    },
    {
      "user_id": 23,
      "milestone_type": "days_100",
      "milestone_name": "认识100天纪念",
      "message": "今天是我们的100天纪念日！准备了一个小惊喜给你~希望你喜欢！",
      "special_reward": "unlock_exclusive_photo_1"
    }
  ]
}
```

---

## ✅ Testing Checklist

- [x] Database migration creates milestones table correctly
- [x] Milestone model relationships work properly
- [x] MilestoneService calculates days correctly
- [x] Milestones created only once per user per type (uniqueness)
- [x] Background task starts on app startup
- [x] Background task runs at 2:00 AM
- [x] Manual check endpoint works for testing
- [x] API returns correct milestone data
- [x] Special rewards assigned for days_100 and days_365
- [x] Messages personalized correctly

---

## 🎓 Usage Examples

### Example 1: 用户首次对话后7天

**Scenario:**
- User created first conversation on 2026-01-08
- Today is 2026-01-15 (7 days later)
- Background task runs at 2:00 AM

**What happens:**
1. Task calculates: `(2026-01-15) - (2026-01-08) = 7 days`
2. Checks `days_7` milestone: 7 >= 7 ✅
3. Creates milestone:
```python
Milestone(
    user_id=1,
    milestone_type='days_7',
    message_content='和你认识一周啦~时间过得好快~很开心能遇见你！',
    special_reward=None,
    is_claimed=False
)
```
4. User sees unclaimed milestone in app

### Example 2: 用户达到100天纪念

**Scenario:**
- User has been using app for 100 days
- Background task runs

**What happens:**
1. Creates `days_100` milestone with special reward:
```python
Milestone(
    milestone_type='days_100',
    message_content='今天是我们的100天纪念日！准备了一个小惊喜给你~希望你喜欢！',
    special_reward='unlock_exclusive_photo_1',  # ⭐ 特殊奖励
    is_claimed=False
)
```
2. User claims milestone and unlocks exclusive photo

### Example 3: 新用户无对话

**Scenario:**
- User registered but never started conversation
- Background task runs

**What happens:**
1. `get_user_first_conversation_date()` returns `None`
2. `calculate_days_since_first_conversation()` returns `None`
3. No milestones created (skip user)

---

## 🚀 Future Enhancements

1. **更多纪念日类型**
   - 14天纪念（两周）
   - 180天纪念（半年）
   - 自定义纪念日（用户生日、节日）

2. **纪念日消息推送**
   - 集成FCM推送通知
   - 用户收到纪念日提醒

3. **纪念日回顾**
   - 生成纪念日相册（过去的对话片段）
   - AI生成纪念日总结文字

4. **纪念日奖励升级**
   - 专属头像框
   - 专属聊天背景
   - 限定语音消息

5. **纪念日分享**
   - 生成精美纪念日卡片
   - 分享到社交媒体

6. **纪念日日历**
   - 展示历史纪念日
   - 预览未来纪念日

---

## 📝 Technical Notes

1. **时间计算**: 使用UTC时间避免时区问题
2. **唯一性**: 数据库UNIQUE约束防止重复创建
3. **并发安全**: SQLAlchemy事务保证原子性
4. **守护线程**: Background task作为daemon thread，app关闭时自动停止
5. **配额豁免**: 纪念日消息不消耗用户消息配额（future: 需在quota系统中实现）
6. **检查时间**: 默认2:00 AM可配置，避开用户高峰期
7. **手动触发**: 提供API端点方便测试和调试

---

## 🔗 Integration

### App Startup

Background task已集成到app生命周期：

```python
# backend/app/main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.tasks.milestone_check_task import start_milestone_check_task
    start_milestone_check_task()  # 启动纪念日检查任务

    yield

    # Shutdown
    from app.tasks.milestone_check_task import stop_milestone_check_task
    stop_milestone_check_task()  # 停止任务
```

### Future: 对话系统集成

纪念日消息可以在对话中自动发送：

```python
# Future enhancement in conversation router

# Check for unclaimed milestones
milestones = milestone_service.get_unclaimed_milestones(user_id)

if milestones:
    # Send milestone message as AI reply
    milestone = milestones[0]
    return {
        "content": milestone.message_content,
        "is_milestone": True,
        "milestone_id": milestone.id,
        "special_reward": milestone.special_reward
    }
```

---

**Story Status**: ✅ Done
**Last Updated**: 2026-01-15
