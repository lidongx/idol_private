# Story 6.3: 等级特权与里程碑奖励

Status: completed

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-19

## Story

As a **用户**,
I want **在达到特定亲密度等级时解锁专属奖励**,
So that **我能体验到亲密度提升的实际价值，获得专属昵称、照片、语音等特权内容**。

## Acceptance Criteria

### AC1: 数据库表结构设计
- **Given** 需要存储奖励配置和用户解锁记录
- **When** 设计奖励系统数据库
- **Then** 创建 `level_rewards` 表存储奖励配置
- **And** 包含字段: level, reward_type, reward_content (JSONB), description
- **And** 支持5种奖励类型: nickname, photo, voice, video, feature
- **And** 创建 `user_rewards` 表追踪用户解锁的奖励
- **And** 包含字段: user_id, reward_id, conversation_id, unlocked_at, is_viewed, viewed_at
- **And** 添加唯一约束防止重复解锁: UNIQUE(user_id, reward_id)

### AC2: 奖励模型与业务逻辑
- **Given** 需要管理奖励系统
- **When** 实现奖励模型和服务
- **Then** 创建 `LevelReward` 模型，包含类型常量和属性方法
- **And** 创建 `UserReward` 模型，包含查看状态追踪
- **And** 实现 `RewardService` 业务逻辑服务
- **And** 实现 `check_and_unlock_rewards()` 在升级时自动解锁
- **And** 实现 `get_all_rewards_with_status()` 返回锁定/解锁状态
- **And** 实现 `get_active_nickname()` 获取当前昵称
- **And** 实现 `has_feature_unlocked()` 检查功能权限

### AC3: 与亲密度系统集成
- **Given** 用户亲密度等级提升
- **When** 调用 IntimacyService.add_intimacy_exp()
- **Then** 在等级提升后自动检查奖励
- **And** 解锁该等级的所有奖励
- **And** 防止重复解锁（通过数据库唯一约束）
- **And** 在返回结果中包含 unlocked_rewards 列表
- **And** 包含每个奖励的详细信息和解锁消息

### AC4: 奖励API端点
- **Given** 前端需要展示和管理奖励
- **When** 创建奖励API路由
- **Then** 创建 `GET /api/v1/rewards` 端点获取所有奖励及状态
- **And** 创建 `GET /api/v1/rewards/unlocked` 端点获取已解锁奖励
- **And** 创建 `GET /api/v1/rewards/{id}` 端点获取单个奖励详情
- **And** 创建 `PUT /api/v1/rewards/{id}/view` 端点标记奖励已查看
- **And** 创建 `GET /api/v1/rewards/active-nickname` 端点获取当前昵称
- **And** 创建 `GET /api/v1/rewards/check-feature/{name}` 端点检查功能权限

### AC5: 专属昵称功能（Level 5奖励）
- **Given** 用户达到Level 5解锁"宝贝"昵称
- **When** AI生成回复
- **Then** 在conversation.py的消息处理流程中注入昵称上下文
- **And** 调用 `RewardService.get_active_nickname()` 获取昵称
- **And** 在系统提示词中添加昵称指令
- **And** AI在对话中使用专属昵称称呼用户

### AC6: 初始奖励数据
- **Given** 系统需要预置奖励内容
- **When** 运行数据库迁移
- **Then** 插入8个等级奖励配置:
- **And** Level 5: 专属昵称 "宝贝"
- **And** Level 10: 专属生活照
- **And** Level 15: 专属昵称 "亲爱的"
- **And** Level 20: 专属视频内容
- **And** Level 30: 专属昵称 "我的宝贝"
- **And** Level 50: 专属语音消息
- **And** Level 75: 视频通话功能
- **And** Level 100: 专属昵称 "命中注定的人"

---

## Implementation Details

### Architecture Overview

