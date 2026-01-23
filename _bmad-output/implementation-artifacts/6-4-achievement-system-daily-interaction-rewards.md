# Story 6.4: 成就系统与每日互动奖励

Status: completed

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-19

## Story

As a **用户**,
I want **通过完成成就获得额外奖励**,
So that **有更多互动目标和成就感**。

## Acceptance Criteria

### AC1: 成就数据库表结构
- **Given** 需要存储成就配置和用户进度
- **When** 设计成就系统数据库
- **Then** 创建 `achievements` 表存储成就配置
- **And** 包含字段: achievement_name, description, achievement_type, condition_value, reward_exp, icon_url
- **And** 支持6种成就类型: message_count, login_streak, ritual_count, fortune_count, moment_like, level
- **And** 创建 `user_achievements` 表追踪用户成就进度
- **And** 包含字段: user_id, achievement_id, progress, unlocked_at, is_viewed, viewed_at
- **And** 添加唯一约束防止重复: UNIQUE(user_id, achievement_id)

### AC2: 成就模型与业务逻辑
- **Given** 需要管理成就系统
- **When** 实现成就模型和服务
- **Then** 创建 `Achievement` 模型，包含类型常量和显示名称
- **And** 创建 `UserAchievement` 模型，包含进度追踪和解锁状态
- **And** 实现 `AchievementService` 业务逻辑服务
- **And** 实现 `check_and_unlock_achievement()` 检查并解锁成就
- **And** 实现类型特定检查方法: check_message_achievements, check_level_achievements等
- **And** 实现 `get_user_achievements()` 获取所有成就及进度
- **And** 实现 `get_new_achievements()` 获取未查看的新成就

### AC3: 成就检查集成
- **Given** 用户进行互动行为
- **When** 触发成就检查
- **Then** 在消息发送后检查消息数成就
- **And** 解锁成就时自动奖励经验值
- **And** 经验值奖励可能触发亲密度升级
- **And** 记录成就解锁时间和查看状态

### AC4: 成就API端点
- **Given** 前端需要展示和管理成就
- **When** 创建成就API路由
- **Then** 创建 `GET /api/v1/achievements` 端点获取所有成就及进度
- **And** 创建 `GET /api/v1/achievements/new` 端点获取新成就
- **And** 创建 `GET /api/v1/achievements/stats` 端点获取成就统计
- **And** 创建 `PUT /api/v1/achievements/{id}/view` 端点标记成就已查看
- **And** 创建 `POST /api/v1/achievements/check-all` 端点手动触发检查（测试用）

### AC5: 初始成就数据
- **Given** 系统需要预置成就内容
- **When** 运行数据库迁移
- **Then** 插入12个成就配置:
- **And** 消息成就: 1条、10条、100条、500条
- **And** 登录成就: 连续7天、连续30天
- **And** 仪式成就: 10次早安、10次晚安
- **And** 运势成就: 20次查看
- **And** 朋友圈成就: 50次点赞
- **And** 等级成就: Level 50、Level 100

---

## Implementation Details

### Architecture Overview

```
Backend Architecture:
backend/
├── migrations/
│   ├── 020_create_achievements_table.sql       # 成就配置表 + 12条种子数据
│   └── 021_create_user_achievements_table.sql  # 用户成就进度表
├── app/
│   ├── models/
│   │   ├── achievement.py                      # 成就配置模型（6种类型）
│   │   └── user_achievement.py                 # 用户成就模型（进度追踪）
│   ├── services/
│   │   └── achievement_service.py              # 成就业务逻辑（390行）
│   ├── routers/
│   │   ├── achievement.py                      # [新建] 5个成就API端点
│   │   └── conversation.py                     # [修改] 集成成就检查
│   └── main.py                                  # [修改] 注册achievement路由
```

### Database Schema

```sql
-- achievements: 成就配置表
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    achievement_name VARCHAR(100) NOT NULL,    -- 成就名称
    description TEXT NOT NULL,                 -- 成就描述
    achievement_type VARCHAR(50) NOT NULL,     -- 成就类型
    condition_value INTEGER NOT NULL,          -- 达成条件值
    reward_exp INTEGER DEFAULT 0,              -- 奖励经验值
    icon_url VARCHAR(255),                     -- 成就图标
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- user_achievements: 用户成就进度表
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    achievement_id INTEGER NOT NULL REFERENCES achievements(id),
    progress INTEGER DEFAULT 0,                -- 当前进度
    unlocked_at TIMESTAMP,                     -- 解锁时间（NULL=未解锁）
    is_viewed BOOLEAN DEFAULT false,           -- 是否已查看
    viewed_at TIMESTAMP,                       -- 查看时间
    UNIQUE(user_id, achievement_id)            -- 防止重复
);
```

