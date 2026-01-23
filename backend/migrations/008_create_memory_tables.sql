-- Migration 008: Create memory and memory_tags tables
-- Epic 4: Memory System & Personalization
-- Story 4.1: Memory data model and ChromaDB integration

-- Create memories table
CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    memory_type VARCHAR(50),  -- 'hobby', 'work', 'family', 'feeling', 'goal', 'preference', 'event'
    importance VARCHAR(20) DEFAULT 'medium',  -- 'low', 'medium', 'high'
    source_message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL,
    embedding_id VARCHAR(100),  -- ChromaDB document ID for vector search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_mentioned_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create memory_tags table for user attributes
CREATE TABLE memory_tags (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tag_name VARCHAR(50) NOT NULL,  -- e.g., 'name', 'job', 'city', 'birthday'
    tag_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, tag_name)
);

-- Create indexes for efficient queries
CREATE INDEX idx_memories_user ON memories(user_id);
CREATE INDEX idx_memories_type ON memories(memory_type);
CREATE INDEX idx_memories_importance ON memories(importance);
CREATE INDEX idx_memories_created ON memories(created_at DESC);
CREATE INDEX idx_memories_last_mentioned ON memories(last_mentioned_at);

CREATE INDEX idx_memory_tags_user ON memory_tags(user_id);
CREATE INDEX idx_memory_tags_name ON memory_tags(tag_name);

-- Add comments
COMMENT ON TABLE memories IS 'User memory storage with vector search integration';
COMMENT ON TABLE memory_tags IS 'User profile tags and attributes';

COMMENT ON COLUMN memories.memory_type IS 'Type of memory: hobby, work, family, feeling, goal, preference, event';
COMMENT ON COLUMN memories.importance IS 'Memory importance level: low, medium, high';
COMMENT ON COLUMN memories.embedding_id IS 'Reference to ChromaDB vector document';
COMMENT ON COLUMN memories.last_mentioned_at IS 'Last time this memory was recalled in conversation';
