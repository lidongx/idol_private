-- Migration: Create AI Cost Tracking Tables
-- Story 10.3: 成本监控与优化 (Cost Monitoring & Optimization)
-- Created: 2026-01-20

-- ==================== AI Cost Logs Table ====================

CREATE TABLE IF NOT EXISTS ai_cost_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- AI Provider信息
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,

    -- Token使用量
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,

    -- 成本（美元）
    input_cost_usd DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
    output_cost_usd DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
    total_cost_usd DECIMAL(10, 6) NOT NULL DEFAULT 0.0,

    -- 人民币成本
    total_cost_cny DECIMAL(10, 4) NOT NULL DEFAULT 0.0,

    -- 性能指标
    latency_ms INTEGER,

    -- 请求详情
    request_type VARCHAR(50),
    endpoint VARCHAR(100),

    -- 错误信息
    success SMALLINT NOT NULL DEFAULT 1,
    error_message TEXT,

    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_ai_cost_logs_user_id ON ai_cost_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_cost_logs_provider ON ai_cost_logs(provider);
CREATE INDEX IF NOT EXISTS idx_ai_cost_logs_created_at ON ai_cost_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_cost_logs_created_provider ON ai_cost_logs(created_at, provider);
CREATE INDEX IF NOT EXISTS idx_ai_cost_logs_user_created ON ai_cost_logs(user_id, created_at);

-- ==================== Cost Budget Table ====================

CREATE TABLE IF NOT EXISTS cost_budgets (
    id SERIAL PRIMARY KEY,

    -- 预算维度
    budget_type VARCHAR(20) NOT NULL,  -- 'global', 'provider', 'user'
    target_id VARCHAR(100),             -- provider名称或user_id

    -- 预算限额（美元）
    daily_limit_usd DECIMAL(10, 2),
    monthly_limit_usd DECIMAL(10, 2),

    -- 告警阈值（百分比）
    warning_threshold DECIMAL(5, 2) NOT NULL DEFAULT 80.0,
    critical_threshold DECIMAL(5, 2) NOT NULL DEFAULT 95.0,

    -- 启用状态
    is_active SMALLINT NOT NULL DEFAULT 1,

    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 预算表索引
CREATE INDEX IF NOT EXISTS idx_cost_budgets_type ON cost_budgets(budget_type);
CREATE INDEX IF NOT EXISTS idx_cost_budgets_active ON cost_budgets(is_active);

-- ==================== 插入默认预算配置 ====================

-- 全局预算：每日$10, 每月$200
INSERT INTO cost_budgets (budget_type, target_id, daily_limit_usd, monthly_limit_usd, warning_threshold, critical_threshold)
VALUES ('global', NULL, 10.00, 200.00, 80.0, 95.0)
ON CONFLICT DO NOTHING;

-- Deepseek预算：每日$5, 每月$100
INSERT INTO cost_budgets (budget_type, target_id, daily_limit_usd, monthly_limit_usd, warning_threshold, critical_threshold)
VALUES ('provider', 'deepseek', 5.00, 100.00, 80.0, 95.0)
ON CONFLICT DO NOTHING;

-- Claude预算：每日$8, 每月$150
INSERT INTO cost_budgets (budget_type, target_id, daily_limit_usd, monthly_limit_usd, warning_threshold, critical_threshold)
VALUES ('provider', 'claude', 8.00, 150.00, 80.0, 95.0)
ON CONFLICT DO NOTHING;

-- Ollama预算：$0（本地部署）
INSERT INTO cost_budgets (budget_type, target_id, daily_limit_usd, monthly_limit_usd, warning_threshold, critical_threshold)
VALUES ('provider', 'ollama', 0.00, 0.00, 80.0, 95.0)
ON CONFLICT DO NOTHING;

-- ==================== 添加注释 ====================

COMMENT ON TABLE ai_cost_logs IS 'AI API调用成本记录表';
COMMENT ON TABLE cost_budgets IS '成本预算配置表';

COMMENT ON COLUMN ai_cost_logs.provider IS 'AI provider: ollama, deepseek, claude';
COMMENT ON COLUMN ai_cost_logs.total_cost_usd IS '总成本（美元）';
COMMENT ON COLUMN ai_cost_logs.total_cost_cny IS '总成本（人民币，汇率7.2）';
COMMENT ON COLUMN ai_cost_logs.success IS '调用是否成功: 1=成功, 0=失败';

COMMENT ON COLUMN cost_budgets.budget_type IS '预算类型: global, provider, user';
COMMENT ON COLUMN cost_budgets.warning_threshold IS '告警阈值（百分比），默认80%';
COMMENT ON COLUMN cost_budgets.critical_threshold IS '严重告警阈值（百分比），默认95%';
