"""
AI Cost Tracking Models
Story 10.3: 成本监控与优化 (Cost Monitoring & Optimization)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from app.database import Base


class AICostLog(Base):
    """
    AI API调用成本记录表

    记录每次AI API调用的详细信息，包括：
    - 调用的provider和model
    - 消耗的token数量
    - 产生的成本
    - 响应时间
    """
    __tablename__ = "ai_cost_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # AI Provider信息
    provider = Column(String(50), nullable=False, index=True)  # ollama, deepseek, claude
    model = Column(String(100), nullable=False)

    # Token使用量
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)

    # 成本（美元）
    input_cost_usd = Column(Float, nullable=False, default=0.0)
    output_cost_usd = Column(Float, nullable=False, default=0.0)
    total_cost_usd = Column(Float, nullable=False, default=0.0)

    # 人民币成本（汇率7.2）
    total_cost_cny = Column(Float, nullable=False, default=0.0)

    # 性能指标
    latency_ms = Column(Integer, nullable=True)  # 响应时间（毫秒）

    # 请求详情
    request_type = Column(String(50), nullable=True)  # chat, memory_extract, emotion_analysis等
    endpoint = Column(String(100), nullable=True)

    # 错误信息
    success = Column(Integer, nullable=False, default=1)  # 1=成功, 0=失败
    error_message = Column(Text, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关联
    user = relationship("User", backref="ai_cost_logs")

    # 组合索引（用于快速查询）
    __table_args__ = (
        Index('idx_ai_cost_created_provider', 'created_at', 'provider'),
        Index('idx_ai_cost_user_created', 'user_id', 'created_at'),
    )

    def __repr__(self):
        return f"<AICostLog(id={self.id}, provider={self.provider}, cost=${self.total_cost_usd:.4f})>"


class CostBudget(Base):
    """
    成本预算配置表

    支持不同维度的预算设置：
    - 全局预算
    - 按Provider的预算
    - 按用户的预算
    """
    __tablename__ = "cost_budgets"

    id = Column(Integer, primary_key=True, index=True)

    # 预算维度
    budget_type = Column(String(20), nullable=False)  # global, provider, user
    target_id = Column(String(100), nullable=True)  # provider名称或user_id

    # 预算限额（美元）
    daily_limit_usd = Column(Float, nullable=True)
    monthly_limit_usd = Column(Float, nullable=True)

    # 告警阈值（百分比）
    warning_threshold = Column(Float, nullable=False, default=80.0)  # 达到80%告警
    critical_threshold = Column(Float, nullable=False, default=95.0)  # 达到95%严重告警

    # 启用状态
    is_active = Column(Integer, nullable=False, default=1)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CostBudget(type={self.budget_type}, daily=${self.daily_limit_usd})>"
