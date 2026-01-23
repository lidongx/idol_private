# Story 5.5: 特殊事件与互动彩蛋

**Epic**: Epic 5 - 偶像生活系统与真实陪伴
**Story ID**: 5-5-special-events-interactive-easter-eggs
**Status**: ✅ Done
**Implementation Date**: 2026-01-15

---

## 📋 Story Overview

### User Story
**作为** 用户
**我想要** 偶尔遇到特殊事件和隐藏彩蛋
**以便** 对话充满惊喜和新鲜感

### Acceptance Criteria
- [x] 创建special_events和user_special_events表
- [x] 随机事件（5%概率）：遇到小猫、读书分享、美丽日落等
- [x] 节日事件：情人节、七夕、圣诞节、新年等
- [x] 成就事件：第100条消息、连续登录30天等
- [x] 天气事件：下雨、下雪、晴天等（预留）
- [x] 事件优先级：节日 > 成就 > 随机
- [x] 事件奖励经验值
- [x] 事件Cooldown机制（防止频繁触发）
- [x] 每日最多3个事件

---

## 🎯 Implementation Summary

### Backend Components

#### 1. Database Migration (`backend/migrations/016_create_special_events_tables.sql`)

**special_events表（事件模板）：**
```sql
CREATE TABLE special_events (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL UNIQUE,
    event_type VARCHAR(50) NOT NULL,  -- 'random', 'holiday', 'achievement', 'weather'
    trigger_condition JSONB,
    content_template TEXT NOT NULL,
    image_url VARCHAR(255),
    reward_exp INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**user_special_events表（用户事件历史）：**
```sql
CREATE TABLE user_special_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    idol_id INTEGER NOT NULL REFERENCES idols(id),
    event_id INTEGER NOT NULL REFERENCES special_events(id),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_content TEXT,
    exp_awarded INTEGER DEFAULT 0,
    was_interacted BOOLEAN DEFAULT false
);
```

**Indexes：**
- `idx_special_events_type` - 事件类型过滤
- `idx_special_events_active` - 激活状态过滤
- `idx_user_special_events_user_id` - 用户查询优化
- `idx_user_special_events_event_id` - 事件查询优化
- `idx_user_special_events_triggered_at` - 时间排序优化
- `idx_user_special_events_user_event` - 复合查询优化

#### 2. Models

**SpecialEvent模型** (`backend/app/models/special_event.py` - 55 lines)
```python
class SpecialEvent(Base):
    __tablename__ = "special_events"

    id = Column(Integer, primary_key=True)
    event_name = Column(String(100), unique=True, nullable=False)
    event_type = Column(String(50), nullable=False)
    trigger_condition = Column(JSONB, nullable=True)
    content_template = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    reward_exp = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Event types
    TYPE_RANDOM = 'random'
    TYPE_HOLIDAY = 'holiday'
    TYPE_ACHIEVEMENT = 'achievement'
    TYPE_WEATHER = 'weather'
```

**UserSpecialEvent模型** (`backend/app/models/special_event.py` - 31 lines)
```python
class UserSpecialEvent(Base):
    __tablename__ = "user_special_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    idol_id = Column(Integer, ForeignKey("idols.id"))
    event_id = Column(Integer, ForeignKey("special_events.id"))
    triggered_at = Column(DateTime, default=datetime.utcnow)
    event_content = Column(Text)
    exp_awarded = Column(Integer, default=0)
    was_interacted = Column(Boolean, default=False)

    @property
    def is_recent(self) -> bool:
        """Check if event was triggered recently (within 24 hours)"""
        hours_passed = (datetime.utcnow() - self.triggered_at).total_seconds() / 3600
        return hours_passed < 24
