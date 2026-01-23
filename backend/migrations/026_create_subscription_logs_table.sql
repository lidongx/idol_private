-- Migration 026: Create subscription_logs table
-- Story 7.5: 订阅激活与权限管理
-- Date: 2026-01-19
-- Description: Track subscription lifecycle events (activate, renew, cancel, expire, refund)

-- Create subscription_logs table
CREATE TABLE IF NOT EXISTS subscription_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    plan_id INTEGER REFERENCES subscription_plans(id) ON DELETE SET NULL,
    order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    expires_at TIMESTAMP NULL,
    notes VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient querying
CREATE INDEX idx_subscription_logs_user_id ON subscription_logs(user_id);
CREATE INDEX idx_subscription_logs_action ON subscription_logs(action);
CREATE INDEX idx_subscription_logs_created_at ON subscription_logs(created_at DESC);

-- Add comments
COMMENT ON TABLE subscription_logs IS '订阅变更日志表';
COMMENT ON COLUMN subscription_logs.user_id IS '用户ID';
COMMENT ON COLUMN subscription_logs.action IS '操作类型: activate, renew, cancel, expire, upgrade, downgrade, refund';
COMMENT ON COLUMN subscription_logs.plan_id IS '关联的订阅套餐ID';
COMMENT ON COLUMN subscription_logs.order_id IS '关联的订单ID';
COMMENT ON COLUMN subscription_logs.expires_at IS '订阅到期时间（记录当时的值）';
COMMENT ON COLUMN subscription_logs.notes IS '备注信息';
COMMENT ON COLUMN subscription_logs.created_at IS '创建时间';
