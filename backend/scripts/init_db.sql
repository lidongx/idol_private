-- idol_private Database Initialization Script
-- Create users table for authentication

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(11) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(20) DEFAULT 'free' NOT NULL,
    subscription_expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create index on phone for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);

-- Add comments for documentation
COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.id IS '用户ID（主键）';
COMMENT ON COLUMN users.phone IS '用户手机号（11位）';
COMMENT ON COLUMN users.password_hash IS 'bcrypt密码哈希';
COMMENT ON COLUMN users.subscription_tier IS '订阅等级: free/basic/premium';
COMMENT ON COLUMN users.subscription_expires_at IS '订阅过期时间';
COMMENT ON COLUMN users.created_at IS '创建时间';
COMMENT ON COLUMN users.updated_at IS '更新时间';

-- Display table structure
SELECT
    column_name,
    data_type,
    character_maximum_length,
    column_default,
    is_nullable
FROM
    information_schema.columns
WHERE
    table_name = 'users'
ORDER BY
    ordinal_position;
