-- Migration 031: Create User Preferences Table
-- Story 9.2: 个性化设置
-- Created: 2026-01-19
--
-- Purpose: Store user personalized settings (theme, font size, notifications, etc.)

CREATE TABLE IF NOT EXISTS user_preferences (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Foreign key to users table
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Theme settings
    theme_mode VARCHAR(20) NOT NULL DEFAULT 'auto',
    -- Values: 'light', 'dark', 'auto'

    -- Font size settings
    font_size VARCHAR(20) NOT NULL DEFAULT 'medium',
    -- Values: 'small', 'medium', 'large'

    -- Notification settings
    notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,

    -- Sound settings
    message_sound_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    typing_sound_enabled BOOLEAN NOT NULL DEFAULT FALSE,

    -- Language settings
    language VARCHAR(10) NOT NULL DEFAULT 'zh_CN',
    -- Values: 'zh_CN', 'en_US'

    -- Privacy settings
    show_online_status BOOLEAN NOT NULL DEFAULT TRUE,

    -- Chat settings
    send_on_enter BOOLEAN NOT NULL DEFAULT TRUE,
    show_typing_indicator BOOLEAN NOT NULL DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);

-- Add comments
COMMENT ON TABLE user_preferences IS 'User personalized settings (Story 9.2)';

COMMENT ON COLUMN user_preferences.id IS 'Primary key';
COMMENT ON COLUMN user_preferences.user_id IS 'Foreign key to users table (one-to-one relationship)';
COMMENT ON COLUMN user_preferences.theme_mode IS 'Theme mode: light, dark, auto (follows system)';
COMMENT ON COLUMN user_preferences.font_size IS 'Font size: small, medium, large';
COMMENT ON COLUMN user_preferences.notifications_enabled IS 'Whether push notifications are enabled';
COMMENT ON COLUMN user_preferences.message_sound_enabled IS 'Whether message notification sound is enabled';
COMMENT ON COLUMN user_preferences.typing_sound_enabled IS 'Whether typing sound effects are enabled';
COMMENT ON COLUMN user_preferences.language IS 'Language code: zh_CN (Chinese), en_US (English)';
COMMENT ON COLUMN user_preferences.show_online_status IS 'Whether to show online status to others';
COMMENT ON COLUMN user_preferences.send_on_enter IS 'Whether Enter key sends message (vs. Shift+Enter)';
COMMENT ON COLUMN user_preferences.show_typing_indicator IS 'Whether to show typing indicator to idol';
COMMENT ON COLUMN user_preferences.created_at IS 'Timestamp when preferences were created';
COMMENT ON COLUMN user_preferences.updated_at IS 'Timestamp when preferences were last updated';

COMMIT;
