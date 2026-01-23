-- Migration 010: Create proactive_mentions table for tracking proactive memory mentions
-- Story 4.6: 主动提及机制与记忆回顾

CREATE TABLE IF NOT EXISTS proactive_mentions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    memory_id INTEGER NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    mention_date DATE NOT NULL,  -- Date when proactive mention was sent (for daily limit)
    proactive_message TEXT NOT NULL,  -- The proactive question that was sent
    was_replied BOOLEAN DEFAULT false,  -- Whether user replied to the proactive message
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure we don't mention same memory multiple times per day
    UNIQUE(user_id, memory_id, mention_date)
);

-- Indexes for efficient queries
CREATE INDEX idx_proactive_mentions_user_id ON proactive_mentions(user_id);
CREATE INDEX idx_proactive_mentions_memory_id ON proactive_mentions(memory_id);
CREATE INDEX idx_proactive_mentions_date ON proactive_mentions(mention_date);
CREATE INDEX idx_proactive_mentions_user_date ON proactive_mentions(user_id, mention_date);

-- Comments
COMMENT ON TABLE proactive_mentions IS 'Tracks when AI proactively mentions memories to users';
COMMENT ON COLUMN proactive_mentions.mention_date IS 'Date of mention (not timestamp) for daily limit checking';
COMMENT ON COLUMN proactive_mentions.proactive_message IS 'The AI-generated question about the memory';
COMMENT ON COLUMN proactive_mentions.was_replied IS 'True if user responded to the proactive mention';
