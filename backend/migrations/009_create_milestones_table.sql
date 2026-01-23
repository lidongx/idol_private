-- Migration 009: Create milestones table for anniversary tracking
-- Story 4.5: 周年纪念与主动回顾

CREATE TABLE IF NOT EXISTS milestones (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    milestone_type VARCHAR(50) NOT NULL,  -- 'days_7', 'days_30', 'days_100', 'days_365'
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_claimed BOOLEAN DEFAULT false,
    message_content TEXT,  -- The congratulatory message sent
    special_reward TEXT,   -- Special content unlocked (e.g., photo URL)

    -- Ensure each milestone only triggered once per user
    UNIQUE(user_id, milestone_type)
);

-- Index for efficient queries
CREATE INDEX idx_milestones_user_id ON milestones(user_id);
CREATE INDEX idx_milestones_triggered_at ON milestones(triggered_at);
CREATE INDEX idx_milestones_type ON milestones(milestone_type);

-- Comments
COMMENT ON TABLE milestones IS 'Tracks anniversary milestones for user-idol relationships';
COMMENT ON COLUMN milestones.milestone_type IS 'Type of milestone: days_7, days_30, days_100, days_365';
COMMENT ON COLUMN milestones.is_claimed IS 'Whether user has viewed the milestone celebration';
COMMENT ON COLUMN milestones.special_reward IS 'Special content URL (e.g., exclusive photos for 100-day milestone)';
