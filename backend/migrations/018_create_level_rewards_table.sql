-- Migration 018: Create level_rewards table for milestone rewards
-- Story 6.3: 等级特权与里程碑奖励

CREATE TABLE IF NOT EXISTS level_rewards (
    id SERIAL PRIMARY KEY,
    level INTEGER UNIQUE NOT NULL,
    reward_type VARCHAR(50) NOT NULL,  -- 'nickname', 'photo', 'voice', 'video', 'feature'
    reward_content JSONB NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient queries
CREATE INDEX idx_level_rewards_level ON level_rewards(level);
CREATE INDEX idx_level_rewards_type ON level_rewards(reward_type);

-- Comments
COMMENT ON TABLE level_rewards IS 'Configuration table for level milestone rewards';
COMMENT ON COLUMN level_rewards.level IS 'Intimacy level at which this reward is unlocked';
COMMENT ON COLUMN level_rewards.reward_type IS 'Type of reward: nickname, photo, voice, video, feature';
COMMENT ON COLUMN level_rewards.reward_content IS 'JSON content specific to reward type';
COMMENT ON COLUMN level_rewards.description IS 'User-facing description of the reward';

-- Seed initial rewards
INSERT INTO level_rewards (level, reward_type, reward_content, description) VALUES
(5, 'nickname', '{"nickname": "宝贝"}', '偶像开始称呼你为"宝贝"'),
(10, 'photo', '{"photo_url": "/rewards/photos/casual_1.jpg", "photo_name": "日常生活照"}', '解锁专属生活照'),
(15, 'feature', '{"feature": "voice_greeting", "feature_name": "语音早安"}', '解锁专属语音早安'),
(20, 'photo', '{"photo_url": "/rewards/photos/artistic_1.jpg", "photo_name": "艺术写真"}', '解锁专属艺术照'),
(30, 'voice', '{"voice_url": "/rewards/voices/diary_1.mp3", "voice_name": "心情日记", "duration": 60}', '解锁专属语音日记'),
(50, 'video', '{"video_url": "/rewards/videos/celebration.mp4", "video_name": "纪念视频", "duration": 120}', '解锁专属纪念视频'),
(75, 'feature', '{"feature": "custom_personality", "feature_name": "个性调整"}', '解锁个性化人设调整'),
(100, 'photo', '{"photo_url": "/rewards/photos/special_100.jpg", "photo_name": "终极纪念照"}', '解锁终极纪念照片');
