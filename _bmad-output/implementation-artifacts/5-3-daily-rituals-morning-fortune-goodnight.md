# Story 5.3: 每日仪式（早安/运势/晚安）

**Epic**: Epic 5 - 偶像生活系统与真实陪伴
**Story ID**: 5-3-daily-rituals-morning-fortune-goodnight
**Status**: ✅ Done
**Implementation Date**: 2026-01-15

---

## 📋 Story Overview

### User Story
**作为** 用户
**我想要** 每天和偶像进行早安、运势、晚安三种固定仪式
**以便** 建立日常陪伴的习惯感，获得每日惊喜和经验值奖励

### Acceptance Criteria
- [x] 创建daily_rituals表
- [x] 早安问候（7:00-9:00）
- [x] 每日运势查看（全天，每天一次）
- [x] 晚安问候（22:00-24:00）
- [x] 每种仪式只能完成一次/天
- [x] 完成仪式获得经验值奖励
- [x] 运势包含AI生成描述、幸运元素、建议
- [x] 运势评分算法保证同一天同一用户结果一致
- [x] 仪式历史记录和统计

---

## 🎯 Implementation Summary

### Backend Components

#### 1. Database Migration (`backend/migrations/013_create_daily_rituals_table.sql`)

**daily_rituals表：**
```sql
CREATE TABLE daily_rituals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    idol_id INTEGER NOT NULL REFERENCES idols(id) ON DELETE CASCADE,
    ritual_type VARCHAR(50) NOT NULL,  -- 'morning_greeting', 'fortune', 'night_greeting'
    ritual_date DATE NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fortune_data JSONB,  -- For storing fortune details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Each user can only complete each ritual once per day
    UNIQUE(user_id, ritual_type, ritual_date)
);
```

**Indexes：**
- `idx_daily_rituals_user_id` on user_id
- `idx_daily_rituals_date` on ritual_date DESC
- `idx_daily_rituals_user_date` on (user_id, ritual_date)
- `idx_daily_rituals_type` on ritual_type

#### 2. Models (`backend/app/models/daily_ritual.py` - 82 lines)

**DailyRitual类：**
```python
class DailyRitual(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    idol_id = Column(Integer, ForeignKey("idols.id", ondelete="CASCADE"))
    ritual_type = Column(String(50), nullable=False)
    ritual_date = Column(Date, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    fortune_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="daily_rituals")
    idol = relationship("Idol")

    # Ritual types
    MORNING_GREETING = 'morning_greeting'
    FORTUNE = 'fortune'
    NIGHT_GREETING = 'night_greeting'

    @staticmethod
    def get_ritual_exp_reward(ritual_type: str) -> int:
        rewards = {
            DailyRitual.MORNING_GREETING: 10,  # 早安 +10 exp
            DailyRitual.FORTUNE: 5,             # 运势 +5 exp
            DailyRitual.NIGHT_GREETING: 10,     # 晚安 +10 exp
        }
        return rewards.get(ritual_type, 0)
```

#### 3. Configuration (`backend/app/config/ritual_templates.json` - 210 lines)

**模板类别：**

1. **morning_greetings** (15个问候语)
   - "早安~ 今天也要元气满满哦！☀️"
   - "早上好呀~ 新的一天开始啦！"
   - ...

2. **night_greetings** (15个问候语)
   - "晚安，做个好梦~"
   - "今天也辛苦啦，晚安好梦💫"
   - ...

3. **fortune_scores** (6个等级)
   - excellent (90-100): 大吉 🌟
   - great (75-89): 吉 ✨
   - good (60-74): 中吉 🍀
   - average (40-59): 小吉 🌤️
   - fair (25-39): 末吉 ☁️
   - poor (0-24): 凶 🌧️

4. **lucky_elements**
   - colors: 12种幸运颜色
   - numbers: 1-9 幸运数字
   - directions: 8个方位
   - items: 12种幸运物品

