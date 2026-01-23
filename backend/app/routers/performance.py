"""
Performance Monitoring API
Story 9.1: 性能优化（首屏加载<2秒）

Endpoints for monitoring application performance metrics.
"""
from fastapi import APIRouter, Depends
from typing import Dict, List
from app.middleware.performance_middleware import get_performance_middleware


router = APIRouter()


@router.get("/metrics")
def get_performance_metrics() -> Dict:
    """
    Get performance metrics for all API endpoints

    Returns:
        dict: Performance statistics including:
        - Request count
        - Average/median/min/max response times
        - P95/P99 percentiles
    """
    middleware = get_performance_middleware()

    if not middleware:
        return {
            "error": "Performance middleware not initialized",
            "stats": {}
        }

    stats = middleware.get_performance_stats()

    # Calculate summary statistics
    total_requests = sum(s['count'] for s in stats.values())
    avg_response_time = sum(s['avg_ms'] * s['count'] for s in stats.values()) / total_requests if total_requests > 0 else 0

    return {
        "summary": {
            "total_endpoints": len(stats),
            "total_requests": total_requests,
            "avg_response_time_ms": round(avg_response_time, 2),
        },
        "endpoints": stats
    }


@router.get("/slow-requests")
def get_slow_requests(limit: int = 20) -> List[Dict]:
    """
    Get recent slow requests

    Args:
        limit: Number of slow requests to return (default: 20)

    Returns:
        list: Recent slow requests with details
    """
    middleware = get_performance_middleware()

    if not middleware:
        return []

    return middleware.get_slow_requests(limit=limit)


@router.get("/summary")
def get_performance_summary() -> Dict:
    """
    Get performance summary

    Returns:
        dict: Summary of performance metrics
    """
    middleware = get_performance_middleware()

    if not middleware:
        return {"error": "Performance middleware not initialized"}

    stats = middleware.get_performance_stats()

    if not stats:
        return {
            "message": "No requests recorded yet",
            "endpoints_monitored": 0
        }

    # Find slowest endpoints
    slowest_endpoints = sorted(
        [(endpoint, metrics['avg_ms']) for endpoint, metrics in stats.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]

    # Find fastest endpoints
    fastest_endpoints = sorted(
        [(endpoint, metrics['avg_ms']) for endpoint, metrics in stats.items()],
        key=lambda x: x[1]
    )[:10]

    # Count slow requests
    slow_threshold_ms = 200
    slow_endpoints = [
        endpoint for endpoint, metrics in stats.items()
        if metrics['avg_ms'] > slow_threshold_ms
    ]

    return {
        "endpoints_monitored": len(stats),
        "total_requests": sum(s['count'] for s in stats.values()),
        "slow_endpoints_count": len(slow_endpoints),
        "slow_threshold_ms": slow_threshold_ms,
        "slowest_endpoints": [
            {"endpoint": ep, "avg_ms": ms}
            for ep, ms in slowest_endpoints
        ],
        "fastest_endpoints": [
            {"endpoint": ep, "avg_ms": ms}
            for ep, ms in fastest_endpoints
        ],
    }


@router.post("/clear")
def clear_performance_metrics() -> Dict:
    """
    Clear all performance metrics

    Returns:
        dict: Confirmation message
    """
    middleware = get_performance_middleware()

    if not middleware:
        return {"error": "Performance middleware not initialized"}

    middleware.clear_metrics()

    return {
        "message": "Performance metrics cleared successfully"
    }


@router.get("/health-check")
def performance_health_check() -> Dict:
    """
    Check if performance meets targets

    Returns:
        dict: Health status and recommendations
    """
    middleware = get_performance_middleware()

    if not middleware:
        return {"error": "Performance middleware not initialized"}

    stats = middleware.get_performance_stats()

    # Performance targets
    TARGET_AVG_RESPONSE_MS = 100
    TARGET_P95_RESPONSE_MS = 200

    issues = []
    warnings = []

    for endpoint, metrics in stats.items():
        # Check average response time
        if metrics['avg_ms'] > TARGET_AVG_RESPONSE_MS:
            issues.append({
                "endpoint": endpoint,
                "issue": "High average response time",
                "current_ms": metrics['avg_ms'],
                "target_ms": TARGET_AVG_RESPONSE_MS
            })

        # Check P95 response time
        if metrics['p95_ms'] > TARGET_P95_RESPONSE_MS:
            warnings.append({
                "endpoint": endpoint,
                "warning": "High P95 response time",
                "current_ms": metrics['p95_ms'],
                "target_ms": TARGET_P95_RESPONSE_MS
            })

    health_status = "healthy" if len(issues) == 0 else "degraded"

    return {
        "status": health_status,
        "targets": {
            "avg_response_ms": TARGET_AVG_RESPONSE_MS,
            "p95_response_ms": TARGET_P95_RESPONSE_MS
        },
        "issues": issues,
        "warnings": warnings,
        "recommendations": _get_recommendations(issues, warnings)
    }


def _get_recommendations(issues: List[Dict], warnings: List[Dict]) -> List[str]:
    """
    Generate performance improvement recommendations
    """
    recommendations = []

    if len(issues) > 0:
        recommendations.append(
            "Add database indexes for slow queries (see migration 030)"
        )
        recommendations.append(
            "Enable Redis caching for frequently accessed endpoints"
        )
        recommendations.append(
            "Consider implementing pagination for list endpoints"
        )

    if len(warnings) > 0:
        recommendations.append(
            "Monitor P95 response times - some requests are significantly slower"
        )
        recommendations.append(
            "Check for N+1 query problems in ORM queries"
        )

    if not recommendations:
        recommendations.append("Performance is within target ranges ✅")

    return recommendations
