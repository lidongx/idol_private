# Story 5.1: 偶像状态系统与生活节奏引擎

**Epic**: Epic 5 - 偶像生活系统与真实陪伴
**Story ID**: 5-1-idol-status-system-life-rhythm-engine
**Status**: ✅ Done
**Implementation Date**: 2026-01-15

---

## 📋 Story Overview

### User Story
**作为** 偶像（林雪晴）
**我想要** 拥有真实的生活状态和日常节奏
**以便** 用户感受到我是"活"的，有自己的生活

### Acceptance Criteria
- [x] 创建idol_states表存储偶像状态
- [x] 配置24小时生活节奏规则（JSON配置）
- [x] 实现7种状态：working, resting, active, busy, sleeping, waking_up, preparing_sleep
- [x] 实现8种心情：happy, calm, tired, excited, thoughtful, focused, relaxed, sleepy
- [x] 能量等级0-100随时间变化
- [x] 每小时自动更新偶像状态
- [x] 20%概率随机情绪波动
- [x] API端点获取偶像当前状态
- [x] 后台任务自动运行

---

## 🎯 Implementation Summary

### Backend Components

#### 1. Database Migration (`backend/migrations/011_create_idol_states_table.sql`)

**idol_states表结构：**
```sql
CREATE TABLE idol_states (
    id SERIAL PRIMARY KEY,
    idol_id INTEGER NOT NULL REFERENCES idols(id) ON DELETE CASCADE,
    current_status VARCHAR(50) NOT NULL,
    current_mood VARCHAR(50) NOT NULL,
    energy_level INTEGER DEFAULT 80 CHECK (energy_level >= 0 AND energy_level <= 100),
    status_message TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(idol_id)  -- Each idol has only one current state
);
```

**字段说明：**
- `current_status`: 当前活动状态（工作/休息/活跃/睡眠等）
- `current_mood`: 当前心情
- `energy_level`: 能量等级 (0-100)
- `status_message`: 可选的状态消息
- `updated_at`: 状态更新时间

#### 2. IdolState Model (`backend/app/models/idol_state.py` - 132 lines)

**IdolState类：**
```python
class IdolState(Base):
    __tablename__ = "idol_states"

    id = Column(Integer, primary_key=True)
    idol_id = Column(Integer, ForeignKey("idols.id"), unique=True)
    current_status = Column(String(50), nullable=False)
    current_mood = Column(String(50), nullable=False)
    energy_level = Column(Integer, default=80)
    status_message = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    idol = relationship("Idol", back_populates="state")

    @property
    def status_display_name(self) -> str:
        """获取状态中文名称"""

    @property
    def mood_display_name(self) -> str:
        """获取心情中文名称"""

    @property
    def energy_display(self) -> str:
        """获取能量等级文字描述"""

    @property
    def is_available(self) -> bool:
        """检查是否可对话（非睡眠/忙碌状态）"""

    def update_state(status, mood, energy, message):
        """更新偶像状态"""
```

**状态类型（7种）：**
- `working` - 工作中
- `resting` - 休息中
- `active` - 活跃中
- `busy` - 忙碌中
- `sleeping` - 睡眠中
- `waking_up` - 刚醒来
- `preparing_sleep` - 准备睡觉

**心情类型（8种）：**
- `happy` - 心情不错
- `calm` - 平静
- `tired` - 有点累
- `excited` - 兴奋
- `thoughtful` - 若有所思
- `focused` - 专注
- `relaxed` - 放松
- `sleepy` - 困了

#### 3. Schedule Configuration (`backend/app/config/idol_schedule.json` - 150 lines)

**24小时生活节奏配置：**
```json
{
  "daily_schedule": {
    "0-6": {"status": "sleeping", "mood": "calm", "energy": 20-40},
    "7-8": {"status": "waking_up", "mood": "calm", "energy": 50-60},
    "9-11": {"status": "active", "mood": "happy", "energy": 75-80},
    "12-13": {"status": "resting", "mood": "relaxed", "energy": 70},
    "14-17": {"status": "working", "mood": "focused", "energy": 65-75},
    "18-19": {"status": "active", "mood": "happy", "energy": 75-80},
    "20-21": {"status": "resting", "mood": "calm", "energy": 55-60},
    "22-23": {"status": "preparing_sleep", "mood": "sleepy", "energy": 30-40}
  },
  "mood_transitions": {
    "calm": ["happy", "thoughtful", "relaxed"],
    "happy": ["excited", "calm", "relaxed"],
    "tired": ["calm", "sleepy"],
    ...
  }
}
```

