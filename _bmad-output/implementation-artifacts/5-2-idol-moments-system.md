# Story 5.2: 偶像朋友圈系统

**Epic**: Epic 5 - 偶像生活系统与真实陪伴
**Story ID**: 5-2-idol-moments-system
**Status**: ✅ Done
**Implementation Date**: 2026-01-15

---

## 📋 Story Overview

### User Story
**作为** 用户
**我想要** 查看偶像的朋友圈动态了解她的日常
**以便** 感受她的生活和心情，增加真实感

### Acceptance Criteria
- [x] 创建idol_moments和idol_moment_likes表
- [x] 显示朋友圈列表（时间倒序）
- [x] 用户可以点赞/取消点赞
- [x] 点赞数实时显示
- [x] 支持图片展示（可选）
- [x] 相对时间显示（2小时前、昨天等）
- [x] 分页支持
- [x] 运营可手动发布朋友圈

---

## 🎯 Implementation Summary

### Backend Components

#### 1. Database Migration (`backend/migrations/012_create_idol_moments_tables.sql`)

**idol_moments表：**
```sql
CREATE TABLE idol_moments (
    id SERIAL PRIMARY KEY,
    idol_id INTEGER NOT NULL REFERENCES idols(id),
    content TEXT NOT NULL CHECK (char_length(content) <= 300),
    image_url VARCHAR(255),
    likes_count INTEGER DEFAULT 0,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**idol_moment_likes表：**
```sql
CREATE TABLE idol_moment_likes (
    id SERIAL PRIMARY KEY,
    moment_id INTEGER NOT NULL REFERENCES idol_moments(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(moment_id, user_id)
);
```

#### 2. Models (`backend/app/models/idol_moment.py` - 102 lines)

**IdolMoment类：**
```python
class IdolMoment(Base):
    id = Column(Integer, primary_key=True)
    idol_id = Column(Integer, ForeignKey("idols.id"))
    content = Column(Text, nullable=False)  # Max 300 chars
    image_url = Column(String(255))
    likes_count = Column(Integer, default=0)
    posted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    idol = relationship("Idol", back_populates="moments")
    likes = relationship("IdolMomentLike", back_populates="moment")

    @property
    def relative_time(self) -> str:
        """相对时间：刚刚、2小时前、昨天、3天前等"""
```

**IdolMomentLike类：**
```python
class IdolMomentLike(Base):
    id = Column(Integer, primary_key=True)
    moment_id = Column(Integer, ForeignKey("idol_moments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    liked_at = Column(DateTime, default=datetime.utcnow)

    # Each user can only like a moment once
    UNIQUE(moment_id, user_id)
```

#### 3. Service (`backend/app/services/idol_moment_service.py` - 261 lines)

**核心方法：**
```python
class IdolMomentService:

    def get_moments(idol_id, limit, offset) -> List[IdolMoment]:
        """获取朋友圈列表（时间倒序）"""

    def create_moment(idol_id, content, image_url) -> IdolMoment:
        """创建新朋友圈"""

    def like_moment(moment_id, user_id) -> Dict:
        """
        点赞/取消点赞

        Returns: {'action': 'liked' or 'unliked', 'likes_count': int}
        """

    def has_user_liked(moment_id, user_id) -> bool:
        """检查用户是否已点赞"""

    def get_moments_with_like_status(idol_id, user_id, limit, offset) -> List[Dict]:
        """获取朋友圈列表（含用户点赞状态）"""

    def get_moment_stats(idol_id) -> Dict:
        """获取朋友圈统计信息"""
```

#### 4. API Endpoints (`backend/app/routers/idol.py` - Modified)

**端点列表：**

```python
GET /api/v1/idols/{idol_id}/moments
# 获取朋友圈列表
# Query params: limit (default: 20), offset (default: 0)
# Response: {
#     'idol_id': int,
#     'idol_name': str,
#     'idol_avatar': str,
#     'moments': [
#         {
#             'id': int,
#             'content': str,
#             'image_url': str | null,
#             'likes_count': int,
#             'posted_at': str (ISO),
#             'relative_time': str,
#             'is_liked': bool
#         }
#     ],
#     'total': int,
#     'limit': int,
#     'offset': int
# }

POST /api/v1/idols/moments/{moment_id}/like
# 点赞/取消点赞
# Response: {
#     'action': 'liked' or 'unliked',
#     'likes_count': int
# }

POST /api/v1/idols/{idol_id}/moments
# 发布朋友圈（管理员/测试用）
# Body: {
#     'content': str (max 300 chars),
#     'image_url': str | null
# }

GET /api/v1/idols/{idol_id}/moments/stats
# 获取朋友圈统计
# Response: {
#     'idol_id': int,
#     'idol_name': str,
#     'total_moments': int,
#     'total_likes': int,
#     'average_likes': float
# }
```

#### 5. Moment Templates (`backend/app/config/moment_templates.json` - 125 lines)

**8大类模板：**
1. **日常分享** - 日常生活记录
2. **感悟思考** - 人生感悟
3. **晚安问候** - 晚安祝福
4. **早安问候** - 早安问候
5. **心情记录** - 情绪表达
6. **兴趣爱好** - 兴趣分享
7. **节日祝福** - 节日问候
8. **互动提问** - 互动话题

**示例模板：**
```json
{
  "moment_templates": [
    {
      "category": "日常分享",
      "templates": [
        "今天读到一段很喜欢的话：「{quote}」",
        "刚才路过一家咖啡店，装修好温馨~",
        "最近在学摄影后期，越学越觉得有意思~"
      ]
    }
  ]
}
```

---

## 📁 Files Created

### Backend
1. `backend/migrations/012_create_idol_moments_tables.sql` (36 lines)
2. `backend/app/models/idol_moment.py` (102 lines)
3. `backend/app/services/idol_moment_service.py` (261 lines)
4. `backend/app/config/moment_templates.json` (125 lines)

### Files Modified
1. `backend/app/models/idol.py` - Added moments relationship
2. `backend/app/models/user.py` - Added moment_likes relationship
3. `backend/app/routers/idol.py` - Added moments endpoints

---

## 🎨 UI Design

### 朋友圈列表布局

```
┌─────────────────────────────────┐
│ 【朋友圈】                       │
├─────────────────────────────────┤
│                                 │
│ 🧑 林雪晴         2小时前        │
│                                 │
│ 今天读到一段很喜欢的话：         │
│ 「生活明朗，万物可爱。」         │
│                                 │
│ [图片]                          │
│                                 │
│ ❤️ 128                  [点赞]  │
│                                 │
├─────────────────────────────────┤
│                                 │
│ 🧑 林雪晴         昨天           │
│                                 │
│ 刚才路过一家咖啡店，             │
│ 装修好温馨~                     │
│                                 │
│ ❤️ 95                   [已赞]  │
│                                 │
└─────────────────────────────────┘
```

---

## 🔧 Technical Details

### 相对时间计算

```python
def relative_time(posted_at: datetime) -> str:
    delta = now - posted_at

    if delta.days == 0:
        hours = delta.seconds // 3600
        if hours == 0:
            minutes = delta.seconds // 60
            return "刚刚" if minutes == 0 else f"{minutes}分钟前"
        return f"{hours}小时前"
    elif delta.days == 1:
        return "昨天"
    elif delta.days < 7:
        return f"{delta.days}天前"
    elif delta.days < 30:
        return f"{delta.days // 7}周前"
    else:
        return posted_at.strftime("%m月%d日")
```

### 点赞/取消点赞逻辑

```
用户点击点赞按钮
    ↓
检查是否已点赞
    ├─ 已点赞：
    │   ├─ 删除点赞记录
    │   ├─ likes_count -= 1
    │   └─ 返回 {'action': 'unliked'}
    │
    └─ 未点赞：
        ├─ 创建点赞记录
        ├─ likes_count += 1
        └─ 返回 {'action': 'liked'}
```

### 唯一性约束

```sql
-- 确保每个用户只能对同一条朋友圈点赞一次
UNIQUE(moment_id, user_id)
```

---

## 📊 API Integration Examples

### Example 1: 获取朋友圈列表

**Request:**
```http
GET /api/v1/idols/1/moments?limit=10&offset=0
Authorization: Bearer {token}
```

**Response:**
```json
{
    "idol_id": 1,
    "idol_name": "林雪晴",
    "idol_avatar": "https://example.com/avatar.jpg",
    "moments": [
        {
            "id": 1,
            "content": "今天读到一段很喜欢的话：「生活明朗，万物可爱。」",
            "image_url": null,
            "likes_count": 128,
            "posted_at": "2026-01-15T10:00:00Z",
            "relative_time": "2小时前",
            "is_liked": false
        },
        {
            "id": 2,
            "content": "刚才路过一家咖啡店，装修好温馨~",
            "image_url": "https://example.com/cafe.jpg",
            "likes_count": 95,
            "posted_at": "2026-01-14T18:30:00Z",
            "relative_time": "昨天",
            "is_liked": true
        }
    ],
    "total": 25,
    "limit": 10,
    "offset": 0
}
```

### Example 2: 点赞朋友圈

**Request:**
```http
POST /api/v1/idols/moments/1/like
Authorization: Bearer {token}
```

**Response (未点赞→点赞):**
```json
{
    "action": "liked",
    "likes_count": 129
}
```

**Response (已点赞→取消):**
```json
{
    "action": "unliked",
    "likes_count": 128
}
```

### Example 3: 发布朋友圈

**Request:**
```http
POST /api/v1/idols/1/moments
Content-Type: application/json

{
    "content": "今天天气真好，心情也跟着变好了呢~",
    "image_url": "https://example.com/sunny.jpg"
}
```

**Response:**
```json
{
    "id": 26,
    "idol_id": 1,
    "content": "今天天气真好，心情也跟着变好了呢~",
    "image_url": "https://example.com/sunny.jpg",
    "likes_count": 0,
    "posted_at": "2026-01-15T14:30:00Z",
    "message": "朋友圈发布成功"
}
```

---

## ✅ Testing Checklist

- [x] Database tables created correctly
- [x] Model relationships work properly
- [x] Can create moments with content only
- [x] Can create moments with content + image
- [x] Content length limited to 300 characters
- [x] Moments listed in desc order by posted_at
- [x] Relative time calculation correct
- [x] Like/unlike toggles correctly
- [x] Like count updates correctly
- [x] User can only like once (uniqueness enforced)
- [x] Pagination works correctly
- [x] Stats calculation correct

---

## 🎓 Usage Scenarios

### Scenario 1: 用户首次打开朋友圈

**What happens:**
1. 前端调用 `GET /idols/1/moments?limit=20&offset=0`
2. 返回最新20条朋友圈
3. 每条显示内容、图片、点赞数、相对时间
4. 用户点赞状态（is_liked）标记为红色/灰色

### Scenario 2: 用户点赞朋友圈

**What happens:**
1. 用户点击朋友圈的点赞按钮
2. 前端调用 `POST /idols/moments/1/like`
3. 服务器检查：用户未点赞
4. 创建点赞记录，likes_count + 1
5. 返回 `{action: 'liked', likes_count: 129}`
6. 前端更新UI：按钮变红色，数字更新

### Scenario 3: 用户取消点赞

**What happens:**
1. 用户再次点击已点赞的朋友圈
2. 服务器检查：用户已点赞
3. 删除点赞记录，likes_count - 1
4. 返回 `{action: 'unliked', likes_count: 128}`
5. 前端更新UI：按钮变灰色，数字更新

### Scenario 4: 运营发布朋友圈

**What happens:**
1. 运营通过管理后台选择模板
2. 可以添加图片（可选）
3. 调用 `POST /idols/1/moments`
4. 创建新朋友圈记录
5. 所有用户下次刷新时看到新动态

---

## 🚀 Future Enhancements

1. **评论功能**
   - 用户可以评论朋友圈
   - 显示评论列表

2. **AI自动生成**
   - 每日定时自动生成1-2条朋友圈
   - 结合偶像状态和时间生成内容

3. **多图片支持**
   - 支持最多9张图片
   - 图片网格布局

4. **视频支持**
   - 支持短视频分享
   - 视频封面和播放

5. **话题标签**
   - #话题 标签
   - 话题聚合页面

6. **朋友圈提醒**
   - 偶像发布新朋友圈推送通知
   - 被点赞时通知偶像（未来互动）

7. **朋友圈分析**
   - 最受欢迎的朋友圈
   - 点赞趋势分析

---

## 📝 Technical Notes

1. **内容长度**: 300字符限制，数据库层和应用层双重校验
2. **点赞缓存**: likes_count冗余字段提高查询性能
3. **唯一性保证**: 数据库UNIQUE约束防止重复点赞
4. **相对时间**: 前端可缓存，定期更新（如每分钟刷新）
5. **图片存储**: MVP阶段使用外部URL，未来可集成OSS
6. **分页策略**: Offset-based pagination，简单但足够MVP使用
7. **模板系统**: JSON配置便于运营调整，未来可迁移到数据库

---

## 🔗 Integration Points

### With Idol State System (Story 5.1)
未来可以：
- 根据偶像当前状态自动生成朋友圈内容
- 睡眠时不发布朋友圈
- 心情好时发布更积极的内容

### With Intimacy System (Future - Epic 6)
- 点赞朋友圈增加亲密度经验值（+3 exp）
- 高亲密度用户看到更多独家朋友圈

### With Notification System (Future - Epic 9)
- 偶像发布新朋友圈推送通知
- 朋友圈被点赞通知

---

**Story Status**: ✅ Done
**Epic Status**: 🔄 Epic 5 进行中 (2/5 stories)
**Last Updated**: 2026-01-15
