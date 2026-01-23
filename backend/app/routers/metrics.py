"""
Prometheus Metrics Endpoint
Story 10.2: 监控告警增强 (Monitoring Alert Enhancement)

Provides /metrics endpoint for Prometheus scraping
"""

from fastapi import APIRouter, Response
from app.core.metrics import get_metrics, get_content_type


router = APIRouter(tags=["monitoring"])


@router.get("/metrics")
def prometheus_metrics():
    """
    Prometheus metrics endpoint

    Returns metrics in Prometheus text format for scraping.

    This endpoint should be scraped by Prometheus at regular intervals
    (e.g., every 15-30 seconds).

    **No authentication required** - typically accessed from internal monitoring network.
    """
    metrics_data = get_metrics()
    return Response(content=metrics_data, media_type=get_content_type())
