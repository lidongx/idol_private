-- Migration 016: Create special events tables
-- Story 5.5: 特殊事件与互动彩蛋

-- Table 1: special_events (event templates/configurations)
CREATE TABLE IF NOT EXISTS special_events (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL UNIQUE,
    event_type VARCHAR(50) NOT NULL,  -- 'random', 'holiday', 'achievement', 'weather'
    trigger_condition JSONB,  -- Conditions for triggering (probability, date, achievement_type, etc.)
    content_template TEXT NOT NULL,
    image_url VARCHAR(255),
    reward_exp INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: user_special_events (user event history)
CREATE TABLE IF NOT EXISTS user_special_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    idol_id INTEGER NOT NULL REFERENCES idols(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES special_events(id) ON DELETE CASCADE,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_content TEXT,  -- Actual content sent to user (may be templated)
    exp_awarded INTEGER DEFAULT 0,
    was_interacted BOOLEAN DEFAULT false  -- Whether user responded/interacted
);

-- Indexes for efficient queries
CREATE INDEX idx_special_events_type ON special_events(event_type);
CREATE INDEX idx_special_events_active ON special_events(is_active);
CREATE INDEX idx_user_special_events_user_id ON user_special_events(user_id);
CREATE INDEX idx_user_special_events_event_id ON user_special_events(event_id);
CREATE INDEX idx_user_special_events_triggered_at ON user_special_events(triggered_at DESC);
CREATE INDEX idx_user_special_events_user_event ON user_special_events(user_id, event_id);

-- Comments
COMMENT ON TABLE special_events IS 'Special event templates and configurations';
COMMENT ON COLUMN special_events.event_type IS 'Type: random, holiday, achievement, weather';
COMMENT ON COLUMN special_events.trigger_condition IS 'JSON conditions for triggering event';
COMMENT ON TABLE user_special_events IS 'User event history tracking';
COMMENT ON COLUMN user_special_events.was_interacted IS 'Whether user responded to the event';
