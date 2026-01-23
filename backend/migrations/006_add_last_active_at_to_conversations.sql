-- Migration 006: Add last_active_at to conversations table
-- Purpose: Track user activity for idle status detection
-- Story: 2-8-conversation-history-idle-status

-- Add last_active_at column
ALTER TABLE conversations
ADD COLUMN last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create index for efficient querying of idle conversations
CREATE INDEX idx_conversations_last_active_at
ON conversations(last_active_at);

-- Update existing conversations to set last_active_at to last_message_at
UPDATE conversations
SET last_active_at = last_message_at
WHERE last_active_at IS NULL;

-- Add comment
COMMENT ON COLUMN conversations.last_active_at IS 'Last user activity timestamp (updated by heartbeat)';