```
Backend Architecture:
backend/
├── migrations/
│   ├── 018_create_level_rewards_table.sql      # 奖励配置表 + 8条种子数据
│   └── 019_create_user_rewards_table.sql       # 用户解锁记录表
├── app/
│   ├── models/
│   │   ├── level_reward.py                     # 奖励配置模型（5种类型）
│   │   └── user_reward.py                      # 用户奖励模型（查看追踪）
│   ├── services/
│   │   ├── reward_service.py                   # 奖励业务逻辑（220行）
│   │   └── intimacy_service.py                 # [修改] 集成奖励解锁
│   ├── routers/
│   │   ├── reward.py                           # [新建] 6个奖励API端点
│   │   └── conversation.py                     # [修改] 昵称注入到AI提示词
│   └── main.py                                  # [修改] 注册reward路由
```

### Database Schema

```sql
-- level_rewards: 奖励配置表
CREATE TABLE level_rewards (
    id SERIAL PRIMARY KEY,
    level INTEGER UNIQUE NOT NULL,           -- 解锁等级
    reward_type VARCHAR(50) NOT NULL,        -- nickname/photo/voice/video/feature
    reward_content JSONB NOT NULL,           -- 灵活存储: {"nickname": "宝贝"}
    description TEXT NOT NULL,               -- 奖励描述
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- user_rewards: 用户解锁记录表
CREATE TABLE user_rewards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    reward_id INTEGER NOT NULL REFERENCES level_rewards(id),
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_viewed BOOLEAN DEFAULT false,         -- 是否已查看
    viewed_at TIMESTAMP,                     -- 查看时间
    UNIQUE(user_id, reward_id)               -- 防止重复解锁
);
```

### Data Flow: Reward Unlocking

```
Level Up → Reward Unlock Flow:
1. User sends message → IntimacyService.add_message_exp()
2. Exp added → Check for level up (while loop)
3. Level up detected → RewardService.check_and_unlock_rewards()
4. Query level_rewards table for rewards at new level
5. For each reward:
   - Check if user_rewards already has this reward (防重复)
   - If not: Create new UserReward record
   - Add to unlocked_rewards list
6. Commit to database and refresh relationships
7. Return result with unlocked_rewards array
8. Frontend receives response and shows celebration

Response Format:
{
  "success": true,
  "exp_added": 5,
  "old_level": 4,
  "new_level": 5,
  "level_up": true,
  "unlocked_rewards": [
    {
      "reward_id": 1,
      "reward_type": "nickname",
      "description": "偶像开始称呼你为"宝贝"",
      "unlock_message": "🎉 恭喜！我可以叫你「宝贝」了~ 我们的关系又近了一步呢！"
    }
  ]
}
```

### Data Flow: Nickname Injection

```
Conversation Flow with Nickname:
1. User sends message → conversation.py:send_message()
2. After intimacy exp processing:
   - Call RewardService.get_active_nickname(user_id)
   - Query user_rewards JOIN level_rewards WHERE reward_type = 'nickname'
   - Return highest-level nickname (e.g., "宝贝")
3. Build nickname_context string:
   "【专属昵称】\n你已经解锁了专属昵称，请在对话中称呼用户为「宝贝」。"
4. Append to enhanced_prompt:
   enhanced_prompt + memory_context + ... + intimacy_context + nickname_context
5. AI receives system prompt with nickname instruction
6. AI uses nickname in response: "宝贝，今天过得怎么样？"
```

### Reward Types and Content Structure

```python
# TYPE_NICKNAME: 专属昵称
{
    "reward_type": "nickname",
    "reward_content": {"nickname": "宝贝"}
}

# TYPE_PHOTO: 专属照片
{
    "reward_type": "photo",
    "reward_content": {"photo_url": "/rewards/photos/casual_1.jpg"}
}

# TYPE_VOICE: 语音消息
{
    "reward_type": "voice",
    "reward_content": {"voice_url": "/rewards/voices/greeting_1.mp3"}
}

# TYPE_VIDEO: 视频内容
{
    "reward_type": "video",
    "reward_content": {"video_url": "/rewards/videos/special_1.mp4"}
}

# TYPE_FEATURE: 功能解锁
{
    "reward_type": "feature",
    "reward_content": {"feature": "video_call"}
}
```