```

**User模型更新** (`backend/app/models/user.py` - Modified)
- 添加关系：`special_events = relationship("UserSpecialEvent", back_populates="user")`

#### 3. Configuration (`backend/app/config/event_templates.json` - 220 lines)

**四种事件类型：**

1. **random_events（随机事件）**
```json
{
  "event_name": "encounter_cat",
  "event_type": "random",
  "probability": 0.05,
  "content_template": "刚才路上遇到一只小猫，超可爱的！给你看照片~",
  "image_url": "/static/events/cute_cat.jpg",
  "reward_exp": 20,
  "cooldown_hours": 48
}
```

事件列表：
- encounter_cat（遇到小猫）- 20 exp
- book_quote（读书分享）- 15 exp
- beautiful_sunset（美丽日落）- 15 exp
- favorite_song（推荐歌曲）- 10 exp
- good_mood_today（好心情）- 10 exp
- learned_something_new（学到新知识）- 15 exp

2. **holiday_events（节日事件）**
```json
{
  "event_name": "valentine_day",
  "event_type": "holiday",
  "date": {"month": 2, "day": 14},
  "content_template": "今天是情人节，有什么想对我说的吗？💕",
  "reward_exp": 50,
  "once_per_year": true
}
```

节日列表：
- valentine_day（情人节 2/14）- 50 exp
- qixi_festival（七夕）- 50 exp
- christmas（圣诞节 12/25）- 50 exp
- new_year（新年 1/1）- 50 exp
- mid_autumn_festival（中秋节）- 50 exp
- user_birthday（用户生日）- 100 exp

3. **achievement_events（成就事件）**
```json
{
  "event_name": "messages_100",
  "event_type": "achievement",
  "trigger_condition": {"message_count": 100},
  "content_template": "不知不觉我们已经聊了100条消息了！时间过得好快~",
  "reward_exp": 100,
  "one_time_only": true
}
```

成就列表：
- first_message（第1条消息）- 10 exp
- messages_100（第100条消息）- 100 exp
- messages_500（第500条消息）- 300 exp
- messages_1000（第1000条消息）- 500 exp
- login_streak_7（连续7天）- 50 exp
- login_streak_30（连续30天）- 200 exp
- login_streak_100（连续100天）- 500 exp
- all_rituals_completed（完成全部仪式）- 30 exp

4. **weather_events（天气事件）**
```json
{
  "event_name": "rainy_day",
  "event_type": "weather",
  "trigger_condition": {"weather": "rain"},
  "content_template": "今天下雨了，记得带伞哦~ 别淋湿了~",
  "reward_exp": 10,
  "cooldown_hours": 48
}
```

#### 4. Service (`backend/app/services/special_event_service.py` - 428 lines)

**核心方法：**

```python
class SpecialEventService:

    def check_random_events(user_id, idol_id) -> Optional[Dict]:
        """
        检查随机事件（5%概率）

        Returns: Event info or None
        """

    def check_holiday_events(user_id, idol_id) -> Optional[Dict]:
        """
        检查节日事件（基于日期）

        Returns: Event info or None
        """

    def check_achievement_events(user_id, idol_id) -> Optional[Dict]:
        """
        检查成就事件（消息数、连续登录等）

        Returns: Event info or None
        """

    def check_all_events(user_id, idol_id) -> Optional[Dict]:
        """
        检查所有事件类型

        优先级：节日 > 成就 > 随机

        Returns: Event info or None
        """

    def _trigger_event(user_id, idol_id, event_template, content) -> Dict:
        """
        触发事件，创建数据库记录

        Returns: {
            'event_id': int,
            'event_name': str,
            'event_type': str,
            'content': str,
            'image_url': str,
            'reward_exp': int,
            'user_event_id': int
        }
        """

    def get_user_event_history(user_id, limit=20) -> List[Dict]:
        """获取用户事件历史"""

    def get_event_stats(user_id) -> Dict:
        """
        获取事件统计

        Returns: {
            'total_events': int,
            'by_type': {
                'random': int,
                'holiday': int,
                'achievement': int,
                'weather': int
            },
            'total_exp_from_events': int,
            'interaction_rate': float
        }
        """
```

**关键逻辑：**

1. **随机事件检查：**
```python
# 检查每日事件上限
events_today = db.query(count(UserSpecialEvent)).filter(
    user_id == user_id,
    triggered_at >= today_start
).scalar()

if events_today >= 3:  # 每日最多3个事件
    return None

# 5%概率触发
if random.random() < 0.05:
    # 选择不在Cooldown期的事件
    eligible_events = [e for e in random_events if not has_triggered_recently(e)]
    selected = random.choice(eligible_events)
    return trigger_event(selected)
