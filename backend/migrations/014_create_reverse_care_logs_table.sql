-- Migration 014: Create reverse_care_logs table for tracking care actions
-- Story 5.4: 反向陪伴机制

CREATE TABLE IF NOT EXISTS reverse_care_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    idol_id INTEGER NOT NULL REFERENCES idols(id) ON DELETE CASCADE,
    care_type VARCHAR(50) NOT NULL,  -- 'inactive_3days', 'late_night', 'low_mood_3days'
    message_content TEXT,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    was_responded BOOLEAN DEFAULT false,  -- Whether user responded to care message
    responded_at TIMESTAMP
);

-- Indexes for efficient queries
CREATE INDEX idx_reverse_care_user_id ON reverse_care_logs(user_id);
CREATE INDEX idx_reverse_care_type ON reverse_care_logs(care_type);
CREATE INDEX idx_reverse_care_triggered_at ON reverse_care_logs(triggered_at DESC);
CREATE INDEX idx_reverse_care_user_type_time ON reverse_care_logs(user_id, care_type, triggered_at DESC);

-- Comments
COMMENT ON TABLE reverse_care_logs IS 'Tracks reverse care actions when idol reaches out to users';
COMMENT ON COLUMN reverse_care_logs.care_type IS 'Type of care: inactive_3days, late_night, low_mood_3days';
COMMENT ON COLUMN reverse_care_logs.message_content IS 'The actual care message sent to the user';
COMMENT ON COLUMN reverse_care_logs.was_responded IS 'Whether user replied to the care message';