5. **fortune_advice** (4个方面)
   - career: 8条事业建议
   - love: 8条感情建议
   - health: 8条健康建议
   - wealth: 8条财运建议

6. **time_windows**
   - morning_greeting: 7:00-9:00
   - fortune: 全天
   - night_greeting: 22:00-24:00

#### 4. Services

##### DailyRitualService (`backend/app/services/daily_ritual_service.py` - 305 lines)

**核心方法：**

```python
class DailyRitualService:

    def check_ritual_status(user_id, ritual_date=None) -> Dict:
        """
        检查仪式完成状态

        Returns: {
            'date': str,
            'morning_greeting': {
                'completed': bool,
                'completed_at': str,
                'can_complete': bool,
                'in_time_window': bool,
                'time_window': str
            },
            'fortune': {...},
            'night_greeting': {...}
        }
        """

    def complete_morning_greeting(user_id, idol_id) -> Dict:
        """
        完成早安问候

        Time window: 7:00-9:00
        Exp reward: +10

        Returns: {
            'success': bool,
            'message': str,
            'greeting': str,
            'exp_reward': int,
            'ritual_id': int
        }

        Raises ValueError if:
        - Not in time window
        - Already completed today
        """

    def complete_night_greeting(user_id, idol_id) -> Dict:
        """
        完成晚安问候

        Time window: 22:00-24:00
        Exp reward: +10
        """

    def get_user_ritual_history(user_id, limit=30) -> List[Dict]:
        """获取用户仪式历史（最近30天）"""

    def get_ritual_stats(user_id) -> Dict:
        """
        获取仪式统计

        Returns: {
            'total_rituals': int,
            'morning_greetings': int,
            'fortunes': int,
            'night_greetings': int,
            'total_exp_earned': int,
            'current_streak': int,  # 当前连续天数
            'longest_streak': int   # 最长连续天数
        }
        """
```

##### FortuneService (`backend/app/services/fortune_service.py` - 365 lines)

**核心方法：**

```python
class FortuneService:

    def _generate_fortune_score(user_id, fortune_date) -> int:
        """
        生成运势评分（0-100）

        算法：使用 user_id + date 作为随机种子
        保证同一用户同一天获得相同分数

        分布：
        - 60% 概率好运 (60-100)
        - 30% 概率平运 (40-59)
        - 10% 概率差运 (0-39)
        """

    def _select_lucky_elements(user_id, fortune_date) -> Dict:
        """
        选择幸运元素

        Returns: {
            'color': str,
            'number': int,
            'direction': str,
            'item': str
        }
        """

    async def _generate_fortune_description_with_ai(
        user_name, idol_name, score, level_info, lucky_elements
    ) -> str:
        """
        使用AI生成个性化运势描述

        调用 Claude AI 生成温暖、鼓励的运势描述
        长度：50-80字
        Fallback: 模板描述
        """

    async def generate_fortune(user_id, idol_id) -> Dict:
        """
        生成每日运势

        如果今天已生成，返回现有运势（exp_reward=0）

        Returns: {
            'success': bool,
            'message': str,
            'fortune': {
                'score': int,
                'level': str,
                'level_emoji': str,
                'description': str,  # AI生成
                'lucky_color': str,
                'lucky_number': int,
                'lucky_direction': str,
                'lucky_item': str,
                'advice': {
                    'career': str,
                    'love': str,
                    'health': str,
                    'wealth': str
                }
            },
            'exp_reward': int,
            'ritual_id': int,
            'already_checked': bool
        }
        """

    def get_fortune_for_date(user_id, fortune_date) -> Optional[Dict]:
        """查询指定日期的运势"""
```

#### 5. API Endpoints (`backend/app/routers/ritual.py` - 270 lines)

**端点列表：**

