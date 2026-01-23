-- Migration 025: Create orders table for subscription purchases
-- Story 7.1: 订阅套餐数据模型与定价策略

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(32) UNIQUE NOT NULL,  -- Unique order number (e.g., IDL20260119123456)
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES subscription_plans(id),
    amount DECIMAL(10, 2) NOT NULL,        -- Order amount in CNY
    payment_method VARCHAR(50),            -- 'alipay', 'wechat', 'apple_iap', 'google_play'
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'paid', 'failed', 'cancelled', 'refunded'
    paid_at TIMESTAMP NULL,                -- Payment completion time
    expires_at TIMESTAMP NULL,             -- Subscription expiry time
    transaction_id VARCHAR(100),           -- Payment gateway transaction ID
    refund_reason TEXT,                    -- Reason for refund (if refunded)
    refunded_at TIMESTAMP NULL,            -- Refund time
    metadata JSONB,                        -- Additional metadata (payment gateway response, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient queries
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_order_no ON orders(order_no);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
CREATE INDEX idx_orders_paid_at ON orders(paid_at DESC);

-- Comments
COMMENT ON TABLE orders IS 'Subscription purchase orders';
COMMENT ON COLUMN orders.order_no IS 'Unique order number for tracking';
COMMENT ON COLUMN orders.user_id IS 'User who placed the order';
COMMENT ON COLUMN orders.plan_id IS 'Subscription plan purchased';
COMMENT ON COLUMN orders.amount IS 'Order amount in CNY';
COMMENT ON COLUMN orders.payment_method IS 'Payment method used';
COMMENT ON COLUMN orders.status IS 'Order status: pending, paid, failed, cancelled, refunded';
COMMENT ON COLUMN orders.paid_at IS 'When payment was completed';
COMMENT ON COLUMN orders.expires_at IS 'When subscription expires';
COMMENT ON COLUMN orders.transaction_id IS 'Payment gateway transaction ID';
COMMENT ON COLUMN orders.refund_reason IS 'Reason for refund (if applicable)';
COMMENT ON COLUMN orders.metadata IS 'Additional data from payment gateway';
