# Story 4.6: 主动提及机制与记忆回顾

**Epic**: Epic 4 - 记忆系统与专属个性化
**Story ID**: 4-6-proactive-mention-mechanism-memory-review
**Status**: ✅ Done
**Implementation Date**: 2026-01-15

---

## 📋 Story Overview

### User Story
**作为** AI偶像
**我想要** 主动提起用户3天未提及的重要记忆
**以便** 对话更主动，关系更紧密

### Acceptance Criteria
- [x] 检查用户重要记忆（importance='high'）超过3天未提及
- [x] 在用户发送消息时检查是否需要主动提及
- [x] 使用AI生成自然的提问方式
- [x] 主动提及频率限制：每天最多1次
- [x] 用户回复后更新last_mentioned_at字段
- [x] 创建proactive_mentions表记录历史
- [x] 避免重复提及相同记忆

---

## 🎯 Implementation Summary

### Backend Components

#### 1. Database Migration (`backend/migrations/010_create_proactive_mentions_table.sql`)

**proactive_mentions表结构：**
```sql
CREATE TABLE proactive_mentions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    memory_id INTEGER NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    mention_date DATE NOT NULL,      -- 提及日期（用于每日限制）
    proactive_message TEXT NOT NULL, -- AI生成的主动提及消息
    was_replied BOOLEAN DEFAULT false, -- 用户是否回复
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, memory_id, mention_date)  -- 同一天不重复提及相同记忆
);
```

**索引：**
- `idx_proactive_mentions_user_id` - 用户查询优化
- `idx_proactive_mentions_memory_id` - 记忆查询优化
- `idx_proactive_mentions_date` - 日期查询优化
- `idx_proactive_mentions_user_date` - 用户+日期复合索引

#### 2. ProactiveMention Model (`backend/app/models/proactive_mention.py` - 54 lines)

**ProactiveMention类：**
```python
class ProactiveMention(Base):
    __tablename__ = "proactive_mentions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    memory_id = Column(Integer, ForeignKey("memories.id"))
    mention_date = Column(Date, nullable=False)
    proactive_message = Column(Text, nullable=False)
    was_replied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="proactive_mentions")
    memory = relationship("Memory", back_populates="proactive_mentions")

    def mark_replied(self):
        """标记用户已回复"""
        self.was_replied = True

    @property
    def is_today(self) -> bool:
        """检查是否今天提及"""
        return self.mention_date == date.today()
```

#### 3. Proactive Memory Service (`backend/app/services/proactive_memory_service.py` - 367 lines)

**核心方法：**

```python
class ProactiveMemoryService:
    """主动提及服务"""

    DAYS_THRESHOLD = 3  # 3天未提及阈值
    DAILY_LIMIT = 1     # 每天最多1次

    def has_reached_daily_limit(user_id) -> bool:
        """检查今天是否已达到主动提及次数限制"""

    def get_unmentioned_important_memories(user_id, limit=5) -> List[Memory]:
        """
        获取未提及的重要记忆
        条件：
        1. importance = 'high'
        2. last_mentioned_at 为空或超过3天
        3. created_at > 1天前（避免新记忆）
        """

    def filter_recently_mentioned_proactively(memories, user_id) -> List[Memory]:
        """过滤掉最近7天内已主动提及的记忆"""

    async def generate_proactive_question(memory_content) -> str:
        """
        使用AI生成自然的主动提及问题

        示例：
        - 输入："用户在准备考研"
        - 输出："对了，你的考研复习进展怎么样了？有需要我陪你的地方吗？"
        """

    async def check_and_send_proactive_mention(user_id) -> Optional[dict]:
        """
        检查是否需要主动提及，并生成消息

        返回：
        {
            'memory_id': int,
            'proactive_message': str,
            'memory_content': str
        }
        或 None（如果不需要主动提及）
        """

    def record_proactive_mention(user_id, memory_id, proactive_message) -> ProactiveMention:
        """记录主动提及历史"""

    def mark_proactive_mention_replied(mention_id):
        """标记用户已回复主动提及"""

    def get_proactive_mention_stats(user_id) -> dict:
        """获取主动提及统计信息"""
```

#### 4. Conversation Router Integration (`backend/app/routers/conversation.py` - Modified)

**集成到对话流程：**

