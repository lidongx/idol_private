-- Migration 011: Create idol_states table for idol life rhythm system
-- Story 5.1: 偶像状态系统与生活节奏引擎

CREATE TABLE IF NOT EXISTS idol_states (
    id SERIAL PRIMARY KEY,
    idol_id INTEGER NOT NULL REFERENCES idols(id) ON DELETE CASCADE,
    current_status VARCHAR(50) NOT NULL,  -- 'working', 'resting', 'active', 'busy', 'sleeping', 'waking_up', 'preparing_sleep'
    current_mood VARCHAR(50) NOT NULL,    -- 'happy', 'calm', 'tired', 'excited', 'thoughtful', 'focused', 'relaxed', 'sleepy'
    energy_level INTEGER DEFAULT 80 CHECK (energy_level >= 0 AND energy_level <= 100),
    status_message TEXT,  -- Optional custom status message
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Each idol has only one current state
    UNIQUE(idol_id)
);

-- Index for efficient queries
CREATE INDEX idx_idol_states_idol_id ON idol_states(idol_id);
CREATE INDEX idx_idol_states_updated_at ON idol_states(updated_at);

-- Comments
COMMENT ON TABLE idol_states IS 'Stores current life state of idols (status, mood, energy)';
COMMENT ON COLUMN idol_states.current_status IS 'Current activity status: working, resting, active, busy, sleeping, waking_up, preparing_sleep';
COMMENT ON COLUMN idol_states.current_mood IS 'Current emotional state: happy, calm, tired, excited, thoughtful, focused, relaxed, sleepy';
COMMENT ON COLUMN idol_states.energy_level IS 'Energy level from 0-100';
COMMENT ON COLUMN idol_states.status_message IS 'Optional custom status message for current state';