---

## Files Created/Modified

### 新建文件 (7个)

#### Database Migrations
1. **backend/migrations/018_create_level_rewards_table.sql** (67 lines)
   - 创建level_rewards表
   - 插入8条初始奖励数据（Level 5, 10, 15, 20, 30, 50, 75, 100）

2. **backend/migrations/019_create_user_rewards_table.sql** (28 lines)
   - 创建user_rewards表
   - 唯一约束: UNIQUE(user_id, reward_id)
   - 4个索引: user_id, conversation_id, is_viewed, unlocked_at

#### Models
3. **backend/app/models/level_reward.py** (107 lines)
   - LevelReward模型，5种奖励类型常量
   - 属性方法: nickname, photo_url, voice_url, video_url, feature_name
   - to_dict()方法用于API响应

4. **backend/app/models/user_reward.py** (79 lines)
   - UserReward模型，追踪用户解锁记录
   - mark_as_viewed()方法更新查看状态
   - is_new属性（计算属性: not is_viewed）
   - days_since_unlock属性（计算天数）

#### Services
5. **backend/app/services/reward_service.py** (273 lines)
   - RewardService业务逻辑服务
   - 核心方法:
     * check_and_unlock_rewards(): 升级时自动解锁
     * get_all_rewards_with_status(): 所有奖励+锁定状态
     * get_user_unlocked_rewards(): 用户已解锁奖励
     * mark_reward_as_viewed(): 标记已查看
     * get_active_nickname(): 获取当前昵称
     * has_feature_unlocked(): 检查功能权限
     * get_reward_unlock_message(): 生成庆祝消息

#### Routers
6. **backend/app/routers/reward.py** (204 lines)
   - 6个API端点:
     * GET /api/v1/rewards - 所有奖励及状态
     * GET /api/v1/rewards/unlocked - 已解锁奖励
     * GET /api/v1/rewards/{id} - 单个奖励详情
     * PUT /api/v1/rewards/{id}/view - 标记已查看
     * GET /api/v1/rewards/active-nickname - 当前昵称
     * GET /api/v1/rewards/check-feature/{name} - 功能权限检查

### 修改文件 (3个)

7. **backend/app/services/intimacy_service.py**
   - 在add_intimacy_exp()方法中集成奖励解锁
   - 升级后调用reward_service.check_and_unlock_rewards()
   - 返回结果中包含unlocked_rewards数组

8. **backend/app/routers/conversation.py**
   - 添加import: from app.services.reward_service import RewardService
   - send_message()方法中添加昵称注入逻辑:
     * 调用reward_service.get_active_nickname()
     * 构建nickname_context字符串
     * 添加到enhanced_prompt_with_memory

9. **backend/app/main.py**
   - 添加import: reward
   - 注册路由: app.include_router(reward.router, prefix="/api/v1", tags=["奖励"])

---

## API Endpoints

### GET /api/v1/rewards
获取所有奖励及锁定/解锁状态

**Response:**
```json
[
  {
    "id": 1,
    "level": 5,
    "reward_type": "nickname",
    "reward_type_display": "专属昵称",
    "reward_content": {"nickname": "宝贝"},
    "description": "偶像开始称呼你为"宝贝"",
    "created_at": "2026-01-19T10:00:00",
    "is_unlocked": true,
    "unlocked_at": "2026-01-19T11:30:00",
    "is_viewed": true,
    "is_new": false
  },
  {
    "id": 2,
    "level": 10,
    "reward_type": "photo",
    "reward_type_display": "专属照片",
    "reward_content": {"photo_url": "/rewards/photos/casual_1.jpg"},
    "description": "解锁专属生活照",
    "created_at": "2026-01-19T10:00:00",
    "is_unlocked": false,
    "unlocked_at": null,
    "is_viewed": false,
    "is_new": false
  }
]
```