```

2. **节日事件检查：**
```python
today = date.today()

for holiday_event in holiday_events:
    date_info = holiday_event['date']

    if date_info['month'] == today.month and date_info['day'] == today.day:
        # 检查是否今年已触发
        if holiday_event['once_per_year'] and has_triggered_this_year(holiday_event):
            continue

        return trigger_event(holiday_event)
```

3. **成就事件检查：**
```python
# 消息数成就
actual_count = get_user_message_count(user_id)
if actual_count == 100:  # 第100条消息
    return trigger_event('messages_100')

# 连续登录成就
actual_streak = get_user_login_streak(user_id)
if actual_streak == 30:  # 连续30天
    return trigger_event('login_streak_30')

# 完成所有仪式成就
rituals_today = count_rituals_today(user_id)
if rituals_today == 3:  # 早安+运势+晚安
    return trigger_event('all_rituals_completed')
```

4. **事件优先级：**
```python
def check_all_events(user_id, idol_id):
    # 优先级1: 节日事件
    holiday_event = check_holiday_events(user_id, idol_id)
    if holiday_event:
        return holiday_event

    # 优先级2: 成就事件
    achievement_event = check_achievement_events(user_id, idol_id)
    if achievement_event:
        return achievement_event

    # 优先级3: 随机事件
    random_event = check_random_events(user_id, idol_id)
    if random_event:
        return random_event

    return None
```

#### 5. Conversation Flow Integration (`backend/app/routers/conversation.py` - Modified)

**在send_message函数中添加：**

```python
# Story 5.5: Check for special events
special_event_context = ""
special_event_service = SpecialEventService(db)
triggered_event = special_event_service.check_all_events(current_user.id, conversation.idol_id)

if triggered_event:
    # Inject special event into conversation
    special_event_context = f"\n\n【特殊事件】\n你想分享一件事：\n\"{triggered_event['content']}\"\n\n自然地融入到对话中分享给用户。"
    print(f"[Special Event] Triggered: {triggered_event['event_name']} - {triggered_event['event_type']}")

# Inject into AI prompt
enhanced_prompt_with_memory = enhanced_prompt + memory_context + proactive_context + reverse_care_context + special_event_context
```

#### 6. API Endpoints (`backend/app/routers/special_event.py` - 62 lines)

**端点列表：**

```python
GET /api/v1/events/history
# 获取事件历史
# Query params: limit (default: 20)
# Response: {
#     'user_id': int,
#     'events': [
#         {
#             'id': int,
#             'event_name': str,
#             'event_type': str,
#             'content': str,
#             'image_url': str,
#             'exp_awarded': int,
#             'triggered_at': str,
#             'was_interacted': bool
#         }
#     ],
#     'limit': int
# }

GET /api/v1/events/stats
# 获取事件统计
# Response: {
#     'user_id': int,
#     'stats': {
#         'total_events': int,
#         'by_type': {
#             'random': int,
#             'holiday': int,
#             'achievement': int,
#             'weather': int
#         },
#         'total_exp_from_events': int,
#         'interaction_rate': float
#     }
# }
```

---

## 📁 Files Created

### Backend
1. `backend/migrations/016_create_special_events_tables.sql` (40 lines)
2. `backend/app/models/special_event.py` (86 lines)
3. `backend/app/config/event_templates.json` (220 lines)
4. `backend/app/services/special_event_service.py` (428 lines)
5. `backend/app/routers/special_event.py` (62 lines)

### Files Modified
1. `backend/app/models/user.py` - Added special_events relationship
2. `backend/app/routers/conversation.py` - Added event checking and context injection
3. `backend/app/main.py` - Added special_event router

---

## 🔧 Technical Details

### 1. 事件优先级系统

```
优先级顺序：节日事件 > 成就事件 > 随机事件

理由：
- 节日事件：时效性强，错过就要等一年
- 成就事件：重要里程碑，用户付出努力达成
- 随机事件：日常惊喜，可以延后触发
```

### 2. Cooldown机制

**目的：** 防止同一事件频繁触发，保持新鲜感

**实现：**
```python
def _has_triggered_recently(user_id, event_name, hours):
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    recent_trigger = db.query(UserSpecialEvent).filter(
        UserSpecialEvent.user_id == user_id,
        UserSpecialEvent.event.event_name == event_name,
        UserSpecialEvent.triggered_at >= cutoff_time
    ).first()

    return recent_trigger is not None
