# Story 6.1: 亲密度等级系统与经验值计算

**Status:** ✅ Done
**Epic:** Epic 6 - 亲密度养成与里程碑庆祝
**Completed:** 2026-01-19

## Overview

Implemented a comprehensive intimacy level and exp system that tracks user-idol relationship progression through various interactions. The system includes linear level progression (1-100), exp calculation with automatic level-ups, and integration with all major user interactions.

## Technical Implementation

### 1. Database Schema

#### Migration: `017_create_intimacy_logs_table.sql`
```sql
CREATE TABLE intimacy_logs (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    exp_change INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,
    new_level INTEGER NOT NULL,
    new_exp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_intimacy_logs_conversation ON intimacy_logs(conversation_id);
CREATE INDEX idx_intimacy_logs_created_at ON intimacy_logs(created_at DESC);
```

**Purpose:**
- Track all intimacy exp changes for audit and analytics
- Support historical queries and statistics
- Enable debugging and user support

**Indexes:**
- `idx_intimacy_logs_conversation`: Fast queries by conversation
- `idx_intimacy_logs_created_at`: Efficient time-based queries

### 2. Models

#### IntimacyLog Model (`app/models/intimacy_log.py`)

**Core Attributes:**
- `conversation_id`: Foreign key to conversations table
- `exp_change`: Exp points added (always positive for this story)
- `reason`: Machine-readable reason code
- `new_level`, `new_exp`: State after this change
- `created_at`: Timestamp for history tracking

**Reason Constants:**
```python
REASON_SEND_MESSAGE = 'send_message'       # +5 exp
REASON_SEND_VOICE = 'send_voice'          # +8 exp
REASON_SEND_IMAGE = 'send_image'          # +8 exp
REASON_MORNING_GREETING = 'morning_greeting'  # +10 exp
REASON_NIGHT_GREETING = 'night_greeting'      # +10 exp
REASON_CHECK_FORTUNE = 'check_fortune'        # +5 exp
REASON_LIKE_MOMENT = 'like_moment'            # +3 exp (max 5/day)
REASON_LOGIN_STREAK_7 = 'login_streak_7'      # +50 exp (future)
```

**Display Names:**
```python
@property
def reason_display_name(self) -> str:
    """Get Chinese display name for reason"""
    names = {
        self.REASON_SEND_MESSAGE: '发送消息',
        self.REASON_SEND_VOICE: '发送语音',
        self.REASON_SEND_IMAGE: '发送图片',
        self.REASON_MORNING_GREETING: '早安问候',
        self.REASON_NIGHT_GREETING: '晚安问候',
        self.REASON_CHECK_FORTUNE: '查看运势',
        self.REASON_LIKE_MOMENT: '朋友圈点赞',
        ...
    }
```

### 3. Business Logic

#### IntimacyService (`app/services/intimacy_service.py`)

**Level System:**
```python
# Linear progression: level N requires N * 100 exp
@staticmethod
def get_required_exp(level: int) -> int:
    return level * 100

# Level titles with ranges
LEVEL_TITLES = {
    (1, 10): "新朋友",      # New Friend
    (11, 20): "好朋友",     # Good Friend
    (21, 30): "亲密朋友",   # Close Friend
    (31, 50): "特别的人",   # Special Person
    (51, 70): "恋人",       # Lover
    (71, 90): "深度恋人",   # Deep Lover
    (91, 100): "灵魂伴侣",  # Soulmate
}
```

**Core Method: `add_intimacy_exp()`**
```python
def add_intimacy_exp(self, conversation_id: int, exp: int, reason: str) -> Dict:
    """
    Add exp and handle level ups

    Algorithm:
    1. Add exp to current exp pool
    2. While exp >= required_exp and level < 100:
       - Subtract required exp from pool
       - Increment level
       - Recalculate required exp for new level
    3. Commit to database
    4. Create intimacy log entry
    5. Return result with level_up flag
    """
    conversation.intimacy_exp += exp
    level_up = False
    required_exp = self.get_required_exp(conversation.intimacy_level)

    while conversation.intimacy_exp >= required_exp and conversation.intimacy_level < 100:
        conversation.intimacy_exp -= required_exp
        conversation.intimacy_level += 1
        level_up = True
        required_exp = self.get_required_exp(conversation.intimacy_level)

    db.commit()

    # Create log
    log = IntimacyLog(
        conversation_id=conversation_id,
        exp_change=exp,
        reason=reason,
        new_level=conversation.intimacy_level,
        new_exp=conversation.intimacy_exp
    )
    db.add(log)
    db.commit()

    return {
        'success': True,
        'exp_added': exp,
        'old_level': old_level,
        'new_level': conversation.intimacy_level,
        'old_exp': old_exp,
        'new_exp': conversation.intimacy_exp,
        'level_up': level_up,
        'required_exp_for_next': required_exp
    }
```