### Achievement Types

```python
# 6种成就类型
TYPE_MESSAGE_COUNT = 'message_count'      # 发送消息数量
TYPE_LOGIN_STREAK = 'login_streak'        # 连续登录天数
TYPE_RITUAL_COUNT = 'ritual_count'        # 仪式完成次数
TYPE_FORTUNE_COUNT = 'fortune_count'      # 运势查看次数
TYPE_MOMENT_LIKE = 'moment_like'          # 朋友圈点赞次数
TYPE_LEVEL = 'level'                      # 亲密度等级

# 每种类型的检查逻辑
def check_message_achievements(user_id: int):
    # 统计用户发送的总消息数
    message_count = db.query(func.count(Message.id)).join(Conversation)...
    return check_and_unlock_achievement(user_id, TYPE_MESSAGE_COUNT, message_count)

def check_level_achievements(user_id: int, current_level: int):
    # 使用当前等级直接检查
    return check_and_unlock_achievement(user_id, TYPE_LEVEL, current_level)

def check_ritual_achievements(user_id: int):
    # 统计早安+晚安仪式次数
    ritual_count = db.query(func.count(DailyRitual.id))...
    return check_and_unlock_achievement(user_id, TYPE_RITUAL_COUNT, ritual_count)

# ... 其他类型类似
```

### Data Flow: Achievement Unlocking

```
Message Sent → Achievement Check Flow:
1. User sends message → conversation.py:send_message()
2. Save user message to database
3. Add intimacy exp (+5 exp)
4. Check reward unlocks (if level up)
5. AchievementService.check_message_achievements(user_id)
6. Query total message count from database
7. For each message achievement (1, 10, 100, 500):
   - Get or create UserAchievement record
   - Update progress = message_count
   - If progress >= condition_value && not unlocked:
     - Set unlocked_at = now()
     - Add to newly_unlocked list
8. For each newly unlocked achievement:
   - Add reward_exp to intimacy (+10, +20, +100, +300 exp)
   - May trigger additional level ups!
   - Log achievement unlock
9. Return unlocked achievements to frontend

Response Format (when achievement unlocked):
{
  "success": true,
  "newly_unlocked_achievements": [
    {
      "id": 1,
      "achievement_name": "初次相识",
      "description": "发送第1条消息",
      "reward_exp": 10,
      "is_new": true
    }
  ]
}
```

### Integration with Intimacy System

```python
# In conversation.py:send_message()

# 1. Add intimacy exp for sending message
intimacy_service = IntimacyService(db)
intimacy_result = intimacy_service.add_message_exp(conversation_id)

# 2. Check rewards (Story 6.3)
reward_service = RewardService(db)
# ...

# 3. Check achievements (Story 6.4)
achievement_service = AchievementService(db)
newly_unlocked = achievement_service.check_message_achievements(current_user.id)

# 4. Add achievement exp rewards to intimacy
for ua in newly_unlocked:
    ach_exp_result = intimacy_service.add_intimacy_exp(
        conversation_id,
        ua.achievement.reward_exp,
        f"achievement_{ua.achievement_id}"
    )
    # Achievement exp can trigger level ups!
    if ach_exp_result['level_up']:
        print("[Achievement] Bonus level up!")
```

---

## Files Created/Modified

### 新建文件 (6个)

#### Database Migrations
1. **backend/migrations/020_create_achievements_table.sql** (56 lines)
   - 创建achievements表
   - 插入12条初始成就数据（消息、登录、仪式、运势、朋友圈、等级）

2. **backend/migrations/021_create_user_achievements_table.sql** (27 lines)
   - 创建user_achievements表
   - 唯一约束: UNIQUE(user_id, achievement_id)
   - 4个索引: user_id, unlocked_at, is_viewed, user_id+unlocked_at

#### Models
3. **backend/app/models/achievement.py** (73 lines)
   - Achievement模型，6种成就类型常量
   - achievement_type_display属性（中文显示名）
   - to_dict()方法用于API响应