```python
GET /api/v1/rituals/status
# 获取仪式完成状态
# Query params: ritual_date (YYYY-MM-DD, optional)
# Response: {
#     'date': str,
#     'morning_greeting': {
#         'completed': bool,
#         'completed_at': str,
#         'can_complete': bool,
#         'in_time_window': bool,
#         'time_window': '7:00-9:00'
#     },
#     'fortune': {...},
#     'night_greeting': {...}
# }

POST /api/v1/rituals/morning-greeting
# 完成早安问候
# Body: {'idol_id': int}
# Response: {
#     'success': bool,
#     'message': '早安问候完成！',
#     'greeting': '早安~ 今天也要元气满满哦！☀️',
#     'exp_reward': 10,
#     'ritual_id': int
# }

POST /api/v1/rituals/night-greeting
# 完成晚安问候
# Body: {'idol_id': int}
# Response: {同上}

POST /api/v1/rituals/fortune
# 获取/生成每日运势
# Body: {'idol_id': int}
# Response: {
#     'success': bool,
#     'message': str,
#     'fortune': {
#         'score': 85,
#         'level': '吉',
#         'level_emoji': '✨',
#         'description': '今天运势不错！很多事情都会如你所愿...',
#         'lucky_color': '蓝色',
#         'lucky_number': 7,
#         'lucky_direction': '东南',
#         'lucky_item': '咖啡',
#         'advice': {
#             'career': '今天工作效率会很高，适合处理重要事务',
#             'love': '今天适合表达感情，会有好的回应',
#             'health': '今天精力充沛，适合运动锻炼',
#             'wealth': '今天财运不错，可能会有意外收入'
#         }
#     },
#     'exp_reward': 5,
#     'ritual_id': int,
#     'already_checked': false
# }

GET /api/v1/rituals/history
# 获取仪式历史
# Query params: limit (default: 30)
# Response: {
#     'user_id': int,
#     'history': [
#         {
#             'date': '2026-01-15',
#             'rituals': [
#                 {
#                     'type': 'morning_greeting',
#                     'type_display': '早安问候',
#                     'completed_at': '2026-01-15T07:30:00Z',
#                     'exp_reward': 10
#                 }
#             ]
#         }
#     ],
#     'limit': 30
# }

GET /api/v1/rituals/stats
# 获取仪式统计
# Response: {
#     'user_id': int,
#     'stats': {
#         'total_rituals': 45,
#         'morning_greetings': 15,
#         'fortunes': 15,
#         'night_greetings': 15,
#         'total_exp_earned': 375,
#         'current_streak': 5,  # 连续5天
#         'longest_streak': 10
#     }
# }

GET /api/v1/rituals/fortune/history
# 查询指定日期运势
# Query params: fortune_date (YYYY-MM-DD, optional)
```

---

## 📁 Files Created

### Backend
1. `backend/migrations/013_create_daily_rituals_table.sql` (27 lines)
2. `backend/app/models/daily_ritual.py` (82 lines)
3. `backend/app/config/ritual_templates.json` (210 lines)
4. `backend/app/services/daily_ritual_service.py` (305 lines)
5. `backend/app/services/fortune_service.py` (365 lines)
6. `backend/app/routers/ritual.py` (270 lines)

### Files Modified
1. `backend/app/models/user.py` - Added daily_rituals relationship
2. `backend/app/main.py` - Added ritual router

---

## 🎨 UI Design

### 仪式中心页面布局