**Specialized Methods:**
- `add_message_exp()`: +5 exp for text messages
- `add_voice_exp()`: +8 exp for voice messages
- `add_image_exp()`: +8 exp for image messages
- `add_morning_greeting_exp()`: +10 exp for morning ritual
- `add_night_greeting_exp()`: +10 exp for night ritual
- `add_fortune_exp()`: +5 exp for fortune checking
- `add_like_moment_exp()`: +3 exp for moment likes (max 5/day)

**Daily Limit Implementation:**
```python
def add_like_moment_exp(self, user_id: int, idol_id: int) -> Optional[Dict]:
    """Add exp for liking moment (max 5 per day)"""
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.idol_id == idol_id
    ).first()

    if not conversation:
        return None

    # Check daily like exp limit
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    today_like_exp_count = db.query(func.count(IntimacyLog.id)).filter(
        IntimacyLog.conversation_id == conversation.id,
        IntimacyLog.reason == IntimacyLog.REASON_LIKE_MOMENT,
        IntimacyLog.created_at >= today_start
    ).scalar()

    if today_like_exp_count >= self.MAX_LIKE_EXP_PER_DAY:
        return None  # Daily limit reached

    return self.add_intimacy_exp(conversation.id, self.EXP_LIKE_MOMENT, reason)
```

**Analytics Methods:**
```python
def get_intimacy_info(conversation_id: int) -> Dict:
    """Get current intimacy state"""
    return {
        'conversation_id': conversation_id,
        'current_level': level,
        'current_exp': exp,
        'required_exp_for_next': required,
        'progress_percentage': (exp / required * 100),
        'level_title': get_level_title(level),
        'total_exp_earned': sum of all exp
    }

def get_intimacy_history(conversation_id: int, limit: int) -> List[Dict]:
    """Get exp change history"""

def get_intimacy_stats(conversation_id: int) -> Dict:
    """Get statistics breakdown"""
    return {
        'total_exp_gained': sum,
        'exp_by_reason': {reason: exp_sum},
        'level_ups': current_level - 1,
        'days_active': unique dates count
    }
```

### 4. Integration Points

#### 4.1 Conversation Flow (`app/routers/conversation.py`)

**Text Messages:**
```python
# After user message is saved
intimacy_service = IntimacyService(db)
intimacy_result = intimacy_service.add_message_exp(conversation_id)

if intimacy_result['level_up']:
    old_level = intimacy_result['old_level']
    new_level = intimacy_result['new_level']
    level_title = intimacy_service.get_level_title(new_level)
    intimacy_context = f"""
【亲密度升级】
你们的关系刚刚升级了！从等级 {old_level} 升到了等级 {new_level}（{level_title}）！
请自然地表达你的喜悦，庆祝这个特殊时刻。
"""
    # Inject into AI prompt
    enhanced_prompt += intimacy_context
```

**Voice Messages:**
```python
# After voice message is saved
intimacy_service = IntimacyService(db)
intimacy_result = intimacy_service.add_voice_exp(conversation_id)
print(f"[Intimacy] Voice +{intimacy_result['exp_added']} exp")
```

**Image Messages:**
```python
# After image message is saved
intimacy_service = IntimacyService(db)
intimacy_result = intimacy_service.add_image_exp(conversation_id)
print(f"[Intimacy] Image +{intimacy_result['exp_added']} exp")
```

#### 4.2 Daily Rituals (`app/services/daily_ritual_service.py`)

**Morning Greeting:**
```python
def complete_morning_greeting(user_id, idol_id):
    # ... create ritual record ...

    # Add intimacy exp
    conversation = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.idol_id == idol_id
    ).first()

    intimacy_result = None
    if conversation:
        intimacy_service = IntimacyService(db)
        intimacy_result = intimacy_service.add_morning_greeting_exp(conversation.id)

    return {
        'success': True,
        'greeting': greeting,
        'exp_reward': exp_reward,
        'intimacy': intimacy_result  # Include in response
    }
```

