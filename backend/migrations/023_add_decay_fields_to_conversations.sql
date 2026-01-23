-- Migration 023: Add decay-related fields to conversations table
-- Story 6.5: 亲密度衰减与保持机制

-- Add decay control fields
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS decay_disabled BOOLEAN DEFAULT false;
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS last_comeback_bonus_at TIMESTAMP;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conversations_decay_disabled ON conversations(decay_disabled);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message_at ON conversations(last_message_at);

-- Comments
COMMENT ON COLUMN conversations.decay_disabled IS 'Whether intimacy decay is disabled for this conversation (user preference or paid feature)';
COMMENT ON COLUMN conversations.last_comeback_bonus_at IS 'Last time user received comeback bonus after being inactive';