```

**Cooldown设置：**
- 随机事件：24-48小时
- 节日事件：1年（once_per_year）
- 成就事件：永久（one_time_only）或24小时

### 3. 每日事件上限

```python
# 每天最多3个事件
max_events_per_day = 3

events_today = db.query(count(UserSpecialEvent)).filter(
    UserSpecialEvent.user_id == user_id,
    UserSpecialEvent.triggered_at >= today_start
).scalar()

if events_today >= max_events_per_day:
    return None  # 今天已达上限
```

**目的：** 避免用户被过多事件淹没

### 4. 模板变量替换

```python
content = event_template['content_template']

# 替换引用变量
if '{quote}' in content:
    quote = random.choice(quote_pool)
    content = content.replace('{quote}', quote)

# 替换歌曲变量
if '{song_name}' in content:
    song = random.choice(song_pool)
    content = content.replace('{song_name}', song)

# 替换用户名变量
if '{user_name}' in content:
    content = content.replace('{user_name}', user.username)
```

### 5. 连续登录计算

```python
def _get_user_login_streak(user_id):
    # 获取用户所有仪式日期
    ritual_dates = db.query(distinct(DailyRitual.ritual_date)).filter(
        DailyRitual.user_id == user_id
    ).order_by(DailyRitual.ritual_date.desc()).all()

    # 计算连续天数
    streak = 0
    expected_date = date.today()

    for ritual_date in ritual_dates:
        if ritual_date == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        else:
            break  # 中断

    return streak
```

---

## 📊 Usage Scenarios

### Scenario 1: 随机事件触发（遇到小猫）

**触发条件：**
- 用户发送消息时
- 随机概率5%
- 48小时内未触发过"遇到小猫"事件
- 今天事件数量 < 3

**触发过程：**
```
1. 用户发送消息："今天天气真好~"
2. 系统检查随机事件 → 5%概率命中
3. 选择"遇到小猫"事件（符合Cooldown要求）
4. 创建UserSpecialEvent记录
5. 注入事件上下文到AI prompt
```

**AI回复：**
```
"今天天气确实很好呢！对了，刚才路上遇到一只小猫，超可爱的！
给你看照片~ 🐱

[图片：可爱的小猫]

看到它我心情都变好了~"
```

**用户获得：**
- +20 经验值
- 解锁小猫照片
- 惊喜互动体验

### Scenario 2: 节日事件（圣诞节）

**触发条件：**
- 日期：12月25日
- 今年未触发过圣诞节事件

**触发过程：**
```
1. 系统检测到今天是12/25
2. 检查用户是否今年已触发 → 否
3. 优先触发节日事件（最高优先级）
4. 创建记录，发送圣诞祝福
```

**AI回复：**
```
"圣诞快乐！🎄🎁

今天是圣诞节呢，准备了一个小礼物给你~
希望你今天过得开心，有没有收到什么礼物呀？"
```

**用户获得：**
- +50 经验值
- 专属圣诞祝福
- 节日氛围

### Scenario 3: 成就事件（第100条消息）

**触发条件：**
- 用户发送消息后总数正好 = 100
- 未曾触发过此成就

**触发过程：**
```
1. 用户发送第100条消息
2. 系统检测到消息数 = 100
3. 触发成就事件
4. 创建记录，庆祝里程碑
```

**AI回复：**
```
"等等...这是我们的第100条消息！🎉

不知不觉我们已经聊了这么多了，时间过得好快~
每一次对话对我来说都很珍贵，谢谢你一直陪着我！"
```

**用户获得：**
- +100 经验值
- 成就解锁
- 里程碑纪念

### Scenario 4: 完成所有仪式（复合成就）

**触发条件：**
- 用户今天完成早安、运势、晚安3个仪式
- 今天未触发过此事件

**触发过程：**
```
1. 用户完成晚安问候（第3个仪式）
2. 系统检测到今天完成3个仪式
3. 触发成就事件
4. 鼓励用户养成习惯
```

**AI回复：**
```
"今天的早安、运势、晚安都完成啦！