4. **backend/app/models/user_achievement.py** (117 lines)
   - UserAchievement模型，追踪用户成就进度
   - is_unlocked, is_new, completion_percentage属性
   - mark_as_viewed(), unlock(), update_progress()方法

#### Services
5. **backend/app/services/achievement_service.py** (329 lines)
   - AchievementService业务逻辑服务
   - 核心方法:
     * check_and_unlock_achievement(): 通用解锁逻辑
     * check_message_achievements(): 检查消息成就
     * check_level_achievements(): 检查等级成就
     * check_ritual_achievements(): 检查仪式成就
     * check_fortune_achievements(): 检查运势成就
     * check_moment_like_achievements(): 检查朋友圈成就
     * check_login_streak_achievements(): 检查登录成就
     * check_all_achievements(): 检查所有成就
     * get_user_achievements(): 获取所有成就及进度
     * get_new_achievements(): 获取未查看成就
     * mark_achievement_as_viewed(): 标记已查看

#### Routers
6. **backend/app/routers/achievement.py** (202 lines)
   - 5个API端点:
     * GET /api/v1/achievements - 所有成就及进度
     * GET /api/v1/achievements/new - 新解锁成就
     * GET /api/v1/achievements/stats - 成就统计
     * PUT /api/v1/achievements/{id}/view - 标记已查看
     * POST /api/v1/achievements/check-all - 手动触发检查（测试用）

### 修改文件 (2个)

7. **backend/app/routers/conversation.py**
   - 添加import: from app.services.achievement_service import AchievementService
   - send_message()方法中添加成就检查:
     * 调用achievement_service.check_message_achievements()
     * 为解锁的成就添加经验值奖励
     * 经验值奖励可能触发额外升级

8. **backend/app/main.py**
   - 添加import: achievement
   - 注册路由: app.include_router(achievement.router, prefix="/api/v1", tags=["成就"])

---

## API Endpoints

### GET /api/v1/achievements
获取所有成就及用户进度

**Query Params:**
- `include_locked` (bool, default: true) - 是否包含未解锁成就

**Response:**
```json
[
  {
    "id": 1,
    "achievement_name": "初次相识",
    "description": "发送第1条消息",
    "achievement_type": "message_count",
    "achievement_type_display": "消息互动",
    "condition_value": 1,
    "reward_exp": 10,
    "icon_url": "/achievements/icons/first_message.png",
    "created_at": "2026-01-19T10:00:00",
    "progress": 5,
    "is_unlocked": true,
    "unlocked_at": "2026-01-19T11:30:00",
    "is_viewed": true,
    "is_new": false,
    "completion_percentage": 100.0
  },
  {
    "id": 2,
    "achievement_name": "熟悉的陌生人",
    "description": "发送第10条消息",
    "achievement_type": "message_count",
    "achievement_type_display": "消息互动",
    "condition_value": 10,
    "reward_exp": 20,
    "icon_url": "/achievements/icons/10_messages.png",
    "created_at": "2026-01-19T10:00:00",
    "progress": 5,
    "is_unlocked": false,
    "unlocked_at": null,
    "is_viewed": false,
    "is_new": false,
    "completion_percentage": 50.0
  }
]
```