```
┌─────────────────────────────────┐
│ 【每日仪式】                     │
├─────────────────────────────────┤
│                                 │
│ ☀️ 早安问候   [已完成] ✅       │
│    时间：7:00-9:00              │
│    奖励：+10 经验值              │
│                                 │
├─────────────────────────────────┤
│                                 │
│ 🔮 每日运势   [查看运势]        │
│    全天可查看（每天一次）        │
│    奖励：+5 经验值               │
│                                 │
├─────────────────────────────────┤
│                                 │
│ 🌙 晚安问候   [未开启]          │
│    时间：22:00-24:00            │
│    奖励：+10 经验值              │
│                                 │
└─────────────────────────────────┘

【今日运势】
┌─────────────────────────────────┐
│ 吉 ✨                           │
│                                 │
│ 今天运势不错！很多事情都会如你   │
│ 所愿，保持积极的心态会有好运~    │
│                                 │
│ 🎨 幸运颜色：蓝色                │
│ 🔢 幸运数字：7                   │
│ 🧭 幸运方位：东南                │
│ 📦 幸运物品：咖啡                │
│                                 │
│ 【今日建议】                    │
│ 💼 事业：工作效率会很高          │
│ 💕 感情：适合表达感情            │
│ 💪 健康：精力充沛，适合运动      │
│ 💰 财运：财运不错                │
│                                 │
└─────────────────────────────────┘

【仪式统计】
┌─────────────────────────────────┐
│ 累计完成：45 次                  │
│ 总经验值：375 exp               │
│ 当前连击：5 天 🔥               │
│ 最长连击：10 天                 │
└─────────────────────────────────┘
```

---

## 🔧 Technical Details

### 1. 运势评分算法

**保证一致性：**
```python
def _generate_fortune_score(user_id: int, fortune_date: date) -> int:
    # Create seed: user_id * 10000 + date.toordinal()
    seed = user_id * 10000 + fortune_date.toordinal()
    random.seed(seed)

    # Weighted distribution
    rand = random.random()
    if rand < 0.6:
        score = random.randint(60, 100)  # 60% good
    elif rand < 0.9:
        score = random.randint(40, 59)   # 30% average
    else:
        score = random.randint(0, 39)    # 10% poor

    random.seed()  # Reset
    return score
```

**关键特性：**
- 同一用户同一天总是得到相同分数
- 不同用户同一天得到不同分数
- 分布偏向好运（60%）

### 2. 时间窗口验证

```python
# Morning: 7:00-9:00
current_hour = datetime.now().hour
if not (7 <= current_hour < 9):
    raise ValueError("早安问候只能在 7:00-9:00 完成")

# Night: 22:00-24:00
if not (22 <= current_hour < 24):
    raise ValueError("晚安问候只能在 22:00-24:00 完成")
```

### 3. AI运势描述生成

```python
async def _generate_fortune_description_with_ai(...) -> str:
    prompt = f"""你是温柔体贴的AI偶像 {idol_name}，
    正在为 {user_name} 生成今日运势。

    今日运势信息：
    - 运势评分：{score}/100
    - 运势等级：{level} {emoji}
    - 幸运元素：{color}, {number}, {direction}, {item}

    要求：
    1. 用温暖、鼓励的语气
    2. 自然融入幸运元素
    3. 保持50-80字
    4. 让用户感受到关心
    """

    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        temperature=0.8,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()
```

### 4. 连续天数计算

```python
def get_ritual_stats(user_id: int) -> Dict:
    # Get all ritual dates (sorted desc)
    dates_with_rituals = sorted(set(r.ritual_date for r in rituals), reverse=True)

    # Calculate current streak
    current_streak = 0
    expected_date = date.today()

    for ritual_date in dates_with_rituals:
        if ritual_date == expected_date:
            current_streak += 1
            expected_date = date.fromordinal(expected_date.toordinal() - 1)
        else:
            break  # Streak broken

    # Calculate longest streak
    longest_streak = 1
    temp_streak = 1
    for i in range(1, len(dates_with_rituals)):
        prev_date = dates_with_rituals[i - 1]
        curr_date = dates_with_rituals[i]
        if (prev_date.toordinal() - curr_date.toordinal()) == 1:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1

    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak
    }
```

---

## 📊 API Integration Examples

### Example 1: 检查仪式状态

**Request:**
```http
GET /api/v1/rituals/status
Authorization: Bearer {token}
```