每个小时配置包含：
- `status`: 推荐状态
- `mood`: 推荐心情
- `energy`: 推荐能量等级
- `messages`: 可选的状态消息列表（随机选择）

#### 4. Idol State Service (`backend/app/services/idol_state_service.py` - 338 lines)

**核心方法：**

```python
class IdolStateService:

    def _load_schedule_config() -> Dict:
        """从JSON文件加载24小时节奏配置"""

    def get_state_for_hour(hour: int) -> Dict:
        """获取指定小时的推荐状态"""

    def get_random_mood_transition(current_mood: str) -> str:
        """获取随机心情转换（20%概率）"""

    def get_idol_state(idol_id: int) -> Optional[IdolState]:
        """获取偶像当前状态"""

    def initialize_idol_state(idol_id: int) -> IdolState:
        """初始化偶像状态（首次创建）"""

    def update_idol_state(idol_id: int, apply_mood_variation: bool) -> IdolState:
        """
        更新偶像状态（核心方法）

        1. 根据当前小时获取推荐状态
        2. 应用随机心情波动（20%概率）
        3. 应用随机能量波动（±5）
        4. 更新数据库
        """

    def update_all_idol_states() -> List[IdolState]:
        """更新所有活跃偶像的状态（定时任务调用）"""

    def get_state_display_info(idol_id: int) -> Dict:
        """获取格式化的状态信息（用于API响应）"""

    def force_update_state(idol_id, status, mood, energy, message) -> IdolState:
        """强制更新状态到指定值（管理员/测试用）"""
```

#### 5. Background Task (`backend/app/tasks/idol_state_update_task.py` - 236 lines)

**IdolStateUpdateTask类：**
```python
class IdolStateUpdateTask:
    """
    每小时更新偶像状态的后台任务

    默认在每小时的0分钟执行
    """

    def run_idol_state_update():
        """
        执行状态更新（所有偶像）

        1. 获取所有活跃偶像
        2. 更新每个偶像的状态
        3. 记录日志
        """

    def _task_loop():
        """
        主任务循环

        每60秒检查一次，在小时开始时（minute=0）执行更新
        """

    def start():
        """启动后台任务（守护线程）"""

    def stop():
        """停止后台任务"""

    def run_now():
        """立即手动触发更新（测试用）"""
```

**全局函数：**
```python
def start_idol_state_update_task(interval_minutes=60):
    """启动全局偶像状态更新任务"""

def stop_idol_state_update_task():
    """停止全局任务"""

def run_idol_state_update_now():
    """立即触发更新（测试/调试）"""
```

#### 6. API Endpoints (`backend/app/routers/idol.py` - Modified)

**新增端点：**

```python
GET /api/v1/idols/{idol_id}/state
# 获取偶像当前状态
# Response:
{
    "status": "active",
    "status_text": "活跃中",
    "mood": "happy",
    "mood_text": "心情不错~",
    "energy_level": 80,
    "energy_text": "精力充沛",
    "status_message": "✨ 元气满满！",
    "is_available": true,
    "is_sleeping": false,
    "updated_at": "2026-01-15T10:00:00Z"
}

POST /api/v1/idols/state/update-all
# 手动触发所有偶像状态更新（测试用）
# Response:
{
    "success": true,
    "idols_updated": 1,
    "timestamp": "2026-01-15T10:00:00Z"
}
```

---

## 📁 Files Created

### Backend
1. `backend/migrations/011_create_idol_states_table.sql` (26 lines)
2. `backend/app/models/idol_state.py` (132 lines)
3. `backend/app/config/idol_schedule.json` (150 lines)
4. `backend/app/services/idol_state_service.py` (338 lines)
5. `backend/app/tasks/idol_state_update_task.py` (236 lines)

