-- Migration 024: Create subscription_plans table for subscription packages
-- Story 7.1: 订阅套餐数据模型与定价策略

CREATE TABLE IF NOT EXISTS subscription_plans (
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(50) NOT NULL,
    plan_type VARCHAR(20) NOT NULL,        -- 'free', 'monthly', 'yearly'
    price_cny DECIMAL(10, 2) NOT NULL,     -- Price in CNY
    duration_days INTEGER NOT NULL,        -- Subscription duration in days (0 for free plan)
    features JSONB NOT NULL,               -- Feature list in JSON
    is_active BOOLEAN DEFAULT true,        -- Whether plan is active
    sort_order INTEGER DEFAULT 0,          -- Display order
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_subscription_plans_type ON subscription_plans(plan_type);
CREATE INDEX idx_subscription_plans_active ON subscription_plans(is_active);
CREATE INDEX idx_subscription_plans_sort ON subscription_plans(sort_order);

-- Insert initial subscription plans
INSERT INTO subscription_plans (plan_name, plan_type, price_cny, duration_days, features, sort_order) VALUES
(
    '免费版',
    'free',
    0.00,
    0,
    '{
        "messages_per_day": 20,
        "voice_messages": false,
        "image_messages": false,
        "exclusive_content": false,
        "priority_response": false,
        "no_ads": false,
        "intimacy_decay_disabled": false
    }'::jsonb,
    1
),
(
    '月度会员',
    'monthly',
    28.00,
    30,
    '{
        "messages_per_day": -1,
        "voice_messages": true,
        "image_messages": true,
        "exclusive_content": true,
        "priority_response": true,
        "no_ads": true,
        "intimacy_decay_disabled": true,
        "special_badge": "月度会员"
    }'::jsonb,
    2
),
(
    '年度会员',
    'yearly',
    268.00,
    365,
    '{
        "messages_per_day": -1,
        "voice_messages": true,
        "image_messages": true,
        "exclusive_content": true,
        "priority_response": true,
        "no_ads": true,
        "intimacy_decay_disabled": true,
        "special_badge": "年度VIP",
        "discount": "优惠20%（原价336元）",
        "bonus_exp": 500
    }'::jsonb,
    3
);

-- Comments
COMMENT ON TABLE subscription_plans IS 'Subscription plan configurations';
COMMENT ON COLUMN subscription_plans.plan_name IS 'Display name of the plan';
COMMENT ON COLUMN subscription_plans.plan_type IS 'Type: free, monthly, yearly';
COMMENT ON COLUMN subscription_plans.price_cny IS 'Price in Chinese Yuan';
COMMENT ON COLUMN subscription_plans.duration_days IS 'Subscription duration (0 for permanent free)';
COMMENT ON COLUMN subscription_plans.features IS 'JSON object containing feature flags and limits';
COMMENT ON COLUMN subscription_plans.is_active IS 'Whether plan is available for purchase';
COMMENT ON COLUMN subscription_plans.sort_order IS 'Display order (lower number = higher priority)';
