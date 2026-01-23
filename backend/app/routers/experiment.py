"""
A/B Testing Experiment API
Story 10.4: A/B测试框架 (A/B Testing Framework)
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.experiment_service import ExperimentService
from app.models.experiment import Experiment


router = APIRouter(prefix="/api/v1/experiments", tags=["A/B Testing"])


# ==================== Request/Response Models ====================

class AssignVariantRequest(BaseModel):
    user_id: int
    method: str = 'hash'  # hash or random


class TrackEventRequest(BaseModel):
    user_id: int
    event_type: str
    event_value: Optional[float] = None
    event_metadata: Optional[dict] = None


class CalculateSignificanceRequest(BaseModel):
    control_conversions: int
    control_total: int
    treatment_conversions: int
    treatment_total: int


# ==================== API Endpoints ====================

@router.get("/list")
def list_experiments(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取实验列表

    Args:
        status: 筛选状态 (draft, running, paused, completed, archived)
    """
    query = db.query(Experiment)

    if status:
        query = query.filter(Experiment.status == status)

    experiments = query.order_by(Experiment.created_at.desc()).all()

    return {
        "status": "success",
        "data": [
            {
                "id": exp.id,
                "name": exp.name,
                "description": exp.description,
                "status": exp.status,
                "experiment_type": exp.experiment_type,
                "traffic_allocation": exp.traffic_allocation,
                "start_date": exp.start_date.isoformat() if exp.start_date else None,
                "end_date": exp.end_date.isoformat() if exp.end_date else None,
                "created_at": exp.created_at.isoformat(),
            }
            for exp in experiments
        ]
    }


@router.get("/{experiment_name}")
def get_experiment(experiment_name: str, db: Session = Depends(get_db)):
    """
    获取实验详情
    """
    experiment = db.query(Experiment).filter(
        Experiment.name == experiment_name
    ).first()

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return {
        "status": "success",
        "data": {
            "id": experiment.id,
            "name": experiment.name,
            "description": experiment.description,
            "hypothesis": experiment.hypothesis,
            "status": experiment.status,
            "experiment_type": experiment.experiment_type,
            "variants_config": experiment.variants_config,
            "metrics_config": experiment.metrics_config,
            "traffic_allocation": experiment.traffic_allocation,
            "min_sample_size": experiment.min_sample_size,
            "start_date": experiment.start_date.isoformat() if experiment.start_date else None,
            "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
            "winning_variant": experiment.winning_variant,
            "confidence_level": float(experiment.confidence_level) if experiment.confidence_level else None,
            "created_by": experiment.created_by,
            "created_at": experiment.created_at.isoformat(),
            "updated_at": experiment.updated_at.isoformat(),
        }
    }


@router.post("/{experiment_name}/assign")
def assign_variant(
    experiment_name: str,
    request: AssignVariantRequest,
    db: Session = Depends(get_db)
):
    """
    为用户分配实验变体

    Args:
        experiment_name: 实验名称
        request: 包含user_id和method
    """
    service = ExperimentService(db)

    variant = service.assign_variant(
        experiment_name=experiment_name,
        user_id=request.user_id,
        method=request.method
    )

    if variant is None:
        return {
            "status": "success",
            "data": {
                "assigned": False,
                "variant": None,
                "reason": "User excluded or experiment not running"
            }
        }

    return {
        "status": "success",
        "data": {
            "assigned": True,
            "variant": variant,
            "user_id": request.user_id
        }
    }


@router.post("/{experiment_name}/track")
def track_event(
    experiment_name: str,
    request: TrackEventRequest,
    db: Session = Depends(get_db)
):
    """
    追踪实验事件

    Args:
        experiment_name: 实验名称
        request: 包含事件数据
    """
    service = ExperimentService(db)

    success = service.track_event(
        experiment_name=experiment_name,
        user_id=request.user_id,
        event_type=request.event_type,
        event_value=request.event_value,
        event_metadata=request.event_metadata
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to track event. User may not be assigned to experiment."
        )

    return {
        "status": "success",
        "data": {
            "tracked": True,
            "event_type": request.event_type
        }
    }


@router.get("/{experiment_name}/stats")
def get_experiment_stats(experiment_name: str, db: Session = Depends(get_db)):
    """
    获取实验统计数据

    返回各变体的用户数、事件统计等
    """
    service = ExperimentService(db)
    stats = service.get_experiment_stats(experiment_name)

    if 'error' in stats:
        raise HTTPException(status_code=404, detail=stats['error'])

    return {
        "status": "success",
        "data": stats
    }


@router.get("/{experiment_name}/conversion-rate")
def get_conversion_rate(
    experiment_name: str,
    conversion_event: str,
    db: Session = Depends(get_db)
):
    """
    计算实验的转化率

    Args:
        experiment_name: 实验名称
        conversion_event: 转化事件类型
    """
    service = ExperimentService(db)
    conversion_rates = service.calculate_conversion_rate(
        experiment_name=experiment_name,
        conversion_event=conversion_event
    )

    if 'error' in conversion_rates:
        raise HTTPException(status_code=404, detail=conversion_rates['error'])

    return {
        "status": "success",
        "data": {
            "experiment_name": experiment_name,
            "conversion_event": conversion_event,
            "variants": conversion_rates
        }
    }


@router.post("/calculate-significance")
def calculate_significance(request: CalculateSignificanceRequest):
    """
    计算统计显著性

    独立工具端点，可用于任何A/B测试数据的统计检验
    """
    service = ExperimentService(None)  # 不需要db
    result = service.calculate_statistical_significance(
        control_conversions=request.control_conversions,
        control_total=request.control_total,
        treatment_conversions=request.treatment_conversions,
        treatment_total=request.treatment_total
    )

    return {
        "status": "success",
        "data": result
    }


@router.get("/{experiment_name}/analysis")
def get_experiment_analysis(
    experiment_name: str,
    conversion_event: str,
    db: Session = Depends(get_db)
):
    """
    获取完整的实验分析

    包括统计数据、转化率、显著性检验
    """
    service = ExperimentService(db)

    # 获取基础统计
    stats = service.get_experiment_stats(experiment_name)

    if 'error' in stats:
        raise HTTPException(status_code=404, detail=stats['error'])

    # 获取转化率
    conversion_rates = service.calculate_conversion_rate(
        experiment_name=experiment_name,
        conversion_event=conversion_event
    )

    # 计算显著性 (假设control vs treatment)
    significance = None
    if 'control' in conversion_rates and 'treatment' in conversion_rates:
        control = conversion_rates['control']
        treatment = conversion_rates['treatment']

        significance = service.calculate_statistical_significance(
            control_conversions=control['converted_users'],
            control_total=control['total_users'],
            treatment_conversions=treatment['converted_users'],
            treatment_total=treatment['total_users']
        )

    return {
        "status": "success",
        "data": {
            "experiment_name": experiment_name,
            "stats": stats,
            "conversion_rates": conversion_rates,
            "significance": significance
        }
    }