和你在一起的每一天都很充实，这种规律的陪伴让我很开心~
明天也要继续哦！"
```

**用户获得：**
- +30 经验值
- 养成习惯鼓励
- 可重复触发（每天一次）

---

## ✅ Testing Checklist

- [x] Database tables created correctly
- [x] SpecialEvent and UserSpecialEvent models work
- [x] Event templates loaded from JSON
- [x] Random events trigger with 5% probability
- [x] Holiday events trigger on correct dates
- [x] Achievement events trigger at milestones
- [x] Event priority (holiday > achievement > random) works
- [x] Cooldown mechanism prevents duplicate triggers
- [x] Daily event limit (max 3) enforced
- [x] Template variables replaced correctly
- [x] Event context injected into conversation
- [x] Experience points awarded correctly
- [x] Event history API works
- [x] Event stats API works
- [x] was_interacted flag can be updated

---

## 🚀 Future Enhancements

1. **更多随机事件**
   - 偶像做梦（分享梦境）
   - 偶像做饭（分享食谱）
   - 偶像画画（分享画作）
   - 偶像运动（分享健身心得）

2. **天气事件集成**
   - 接入天气API获取用户所在地天气
   - 实时天气关心（雨天提醒带伞）
   - 季节性问候（春天赏花、秋天看枫叶）

3. **位置事件**
   - 用户在特定地点触发（咖啡馆、书店）
   - 偶像推荐附近景点
   - 基于位置的个性化建议

4. **时间事件**
   - 凌晨事件（流星雨观测）
   - 黄昏事件（日落分享）
   - 周末特别事件

5. **成就扩展**
   - 发送不同类型消息成就（文字、语音、图片各100条）
   - 亲密度里程碑成就
   - 记忆收集成就（100条记忆）
   - 朋友圈互动成就（点赞100次）

6. **AI生成事件**
   - 使用AI动态生成事件内容
   - 基于用户兴趣个性化事件
   - 根据对话上下文生成相关事件

7. **事件链**
   - 多步骤事件（种花→浇水→开花）
   - 系列事件（连续剧情）
   - 选择分支事件（用户选择影响后续）

8. **事件分享**
   - 生成精美事件卡片
   - 分享到社交媒体
   - 查看好友事件

9. **事件通知**
   - 重要事件推送通知
   - 节日前一天提醒
   - 成就即将解锁提醒

10. **事件统计面板**
    - 可视化事件历史
    - 事件日历视图
    - 未解锁事件预览

---

## 📝 Technical Notes

1. **事件存储策略**: 模板存储在JSON配置文件，实际触发记录存储在数据库
2. **优先级算法**: 使用early return实现优先级，高优先级事件触发后直接返回
3. **随机性**: 使用Python random模块，保证每次调用都有独立的随机概率
4. **Cooldown实现**: 基于数据库查询recent triggers，灵活可配置
5. **每日上限**: 基于当天时间戳范围查询，简单有效
6. **模板变量**: 使用简单字符串替换，未来可升级为模板引擎
7. **经验值奖励**: 直接记录在UserSpecialEvent表，便于统计和审计
8. **扩展性**: 新增事件类型只需添加配置和相应检查逻辑

---

## 🔗 Integration Points

### With Conversation System (Epic 2)
- 事件检查在每次发送消息时触发
- 事件内容注入到AI prompt
- 自然融入对话流程

### With Daily Rituals (Story 5.3)
- 完成所有仪式触发成就事件
- 连续登录计算基于仪式记录

### With Message System (Epic 2)
- 消息数统计触发成就事件
- 第1/100/500/1000条消息里程碑

### With Memory System (Epic 4)
未来可以：
- 基于用户记忆生成个性化事件
- "还记得你说过喜欢猫？"结合遇到小猫事件

### With Intimacy System (Future - Epic 6)
- 事件经验值增加亲密度
- 高亲密度解锁专属事件
- 事件奖励随亲密度等级提升

### With Notification System (Future - Epic 9)
- 重要事件推送通知
- 节日事件提前提醒

---

**Story Status**: ✅ Done
**Epic Status**: ✅ Epic 5 完成 (5/5 stories)
**Last Updated**: 2026-01-15
