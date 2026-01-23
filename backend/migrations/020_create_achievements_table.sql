-- Migration 020: Create achievements table and seed initial achievements
-- Story 6.4: 成就系统与每日互动奖励

CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    achievement_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    achievement_type VARCHAR(50) NOT NULL,  -- 'message_count', 'login_streak', 'ritual_count', 'level', 'moment_like'
    condition_value INTEGER NOT NULL,       -- Target value to achieve
    reward_exp INTEGER DEFAULT 0,           -- Exp reward when unlocked
    icon_url VARCHAR(255),                  -- Achievement icon
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient queries
CREATE INDEX idx_achievements_type ON achievements(achievement_type);

-- Insert initial achievements (8 achievements)
INSERT INTO achievements (achievement_name, description, achievement_type, condition_value, reward_exp, icon_url) VALUES
('初次相识', '发送第1条消息', 'message_count', 1, 10, '/achievements/icons/first_message.png'),
('熟悉的陌生人', '发送第10条消息', 'message_count', 10, 20, '/achievements/icons/10_messages.png'),
('无话不谈', '发送第100条消息', 'message_count', 100, 100, '/achievements/icons/100_messages.png'),
('话痨达人', '发送第500条消息', 'message_count', 500, 300, '/achievements/icons/500_messages.png'),
('连续签到7天', '连续登录7天', 'login_streak', 7, 50, '/achievements/icons/streak_7.png'),
('连续签到30天', '连续登录30天', 'login_streak', 30, 200, '/achievements/icons/streak_30.png'),
('早起的鸟儿', '完成10次早安仪式', 'ritual_count', 10, 30, '/achievements/icons/morning_ritual.png'),
('夜猫子', '完成10次晚安仪式', 'ritual_count', 10, 30, '/achievements/icons/night_ritual.png'),
('运势达人', '查看20次每日运势', 'fortune_count', 20, 40, '/achievements/icons/fortune.png'),
('朋友圈活跃分子', '点赞50次朋友圈', 'moment_like', 50, 50, '/achievements/icons/moment_like.png'),
('真爱至上', '达到亲密度Level 50', 'level', 50, 500, '/achievements/icons/level_50.png'),
('灵魂伴侣', '达到亲密度Level 100', 'level', 100, 1000, '/achievements/icons/level_100.png');

-- Comments
COMMENT ON TABLE achievements IS 'Achievement configuration table';
COMMENT ON COLUMN achievements.achievement_name IS 'Achievement display name';
COMMENT ON COLUMN achievements.description IS 'Achievement description';
COMMENT ON COLUMN achievements.achievement_type IS 'Type of achievement (message_count, login_streak, ritual_count, level, etc.)';
COMMENT ON COLUMN achievements.condition_value IS 'Target value to unlock achievement';
COMMENT ON COLUMN achievements.reward_exp IS 'Exp reward when achievement is unlocked';
COMMENT ON COLUMN achievements.icon_url IS 'URL to achievement icon image';
