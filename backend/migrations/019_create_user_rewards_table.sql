-- Migration 019: Create user_rewards table for tracking unlocked rewards
-- Story 6.3: 等级特权与里程碑奖励

CREATE TABLE IF NOT EXISTS user_rewards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reward_id INTEGER NOT NULL REFERENCES level_rewards(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_viewed BOOLEAN DEFAULT false,
    viewed_at TIMESTAMP,
    UNIQUE(user_id, reward_id)  -- Prevent duplicate unlocks
);

-- Indexes for efficient queries
CREATE INDEX idx_user_rewards_user ON user_rewards(user_id);
CREATE INDEX idx_user_rewards_conversation ON user_rewards(conversation_id);
CREATE INDEX idx_user_rewards_viewed ON user_rewards(is_viewed);
CREATE INDEX idx_user_rewards_unlocked ON user_rewards(unlocked_at DESC);

-- Comments
COMMENT ON TABLE user_rewards IS 'Tracks which rewards each user has unlocked';
COMMENT ON COLUMN user_rewards.user_id IS 'User who unlocked the reward';
COMMENT ON COLUMN user_rewards.reward_id IS 'Reference to level_rewards table';
COMMENT ON COLUMN user_rewards.conversation_id IS 'Conversation where reward was unlocked';
COMMENT ON COLUMN user_rewards.is_viewed IS 'Whether user has viewed the reward details';
COMMENT ON COLUMN user_rewards.viewed_at IS 'Timestamp when reward was first viewed';
