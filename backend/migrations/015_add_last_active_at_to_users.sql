-- Migration 015: Add last_active_at column to users table
-- Story 5.4: 反向陪伴机制

-- Add last_active_at column
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;

-- Create index for efficient querying of inactive users
CREATE INDEX IF NOT EXISTS idx_users_last_active_at ON users(last_active_at DESC);

-- Comment
COMMENT ON COLUMN users.last_active_at IS '最后活跃时间，用于检测久未登录用户';

-- Initialize last_active_at for existing users
UPDATE users SET last_active_at = created_at WHERE last_active_at IS NULL;
