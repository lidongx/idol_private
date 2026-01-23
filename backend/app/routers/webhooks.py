"""
Webhook Endpoints
Story 10.2: 监控告警增强 (Monitoring Alert Enhancement)

Receives webhooks from Prometheus AlertManager and forwards to DingTalk/Feishu
"""

from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict
from datetime import datetime

from app.services.alert_service import AlertService, AlertSeverity
from app.config.alert_rules import ALERT_ROUTING, AT_ALL_ON_CRITICAL, CRITICAL_ALERT_MOBILES


router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("/alertmanager")
async def alertmanager_webhook(request: Request):
    """
    Receive alerts from Prometheus AlertManager

    AlertManager sends alerts in this format:
    {
      "receiver": "webhook",
      "status": "firing",
      "alerts": [
        {
          "status": "firing",
          "labels": {
            "alertname": "HighHttpErrorRate",
            "severity": "warning",
            "component": "api"
          },
          "annotations": {
            "summary": "High HTTP error rate detected",
            "description": "Error rate is 8.5% (threshold: 5%)"
          },
          "startsAt": "2026-01-20T10:00:00.000Z",
          "endsAt": "0001-01-01T00:00:00Z",
          "generatorURL": "http://prometheus:9090/graph?..."
        }
      ],
      "groupLabels": {"alertname": "HighHttpErrorRate"},
      "commonLabels": {...},
      "commonAnnotations": {...},
      "externalURL": "http://alertmanager:9093",
      "version": "4",
      "groupKey": "..."
    }
    """
    try:
        payload = await request.json()

        # Extract alerts
        alerts = payload.get('alerts', [])
        if not alerts:
            return {"status": "ok", "message": "No alerts to process"}

        alert_service = AlertService()
        results = []

        for alert in alerts:
            # Extract alert information
            status = alert.get('status', 'unknown')
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})

            alertname = labels.get('alertname', 'Unknown Alert')
            severity = labels.get('severity', 'info')
            component = labels.get('component', 'system')

            summary = annotations.get('summary', 'No summary')
            description = annotations.get('description', 'No description')

            # Skip resolved alerts (optional)
            if status == 'resolved':
                print(f"[Webhook] Alert resolved: {alertname}")
                continue

            # Format alert message
            title = f"{alertname} - {component.upper()}"
            message = f"**状态**: {status}\n\n**摘要**: {summary}\n\n**详情**: {description}"

            # Determine platforms to send to based on severity
            platforms = ALERT_ROUTING.get(severity, ['dingtalk'])

            # Send alert
            kwargs = {}
            if severity == AlertSeverity.CRITICAL and AT_ALL_ON_CRITICAL:
                kwargs['at_all'] = True
                kwargs['at_mobiles'] = CRITICAL_ALERT_MOBILES

            result = alert_service.send_alert(
                title=title,
                message=message,
                severity=severity,
                platforms=platforms,
                **kwargs,
            )

            results.append({
                'alertname': alertname,
                'status': status,
                'severity': severity,
                'result': result,
            })

            print(f"[Webhook] Processed alert: {alertname} ({severity}) - {result}")

        return {
            "status": "ok",
            "processed": len(results),
            "results": results,
        }

    except Exception as e:
        print(f"[Webhook] Error processing alertmanager webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-alert")
async def test_alert(
    title: str = "测试告警",
    message: str = "这是一条测试告警消息",
    severity: str = AlertSeverity.INFO,
    platforms: List[str] = None,
):
    """
    Test alert endpoint

    Send a test alert to configured platforms.

    **Parameters:**
    - title: Alert title
    - message: Alert message
    - severity: Alert severity (info/warning/error/critical)
    - platforms: List of platforms (dingtalk/feishu). If not provided, sends to all.

    **Example:**
    ```
    POST /api/v1/webhooks/test-alert?title=Test&message=Hello&severity=info
    ```
    """
    try:
        alert_service = AlertService()

        result = alert_service.send_alert(
            title=title,
            message=message,
            severity=severity,
            platforms=platforms,
        )

        return {
            "status": "ok",
            "title": title,
            "message": message,
            "severity": severity,
            "platforms": platforms or "all configured",
            "result": result,
        }

    except Exception as e:
        print(f"[Webhook] Error sending test alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))
