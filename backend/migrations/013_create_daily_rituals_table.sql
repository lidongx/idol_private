-- Migration 013: Create daily_rituals table for daily routine tracking
-- Story 5.3: 每日仪式（早安/运势/晚安）

CREATE TABLE IF NOT EXISTS daily_rituals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    idol_id INTEGER NOT NULL REFERENCES idols(id) ON DELETE CASCADE,
    ritual_type VARCHAR(50) NOT NULL,  -- 'morning_greeting', 'fortune', 'night_greeting'
    ritual_date DATE NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fortune_data JSONB,  -- For storing fortune details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Each user can only complete each ritual once per day
    UNIQUE(user_id, ritual_type, ritual_date)
);

-- Indexes for efficient queries
CREATE INDEX idx_daily_rituals_user_id ON daily_rituals(user_id);
CREATE INDEX idx_daily_rituals_date ON daily_rituals(ritual_date DESC);
CREATE INDEX idx_daily_rituals_user_date ON daily_rituals(user_id, ritual_date);
CREATE INDEX idx_daily_rituals_type ON daily_rituals(ritual_type);

-- Comments
COMMENT ON TABLE daily_rituals IS 'Tracks daily rituals (morning greeting, fortune, night greeting) for users';
COMMENT ON COLUMN daily_rituals.ritual_type IS 'Type of ritual: morning_greeting, fortune, night_greeting';
COMMENT ON COLUMN daily_rituals.ritual_date IS 'Date of the ritual (not timestamp)';
COMMENT ON COLUMN daily_rituals.completed_at IS 'When the ritual was completed';
COMMENT ON COLUMN daily_rituals.fortune_data IS 'JSON data for fortune ritual (score, description, lucky_color, etc.)';
