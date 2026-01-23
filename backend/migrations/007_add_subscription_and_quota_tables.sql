-- Migration 007: Add subscription tier and message quotas
-- Purpose: Enable freemium model with daily message limits
-- Story: 3-1-message-quota-data-model-metering

-- Add subscription fields to users table
ALTER TABLE users
ADD COLUMN subscription_tier VARCHAR(20) DEFAULT 'free'
    CHECK (subscription_tier IN ('free', 'premium'));

ALTER TABLE users
ADD COLUMN subscription_expires_at TIMESTAMP NULL;

-- Create index for subscription queries
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);

-- Add comments
COMMENT ON COLUMN users.subscription_tier IS '订阅等级: free/premium';
COMMENT ON COLUMN users.subscription_expires_at IS '订阅过期时间（免费用户为NULL）';

-- Create message_quotas table
CREATE TABLE message_quotas (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    messages_sent INTEGER DEFAULT 0 NOT NULL,
    quota_limit INTEGER NOT NULL,  -- -1 表示无限制
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure one quota record per user per day
    UNIQUE(user_id, date)
);

-- Create indexes for efficient queries
CREATE INDEX idx_message_quotas_user_id ON message_quotas(user_id);
CREATE INDEX idx_message_quotas_date ON message_quotas(date);
CREATE INDEX idx_message_quotas_user_date ON message_quotas(user_id, date);

-- Add comments
COMMENT ON TABLE message_quotas IS '消息配额追踪表';
COMMENT ON COLUMN message_quotas.user_id IS '用户ID';
COMMENT ON COLUMN message_quotas.date IS '配额日期（UTC+8时区）';
COMMENT ON COLUMN message_quotas.messages_sent IS '已发送消息数';
COMMENT ON COLUMN message_quotas.quota_limit IS '每日限额（-1表示无限制）';

-- Update existing users to have default free tier
UPDATE users SET subscription_tier = 'free' WHERE subscription_tier IS NULL;

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_message_quotas_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at on message_quotas
CREATE TRIGGER trigger_update_message_quotas_updated_at
    BEFORE UPDATE ON message_quotas
    FOR EACH ROW
    EXECUTE FUNCTION update_message_quotas_updated_at();