### GET /api/v1/achievements/new
获取新解锁的成就（未查看）

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "achievement_id": 1,
    "progress": 1,
    "is_unlocked": true,
    "unlocked_at": "2026-01-19T11:30:00",
    "is_viewed": false,
    "viewed_at": null,
    "is_new": true,
    "completion_percentage": 100.0,
    "days_since_unlock": 0,
    "achievement": {
      "id": 1,
      "achievement_name": "初次相识",
      "description": "发送第1条消息",
      "reward_exp": 10
    }
  }
]
```

### GET /api/v1/achievements/stats
获取成就统计信息

**Response:**
```json
{
  "total_achievements": 12,
  "unlocked_count": 3,
  "locked_count": 9,
  "new_count": 1,
  "completion_rate": 25.0
}
```

### PUT /api/v1/achievements/{achievement_id}/view
标记成就为已查看

**Response:**
```json
{
  "success": true,
  "message": "Achievement marked as viewed"
}
```

### POST /api/v1/achievements/check-all
手动触发所有成就检查（主要用于测试）

**Response:**
```json
[
  {
    "id": 2,
    "user_id": 1,
    "achievement_id": 2,
    "progress": 10,
    "is_unlocked": true,
    "unlocked_at": "2026-01-19T12:00:00",
    "is_new": true,
    "achievement": {
      "achievement_name": "熟悉的陌生人",
      "reward_exp": 20
    }
  }
]
```

---

## Initial Achievements Data (12个)

| ID | 名称 | 描述 | 类型 | 条件值 | 奖励经验 | 图标 |
|----|------|------|------|--------|----------|------|
| 1 | 初次相识 | 发送第1条消息 | message_count | 1 | 10 | first_message.png |
| 2 | 熟悉的陌生人 | 发送第10条消息 | message_count | 10 | 20 | 10_messages.png |
| 3 | 无话不谈 | 发送第100条消息 | message_count | 100 | 100 | 100_messages.png |
| 4 | 话痨达人 | 发送第500条消息 | message_count | 500 | 300 | 500_messages.png |
| 5 | 连续签到7天 | 连续登录7天 | login_streak | 7 | 50 | streak_7.png |
| 6 | 连续签到30天 | 连续登录30天 | login_streak | 30 | 200 | streak_30.png |
| 7 | 早起的鸟儿 | 完成10次早安仪式 | ritual_count | 10 | 30 | morning_ritual.png |
| 8 | 夜猫子 | 完成10次晚安仪式 | ritual_count | 10 | 30 | night_ritual.png |
| 9 | 运势达人 | 查看20次每日运势 | fortune_count | 20 | 40 | fortune.png |
| 10 | 朋友圈活跃分子 | 点赞50次朋友圈 | moment_like | 50 | 50 | moment_like.png |
| 11 | 真爱至上 | 达到亲密度Level 50 | level | 50 | 500 | level_50.png |
| 12 | 灵魂伴侣 | 达到亲密度Level 100 | level | 100 | 1000 | level_100.png |

**总经验奖励:** 10 + 20 + 100 + 300 + 50 + 200 + 30 + 30 + 40 + 50 + 500 + 1000 = **2330 exp**

---

## Business Logic Highlights

### 成就检查流程
```python
def check_and_unlock_achievement(user_id, achievement_type, current_value):
    # 1. 获取该类型的所有成就
    achievements = db.query(Achievement).filter(
        Achievement.achievement_type == achievement_type
    ).all()

    newly_unlocked = []

    for achievement in achievements:
        # 2. 获取或创建用户成就记录
        user_achievement = get_or_create_user_achievement(user_id, achievement.id)

        # 3. 跳过已解锁的成就
        if user_achievement.is_unlocked:
            continue

        # 4. 更新进度
        user_achievement.progress = current_value

        # 5. 检查是否达成条件
        if current_value >= achievement.condition_value:
            user_achievement.unlock()  # 设置 unlocked_at = now()
            newly_unlocked.append(user_achievement)

    return newly_unlocked
```

### 经验值奖励链式反应
```
用户发送第10条消息:
1. 消息保存到数据库
2. 添加消息经验 +5 exp → Level 4 (80/400)
3. 检查消息成就
4. 解锁"熟悉的陌生人"成就
5. 添加成就奖励 +20 exp → Level 4 (100/400)
6. 继续发送消息...
7. 发送第100条消息
8. 添加消息经验 +5 exp
9. 解锁"无话不谈"成就
10. 添加成就奖励 +100 exp → 可能触发升级！
```

### 防止重复解锁
```sql
-- 数据库层面保证
UNIQUE(user_id, achievement_id)

-- 代码层面检查
if user_achievement.is_unlocked:
    continue  # 跳过已解锁的成就