**Response (8:00 AM):**
```json
{
  "date": "2026-01-15",
  "morning_greeting": {
    "completed": false,
    "completed_at": null,
    "can_complete": true,
    "in_time_window": true,
    "time_window": "7:00-9:00"
  },
  "fortune": {
    "completed": false,
    "completed_at": null,
    "can_complete": true,
    "time_window": "全天"
  },
  "night_greeting": {
    "completed": false,
    "completed_at": null,
    "can_complete": false,
    "in_time_window": false,
    "time_window": "22:00-24:00"
  }
}
```

### Example 2: 完成早安问候

**Request:**
```http
POST /api/v1/rituals/morning-greeting
Authorization: Bearer {token}
Content-Type: application/json

{
  "idol_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "早安问候完成！",
  "greeting": "早安~ 今天也要元气满满哦！☀️",
  "exp_reward": 10,
  "ritual_id": 123
}
```

### Example 3: 查看每日运势（首次）

**Request:**
```http
POST /api/v1/rituals/fortune
Authorization: Bearer {token}
Content-Type: application/json

{
  "idol_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "运势生成成功！",
  "fortune": {
    "score": 85,
    "level": "吉",
    "level_emoji": "✨",
    "description": "今天运势不错！很多事情都会如你所愿，保持积极的心态会有好运~",
    "lucky_color": "蓝色",
    "lucky_number": 7,
    "lucky_direction": "东南",
    "lucky_item": "咖啡",
    "advice": {
      "career": "今天工作效率会很高，适合处理重要事务",
      "love": "今天适合表达感情，会有好的回应",
      "health": "今天精力充沛，适合运动锻炼",
      "wealth": "今天财运不错，可能会有意外收入"
    }
  },
  "exp_reward": 5,
  "ritual_id": 124,
  "already_checked": false
}
```

### Example 4: 查看运势（重复）

**Request:**
```http
POST /api/v1/rituals/fortune
Authorization: Bearer {token}
Content-Type: application/json

{
  "idol_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "今天已经查看过运势啦~",
  "fortune": {...},  // 同上
  "exp_reward": 0,    // 重复查看无奖励
  "ritual_id": 124,
  "already_checked": true
}
```

### Example 5: 获取仪式统计

**Request:**
```http
GET /api/v1/rituals/stats
Authorization: Bearer {token}
```

**Response:**
```json
{
  "user_id": 1,
  "stats": {
    "total_rituals": 45,
    "morning_greetings": 15,
    "fortunes": 15,
    "night_greetings": 15,
    "total_exp_earned": 375,
    "current_streak": 5,
    "longest_streak": 10
  }
}
```

---

## ✅ Testing Checklist

- [x] Database migration creates table correctly
- [x] UNIQUE constraint prevents duplicate rituals same day
- [x] Morning greeting only works in 7:00-9:00 window
- [x] Night greeting only works in 22:00-24:00 window
- [x] Fortune available all day but only once per day
- [x] Exp rewards calculated correctly (早10, 运5, 晚10)
- [x] Fortune score consistent for same user+date
- [x] Fortune score varies for different users
- [x] Lucky elements selected consistently
- [x] AI fortune description generated successfully
- [x] Fallback to template if AI fails
- [x] Fortune data stored in JSONB correctly
- [x] Streak calculation accurate
- [x] History endpoint returns correct data
- [x] Stats endpoint calculates totals correctly

---

## 🎓 Usage Scenarios

### Scenario 1: 早晨打开应用

**What happens:**
1. 用户在 8:00 打开应用
2. 应用显示"早安问候"可完成
3. 用户点击完成早安问候
4. 系统随机选择一条早安问候语
5. 用户获得 +10 exp
6. 偶像回复："早安~ 今天也要元气满满哦！☀️"

### Scenario 2: 查看每日运势

