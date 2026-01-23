-- Create conversations and messages tables for chat functionality
-- Migration: 004_create_conversations_messages_tables
-- Description: Store user-idol conversations and individual messages

-- Conversations table: stores conversation sessions between user and idol
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    idol_id INTEGER NOT NULL REFERENCES idols(id) ON DELETE CASCADE,
    intimacy_level INTEGER DEFAULT 1 CHECK (intimacy_level >= 1 AND intimacy_level <= 100),
    intimacy_exp INTEGER DEFAULT 0 CHECK (intimacy_exp >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_idol UNIQUE(user_id, idol_id)
);

-- Messages table: stores individual messages within conversations
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('user', 'idol')),
    content TEXT NOT NULL,
    emotion VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'read'))
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message ON conversations(last_message_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);

-- Comments for documentation
COMMENT ON TABLE conversations IS 'Conversation sessions between users and idols';
COMMENT ON TABLE messages IS 'Individual messages within conversations';
COMMENT ON COLUMN conversations.intimacy_level IS 'Current intimacy level (1-100)';
COMMENT ON COLUMN conversations.intimacy_exp IS 'Intimacy experience points';
COMMENT ON COLUMN messages.sender_type IS 'Message sender: user or idol';
COMMENT ON COLUMN messages.emotion IS 'Detected or expressed emotion (happy, sad, calm, etc.)';
COMMENT ON COLUMN messages.status IS 'Message delivery status';
