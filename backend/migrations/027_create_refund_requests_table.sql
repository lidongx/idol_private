-- Migration 027: Create refund_requests table
-- Story 7.6: 订阅管理与退款处理
-- Date: 2026-01-19
-- Description: Track subscription refund requests and their processing status

-- Create refund_requests table
CREATE TABLE IF NOT EXISTS refund_requests (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason VARCHAR(200) NOT NULL,
    detailed_reason TEXT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    admin_notes TEXT NULL,
    processed_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient querying
CREATE INDEX idx_refund_requests_user_id ON refund_requests(user_id);
CREATE INDEX idx_refund_requests_order_id ON refund_requests(order_id);
CREATE INDEX idx_refund_requests_status ON refund_requests(status);
CREATE INDEX idx_refund_requests_created_at ON refund_requests(created_at DESC);

-- Add comments
COMMENT ON TABLE refund_requests IS '退款申请表';
COMMENT ON COLUMN refund_requests.order_id IS '关联的订单ID';
COMMENT ON COLUMN refund_requests.user_id IS '申请退款的用户ID';
COMMENT ON COLUMN refund_requests.reason IS '退款原因（预设选项）';
COMMENT ON COLUMN refund_requests.detailed_reason IS '详细说明（可选）';
COMMENT ON COLUMN refund_requests.status IS '状态: pending（待审核）, approved（已通过）, rejected（已拒绝）';
COMMENT ON COLUMN refund_requests.admin_notes IS '管理员备注（内部使用）';
COMMENT ON COLUMN refund_requests.processed_at IS '处理时间';
COMMENT ON COLUMN refund_requests.created_at IS '创建时间';
