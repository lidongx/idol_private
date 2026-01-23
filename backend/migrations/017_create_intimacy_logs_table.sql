-- Migration 017: Create intimacy_logs table for tracking exp changes
-- Story 6.1: 亲密度等级系统与经验值计算

CREATE TABLE IF NOT EXISTS intimacy_logs (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    exp_change INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,
    new_level INTEGER NOT NULL,
    new_exp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient queries
CREATE INDEX idx_intimacy_logs_conversation ON intimacy_logs(conversation_id);
CREATE INDEX idx_intimacy_logs_created_at ON intimacy_logs(created_at DESC);

-- Comments
COMMENT ON TABLE intimacy_logs IS 'Tracks intimacy exp changes for analysis and audit';
COMMENT ON COLUMN intimacy_logs.exp_change IS 'Exp points added (positive) or removed (negative)';
COMMENT ON COLUMN intimacy_logs.reason IS 'Reason for exp change (e.g., send_message, morning_greeting)';
COMMENT ON COLUMN intimacy_logs.new_level IS 'Intimacy level after this change';
COMMENT ON COLUMN intimacy_logs.new_exp IS 'Intimacy exp after this change';
