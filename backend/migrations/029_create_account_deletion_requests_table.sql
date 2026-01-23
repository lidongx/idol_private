-- Migration 029: Create account_deletion_requests table
-- Story 8.4: 账号删除与数据清除
-- Date: 2026-01-19

CREATE TABLE IF NOT EXISTS account_deletion_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    reason VARCHAR(50),
    detailed_reason TEXT,
    scheduled_deletion_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    backup_created BOOLEAN DEFAULT FALSE,
    backup_filepath VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_account_deletion_requests_user_id ON account_deletion_requests(user_id);
CREATE INDEX idx_account_deletion_requests_status ON account_deletion_requests(status);
CREATE INDEX idx_account_deletion_requests_scheduled_deletion_at ON account_deletion_requests(scheduled_deletion_at);

-- Add comments
COMMENT ON TABLE account_deletion_requests IS '账号删除请求表';
COMMENT ON COLUMN account_deletion_requests.id IS '主键ID';
COMMENT ON COLUMN account_deletion_requests.user_id IS '用户ID';
COMMENT ON COLUMN account_deletion_requests.status IS '状态: pending(待删除), cancelled(已取消), completed(已完成)';
COMMENT ON COLUMN account_deletion_requests.reason IS '删除原因';
COMMENT ON COLUMN account_deletion_requests.detailed_reason IS '详细说明';
COMMENT ON COLUMN account_deletion_requests.scheduled_deletion_at IS '预定删除时间（7天后）';
COMMENT ON COLUMN account_deletion_requests.completed_at IS '实际删除时间';
COMMENT ON COLUMN account_deletion_requests.backup_created IS '是否已创建备份';
COMMENT ON COLUMN account_deletion_requests.backup_filepath IS '备份文件路径';
COMMENT ON COLUMN account_deletion_requests.created_at IS '创建时间';
COMMENT ON COLUMN account_deletion_requests.updated_at IS '更新时间';