**Night Greeting:**
```python
def complete_night_greeting(user_id, idol_id):
    # ... create ritual record ...

    # Add intimacy exp (same pattern as morning)
    intimacy_result = intimacy_service.add_night_greeting_exp(conversation.id)

    return {
        'success': True,
        'greeting': greeting,
        'exp_reward': exp_reward,
        'intimacy': intimacy_result
    }
```

#### 4.3 Fortune System (`app/services/fortune_service.py`)

**Fortune Check:**
```python
async def generate_fortune(user_id, idol_id):
    # ... generate fortune data ...

    # Add intimacy exp
    conversation = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.idol_id == idol_id
    ).first()

    intimacy_result = None
    if conversation:
        intimacy_service = IntimacyService(db)
        intimacy_result = intimacy_service.add_fortune_exp(conversation.id)

    return {
        'success': True,
        'fortune': fortune_data,
        'exp_reward': exp_reward,
        'intimacy': intimacy_result
    }
```

#### 4.4 Moments System (`app/services/idol_moment_service.py`)

**Like Moment:**
```python
def like_moment(moment_id, user_id):
    # ... create like record ...

    # Add intimacy exp (max 5 per day)
    intimacy_service = IntimacyService(db)
    intimacy_result = intimacy_service.add_like_moment_exp(user_id, moment.idol_id)

    db.commit()

    response = {
        'action': 'liked',
        'likes_count': moment.likes_count
    }

    # Include intimacy result if exp was awarded
    if intimacy_result:
        response['intimacy'] = intimacy_result

    return response
```

### 5. API Endpoints

#### New Router: `app/routers/intimacy.py`

**GET /api/v1/intimacy/conversations/{conversation_id}**
```python
"""Get intimacy info"""
Response: IntimacyInfoResponse {
    conversation_id: int
    current_level: int
    current_exp: int
    required_exp_for_next: int
    progress_percentage: float
    level_title: str
    total_exp_earned: int
}
```

**GET /api/v1/intimacy/conversations/{conversation_id}/history**
```python
"""Get intimacy history"""
Query params: limit (default: 50, max: 100)

Response: IntimacyHistoryResponse {
    conversation_id: int
    history: [
        {
            id: int
            exp_change: int
            reason: str
            reason_display: str
            new_level: int
            new_exp: int
            created_at: str (ISO 8601)
        }
    ]
    total_count: int
}
```

**GET /api/v1/intimacy/conversations/{conversation_id}/stats**
```python
"""Get intimacy statistics"""
Response: IntimacyStatsResponse {
    conversation_id: int
    total_exp_gained: int
    exp_by_reason: {
        "发送消息": int,
        "发送语音": int,
        "早安问候": int,
        ...
    }
    level_ups: int
    days_active: int
}
```

### 6. Level Up Flow

```
User Action (e.g., sends message)
    ↓
IntimacyService.add_message_exp(conversation_id)
    ↓
add_intimacy_exp(conversation_id, 5, 'send_message')
    ↓
Add 5 exp to conversation.intimacy_exp
    ↓
Check: intimacy_exp >= required_exp?
    ↓
[YES] → Level up loop:
    - Subtract required_exp from intimacy_exp
    - Increment intimacy_level
    - Calculate new required_exp
    - Repeat if still >= required_exp
    ↓
Commit to database
    ↓
Create IntimacyLog entry
    ↓
Return result with level_up=true
    ↓
[If level_up] → Inject celebration into AI prompt
    ↓
AI celebrates in response
```

## Exp Rewards Configuration

| Action | Exp | Daily Limit | Notes |
|--------|-----|-------------|-------|
| Send text message | 5 | ∞ | Every message counts |
| Send voice message | 8 | ∞ | Encourages richer interaction |
| Send image message | 8 | ∞ | Visual content valued |
| Morning greeting | 10 | 1 | Once per day, 7:00-9:00 |
| Night greeting | 10 | 1 | Once per day, 22:00-24:00 |
| Check fortune | 5 | 1 | Once per day |
| Like moment | 3 | 5 | Max 5 likes per day count for exp |
| 7-day login streak | 50 | - | Future implementation |