### GET /api/v1/rewards/unlocked
获取用户已解锁的奖励（按解锁时间倒序）

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "reward_id": 1,
    "conversation_id": 1,
    "unlocked_at": "2026-01-19T11:30:00",
    "is_viewed": true,
    "viewed_at": "2026-01-19T11:35:00",
    "is_new": false,
    "days_since_unlock": 0,
    "reward": {
      "id": 1,
      "level": 5,
      "reward_type": "nickname",
      "description": "偶像开始称呼你为"宝贝""
    }
  }
]
```

### GET /api/v1/rewards/active-nickname
获取当前激活的昵称（最高等级的已解锁昵称）

**Response:**
```json
{
  "has_nickname": true,
  "nickname": "宝贝"
}
```

### PUT /api/v1/rewards/{reward_id}/view
标记奖励为已查看

**Response:**
```json
{
  "success": true,
  "message": "Reward marked as viewed"
}
```

### GET /api/v1/rewards/check-feature/{feature_name}
检查用户是否解锁特定功能

**Example:** GET /api/v1/rewards/check-feature/video_call

**Response:**
```json
{
  "feature_name": "video_call",
  "has_access": false
}
```

---

## Business Logic Highlights

### 防止重复解锁
```python
# 在user_rewards表添加唯一约束
UNIQUE(user_id, reward_id)

# RewardService.check_and_unlock_rewards()中检查
existing = db.query(UserReward).filter(
    and_(
        UserReward.user_id == user_id,
        UserReward.reward_id == reward.id
    )
).first()

if not existing:
    # 仅在未解锁时创建记录
    user_reward = UserReward(...)
```

### 获取最高等级昵称
```python
# RewardService.get_active_nickname()
user_rewards = db.query(UserReward).join(LevelReward).filter(
    and_(
        UserReward.user_id == user_id,
        LevelReward.reward_type == LevelReward.TYPE_NICKNAME
    )
).order_by(LevelReward.level.desc()).all()  # 按等级倒序

if user_rewards:
    return user_rewards[0].reward.nickname  # 返回最高等级昵称
