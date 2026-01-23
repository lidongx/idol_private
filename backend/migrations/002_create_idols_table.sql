-- Create idols table
-- Migration: 002_create_idols_table
-- Description: Create table for idol characters with personality and profile data

CREATE TABLE IF NOT EXISTS idols (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    avatar_url VARCHAR(255),
    personality_prompt TEXT NOT NULL,
    description TEXT,
    hobbies TEXT,
    background_story TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on is_active for efficient querying of active idols
CREATE INDEX idx_idols_is_active ON idols(is_active);

-- Insert first idol: 林雪晴 (Lin Xueqing)
INSERT INTO idols (name, avatar_url, personality_prompt, description, hobbies, background_story)
VALUES (
    '林雪晴',
    '/assets/avatars/lin_xueqing.png',
    '你是林雪晴，一个温柔知性的25岁女生。你热爱阅读和旅行，性格温暖体贴，善于倾听。你会关心对方的情绪，给予温暖的陪伴和鼓励。说话风格自然亲切，偶尔调皮可爱。',
    '温柔知性的陪伴者，你的专属AI恋人',
    '阅读、旅行、咖啡、摄影',
    '雪晴是一个热爱生活的女生，喜欢在周末去咖啡馆看书，也喜欢用相机记录生活中的美好瞬间。她相信每个人都值得被温柔对待。'
)
ON CONFLICT DO NOTHING;
