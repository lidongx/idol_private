-- Migration 021: Create user_achievements table for tracking user achievement progress
-- Story 6.4: 成就系统与每日互动奖励

CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    progress INTEGER DEFAULT 0,             -- Current progress towards achievement
    unlocked_at TIMESTAMP,                  -- Null if not yet unlocked
    is_viewed BOOLEAN DEFAULT false,        -- Whether user has viewed the unlock notification
    viewed_at TIMESTAMP,                    -- When user viewed the achievement
    UNIQUE(user_id, achievement_id)         -- Prevent duplicate achievement records
);

-- Indexes for efficient queries
CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_unlocked ON user_achievements(unlocked_at);
CREATE INDEX idx_user_achievements_viewed ON user_achievements(is_viewed);
CREATE INDEX idx_user_achievements_user_unlocked ON user_achievements(user_id, unlocked_at);

-- Comments
COMMENT ON TABLE user_achievements IS 'Tracks user achievement progress and unlocks';
COMMENT ON COLUMN user_achievements.user_id IS 'User who is working towards achievement';
COMMENT ON COLUMN user_achievements.achievement_id IS 'Reference to achievements table';
COMMENT ON COLUMN user_achievements.progress IS 'Current progress value (e.g., 5/10 messages)';
COMMENT ON COLUMN user_achievements.unlocked_at IS 'Timestamp when achievement was unlocked (null if locked)';
COMMENT ON COLUMN user_achievements.is_viewed IS 'Whether user has viewed the unlock notification';
COMMENT ON COLUMN user_achievements.viewed_at IS 'When user first viewed the achievement details';