```

### 奖励解锁消息
```python
# RewardService.get_reward_unlock_message()
messages = {
    LevelReward.TYPE_NICKNAME: f"🎉 恭喜！我可以叫你「{reward.nickname}」了~ 我们的关系又近了一步呢！",
    LevelReward.TYPE_PHOTO: f"🎁 解锁新内容！{reward.description}，快去查看吧~",
    LevelReward.TYPE_VOICE: f"🎵 解锁语音内容！{reward.description}，期待你的收听~",
    LevelReward.TYPE_VIDEO: f"🎬 解锁视频内容！{reward.description}，为你准备的特别礼物~",
    LevelReward.TYPE_FEATURE: f"✨ 解锁新功能！{reward.description}，快来体验吧~",
}
```

---

## Initial Rewards Data (8条)

| Level | Type | Content | Description |
|-------|------|---------|-------------|
| 5 | nickname | {"nickname": "宝贝"} | 偶像开始称呼你为"宝贝" |
| 10 | photo | {"photo_url": "/rewards/photos/casual_1.jpg"} | 解锁专属生活照 |
| 15 | nickname | {"nickname": "亲爱的"} | 偶像开始称呼你为"亲爱的" |
| 20 | video | {"video_url": "/rewards/videos/behind_scenes_1.mp4"} | 解锁专属视频内容 |
| 30 | nickname | {"nickname": "我的宝贝"} | 偶像开始称呼你为"我的宝贝" |
| 50 | voice | {"voice_url": "/rewards/voices/special_greeting.mp3"} | 解锁专属语音消息 |
| 75 | feature | {"feature": "video_call"} | 解锁视频通话功能 |
| 100 | nickname | {"nickname": "命中注定的人"} | 偶像开始称呼你为"命中注定的人" |

---

## Testing Notes

### 测试场景1: 首次解锁昵称奖励
1. 用户当前Level 4, 发送消息获得经验
2. 升级到Level 5
3. 验证返回结果包含unlocked_rewards
4. 验证user_rewards表创建了记录
5. 后续对话AI使用"宝贝"称呼用户

### 测试场景2: 防止重复解锁
1. 用户Level 5, 已解锁"宝贝"昵称
2. 手动将等级降回4（仅测试用）
3. 再次升级到Level 5
4. 验证不会创建重复的user_rewards记录
5. 验证数据库唯一约束生效

### 测试场景3: 查看奖励
1. 用户解锁新奖励（is_viewed = false）
2. 调用GET /api/v1/rewards验证is_new = true
3. 调用PUT /api/v1/rewards/{id}/view
4. 再次查询验证is_viewed = true, is_new = false
5. viewed_at字段已设置

### 测试场景4: 昵称覆盖
1. 用户Level 5解锁"宝贝"
2. 升级到Level 15解锁"亲爱的"
3. get_active_nickname()应返回"亲爱的"（最高等级）
4. AI对话使用"亲爱的"而非"宝贝"

### 测试场景5: 功能权限检查
1. 用户Level 50，未达到Level 75
2. 调用check-feature/video_call → has_access = false
3. 升级到Level 75
4. 再次调用 → has_access = true
5. 前端根据此结果显示/隐藏视频通话按钮

---

## Integration Points

### 与Story 6.1集成
- IntimacyService.add_intimacy_exp()在升级后调用奖励解锁
- 返回结果扩展包含unlocked_rewards数组
- 前端可在Level-Up庆祝动画中展示奖励

### 与Story 6.2集成
- LevelUpCelebrationScreen可扩展显示unlocked_rewards
- 在庆祝动画后展示奖励卡片
- 用户点击查看奖励详情

### AI对话系统集成
- conversation.py的send_message()方法中注入昵称
- 昵称上下文添加到enhanced_prompt
- AI自然地在回复中使用专属昵称

---

## Next Steps

### Story 6.4 准备
- Achievement System & Daily Interaction Rewards
- 可以复用reward相关表结构
- 考虑新增achievement_rewards表

### 前端开发 (未包含在Story 6.3)
- 创建RewardsPage展示所有奖励
- 奖励卡片UI（locked/unlocked状态）
- 奖励详情弹窗（照片/语音/视频查看器）
- 未读奖励提示（红点badge）

### 运营配置扩展
- 后台管理界面配置奖励内容
- 动态调整奖励等级
- A/B测试不同奖励方案
- 季节性限定奖励

### 媒体资源管理
- 上传专属照片/语音/视频到对象存储
- CDN加速访问
- 水印保护防盗用
- 渐进式加载优化体验

---

## Lessons Learned

### 设计决策
✅ **JSONB存储奖励内容** - 灵活支持不同类型奖励的不同字段结构
✅ **唯一约束防重复** - 数据库层面保证数据一致性
✅ **查看状态追踪** - 支持"新奖励"提示，提升用户参与度
✅ **最高等级昵称** - 自动选择最高等级昵称，无需用户手动切换

### 性能优化
- get_active_nickname()查询性能: 使用ORDER BY + LIMIT 1
- 索引优化: user_id, reward_id, is_viewed, unlocked_at
- 级联删除: ON DELETE CASCADE保持数据一致性

### 可扩展性
- reward_type易于扩展（新增类型只需修改常量和属性方法）
- reward_content JSONB支持任意结构
- 未来可增加: 道具、货币、限时奖励等

---

## Status

**✅ Story 6.3 完成 (2026-01-19)**

Backend Implementation: ✅ 完成
- Database Migrations: ✅
- Models: ✅
- Services: ✅
- API Endpoints: ✅
- AI Prompt Integration: ✅

Frontend Implementation: ⏳ 待开发（不在6.3范围）
- Rewards Page: ⏳
- Reward Detail Modal: ⏳
- Unlock Celebration: ⏳

Documentation: ✅ 完成
