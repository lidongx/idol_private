# Story 2.4: 打字动画与消息状态

Status: done

> **⏱️ 实际开发时间:** ~0.5天
> **✅ 完成日期:** 2026-01-13

## Story

As a **用户**,
I want **看到偶像正在输入的动画和消息的发送状态**,
So that **获得更真实的聊天体验和及时的反馈**。

## Acceptance Criteria

### AC1: 消息状态管理（Backend）
- **Given** 需要追踪消息状态
- **When** 消息在系统中流转
- **Then** 支持以下状态：
  - `sending`: 正在发送（前端临时状态）
  - `sent`: 已发送到服务器
  - `delivered`: 已送达（AI回复已生成）
  - `read`: 已读（用户查看了消息）
  - `failed`: 发送失败（前端错误处理）
- **And** 创建消息状态更新API端点

### AC2: 批量消息状态更新API
- **Given** 用户查看对话
- **When** 调用状态更新API
- **Then** 创建 `PUT /api/v1/conversations/{id}/messages/status`
- **And** 支持批量更新多条消息状态
- **And** 只能更新偶像发送的消息（sender_type='idol'）
- **And** 只能更新自己对话中的消息
- **And** 返回更新的消息数量

### AC3: 打字动画指示器Widget（Flutter）
- **Given** 偶像正在生成回复
- **When** 前端等待AI响应
- **Then** 创建 `TypingIndicator` Widget
- **And** 显示3个圆点的弹跳动画
- **And** 动画流畅自然（错峰弹跳）
- **And** 使用Material Design配色
- **And** 动画循环播放直到收到回复

### AC4: 消息状态指示器Widget（Flutter）
- **Given** 需要显示消息状态
- **When** 渲染用户消息
- **Then** 创建 `MessageStatusIndicator` Widget
- **And** 显示不同状态的图标：
  - `sent`: 单勾 ✓（灰色）
  - `delivered`: 双勾 ✓✓（灰色）
  - `read`: 双勾 ✓✓（蓝色/主题色）
  - `sending`: 加载圆圈
  - `failed`: 错误图标（红色）
- **And** 只在用户消息上显示（偶像消息不显示）

### AC5: ConversationService状态更新方法
- **Given** 需要标记消息为已读
- **When** Flutter层调用服务
- **Then** 添加 `updateMessageStatus()` 方法
- **And** 接收conversation_id, message_ids, status参数
- **And** 发送PUT请求到后端API
- **And** 返回更新成功的消息数量
- **And** 处理认证和网络错误

---

## Implementation Details

### Message Status State Machine

```
Message Status Flow:

User sends message:
  sending → sent → delivered → read
     ↓        ↓        ↓         ↓
   (local)  (API)   (AI reply) (user viewed)

Idol sends reply:
  (generated) → delivered → read
                    ↓         ↓
                  (API)   (user viewed)

Failed case:
  sending → failed
     ↓
  (network error)
```

### Typing Animation Timing

```
Typing Animation (1.2s cycle, 3 dots):

Dot 1: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       0.0s   ↑   ↓         (bounce)

Dot 2: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
             0.2s   ↑   ↓   (staggered)

Dot 3: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   0.4s   ↑   ↓ (staggered)

Each dot:
- Rises 8px over 0.2s (easeOut)
- Falls 8px over 0.2s (easeIn)
- Rests for 0.8s
- Total cycle: 1.2s, repeats infinitely
```

### Status Icon Design

| Status | Icon | Color | Meaning |
|--------|------|-------|---------|
| sending | ⏳ CircularProgress | Grey (60%) | Sending to server |
| sent | ✓ Single Check | Grey (60%) | Server received |
| delivered | ✓✓ Double Check | Grey (60%) | AI replied |
| read | ✓✓ Double Check | Blue/Primary (100%) | User viewed |
| failed | ❌ Error | Red | Send failed |

---

## Files Created/Modified

### Backend

1. **backend/app/schemas/conversation.py** (Updated +17 lines)
   - `MessageStatusUpdate`: Request schema for status updates
   - `MessageStatusUpdateResponse`: Response schema with update count

2. **backend/app/routers/conversation.py** (Updated +59 lines)
   - Import new schemas
   - `PUT /conversations/{id}/messages/status` endpoint
   - Batch update message status
   - Only update idol messages
   - Validate user owns conversation

