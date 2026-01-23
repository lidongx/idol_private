"""
AI Cost Tracking Service
Story 10.3: 成本监控与优化 (Cost Monitoring & Optimization)

提供AI API调用成本追踪和预算监控功能
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.ai_cost import AICostLog, CostBudget


class CostTracker:
    """
    AI成本追踪器

    功能：
    1. 记录AI API调用成本
    2. 计算不同provider的成本
    3. 检查预算限制
    4. 生成成本报告
    """

    # AI Provider定价（美元/1M tokens）
    PRICING = {
        'ollama': {
            'input': 0.0,  # 本地部署，免费
            'output': 0.0,
        },
        'deepseek': {
            'input': 0.14,  # $0.14/1M input tokens
            'output': 0.28,  # $0.28/1M output tokens
        },
        'claude-3-5-sonnet': {
            'input': 3.0,  # $3.00/1M input tokens
            'output': 15.0,  # $15.00/1M output tokens
        },
        'claude-3-haiku': {
            'input': 0.25,  # $0.25/1M input tokens
            'output': 1.25,  # $1.25/1M output tokens
        },
    }

    # 人民币汇率
    USD_TO_CNY = 7.2

    def __init__(self, db: Session):
        self.db = db

    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> Tuple[float, float, float]:
        """
        计算AI调用成本

        Args:
            provider: AI provider名称
            model: 模型名称
            input_tokens: 输入token数
            output_tokens: 输出token数

        Returns:
            (input_cost_usd, output_cost_usd, total_cost_usd)
        """
        # 获取定价
        pricing_key = f"{provider}-{model}" if provider != 'ollama' else provider
        pricing = self.PRICING.get(pricing_key) or self.PRICING.get(provider, {'input': 0, 'output': 0})

        # 计算成本（美元）
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        total_cost = input_cost + output_cost

        return input_cost, output_cost, total_cost

    def log_ai_call(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: Optional[int] = None,
        user_id: Optional[int] = None,
        request_type: Optional[str] = None,
        endpoint: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AICostLog:
        """
        记录一次AI API调用

        Args:
            provider: AI provider
            model: 模型名称
            input_tokens: 输入token数
            output_tokens: 输出token数
            latency_ms: 响应时间（毫秒）
            user_id: 用户ID
            request_type: 请求类型
            endpoint: API端点
            success: 是否成功
            error_message: 错误信息

        Returns:
            AICostLog记录
        """
        # 计算成本
        input_cost, output_cost, total_cost_usd = self.calculate_cost(
            provider, model, input_tokens, output_tokens
        )

        # 转换为人民币
        total_cost_cny = total_cost_usd * self.USD_TO_CNY

        # 创建日志记录
        log = AICostLog(
            user_id=user_id,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            input_cost_usd=input_cost,
            output_cost_usd=output_cost,
            total_cost_usd=total_cost_usd,
            total_cost_cny=total_cost_cny,
            latency_ms=latency_ms,
            request_type=request_type,
            endpoint=endpoint,
            success=1 if success else 0,
            error_message=error_message,
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        return log

    def get_cost_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        provider: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict:
        """
        获取成本汇总

        Args:
            start_date: 开始日期
            end_date: 结束日期
            provider: 按provider筛选
            user_id: 按用户筛选

        Returns:
            成本汇总数据
        """
        # 构建查询
        query = self.db.query(
            func.count(AICostLog.id).label('total_calls'),
            func.sum(AICostLog.total_tokens).label('total_tokens'),
            func.sum(AICostLog.total_cost_usd).label('total_cost_usd'),
            func.sum(AICostLog.total_cost_cny).label('total_cost_cny'),
            func.avg(AICostLog.latency_ms).label('avg_latency_ms'),
            func.sum(func.cast(1 - AICostLog.success, Integer)).label('failed_calls'),
        )

        # 添加筛选条件
        filters = []
        if start_date:
            filters.append(AICostLog.created_at >= start_date)
        if end_date:
            filters.append(AICostLog.created_at < end_date)
        if provider:
            filters.append(AICostLog.provider == provider)
        if user_id:
            filters.append(AICostLog.user_id == user_id)

        if filters:
            query = query.filter(and_(*filters))

        result = query.first()

        return {
            'total_calls': result.total_calls or 0,
            'total_tokens': int(result.total_tokens or 0),
            'total_cost_usd': float(result.total_cost_usd or 0),
            'total_cost_cny': float(result.total_cost_cny or 0),
            'avg_latency_ms': int(result.avg_latency_ms or 0),
            'failed_calls': result.failed_calls or 0,
            'success_rate': (
                (result.total_calls - result.failed_calls) / result.total_calls * 100
                if result.total_calls > 0 else 100.0
            ),
        }

    def get_cost_by_provider(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        按provider分组的成本统计

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            按provider分组的成本列表
        """
        query = self.db.query(
            AICostLog.provider,
            func.count(AICostLog.id).label('total_calls'),
            func.sum(AICostLog.total_tokens).label('total_tokens'),
            func.sum(AICostLog.total_cost_usd).label('total_cost_usd'),
            func.sum(AICostLog.total_cost_cny).label('total_cost_cny'),
        ).group_by(AICostLog.provider)

        # 添加筛选条件
        if start_date:
            query = query.filter(AICostLog.created_at >= start_date)
        if end_date:
            query = query.filter(AICostLog.created_at < end_date)

        results = query.all()

        return [
            {
                'provider': r.provider,
                'total_calls': r.total_calls,
                'total_tokens': int(r.total_tokens or 0),
                'total_cost_usd': float(r.total_cost_usd or 0),
                'total_cost_cny': float(r.total_cost_cny or 0),
            }
            for r in results
        ]

    def get_daily_cost_trend(
        self,
        days: int = 30,
        provider: Optional[str] = None
    ) -> List[Dict]:
        """
        获取每日成本趋势

        Args:
            days: 天数
            provider: 按provider筛选

        Returns:
            每日成本列表
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        query = self.db.query(
            func.date(AICostLog.created_at).label('date'),
            func.count(AICostLog.id).label('total_calls'),
            func.sum(AICostLog.total_cost_usd).label('total_cost_usd'),
            func.sum(AICostLog.total_cost_cny).label('total_cost_cny'),
        ).filter(AICostLog.created_at >= start_date)

        if provider:
            query = query.filter(AICostLog.provider == provider)

        query = query.group_by(func.date(AICostLog.created_at)).order_by(func.date(AICostLog.created_at))

        results = query.all()

        return [
            {
                'date': r.date.isoformat(),
                'total_calls': r.total_calls,
                'total_cost_usd': float(r.total_cost_usd or 0),
                'total_cost_cny': float(r.total_cost_cny or 0),
            }
            for r in results
        ]

    def check_budget(
        self,
        budget_type: str = 'global',
        target_id: Optional[str] = None
    ) -> Dict:
        """
        检查预算使用情况

        Args:
            budget_type: 预算类型 (global, provider, user)
            target_id: provider名称或user_id

        Returns:
            预算使用情况
        """
        # 获取预算配置
        budget_query = self.db.query(CostBudget).filter(
            CostBudget.budget_type == budget_type,
            CostBudget.is_active == 1
        )

        if target_id:
            budget_query = budget_query.filter(CostBudget.target_id == target_id)

        budget = budget_query.first()

        if not budget:
            return {
                'has_budget': False,
                'message': 'No budget configured',
            }

        # 计算今日成本
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_cost = self.get_cost_summary(
            start_date=today_start,
            provider=target_id if budget_type == 'provider' else None,
            user_id=int(target_id) if budget_type == 'user' and target_id else None
        )['total_cost_usd']

        # 计算本月成本
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_cost = self.get_cost_summary(
            start_date=month_start,
            provider=target_id if budget_type == 'provider' else None,
            user_id=int(target_id) if budget_type == 'user' and target_id else None
        )['total_cost_usd']

        # 计算使用百分比
        daily_usage_pct = (daily_cost / budget.daily_limit_usd * 100) if budget.daily_limit_usd else 0
        monthly_usage_pct = (monthly_cost / budget.monthly_limit_usd * 100) if budget.monthly_limit_usd else 0

        # 判断告警级别
        alert_level = 'normal'
        if daily_usage_pct >= budget.critical_threshold or monthly_usage_pct >= budget.critical_threshold:
            alert_level = 'critical'
        elif daily_usage_pct >= budget.warning_threshold or monthly_usage_pct >= budget.warning_threshold:
            alert_level = 'warning'

        return {
            'has_budget': True,
            'budget_type': budget_type,
            'target_id': target_id,
            'daily_limit_usd': float(budget.daily_limit_usd) if budget.daily_limit_usd else None,
            'monthly_limit_usd': float(budget.monthly_limit_usd) if budget.monthly_limit_usd else None,
            'daily_cost_usd': daily_cost,
            'monthly_cost_usd': monthly_cost,
            'daily_usage_pct': daily_usage_pct,
            'monthly_usage_pct': monthly_usage_pct,
            'alert_level': alert_level,
            'warning_threshold': float(budget.warning_threshold),
            'critical_threshold': float(budget.critical_threshold),
        }

    def get_top_users_by_cost(
        self,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        获取成本最高的用户

        Args:
            limit: 返回数量
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            用户成本列表
        """
        query = self.db.query(
            AICostLog.user_id,
            func.count(AICostLog.id).label('total_calls'),
            func.sum(AICostLog.total_cost_usd).label('total_cost_usd'),
            func.sum(AICostLog.total_cost_cny).label('total_cost_cny'),
        ).filter(AICostLog.user_id.isnot(None))

        if start_date:
            query = query.filter(AICostLog.created_at >= start_date)
        if end_date:
            query = query.filter(AICostLog.created_at < end_date)

        query = query.group_by(AICostLog.user_id).order_by(
            func.sum(AICostLog.total_cost_usd).desc()
        ).limit(limit)

        results = query.all()

        return [
            {
                'user_id': r.user_id,
                'total_calls': r.total_calls,
                'total_cost_usd': float(r.total_cost_usd or 0),
                'total_cost_cny': float(r.total_cost_cny or 0),
            }
            for r in results
        ]
