-- Migration 030: Add Performance Indexes
-- Story 9.1: 性能优化（首屏加载<2秒）
-- Created: 2026-01-19
--
-- Purpose: Add database indexes to improve query performance
-- Target: Reduce API response time from 500ms to <100ms for common queries

-- ==================== Conversations Table ====================

-- Index for fetching user's conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_id
ON conversations(user_id);

-- Index for sorting conversations by creation date
CREATE INDEX IF NOT EXISTS idx_conversations_created_at
ON conversations(created_at DESC);

-- Composite index for user conversations sorted by last updated
CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
ON conversations(user_id, updated_at DESC);

COMMENT ON INDEX idx_conversations_user_id IS 'Query: Get all conversations for user';
COMMENT ON INDEX idx_conversations_created_at IS 'Query: Get recent conversations';
COMMENT ON INDEX idx_conversations_user_updated IS 'Query: Get user conversations sorted by activity';


-- ==================== Messages Table ====================

-- Index for fetching conversation messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
ON messages(conversation_id);

-- Index for sorting messages by time
CREATE INDEX IF NOT EXISTS idx_messages_created_at
ON messages(created_at DESC);

-- Composite index for conversation messages sorted by time
CREATE INDEX IF NOT EXISTS idx_messages_conv_created
ON messages(conversation_id, created_at DESC);

COMMENT ON INDEX idx_messages_conversation_id IS 'Query: Get all messages in conversation';
COMMENT ON INDEX idx_messages_created_at IS 'Query: Get recent messages';
COMMENT ON INDEX idx_messages_conv_created IS 'Query: Get conversation messages sorted by time (most common query)';


-- ==================== Memories Table ====================

-- Index for fetching user memories
CREATE INDEX IF NOT EXISTS idx_memories_user_id
ON memories(user_id);

-- Index for sorting memories by creation date
CREATE INDEX IF NOT EXISTS idx_memories_created_at
ON memories(created_at DESC);

-- Composite index for user memories sorted by time
CREATE INDEX IF NOT EXISTS idx_memories_user_created
ON memories(user_id, created_at DESC);

COMMENT ON INDEX idx_memories_user_id IS 'Query: Get all memories for user';
COMMENT ON INDEX idx_memories_created_at IS 'Query: Get recent memories';
COMMENT ON INDEX idx_memories_user_created IS 'Query: Get user memories sorted by time';


-- ==================== Intimacy Table ====================

-- Composite index for user-idol intimacy lookup
CREATE INDEX IF NOT EXISTS idx_intimacy_user_idol
ON intimacy(user_id, idol_id);

-- Index for sorting by updated date
CREATE INDEX IF NOT EXISTS idx_intimacy_updated_at
ON intimacy(updated_at DESC);

COMMENT ON INDEX idx_intimacy_user_idol IS 'Query: Get intimacy level for user-idol pair';
COMMENT ON INDEX idx_intimacy_updated_at IS 'Query: Get recently updated intimacy records';


-- ==================== User Achievements Table ====================

-- Index for fetching user achievements
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id
ON user_achievements(user_id);

-- Index for sorting achievements by unlock date
CREATE INDEX IF NOT EXISTS idx_user_achievements_unlocked
ON user_achievements(unlocked_at DESC);

-- Composite index for user achievements sorted by unlock time
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_unlocked
ON user_achievements(user_id, unlocked_at DESC);

COMMENT ON INDEX idx_user_achievements_user_id IS 'Query: Get all achievements for user';
COMMENT ON INDEX idx_user_achievements_unlocked IS 'Query: Get recently unlocked achievements';
COMMENT ON INDEX idx_user_achievements_user_unlocked IS 'Query: Get user achievements sorted by unlock time';


-- ==================== User Devices Table ====================

-- Index for fetching user devices
CREATE INDEX IF NOT EXISTS idx_user_devices_user_id
ON user_devices(user_id);

-- Index for sorting devices by last login
CREATE INDEX IF NOT EXISTS idx_user_devices_last_login
ON user_devices(last_login_at DESC);

-- Composite index for user devices sorted by last login
CREATE INDEX IF NOT EXISTS idx_user_devices_user_login
ON user_devices(user_id, last_login_at DESC);

COMMENT ON INDEX idx_user_devices_user_id IS 'Query: Get all devices for user';
COMMENT ON INDEX idx_user_devices_last_login IS 'Query: Get recently active devices';
COMMENT ON INDEX idx_user_devices_user_login IS 'Query: Get user devices sorted by last login';


-- ==================== Milestones Table ====================

-- Index for fetching user milestones
CREATE INDEX IF NOT EXISTS idx_milestones_user_id
ON milestones(user_id);

-- Index for sorting milestones by date
CREATE INDEX IF NOT EXISTS idx_milestones_milestone_date
ON milestones(milestone_date DESC);

-- Composite index for user milestones sorted by date
CREATE INDEX IF NOT EXISTS idx_milestones_user_date
ON milestones(user_id, milestone_date DESC);

COMMENT ON INDEX idx_milestones_user_id IS 'Query: Get all milestones for user';
COMMENT ON INDEX idx_milestones_milestone_date IS 'Query: Get recent milestones';
COMMENT ON INDEX idx_milestones_user_date IS 'Query: Get user milestones sorted by date';


-- ==================== Moments Table ====================

-- Index for fetching idol moments
CREATE INDEX IF NOT EXISTS idx_moments_idol_id
ON moments(idol_id);

-- Index for sorting moments by created date
CREATE INDEX IF NOT EXISTS idx_moments_created_at
ON moments(created_at DESC);

-- Composite index for idol moments sorted by time
CREATE INDEX IF NOT EXISTS idx_moments_idol_created
ON moments(idol_id, created_at DESC);

COMMENT ON INDEX idx_moments_idol_id IS 'Query: Get all moments for idol';
COMMENT ON INDEX idx_moments_created_at IS 'Query: Get recent moments';
COMMENT ON INDEX idx_moments_idol_created IS 'Query: Get idol moments sorted by time';


-- ==================== Performance Analysis ====================

-- Expected performance improvements:
--
-- 1. Conversation List (GET /api/v1/conversations):
--    Before: ~500ms (full table scan)
--    After: ~50ms (index scan)
--    Improvement: 90%
--
-- 2. Message History (GET /api/v1/conversations/{id}/messages):
--    Before: ~300ms (sorting 1000+ messages)
--    After: ~30ms (index-based sort)
--    Improvement: 90%
--
-- 3. User Memories (GET /api/v1/memories):
--    Before: ~200ms
--    After: ~20ms
--    Improvement: 90%
--
-- 4. Intimacy Lookup (GET /api/v1/intimacy):
--    Before: ~100ms
--    After: ~10ms
--    Improvement: 90%
--
-- Overall API response time improvement: 70-90% for read operations

COMMIT;
