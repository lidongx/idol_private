"""
A/B Testing Experiment Service
Story 10.4: A/B测试框架 (A/B Testing Framework)

提供实验管理、用户分组、事件追踪、统计分析功能
"""
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.experiment import Experiment, ExperimentAssignment, ExperimentEvent


class ExperimentService:
    """
    A/B测试实验服务

    功能：
    1. 用户分组（基于hash或random）
    2. 事件追踪
    3. 指标计算
    4. 统计显著性检验
    """

    def __init__(self, db: Session):
        self.db = db

    def assign_variant(
        self,
        experiment_name: str,
        user_id: int,
        method: str = 'hash'
    ) -> Optional[str]:
        """
        为用户分配实验变体

        Args:
            experiment_name: 实验名称
            user_id: 用户ID
            method: 分配方式 (hash/random)

        Returns:
            变体名称，如果实验不存在或用户被排除则返回None
        """
        # 获取实验
        experiment = self.db.query(Experiment).filter(
            Experiment.name == experiment_name,
            Experiment.status.in_(['running', 'paused'])
        ).first()

        if not experiment:
            return None

        # 检查是否已分配
        existing = self.db.query(ExperimentAssignment).filter(
            ExperimentAssignment.experiment_id == experiment.id,
            ExperimentAssignment.user_id == user_id
        ).first()

        if existing:
            return None if existing.is_excluded else existing.variant

        # 决定是否参与实验（流量分配）
        if experiment.traffic_allocation < 100:
            hash_val = self._hash_user(user_id, experiment.name)
            if hash_val % 100 >= experiment.traffic_allocation:
                # 用户不在实验流量中，排除
                self._create_assignment(
                    experiment.id,
                    user_id,
                    variant='control',
                    method=method,
                    is_excluded=True,
                    exclusion_reason='traffic_allocation'
                )
                return None

        # 选择变体
        variant = self._select_variant(experiment, user_id, method)

        # 创建分配记录
        self._create_assignment(experiment.id, user_id, variant, method)

        return variant

    def _select_variant(
        self,
        experiment: Experiment,
        user_id: int,
        method: str
    ) -> str:
        """
        根据配置选择变体

        Args:
            experiment: 实验对象
            user_id: 用户ID
            method: 分配方式

        Returns:
            变体名称
        """
        variants_config = experiment.variants_config

        if method == 'hash':
            # 基于user_id和experiment_name的hash
            hash_val = self._hash_user(user_id, experiment.name)

            # 根据ratio分配
            total_ratio = sum(v['ratio'] for v in variants_config)
            normalized_hash = hash_val % total_ratio

            cumulative = 0
            for variant_config in variants_config:
                cumulative += variant_config['ratio']
                if normalized_hash < cumulative:
                    return variant_config['variant']

            # 默认返回第一个
            return variants_config[0]['variant']

        elif method == 'random':
            import random
            random.seed()

            total_ratio = sum(v['ratio'] for v in variants_config)
            rand_val = random.randint(0, total_ratio - 1)

            cumulative = 0
            for variant_config in variants_config:
                cumulative += variant_config['ratio']
                if rand_val < cumulative:
                    return variant_config['variant']

            return variants_config[0]['variant']

        else:
            # 默认返回control
            return 'control'

    def _hash_user(self, user_id: int, experiment_name: str) -> int:
        """
        生成用户hash值（确定性）

        Args:
            user_id: 用户ID
            experiment_name: 实验名称

        Returns:
            hash值 (0-99)
        """
        hash_input = f"{experiment_name}:{user_id}".encode('utf-8')
        hash_digest = hashlib.md5(hash_input).hexdigest()
        return int(hash_digest[:8], 16) % 100

    def _create_assignment(
        self,
        experiment_id: int,
        user_id: int,
        variant: str,
        method: str,
        is_excluded: bool = False,
        exclusion_reason: Optional[str] = None
    ):
        """创建分配记录"""
        assignment = ExperimentAssignment(
            experiment_id=experiment_id,
            user_id=user_id,
            variant=variant,
            assignment_method=method,
            is_excluded=1 if is_excluded else 0,
            exclusion_reason=exclusion_reason
        )
        self.db.add(assignment)
        self.db.commit()

    def track_event(
        self,
        experiment_name: str,
        user_id: int,
        event_type: str,
        event_value: Optional[float] = None,
        event_metadata: Optional[Dict] = None
    ) -> bool:
        """
        追踪实验事件

        Args:
            experiment_name: 实验名称
            user_id: 用户ID
            event_type: 事件类型
            event_value: 事件值
            event_metadata: 事件元数据

        Returns:
            是否成功
        """
        # 获取实验和用户分配
        experiment = self.db.query(Experiment).filter(
            Experiment.name == experiment_name
        ).first()

        if not experiment:
            return False

        assignment = self.db.query(ExperimentAssignment).filter(
            ExperimentAssignment.experiment_id == experiment.id,
            ExperimentAssignment.user_id == user_id,
            ExperimentAssignment.is_excluded == 0
        ).first()

        if not assignment:
            return False

        # 创建事件记录
        event = ExperimentEvent(
            experiment_id=experiment.id,
            user_id=user_id,
            variant=assignment.variant,
            event_type=event_type,
            event_value=event_value,
            event_metadata=event_metadata
        )
        self.db.add(event)
        self.db.commit()

        return True

    def get_experiment_stats(self, experiment_name: str) -> Dict:
        """
        获取实验统计数据

        Args:
            experiment_name: 实验名称

        Returns:
            统计数据
        """
        experiment = self.db.query(Experiment).filter(
            Experiment.name == experiment_name
        ).first()

        if not experiment:
            return {'error': 'Experiment not found'}

        # 获取各变体的用户数
        variant_users = self.db.query(
            ExperimentAssignment.variant,
            func.count(ExperimentAssignment.id).label('user_count')
        ).filter(
            ExperimentAssignment.experiment_id == experiment.id,
            ExperimentAssignment.is_excluded == 0
        ).group_by(ExperimentAssignment.variant).all()

        # 获取各变体的事件统计
        variant_events = self.db.query(
            ExperimentEvent.variant,
            ExperimentEvent.event_type,
            func.count(ExperimentEvent.id).label('event_count'),
            func.avg(ExperimentEvent.event_value).label('avg_value')
        ).filter(
            ExperimentEvent.experiment_id == experiment.id
        ).group_by(
            ExperimentEvent.variant,
            ExperimentEvent.event_type
        ).all()

        # 组织数据
        stats = {
            'experiment_id': experiment.id,
            'experiment_name': experiment.name,
            'status': experiment.status,
            'variants': {}
        }

        for variant_user in variant_users:
            variant = variant_user.variant
            stats['variants'][variant] = {
                'user_count': variant_user.user_count,
                'events': {}
            }

        for variant_event in variant_events:
            variant = variant_event.variant
            event_type = variant_event.event_type

            if variant not in stats['variants']:
                stats['variants'][variant] = {'user_count': 0, 'events': {}}

            stats['variants'][variant]['events'][event_type] = {
                'count': variant_event.event_count,
                'avg_value': float(variant_event.avg_value) if variant_event.avg_value else 0
            }

        return stats

    def calculate_conversion_rate(
        self,
        experiment_name: str,
        conversion_event: str
    ) -> Dict:
        """
        计算转化率

        Args:
            experiment_name: 实验名称
            conversion_event: 转化事件类型

        Returns:
            各变体的转化率
        """
        experiment = self.db.query(Experiment).filter(
            Experiment.name == experiment_name
        ).first()

        if not experiment:
            return {'error': 'Experiment not found'}

        # 获取各变体的用户数
        variant_users = self.db.query(
            ExperimentAssignment.variant,
            func.count(func.distinct(ExperimentAssignment.user_id)).label('total_users')
        ).filter(
            ExperimentAssignment.experiment_id == experiment.id,
            ExperimentAssignment.is_excluded == 0
        ).group_by(ExperimentAssignment.variant).all()

        # 获取各变体的转化用户数
        variant_conversions = self.db.query(
            ExperimentEvent.variant,
            func.count(func.distinct(ExperimentEvent.user_id)).label('converted_users')
        ).filter(
            ExperimentEvent.experiment_id == experiment.id,
            ExperimentEvent.event_type == conversion_event
        ).group_by(ExperimentEvent.variant).all()

        # 计算转化率
        conversion_rates = {}
        users_dict = {v.variant: v.total_users for v in variant_users}
        conversions_dict = {v.variant: v.converted_users for v in variant_conversions}

        for variant, total_users in users_dict.items():
            converted_users = conversions_dict.get(variant, 0)
            conversion_rate = (converted_users / total_users * 100) if total_users > 0 else 0

            conversion_rates[variant] = {
                'total_users': total_users,
                'converted_users': converted_users,
                'conversion_rate': conversion_rate
            }

        return conversion_rates

    def calculate_statistical_significance(
        self,
        control_conversions: int,
        control_total: int,
        treatment_conversions: int,
        treatment_total: int
    ) -> Dict:
        """
        计算统计显著性 (简化版Z-test)

        Args:
            control_conversions: 对照组转化数
            control_total: 对照组总数
            treatment_conversions: 实验组转化数
            treatment_total: 实验组总数

        Returns:
            统计检验结果
        """
        if control_total == 0 or treatment_total == 0:
            return {
                'is_significant': False,
                'p_value': 1.0,
                'confidence_level': 0.0,
                'message': 'Insufficient data'
            }

        # 计算转化率
        p1 = control_conversions / control_total
        p2 = treatment_conversions / treatment_total

        # 计算pooled proportion
        p_pool = (control_conversions + treatment_conversions) / (control_total + treatment_total)

        # 计算标准误差
        se = (p_pool * (1 - p_pool) * (1/control_total + 1/treatment_total)) ** 0.5

        if se == 0:
            return {
                'is_significant': False,
                'p_value': 1.0,
                'confidence_level': 0.0,
                'message': 'Zero standard error'
            }

        # 计算z-score
        z = (p2 - p1) / se

        # 简化的p-value估算 (双侧检验)
        # 使用标准正态分布近似
        import math
        p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))

        # 判断显著性 (α = 0.05)
        is_significant = p_value < 0.05
        confidence_level = (1 - p_value) * 100

        return {
            'is_significant': is_significant,
            'p_value': p_value,
            'confidence_level': confidence_level,
            'z_score': z,
            'lift': ((p2 - p1) / p1 * 100) if p1 > 0 else 0,
            'message': 'Significant' if is_significant else 'Not significant'
        }