### Frontend

1. **lib/features/conversation/widgets/typing_indicator.dart** (NEW, 114 lines)
   - `TypingIndicator` StatefulWidget
   - AnimationController with 1.2s cycle
   - 3 staggered dot animations
   - Material Design styling
   - Customizable dot color and size

2. **lib/features/conversation/widgets/message_status_indicator.dart** (NEW, 95 lines)
   - `MessageStatusIndicator` Widget
   - `MessageStatus` enum for type safety
   - Icon selection based on status
   - Color coding (grey for sent/delivered, blue for read)
   - Only shows for user messages

3. **lib/features/conversation/services/conversation_service.dart** (Updated +38 lines)
   - Added `updateMessageStatus()` method
   - PUT request to status API
   - Batch update support
   - Error handling (401, 404, network)

---

## API Endpoints

### PUT /api/v1/conversations/{conversation_id}/messages/status

**Authentication:** Required (JWT Bearer token)

**Request:**
```json
{
  "message_ids": [1, 2, 3],
  "status": "read"
}
```

**Success Response (200 OK):**
```json
{
  "updated_count": 3,
  "message": "成功更新 3 条消息状态为 read"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing JWT token
- `404 Not Found`: Conversation not found or not owned by user
- `500 Internal Server Error`: Database error

**Validation:**
- `message_ids`: Required, array of integers
- `status`: Required, must be "read" or "delivered"
- Only updates idol messages (sender_type='idol')
- Only updates messages in user's own conversation

---

## Widget Usage Examples

### TypingIndicator Usage

```dart
// Show typing indicator while waiting for AI reply
if (isIdolTyping) {
  TypingIndicator(
    dotColor: Theme.of(context).colorScheme.primary,
    dotSize: 8.0,
  )
}

// Custom colors
TypingIndicator(
  dotColor: Colors.pink.shade300,
  dotSize: 10.0,
)
```

### MessageStatusIndicator Usage

```dart
// In message bubble widget
Row(
  children: [
    Text(message.content),
    const SizedBox(width: 4),
    MessageStatusIndicator(
      message: message,
      color: Theme.of(context).colorScheme.onSurface,
    ),
  ],
)

// Auto-hides for idol messages
// Shows appropriate icon for user messages
```

### ConversationService.updateMessageStatus Usage

```dart
// Mark messages as read when user views them
final conversationService = ConversationService();

try {
  final updatedCount = await conversationService.updateMessageStatus(
    conversationId: 1,
    messageIds: [5, 6, 7], // Unread idol messages
    status: 'read',
  );

  print('Marked $updatedCount messages as read');
} catch (e) {
  print('Failed to update status: $e');
}
```

---

## Technical Decisions

### 1. Simulated Typing Animation (Not Real-Time)
**Decision:** Show typing indicator while waiting for API response (not SSE/WebSocket)
**Rationale:**
- MVP simplicity: No need for real-time infrastructure
- User experience: Still provides visual feedback during wait
- Cost: Avoid WebSocket server costs
- Latency: 2-5s AI response time is acceptable for simulated animation

**How it works:**
1. User sends message
2. Show typing indicator immediately
3. Wait for POST /messages API response (includes AI reply)
4. Hide typing indicator, show AI reply

**Future:** Real-time typing with Server-Sent Events (SSE) or WebSocket

### 2. Status Transitions Are Client-Driven
**Decision:** Frontend controls status transitions (not server push)
**Rationale:**
- Sent → Delivered: Automatic when API returns idol_reply
- Delivered → Read: Manual when user opens chat (call updateMessageStatus)
- No need for real-time push for MVP

**Alternatives Considered:**
- Server push via SSE → Rejected (over-engineering for MVP)
- Auto-mark as read → Rejected (should require user action)

### 3. Batch Status Update (Not Single Message)
**Decision:** API accepts array of message_ids
**Rationale:**
- Efficiency: Update all unread messages in one request
- Common use case: User opens chat, mark all as read
- Reduces API calls (10 messages = 1 request vs 10)

**Example:**
```dart
// Mark all unread messages as read at once
final unreadIds = messages
    .where((m) => m.senderType == 'idol' && m.status != 'read')
    .map((m) => m.id)
    .toList();