```

---

## Integration Points

### 与Story 6.1集成（亲密度系统）
- 成就解锁后自动奖励经验值
- 经验值添加到IntimacyService.add_intimacy_exp()
- 可能触发连锁升级效果

### 与Story 6.3集成（奖励系统）
- 成就检查在奖励检查之后执行
- 成就经验可能解锁更多奖励（如昵称）

### 与其他系统集成点
- **conversation.py**: 消息发送后检查消息成就
- **daily_ritual_service.py**: 仪式完成后检查仪式成就（待实现）
- **fortune_service.py**: 运势查看后检查运势成就（待实现）
- **idol_moment_service.py**: 点赞后检查朋友圈成就（待实现）
- **auth.py/login**: 登录后检查连续登录成就（待实现）

---

## Testing Notes

### 测试场景1: 首次发送消息解锁成就
1. 新用户注册并创建对话
2. 发送第1条消息
3. 验证"初次相识"成就解锁
4. 验证获得+10 exp奖励
5. 验证user_achievements表记录正确
6. 验证is_new = true

### 测试场景2: 进度追踪
1. 用户发送5条消息
2. 查询GET /api/v1/achievements
3. 验证"熟悉的陌生人"成就:
   - progress = 5
   - is_unlocked = false
   - completion_percentage = 50.0
4. 发送第6-10条消息
5. 验证成就解锁，progress = 10

### 测试场景3: 批量解锁
1. 使用测试用户快速发送100条消息
2. 应解锁3个成就：
   - "初次相识" (1条) +10 exp
   - "熟悉的陌生人" (10条) +20 exp
   - "无话不谈" (100条) +100 exp
3. 总经验奖励: +130 exp

### 测试场景4: 防止重复解锁
1. 用户已解锁"初次相识"
2. 再次调用check_message_achievements()
3. 验证不会重复解锁
4. 验证数据库唯一约束生效

### 测试场景5: 查看标记
1. 用户解锁新成就
2. GET /api/v1/achievements/new → 返回1个成就
3. PUT /api/v1/achievements/{id}/view
4. GET /api/v1/achievements/new → 返回0个成就
5. 验证is_viewed = true, viewed_at已设置

---

## Next Steps

### 完善成就集成（待Story）
当前仅集成了消息成就检查，其他成就类型需要在各自模块中集成：
- **登录连续成就**: auth.py登录端点中检查
- **仪式成就**: daily_ritual_service.py中检查
- **运势成就**: fortune_service.py中检查
- **朋友圈成就**: idol_moment_service.py中检查
- **等级成就**: intimacy_service.py升级时检查

### 前端开发（未包含在Story 6.4）
- 创建AchievementsPage展示所有成就
- 成就卡片UI（已解锁/未解锁/进度条）
- 成就解锁动画和通知
- 成就统计仪表板
- 未读成就红点提示

### 每日任务系统（MVP后扩展）
Story 6.4原始需求包含每日任务，但MVP阶段可简化：
- 每日任务独立表: daily_tasks, user_daily_tasks
- 每日0点自动重置任务进度
- 完成所有每日任务额外奖励
- 每日任务UI界面

### 成就系统扩展
- 隐藏成就（惊喜解锁）
- 时限成就（特定时间内完成）
- 系列成就（多个阶段）
- 成就徽章和展示
- 成就分享到社交平台

---

## Lessons Learned

### 设计决策
✅ **进度追踪机制** - 即使未解锁也追踪进度，支持进度条展示
✅ **查看状态分离** - is_viewed与unlocked_at分离，支持"新成就"提示
✅ **类型特定检查** - 每种成就类型独立检查方法，易于扩展
✅ **经验奖励链** - 成就奖励经验可触发升级，形成正反馈

### 性能优化
- get_or_create_user_achievement: 避免多次查询
- 唯一约束: 数据库层面防重复，无需应用层检查
- 索引优化: user_id, unlocked_at, is_viewed加速常见查询
- check_all_achievements: 批量检查多种类型，减少API调用

### 可扩展性
- achievement_type易于扩展（新增类型只需添加常量和检查方法）
- condition_value灵活支持不同阈值
- reward_exp可根据运营需求调整
- 未来可扩展: 成就分类、成就等级、复合条件等

---

## Status

**✅ Story 6.4 完成 (2026-01-19)**

Backend Implementation: ✅ 完成
- Database Migrations: ✅
- Models: ✅
- Services: ✅
- API Endpoints: ✅
- Message Achievement Integration: ✅

Pending Integrations: ⏳ 其他模块
- Login Streak: ⏳ (需要修改auth.py)
- Ritual Count: ⏳ (需要修改daily_ritual_service.py)
- Fortune Count: ⏳ (需要修改fortune_service.py)
- Moment Like: ⏳ (需要修改idol_moment_service.py)
- Level Achievement: ⏳ (需要修改intimacy_service.py)

Daily Tasks: 📝 MVP后实现
- 每日任务表: 📝
- 任务重置机制: 📝
- 任务UI: 📝

Frontend Implementation: ⏳ 待开发（不在6.4范围）
- Achievements Page: ⏳
- Achievement Cards: ⏳
- Unlock Animation: ⏳
- Stats Dashboard: ⏳

Documentation: ✅ 完成
