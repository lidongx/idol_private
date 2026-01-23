-- Migration 022: Create intimacy_decay_logs table for tracking intimacy decay
-- Story 6.5: 亲密度衰减与保持机制

CREATE TABLE IF NOT EXISTS intimacy_decay_logs (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    decay_amount INTEGER NOT NULL,          -- Amount of exp lost (e.g., -5)
    reason VARCHAR(100) NOT NULL,           -- Reason for decay (e.g., 'inactive_7days')
    intimacy_exp_before INTEGER NOT NULL,   -- Exp before decay
    intimacy_exp_after INTEGER NOT NULL,    -- Exp after decay
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient queries
CREATE INDEX idx_intimacy_decay_conversation ON intimacy_decay_logs(conversation_id);
CREATE INDEX idx_intimacy_decay_created ON intimacy_decay_logs(created_at DESC);

-- Comments
COMMENT ON TABLE intimacy_decay_logs IS 'Tracks intimacy exp decay events for inactive users';
COMMENT ON COLUMN intimacy_decay_logs.conversation_id IS 'Conversation where decay occurred';
COMMENT ON COLUMN intimacy_decay_logs.decay_amount IS 'Amount of exp lost (negative value)';
COMMENT ON COLUMN intimacy_decay_logs.reason IS 'Reason for decay (inactive_7days, inactive_14days, etc.)';
COMMENT ON COLUMN intimacy_decay_logs.intimacy_exp_before IS 'Intimacy exp before decay';
COMMENT ON COLUMN intimacy_decay_logs.intimacy_exp_after IS 'Intimacy exp after decay';