if (unreadIds.isNotEmpty) {
  await conversationService.updateMessageStatus(
    conversationId: conversationId,
    messageIds: unreadIds,
    status: 'read',
  );
}
```

### 4. Only Update Idol Messages
**Decision:** Backend filters `sender_type='idol'` in query
**Rationale:**
- User messages don't need "read" status (user is the sender)
- "Read" means "user read idol's message"
- Prevents accidental updates to user messages

**SQL Filter:**
```python
db.query(Message).filter(
    Message.conversation_id == conversation_id,
    Message.id.in_(message_ids),
    Message.sender_type == "idol"  # ← Only idol messages
)
```

### 5. Staggered Animation (Not Synchronized)
**Decision:** 3 dots bounce with 0.2s offset
**Rationale:**
- More natural and visually interesting
- Industry standard (WhatsApp, Telegram, iMessage)
- Clearly indicates "typing" vs "loading"

**Animation Timing:**
- Dot 1: starts at 0.0s
- Dot 2: starts at 0.2s (+200ms)
- Dot 3: starts at 0.4s (+400ms)
- Total cycle: 1.2s, repeats

### 6. Status Icon Color Coding
**Decision:** Grey for sent/delivered, Primary color for read
**Rationale:**
- Grey: Neutral, "pending" states
- Blue/Primary: Positive feedback, "completed"
- Matches user mental model (WhatsApp blue checkmarks)

**Accessibility:**
- Don't rely only on color (use icon shape too)
- Single check vs double check distinguishes sent/delivered
- Color is additional signal for read status

---

## Message Flow Example

### Complete Flow: User Sends Message

```dart
// 1. User types and sends
final message = Message.local(
  content: "你好",
  senderType: "user",
  status: "sending",  // ← Local optimistic update
);

// Add to UI immediately
messages.add(message);
setState(() {
  isIdolTyping = true;  // ← Show typing indicator
});

// 2. Send to backend
try {
  final result = await conversationService.sendMessage(
    conversationId: conversationId,
    content: "你好",
  );

  // 3. Update user message to 'sent'
  message.status = "sent";
  message.id = result['user_message'].id;

  // 4. Add idol reply (status already 'delivered')
  final idolReply = result['idol_reply'];
  messages.add(idolReply);

  setState(() {
    isIdolTyping = false;  // ← Hide typing indicator
  });

} catch (e) {
  // 5. Mark as failed if error
  message.status = "failed";
  setState(() {
    isIdolTyping = false;
  });
}

// 6. Later: Mark idol messages as read
await conversationService.updateMessageStatus(
  conversationId: conversationId,
  messageIds: [idolReply.id],
  status: 'read',
);
```

### Timeline Visualization

```
User Action         Frontend State            Backend           UI Display
============================================================================
User hits send  →  status: "sending"                        ⏳ Sending...
                   isIdolTyping: true                       ● ● ● Typing

POST /messages  →  Wait for response...      AI generates  ● ● ● Typing
(2-5 seconds)                                response

API returns     →  user msg: "sent"          Saved to DB   ✓ Sent
                   idol msg: "delivered"                   ✓✓ Idol reply
                   isIdolTyping: false

User views chat →  PUT /status               Updated to    ✓✓ (blue)
                   status: "read"            "read"        Read
