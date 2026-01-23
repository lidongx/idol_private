# Story 3.1: 消息配额数据模型与计量逻辑

**Epic**: Epic 3 - Freemium边界与消息计量
**Story ID**: 3-1-message-quota-data-model-metering
**Status**: ✅ Done
**Implementation Date**: 2026-01-14

---

## 📋 Story Overview

### User Story
**作为** 系统管理员
**我想要** 建立消息配额追踪机制
**以便** 可以准确统计用户每日消息使用情况

### Acceptance Criteria
- [x] 创建message_quotas表追踪每日配额
- [x] 用户表添加subscription_tier字段
- [x] 免费用户每日限额20条
- [x] 付费用户无限制（quota_limit = -1）
- [x] 发送消息前检查配额
- [x] 配额耗尽时返回429错误
- [x] 使用UTC+8时区（北京时间）

---

## 🎯 Implementation Summary

### Database Schema

**Migration 007**: `007_add_subscription_and_quota_tables.sql`

```sql
-- Add subscription fields to users
ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(20) DEFAULT 'free';
ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMP NULL;

-- Create message_quotas table
CREATE TABLE message_quotas (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    messages_sent INTEGER DEFAULT 0,
    quota_limit INTEGER NOT NULL,  -- -1 = unlimited
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);
```

### Models

**MessageQuota** (`backend/app/models/message_quota.py`):
- Properties: `remaining`, `is_exhausted`, `is_unlimited`
- Tracks daily message usage per user

### Services

**QuotaService** (`backend/app/services/quota_service.py`):
- `check_and_increment_quota()`: Check quota and increment counter
- `get_quota_info()`: Get current quota status
- `get_quota_stats()`: Get historical usage

### API Integration

Integrated into `POST /conversations/{id}/messages`:
```python
# Check quota before sending message
quota_service = QuotaService(db)
quota = quota_service.check_and_increment_quota(current_user.id)
```

---

## 📁 Files Created

1. `backend/migrations/007_add_subscription_and_quota_tables.sql`
2. `backend/app/models/message_quota.py` (100 lines)
3. `backend/app/services/quota_service.py` (220 lines)

---

## ✅ Quota Rules

| User Tier | quota_limit | Daily Limit |
|-----------|-------------|-------------|
| Free | 20 | 20 messages |
| Premium | -1 | Unlimited ∞ |

---

**Story Status**: ✅ Done
**Last Updated**: 2026-01-14
