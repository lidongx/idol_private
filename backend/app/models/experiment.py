"""
A/B Testing Experiment Models
Story 10.4: A/B测试框架 (A/B Testing Framework)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Experiment(Base):
    """
    A/B测试实验配置表

    定义实验的基本信息、分组策略、指标等
    """
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)

    # 实验基本信息
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    hypothesis = Column(Text, nullable=True)  # 实验假设

    # 实验状态
    status = Column(String(20), nullable=False, default='draft')  # draft, running, paused, completed, archived

    # 实验类型
    experiment_type = Column(String(50), nullable=False)  # feature_flag, ui_variant, algorithm, pricing等

    # 分组配置 (JSON)
    # Example: [{"variant": "control", "ratio": 50}, {"variant": "treatment", "ratio": 50}]
    variants_config = Column(JSON, nullable=False)

    # 目标指标 (JSON)
    # Example: {"primary": "conversion_rate", "secondary": ["retention_7d", "engagement"]}
    metrics_config = Column(JSON, nullable=True)

    # 流量分配比例
    traffic_allocation = Column(Integer, nullable=False, default=100)  # 0-100%

    # 最小样本量
    min_sample_size = Column(Integer, nullable=True, default=1000)

    # 实验时间
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    # 实验结果
    winning_variant = Column(String(50), nullable=True)  # 获胜变体
    confidence_level = Column(Float, nullable=True)  # 置信度

    # 创建者
    created_by = Column(String(100), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    assignments = relationship("ExperimentAssignment", back_populates="experiment")
    events = relationship("ExperimentEvent", back_populates="experiment")

    def __repr__(self):
        return f"<Experiment(name={self.name}, status={self.status})>"


class ExperimentAssignment(Base):
    """
    实验分组分配表

    记录每个用户被分配到哪个实验的哪个变体
    """
    __tablename__ = "experiment_assignments"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 分配的变体
    variant = Column(String(50), nullable=False)

    # 分配方式
    assignment_method = Column(String(20), nullable=False, default='hash')  # hash, random, manual

    # 是否排除（某些用户可能不适合某些实验）
    is_excluded = Column(Integer, nullable=False, default=0)
    exclusion_reason = Column(String(200), nullable=True)

    # 时间戳
    assigned_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关联
    experiment = relationship("Experiment", back_populates="assignments")

    # 组合索引
    __table_args__ = (
        Index('idx_experiment_user', 'experiment_id', 'user_id', unique=True),
    )

    def __repr__(self):
        return f"<ExperimentAssignment(exp={self.experiment_id}, user={self.user_id}, variant={self.variant})>"


class ExperimentEvent(Base):
    """
    实验事件追踪表

    记录实验中的用户行为事件，用于计算指标
    """
    __tablename__ = "experiment_events"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 用户所在变体
    variant = Column(String(50), nullable=False, index=True)

    # 事件信息
    event_type = Column(String(50), nullable=False, index=True)  # page_view, click, conversion, retention等
    event_value = Column(Float, nullable=True)  # 事件值（如收入金额）
    event_metadata = Column(JSON, nullable=True)  # 事件额外数据

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关联
    experiment = relationship("Experiment", back_populates="events")

    # 组合索引
    __table_args__ = (
        Index('idx_experiment_variant_event', 'experiment_id', 'variant', 'event_type'),
        Index('idx_experiment_created', 'experiment_id', 'created_at'),
    )

    def __repr__(self):
        return f"<ExperimentEvent(exp={self.experiment_id}, variant={self.variant}, event={self.event_type})>"