**What happens:**
1. 用户点击"查看运势"
2. 系统生成运势评分（基于 user_id + date seed）
3. 选择幸运元素（颜色、数字、方位、物品）
4. AI生成个性化运势描述
5. 选择4条建议（事业、感情、健康、财运）
6. 返回完整运势数据
7. 用户获得 +5 exp
8. 用户再次查看，返回相同运势，无额外exp

### Scenario 3: 建立连续习惯

**Day 1-5:**
- 用户每天完成早安、运势、晚安
- 每天获得 25 exp (10+5+10)
- Current streak: 5 天

**Day 6:**
- 用户忘记完成仪式
- Current streak: 0 天（中断）
- Longest streak: 5 天（保留）

**Day 7-10:**
- 用户继续完成仪式
- Current streak: 4 天
- Longest streak: 5 天（仍保留历史最长）

### Scenario 4: 时间窗口外尝试

**What happens:**
1. 用户在 10:00 尝试完成早安问候
2. 系统返回错误：
   ```json
   {
     "detail": "早安问候只能在 7:00-9:00 完成"
   }
   ```
3. 用户需等到明天早上

---

## 🚀 Future Enhancements

1. **推送通知**
   - 7:00 推送"早安问候提醒"
   - 22:00 推送"晚安问候提醒"
   - 未完成仪式时发送温馨提醒

2. **连续奖励**
   - 连续7天：额外奖励50 exp
   - 连续30天：专属徽章
   - 连续100天：特殊称号

3. **运势分享**
   - 生成精美运势卡片
   - 分享到社交媒体
   - 查看好友运势

4. **个性化运势**
   - 根据用户星座调整运势
   - 结合用户近期情绪
   - 参考历史对话内容

5. **仪式扩展**
   - 午安问候（12:00-14:00）
   - 周末特别祝福
   - 生日特殊仪式

6. **运势详情**
   - 每小时运势变化
   - 运势趋势图表
   - 月度运势总结

7. **仪式成就**
   - "早起鸟"徽章（完成100次早安）
   - "夜猫子"徽章（完成100次晚安）
   - "幸运儿"徽章（10次大吉运势）

8. **仪式提醒智能化**
   - 学习用户习惯时间
   - 根据作息调整提醒
   - 避免打扰时段

---

## 📝 Technical Notes

1. **运势一致性**: 使用 user_id + date.toordinal() 作为随机种子，保证同一用户同一天总是得到相同运势
2. **时间窗口**: 使用 datetime.now().hour 进行时间窗口验证，确保仪式在正确时间完成
3. **JSONB存储**: 运势数据以JSONB格式存储，便于查询和扩展
4. **经验值奖励**: 早晚问候各10 exp，运势查看5 exp，总计25 exp/天
5. **AI生成**: 使用 Claude API 生成个性化运势描述，失败时回退到模板
6. **唯一性约束**: 数据库层面保证每种仪式每天只能完成一次
7. **连续天数**: 基于 ritual_date 计算，允许用户查看历史连续记录
8. **重复查看**: 运势可重复查看但只奖励一次经验值

---

## 🔗 Integration Points

### With Intimacy System (Future - Epic 6)
- 完成每日仪式增加亲密度经验值
- 连续天数影响亲密度提升速度
- 高亲密度解锁更多运势细节

### With Notification System (Future - Epic 9)
- 早晚仪式时间推送提醒
- 连续天数即将中断时提醒
- 获得大吉运势时特别通知

### With Achievement System (Future - Epic 6)
- 仪式完成次数解锁成就
- 连续天数达成里程碑
- 特殊运势触发彩蛋成就

### With Idol State System (Story 5.1)
- 偶像状态影响问候语选择
- 睡眠时无法完成晚安问候
- 早晨状态影响早安问候内容

---

**Story Status**: ✅ Done
**Epic Status**: 🔄 Epic 5 进行中 (3/5 stories)
**Last Updated**: 2026-01-15