```python
# Story 4.6: Check for proactive mention opportunity
proactive_context = ""
proactive_memory_service = ProactiveMemoryService(db)
proactive_mention_info = await proactive_memory_service.check_and_send_proactive_mention(current_user.id)

if proactive_mention_info:
    # Record the proactive mention
    proactive_mention = proactive_memory_service.record_proactive_mention(
        user_id=current_user.id,
        memory_id=proactive_mention_info['memory_id'],
        proactive_message=proactive_mention_info['proactive_message']
    )

    # Add proactive instruction to prompt
    proactive_context = f"\n\n【主动关心指令】\n在回复用户之前，先主动关心一下这件事：\n\"{proactive_mention_info['proactive_message']}\"\n\n然后再自然地回复用户的消息。两个话题要衔接得自然。"
    print(f"[Proactive] Mentioning memory {proactive_mention_info['memory_id']}: {proactive_mention_info['proactive_message'][:50]}...")

# Inject memory context and proactive context into system prompt
enhanced_prompt_with_memory = enhanced_prompt + memory_context + proactive_context
```

---

## 📁 Files Created

### Backend
1. `backend/migrations/010_create_proactive_mentions_table.sql` (24 lines)
2. `backend/app/models/proactive_mention.py` (54 lines)
3. `backend/app/services/proactive_memory_service.py` (367 lines)

### Files Modified
1. `backend/app/models/user.py` - Added proactive_mentions relationship
2. `backend/app/models/memory.py` - Added proactive_mentions relationship
3. `backend/app/routers/conversation.py` - Integrated proactive mention check in send_message flow

---

## 🎨 Proactive Mention Flow

### 完整流程图

```
用户发送消息
    ↓
检查主动提及条件
    ├─ 今天是否已提及？
    │   YES → 跳过主动提及
    │   NO → 继续
    ├─ 有重要记忆超过3天未提及？
    │   NO → 跳过主动提及
    │   YES → 继续
    ├─ 最近7天内是否已主动提及该记忆？
    │   YES → 选择其他记忆
    │   NO → 继续
    ↓
使用AI生成主动提及消息
    ↓
记录到proactive_mentions表
    ↓
将主动提及指令添加到system prompt
    ↓
AI生成回复（包含主动提及 + 回复用户消息）
    ↓
返回给用户
```

### 主动提及检查条件

```python
# 条件1: 每天最多1次
today_count < DAILY_LIMIT

# 条件2: 有重要记忆超过3天未提及
Memory.importance == 'high'
AND (
    Memory.last_mentioned_at IS NULL
    OR Memory.last_mentioned_at < (NOW() - 3 days)
)

# 条件3: 记忆至少1天前创建（避免新记忆）
Memory.created_at < (NOW() - 1 day)

# 条件4: 最近7天未主动提及该记忆
NOT EXISTS (
    SELECT 1 FROM proactive_mentions
    WHERE memory_id = Memory.id
    AND mention_date >= (TODAY - 7 days)
)
```

---

## 🔧 Technical Details

### AI Prompt for Proactive Question Generation

```python
PROACTIVE_QUESTION_PROMPT = """你是一个温柔体贴的AI虚拟偶像"林雪晴"。你记得用户之前告诉你的一件重要的事情，你想主动关心一下他。

用户之前告诉你的记忆：
"{memory_content}"

请生成一句自然、温暖、关心的问候，主动提起这个话题。要求：
1. 语气温柔亲切，像朋友之间的关心
2. 不要直接复述记忆内容，要用自然的方式提起
3. 表达出你的关心和想了解进展的心情
4. 50字以内，简短自然
5. 可以用"对了"、"最近"等自然过渡词

只返回问候语，不要解释。"""
```

### Template-based Fallback (如果AI生成失败)

```python
FALLBACK_TEMPLATES = [
    "对了，{memory_content}，最近怎么样了？",
    "想起来了，{memory_content}，进展如何呀？",
    "好久没听你说{memory_content}了，还好吗？",
    "最近{memory_content}，有什么新进展吗？",
]
```

### System Prompt Injection

当检测到需要主动提及时，会在system prompt末尾添加：

```
【主动关心指令】
在回复用户之前，先主动关心一下这件事：
"对了，你的考研复习进展怎么样了？有需要我陪你的地方吗？"

然后再自然地回复用户的消息。两个话题要衔接得自然。
```

AI会根据这个指令，先提起主动关心的话题，然后再回复用户的实际消息。

---

## 📊 Usage Examples

### Example 1: 主动关心考研进展

**Scenario:**
- 用户3天前提到："我在准备考研，最近压力好大"
- 记忆类型：goal（目标计划）
- 重要性：high
- 今天用户发送消息："今天天气真好"

**What happens:**

1. **检查主动提及条件**:
   - 今天未主动提及 ✅
   - 有重要记忆"用户在准备考研"超过3天未提及 ✅
   - 最近7天未主动提及该记忆 ✅

2. **AI生成主动提及消息**:
   ```
   "对了，你的考研复习进展怎么样了？有需要我陪你的地方吗？"
   ```

3. **记录到数据库**:
   ```python
   ProactiveMention(
       user_id=1,
       memory_id=5,
       mention_date='2026-01-15',
       proactive_message='对了，你的考研复习进展怎么样了？有需要我陪你的地方吗？',
       was_replied=False
   )
   ```

