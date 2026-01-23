-- Migration: Create A/B Testing Tables
-- Story 10.4: A/B测试框架 (A/B Testing Framework)
-- Created: 2026-01-20

-- ==================== Experiments Table ====================

CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,

    -- 实验基本信息
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    hypothesis TEXT,

    -- 实验状态
    status VARCHAR(20) NOT NULL DEFAULT 'draft',  -- draft, running, paused, completed, archived

    -- 实验类型
    experiment_type VARCHAR(50) NOT NULL,

    -- 分组配置 (JSONB)
    variants_config JSONB NOT NULL,

    -- 目标指标 (JSONB)
    metrics_config JSONB,

    -- 流量分配
    traffic_allocation INTEGER NOT NULL DEFAULT 100,

    -- 最小样本量
    min_sample_size INTEGER DEFAULT 1000,

    -- 实验时间
    start_date TIMESTAMP,
    end_date TIMESTAMP,

    -- 实验结果
    winning_variant VARCHAR(50),
    confidence_level DECIMAL(5, 2),

    -- 创建者
    created_by VARCHAR(100),

    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_experiments_name ON experiments(name);
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);

-- ==================== Experiment Assignments Table ====================

CREATE TABLE IF NOT EXISTS experiment_assignments (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- 分配的变体
    variant VARCHAR(50) NOT NULL,

    -- 分配方式
    assignment_method VARCHAR(20) NOT NULL DEFAULT 'hash',

    -- 是否排除
    is_excluded SMALLINT NOT NULL DEFAULT 0,
    exclusion_reason VARCHAR(200),

    -- 时间戳
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_exp_assign_experiment ON experiment_assignments(experiment_id);
CREATE INDEX IF NOT EXISTS idx_exp_assign_user ON experiment_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_exp_assign_assigned_at ON experiment_assignments(assigned_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_exp_assign_experiment_user ON experiment_assignments(experiment_id, user_id);

-- ==================== Experiment Events Table ====================

CREATE TABLE IF NOT EXISTS experiment_events (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- 变体
    variant VARCHAR(50) NOT NULL,

    -- 事件信息
    event_type VARCHAR(50) NOT NULL,
    event_value DECIMAL(10, 2),
    event_metadata JSONB,

    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_exp_events_experiment ON experiment_events(experiment_id);
CREATE INDEX IF NOT EXISTS idx_exp_events_user ON experiment_events(user_id);
CREATE INDEX IF NOT EXISTS idx_exp_events_variant ON experiment_events(variant);
CREATE INDEX IF NOT EXISTS idx_exp_events_event_type ON experiment_events(event_type);
CREATE INDEX IF NOT EXISTS idx_exp_events_created_at ON experiment_events(created_at);
CREATE INDEX IF NOT EXISTS idx_exp_events_experiment_variant_event ON experiment_events(experiment_id, variant, event_type);
CREATE INDEX IF NOT EXISTS idx_exp_events_experiment_created ON experiment_events(experiment_id, created_at);

-- ==================== 添加注释 ====================

COMMENT ON TABLE experiments IS 'A/B测试实验配置表';
COMMENT ON TABLE experiment_assignments IS '实验分组分配表';
COMMENT ON TABLE experiment_events IS '实验事件追踪表';

COMMENT ON COLUMN experiments.status IS '状态: draft, running, paused, completed, archived';
COMMENT ON COLUMN experiments.variants_config IS 'JSON格式的变体配置';
COMMENT ON COLUMN experiments.traffic_allocation IS '流量分配百分比 (0-100)';
COMMENT ON COLUMN experiment_assignments.assignment_method IS '分配方式: hash, random, manual';
COMMENT ON COLUMN experiment_events.event_type IS '事件类型: page_view, click, conversion, retention等';

-- ==================== 插入示例实验 ====================

-- 示例：测试新的消息推荐算法
INSERT INTO experiments (
    name,
    description,
    hypothesis,
    status,
    experiment_type,
    variants_config,
    metrics_config,
    traffic_allocation,
    created_by
) VALUES (
    'message_recommendation_v2',
    '测试新的消息推荐算法是否能提升用户参与度',
    '新的AI推荐算法能提升10%以上的消息回复率',
    'draft',
    'algorithm',
    '[
        {"variant": "control", "ratio": 50, "description": "当前算法"},
        {"variant": "treatment", "ratio": 50, "description": "新AI推荐算法"}
    ]'::jsonb,
    '{
        "primary": "message_reply_rate",
        "secondary": ["session_duration", "messages_per_session"]
    }'::jsonb,
    100,
    'system'
) ON CONFLICT DO NOTHING;

-- 示例：测试新的订阅定价
INSERT INTO experiments (
    name,
    description,
    hypothesis,
    status,
    experiment_type,
    variants_config,
    metrics_config,
    traffic_allocation,
    created_by
) VALUES (
    'subscription_pricing_test',
    '测试不同订阅价格对转化率的影响',
    '降价10%能提升20%的转化率，整体收入增加',
    'draft',
    'pricing',
    '[
        {"variant": "control", "ratio": 50, "price": 30},
        {"variant": "discount_10pct", "ratio": 50, "price": 27}
    ]'::jsonb,
    '{
        "primary": "subscription_conversion_rate",
        "secondary": ["revenue_per_user", "ltv"]
    }'::jsonb,
    50,
    'system'
) ON CONFLICT DO NOTHING;