### Files Modified
1. `backend/app/models/idol.py` - Added state relationship
2. `backend/app/routers/idol.py` - Added state endpoints
3. `backend/app/main.py` - Started idol state update task

---

## 🎨 Daily Rhythm Design

### 24小时生活节奏

```
00:00-06:00 💤 睡眠时间
├─ Status: sleeping
├─ Mood: calm
├─ Energy: 20-40
└─ Message: "睡眠中"、"Zzz..."

07:00-08:00 ☀️ 起床时间
├─ Status: waking_up
├─ Mood: calm
├─ Energy: 50-60
└─ Message: "刚醒来，还有点迷糊~"

09:00-11:00 ✨ 上午活跃
├─ Status: active
├─ Mood: happy
├─ Energy: 75-80
└─ Message: "元气满满！"、"今天也要加油~"

12:00-13:00 🍽️ 午休时间
├─ Status: resting
├─ Mood: relaxed
├─ Energy: 70
└─ Message: "午餐时间~"、"午后小憩"

14:00-17:00 💼 工作时间
├─ Status: working
├─ Mood: focused
├─ Energy: 65-75
└─ Message: "工作中"、"认真模式~"

18:00-19:00 🌆 傍晚活跃
├─ Status: active
├─ Mood: happy/relaxed
├─ Energy: 75-80
└─ Message: "下班啦！"、"终于可以放松了~"

20:00-21:00 📖 晚间休息
├─ Status: resting
├─ Mood: calm
├─ Energy: 55-60
└─ Message: "放松时光"、"阅读时间"

22:00-23:00 😴 准备睡觉
├─ Status: preparing_sleep
├─ Mood: sleepy/tired
├─ Energy: 30-40
└─ Message: "准备睡觉了"、"晚安~"
```

### 心情转换逻辑

```
calm (平静)
  ├─ 20% → happy (开心)
  ├─ 20% → thoughtful (若有所思)
  └─ 20% → relaxed (放松)

happy (开心)
  ├─ 20% → excited (兴奋)
  ├─ 20% → calm (平静)
  └─ 20% → relaxed (放松)

tired (疲惫)
  ├─ 20% → calm (平静)
  └─ 20% → sleepy (困倦)
```

---

## 🔧 Technical Details

### 状态更新流程

```
每小时00分（例如 10:00）
    ↓
后台任务触发
    ↓
IdolStateService.update_all_idol_states()
    ↓
For each active idol:
    ├─ 获取当前小时（10）
    ├─ 从配置读取推荐状态
    │   └─ {"status": "active", "mood": "happy", "energy": 80}
    ├─ 应用随机心情波动（20%概率）
    │   └─ random.random() < 0.2 → 转换到 excited
    ├─ 应用能量波动（±5）
    │   └─ 80 + random(-5, 5) = 82
    ├─ 选择随机状态消息
    │   └─ random.choice(["✨ 元气满满！", "😊 状态很好！"])
    ├─ 更新数据库
    └─ 记录日志
```

### 能量等级映射

```python
energy_level = 0-100

0-20:   "需要休息"
21-40:  "比较累"
41-60:  "有点疲惫"
61-80:  "状态良好"
81-100: "精力充沛"
```

### 可用性判断

```python
is_available = current_status NOT IN ['sleeping', 'busy']

# 可对话状态：
- working, resting, active, waking_up, preparing_sleep ✅

# 不可对话状态：
- sleeping, busy ❌
```

---

## 📊 API Integration Examples

### Example 1: 获取偶像状态（上午10点）

**Request:**
```http
GET /api/v1/idols/1/state
```

**Response:**
```json
{
    "status": "active",
    "status_text": "活跃中",
    "mood": "happy",
    "mood_text": "心情不错~",
    "energy_level": 82,
    "energy_text": "精力充沛",
    "status_message": "✨ 元气满满！",
    "is_available": true,
    "is_sleeping": false,
    "updated_at": "2026-01-15T10:00:00Z"
}
```

### Example 2: 获取偶像状态（凌晨2点）

