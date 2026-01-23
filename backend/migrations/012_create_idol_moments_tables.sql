-- Migration 012: Create idol_moments and idol_moment_likes tables
-- Story 5.2: 偶像朋友圈系统

-- Idol moments (朋友圈动态)
CREATE TABLE IF NOT EXISTS idol_moments (
    id SERIAL PRIMARY KEY,
    idol_id INTEGER NOT NULL REFERENCES idols(id) ON DELETE CASCADE,
    content TEXT NOT NULL CHECK (char_length(content) <= 300),  -- Max 300 characters
    image_url VARCHAR(255),  -- Optional image
    likes_count INTEGER DEFAULT 0 CHECK (likes_count >= 0),
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Idol moment likes (点赞记录)
CREATE TABLE IF NOT EXISTS idol_moment_likes (
    id SERIAL PRIMARY KEY,
    moment_id INTEGER NOT NULL REFERENCES idol_moments(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Each user can only like a moment once
    UNIQUE(moment_id, user_id)
);

-- Indexes for efficient queries
CREATE INDEX idx_idol_moments_idol_id ON idol_moments(idol_id);
CREATE INDEX idx_idol_moments_posted_at ON idol_moments(posted_at DESC);
CREATE INDEX idx_idol_moment_likes_moment_id ON idol_moment_likes(moment_id);
CREATE INDEX idx_idol_moment_likes_user_id ON idol_moment_likes(user_id);
CREATE INDEX idx_idol_moment_likes_user_moment ON idol_moment_likes(user_id, moment_id);

-- Comments
COMMENT ON TABLE idol_moments IS 'Idol social moments (like WeChat Moments)';
COMMENT ON COLUMN idol_moments.content IS 'Moment text content, max 300 characters';
COMMENT ON COLUMN idol_moments.image_url IS 'Optional image URL';
COMMENT ON COLUMN idol_moments.likes_count IS 'Cached like count for performance';

COMMENT ON TABLE idol_moment_likes IS 'User likes on idol moments';
COMMENT ON COLUMN idol_moment_likes.liked_at IS 'When user liked the moment';