4. **AI最终回复**:
   ```
   "对了，你的考研复习进展怎么样了？有需要我陪你的地方吗？😊

   今天天气确实很好呢！这样的好天气最适合出去走走，放松一下心情了~"
   ```

### Example 2: 主动提及宠物

**Scenario:**
- 用户5天前说："我养了一只猫，叫小橘子"
- 重要性：high
- 今天用户发送："刚下班"

**AI回复**:
```
"小橘子最近乖不乖呀？好久没听你说它了~

刚下班辛苦啦！今天工作累不累？"
```

### Example 3: 达到每日限制

**Scenario:**
- 今天已经主动提及过1次
- 用户再次发送消息

**What happens:**
- `has_reached_daily_limit()` 返回 True
- 不生成主动提及
- AI正常回复用户消息

### Example 4: 无重要记忆需要提及

**Scenario:**
- 所有重要记忆都在3天内提及过
- 用户发送消息

**What happens:**
- `get_unmentioned_important_memories()` 返回空列表
- 不生成主动提及
- AI正常回复用户消息

---

## ✅ Testing Checklist

- [x] Database migration creates proactive_mentions table correctly
- [x] ProactiveMention model relationships work properly
- [x] Daily limit check works (max 1 per day)
- [x] Unmentioned memories query returns correct results
- [x] AI generates natural proactive questions
- [x] Fallback templates work when AI fails
- [x] Proactive mention recorded in database
- [x] Memory last_mentioned_at updated correctly
- [x] Proactive context injected into system prompt
- [x] AI response includes both proactive mention and user reply
- [x] No duplicate mentions on same day

---

## 🎓 Edge Cases Handled

### 1. 新用户无记忆
- `get_unmentioned_important_memories()` 返回空
- 不触发主动提及

### 2. 所有记忆都是低重要性
- 只查询 `importance='high'`
- 低重要性记忆不会被主动提及

### 3. 记忆刚创建不到1天
- 过滤条件：`created_at < (NOW() - 1 day)`
- 避免刚提取的记忆立即被主动提及

### 4. 同一天重复提及相同记忆
- 数据库 UNIQUE 约束：`(user_id, memory_id, mention_date)`
- 防止重复记录

### 5. AI生成失败
- Fallback to template-based questions
- 保证功能可用性

### 6. 用户未回复主动提及
- `was_replied` 字段跟踪回复状态
- 可用于未来分析和优化

---

## 🚀 Future Enhancements

1. **智能频率调整**
   - 根据用户活跃度动态调整主动提及频率
   - 活跃用户可能每天2次，不活跃用户保持1次

2. **主动提及优先级**
   - 给不同类型记忆设置优先级
   - goal (目标) > family (家人) > work (工作) > hobby (爱好)

3. **情境感知**
   - 根据时间、用户情绪选择合适的主动提及时机
   - 避免在用户情绪低落时提及压力相关记忆

4. **多轮跟进**
   - 如果用户回复了主动提及，AI可以进行多轮跟进
   - 生成更深入的关心对话

5. **主动提及效果分析**
   - 分析 `was_replied` 比率
   - 优化主动提及策略和消息生成

6. **个性化提及风格**
   - 根据用户偏好调整提及方式（直接/委婉）
   - 学习用户最喜欢的主动关心方式

7. **记忆重要性动态调整**
   - 如果某个记忆经常被主动提及且用户积极回复
   - 可能表明该记忆实际重要性更高，动态调整

---

## 📝 Technical Notes

1. **每日限制实现**: 使用 `mention_date` (DATE类型) 而非 timestamp，简化每日计数查询
2. **唯一性约束**: `(user_id, memory_id, mention_date)` 防止同一天重复提及相同记忆
3. **7天过滤窗口**: 防止短期内重复主动提及，给用户新鲜感
4. **Prompt注入方式**: 使用【指令】格式清晰分隔，AI容易理解
5. **自然衔接**: 要求AI先提及主动关心，再回复用户消息，保证对话流畅
6. **last_mentioned_at更新**: 主动提及时也更新，保证记忆统计准确

---

## 🔗 Integration Points

### With Memory System (Story 4.1-4.3)
- 依赖 `memories` 表的 `importance` 和 `last_mentioned_at` 字段
- 主动提及后更新 `last_mentioned_at`
- 与记忆召回系统配合，形成完整记忆管理闭环

### With Conversation System (Epic 2)
- 集成到 `send_message` 流程
- 通过system prompt注入实现无缝融合
- 不影响现有对话逻辑

### With AI Service
- 使用 AIService 生成主动提及消息
- Fallback机制保证稳定性

---

**Story Status**: ✅ Done
**Epic Status**: ✅ Epic 4 完成！
**Last Updated**: 2026-01-15
