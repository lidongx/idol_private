-- Migration: Add voice_url to messages table
-- Story: 2.5 - Voice Message Record & Playback

-- Add voice_url column for storing voice message file URLs
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS voice_url VARCHAR(500);

-- Add message_type column to distinguish text/voice messages
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS message_type VARCHAR(20) DEFAULT 'text'
CHECK (message_type IN ('text', 'voice', 'image', 'emoji'));

-- Add voice_duration column for storing voice message duration in seconds
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS voice_duration INTEGER;

-- Add index for message_type for faster filtering
CREATE INDEX IF NOT EXISTS idx_messages_message_type ON messages(message_type);

-- Update existing messages to have type 'text'
UPDATE messages SET message_type = 'text' WHERE message_type IS NULL;

-- Add comment
COMMENT ON COLUMN messages.voice_url IS 'URL to voice message audio file (MP3/M4A)';
COMMENT ON COLUMN messages.message_type IS 'Type of message: text, voice, image, emoji';
COMMENT ON COLUMN messages.voice_duration IS 'Voice message duration in seconds';