```

---

## Performance Considerations

1. **Animation Performance:**
   - Uses `SingleTickerProviderStateMixin` (efficient)
   - Only 3 animated widgets (minimal overhead)
   - Automatically disposed with widget lifecycle

2. **API Call Reduction:**
   - Batch status updates (1 call for multiple messages)
   - Don't spam status updates (only on view, not on scroll)

3. **Optimistic Updates:**
   - Show "sending" status immediately (before API)
   - Better perceived performance
   - Rollback to "failed" if error

---

## Testing Scenarios

### 1. Happy Path
```
User sends "你好"
→ Shows sending icon ⏳
→ Shows typing animation ● ● ●
→ Receives reply in 3s
→ Typing stops
→ User message shows ✓ (sent)
→ Idol message shows ✓✓ (delivered, grey)
→ User views chat
→ Call updateMessageStatus
→ Idol message shows ✓✓ (read, blue)
```

### 2. Network Error
```
User sends message
→ Shows sending icon ⏳
→ Network error after 5s
→ Status changes to ❌ failed
→ Show retry button
```

### 3. Batch Read Update
```
User has 5 unread messages
→ All show ✓✓ (delivered, grey)
→ User opens chat
→ Call updateMessageStatus([1,2,3,4,5])
→ All change to ✓✓ (read, blue)
→ Returns updated_count: 5
```

### 4. Animation Smoothness
```
Typing animation plays
→ 3 dots bounce smoothly
→ Staggered timing (not synchronized)
→ 60 FPS on device
→ No jank or stuttering
```

---

## Limitations & Future Work

### Current Limitations (MVP):

1. **No Real-Time Status Updates:** User B won't see when User A reads a message
2. **Simulated Typing:** Indicator doesn't reflect actual AI typing speed
3. **No "Typing..." Text:** Only shows animation, no text label
4. **No Custom Timing:** Can't adjust animation speed
5. **No Read Receipts Toggle:** Can't disable read receipts
6. **No Timestamp Next to Status:** Only icon, no "delivered at 10:30 AM"
7. **No Retry Button:** Failed messages can't be retried (MVP)

### Future Enhancements (Post-MVP):

1. **Real-Time Status Updates (SSE/WebSocket):**
   - Server pushes status changes
   - User sees "read" status update in real-time
   - Idol sees when user is typing

2. **Streaming AI Responses (Story 2.1 future work):**
   - Typing animation stops when first token arrives
   - Words appear one by one (typewriter effect)
   - More engaging UX

3. **Read Receipts Toggle:**
   - User setting to disable read receipts
   - Privacy consideration
   - "Delivered" only, never "Read"

4. **Message Retry:**
   - Tap failed message to retry sending
   - Exponential backoff for retries
   - Offline queue

5. **Detailed Timestamps:**
   ```
   Your message  ✓✓
   Delivered 10:32 AM
   Read 10:35 AM
   ```

6. **Typing Indicator with Avatar:**
   - Show idol avatar next to typing dots
   - "雪晴 is typing..." text

7. **Custom Animation Styles:**
   - Pulse animation
   - Wave animation
   - Fade animation
   - User preference

8. **Sound Effects:**
   - "Sent" sound
   - "Received" sound
   - "Typing" subtle sound

---

## Related Stories

- **Depends on:**
  - Story 2.1: Basic AI conversation (provides message API)
  - Story 2.3: Emotion recognition (emotion field in messages)

- **Enables:**
  - Story 2.5: Voice messages (similar status flow)
  - Story 2.6: Image messages (similar status indicators)
  - Story 2.8: Conversation history (show status in history)
  - Epic 8: Real-time sync (upgrade to real-time status)

---

## Acceptance Criteria Status

| AC | Status | Notes |
|----|--------|-------|
| AC1: 消息状态管理 | ✅ Done | 5 states: sending, sent, delivered, read, failed |
| AC2: 批量消息状态更新API | ✅ Done | PUT /messages/status with batch support |
| AC3: 打字动画指示器Widget | ✅ Done | TypingIndicator with 3-dot staggered animation |
| AC4: 消息状态指示器Widget | ✅ Done | MessageStatusIndicator with 5 status icons |
| AC5: ConversationService状态更新 | ✅ Done | updateMessageStatus() method with error handling |

---

**Story 2.4 Complete!** ✅

聊天界面现在拥有完整的视觉反馈系统：打字动画指示器提供实时反馈，消息状态图标清晰显示发送状态。用户可以看到消息的完整生命周期（发送→已送达→已读），获得更真实、更流畅的聊天体验。

**Key Features:**
- 🎨 **打字动画**: 3个圆点的流畅弹跳动画，循环播放
- ✅ **状态指示器**: 5种状态图标（发送中、已发送、已送达、已读、失败）
- 📊 **批量更新**: 一次性标记多条消息为已读
- ⚡ **乐观更新**: 立即显示"发送中"状态，提升体验
- 🎯 **Material Design**: 符合MD3设计规范的配色和动效

**Next Steps:**
- Story 2.5: 实现语音消息录制和播放功能
- Story 2.6: 添加图片消息上传和显示功能
- Story 2.8: 完善对话历史和空闲状态管理