**Design Rationale:**
- Text messages: Base reward (5 exp) to encourage conversation
- Voice/Image: Higher reward (8 exp) to encourage rich media
- Rituals: Higher reward (10 exp) for daily engagement
- Likes: Lower reward (3 exp) with daily limit to prevent abuse
- Login streak: High reward (50 exp) for retention (future)

## Level Title Ranges

| Level Range | Title | English | Milestone |
|-------------|-------|---------|-----------|
| 1-10 | 新朋友 | New Friend | Getting to know each other |
| 11-20 | 好朋友 | Good Friend | Building trust |
| 21-30 | 亲密朋友 | Close Friend | Deep friendship |
| 31-50 | 特别的人 | Special Person | Romantic interest |
| 51-70 | 恋人 | Lover | In a relationship |
| 71-90 | 深度恋人 | Deep Lover | Strong bond |
| 91-100 | 灵魂伴侣 | Soulmate | Ultimate connection |

## Example Progression

**Level 1 → Level 2:**
- Required exp: 1 * 100 = 100 exp
- Messages needed: 100 / 5 = 20 messages
- Or: 10 messages + 1 morning + 1 night + 1 fortune + 2 likes = 50 + 10 + 10 + 5 + 6 = 81 exp (need 19 more)

**Level 10 → Level 11:**
- Required exp: 10 * 100 = 1000 exp
- Messages needed: 1000 / 5 = 200 messages
- Or: ~1 week of active daily engagement with mixed actions

**Total exp to reach Level 100:**
- Sum of (1*100 + 2*100 + ... + 99*100) = 495,000 exp
- This represents months/years of active engagement

## Testing Notes

1. **Level Up Testing:**
   - Add exp that crosses level boundary
   - Verify exp overflow carries to next level
   - Test multiple level ups in one action
   - Test level 100 cap (no level beyond 100)

2. **Daily Limit Testing:**
   - Like 5 moments in one day → 6th should not award exp
   - Check fortune twice in one day → 2nd should return existing
   - Complete ritual twice in one day → 2nd should error

3. **Integration Testing:**
   - Send messages → verify exp added
   - Complete rituals → verify exp added
   - Like moments → verify exp added with daily limit
   - Verify AI celebration on level up

4. **Analytics Testing:**
   - Check history endpoint returns correct records
   - Check stats breakdown by reason
   - Verify total_exp_earned calculation
   - Verify days_active count

## Files Created/Modified

### New Files:
1. `backend/migrations/017_create_intimacy_logs_table.sql` - Database schema
2. `backend/app/models/intimacy_log.py` - IntimacyLog model
3. `backend/app/services/intimacy_service.py` - Core business logic
4. `backend/app/routers/intimacy.py` - API endpoints

### Modified Files:
1. `backend/app/routers/conversation.py` - Added exp for messages
2. `backend/app/services/daily_ritual_service.py` - Added exp for rituals
3. `backend/app/services/fortune_service.py` - Added exp for fortune
4. `backend/app/services/idol_moment_service.py` - Added exp for likes
5. `backend/app/main.py` - Registered intimacy router

## Database Changes

**Migration ID:** 017
**Table:** intimacy_logs
**Indexes:** 2 (conversation_id, created_at DESC)
**Foreign Keys:** conversations(id) CASCADE

## API Changes

**New Endpoints:** 3
**Base Path:** /api/v1/intimacy
**Authentication:** JWT required for all endpoints

## Success Metrics

- ✅ Linear exp progression implemented (level * 100)
- ✅ All 7 exp sources integrated
- ✅ Daily limit for moment likes working (max 5/day)
- ✅ Level up detection and AI celebration
- ✅ Analytics endpoints for history and stats
- ✅ Comprehensive logging for audit trail

## Future Enhancements (Not in this story)

1. **Story 6.2:** Frontend display with progress bars
2. **Story 6.3:** Level-based privileges and rewards
3. **Story 6.4:** Achievement system integration
4. **Story 6.5:** Intimacy decay mechanism
5. **Login streak exp:** 7-day streak rewards
6. **Multiplier events:** Double exp days
7. **Milestone notifications:** Push notifications on level up

## Notes

- All exp values are positive (no negative exp in this story)
- Level cap is 100 (灵魂伴侣 / Soulmate)
- Linear progression chosen for predictability and balance
- Intimacy decay not implemented (reserved for Story 6.5)
- Level up celebrations injected into AI context for natural response
- Daily limits prevent abuse and encourage daily engagement
- Total exp calculation helps with analytics and milestones