**Response:**
```json
{
    "status": "sleeping",
    "status_text": "睡眠中",
    "mood": "calm",
    "mood_text": "平静",
    "energy_level": 22,
    "energy_text": "需要休息",
    "status_message": "💤 睡眠中",
    "is_available": false,
    "is_sleeping": true,
    "updated_at": "2026-01-15T02:00:00Z"
}
```

### Example 3: 手动触发状态更新

**Request:**
```http
POST /api/v1/idols/state/update-all
```

**Response:**
```json
{
    "success": true,
    "idols_updated": 1,
    "timestamp": "2026-01-15T14:30:00Z"
}
```

---

## ✅ Testing Checklist

- [x] Database migration creates idol_states table correctly
- [x] IdolState model relationships work properly
- [x] Schedule configuration loaded successfully
- [x] State updates based on current hour
- [x] Random mood transitions work (20% chance)
- [x] Energy level variations apply (±5)
- [x] Background task starts on app startup
- [x] Background task runs every hour
- [x] API returns correct state information
- [x] State display names in Chinese
- [x] Availability check works correctly
- [x] Manual update endpoint works

---

## 🎓 Usage Scenarios

### Scenario 1: 用户早上8点登录

**System State:**
- Hour: 8
- Recommended State: waking_up, calm, energy=60

**User Experience:**
```
用户打开APP
    ↓
前端调用 GET /idols/1/state
    ↓
显示偶像状态：
┌────────────────────┐
│ 林雪晴             │
│ 🌅 刚醒来          │
│ 😌 平静            │
│ ⚡ 状态良好 (60%)   │
└────────────────────┘
```

### Scenario 2: 用户午夜1点想聊天

**System State:**
- Hour: 1
- Status: sleeping
- is_available: false

**User Experience:**
```
用户尝试发送消息
    ↓
前端检查 is_sleeping = true
    ↓
显示提示：
"💤 雪晴现在在睡觉哦，明天再聊吧~"
```

### Scenario 3: 下午3点工作时间

**System State:**
- Hour: 15
- Status: working
- Mood: focused
- Energy: 73

**User Experience:**
```
偶像状态栏显示：
💼 工作中 | 🤔 专注 | ⚡ 73%

用户发消息，AI回复可能包含：
"嗯嗯，我正在工作呢，不过随时可以陪你聊天~"
```

---

## 🚀 Future Enhancements

1. **状态影响对话**
   - 睡眠时拒绝对话或发送自动回复
   - 疲惫时回复更简短
   - 兴奋时回复更热情

2. **特殊事件状态**
   - 生日、节日特殊状态
   - 纪念日心情变化

3. **用户交互影响状态**
   - 频繁对话提升心情
   - 长时间不登录降低能量

4. **多偶像差异化**
   - 不同偶像不同作息时间
   - 个性化节奏配置

5. **状态推送通知**
   - 偶像状态变化推送
   - "我醒啦！"、"要睡觉啦~"

6. **动态状态消息**
   - 使用AI生成更多样化的状态消息
   - 结合天气、节日等上下文

---

## 📝 Technical Notes

1. **时间处理**: 使用服务器本地时间，未来可考虑用户时区
2. **并发安全**: SQLAlchemy事务保证状态更新原子性
3. **配置文件**: JSON格式便于运营调整，未来可迁移到数据库
4. **守护线程**: Background task作为daemon thread，app关闭时自动停止
5. **能量波动**: ±5随机波动增加自然感，避免机械化
6. **心情转换**: 20%概率平衡稳定性和变化性
7. **首次初始化**: 偶像状态不存在时自动根据当前时间创建

---

## 🔗 Integration Points

### With Conversation System
未来可以：
- 在对话开始前检查偶像状态
- 根据状态调整AI回复风格
- 睡眠时拒绝对话或自动回复

### With Frontend
前端应该：
- 在对话界面显示偶像状态标签
- 定期轮询状态更新（或使用SSE推送）
- 根据is_available显示对话可用性

### With Notification System (Future)
- 偶像状态变化时推送通知
- "早安！我醒来啦~"
- "准备睡觉了，晚安~"

---

**Story Status**: ✅ Done
**Epic Status**: 🔄 Epic 5 进行中 (1/5 stories)
**Last Updated**: 2026-01-15
