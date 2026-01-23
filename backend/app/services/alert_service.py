"""
Alert Service
Story 10.2: 监控告警增强 (Monitoring Alert Enhancement)

Sends alerts to DingTalk (钉钉) and Feishu (飞书) via webhooks
"""

import requests
import hashlib
import hmac
import base64
import time
from typing import Optional, Dict
from datetime import datetime

from app.config import settings


class AlertSeverity:
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertService:
    """Service for sending alerts to various platforms"""

    def __init__(self):
        self.dingtalk_webhook = getattr(settings, 'DINGTALK_WEBHOOK_URL', None)
        self.dingtalk_secret = getattr(settings, 'DINGTALK_WEBHOOK_SECRET', None)
        self.feishu_webhook = getattr(settings, 'FEISHU_WEBHOOK_URL', None)

    # ==================== DingTalk ====================

    def _generate_dingtalk_sign(self, timestamp: int, secret: str) -> str:
        """
        Generate DingTalk signature

        Args:
            timestamp: Unix timestamp in milliseconds
            secret: Webhook secret

        Returns:
            Base64-encoded signature
        """
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256,
        ).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    def send_dingtalk_alert(
        self,
        title: str,
        message: str,
        severity: str = AlertSeverity.INFO,
        at_all: bool = False,
        at_mobiles: Optional[list] = None,
    ) -> bool:
        """
        Send alert to DingTalk

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (info/warning/error/critical)
            at_all: Whether to @ everyone
            at_mobiles: List of phone numbers to @

        Returns:
            True if successful, False otherwise
        """
        if not self.dingtalk_webhook:
            print("[AlertService] DingTalk webhook not configured")
            return False

        try:
            # Generate signature if secret is configured
            params = {}
            if self.dingtalk_secret:
                timestamp = int(time.time() * 1000)
                sign = self._generate_dingtalk_sign(timestamp, self.dingtalk_secret)
                params = {
                    'timestamp': timestamp,
                    'sign': sign,
                }

            # Severity emoji
            severity_emoji = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️",
                AlertSeverity.ERROR: "❌",
                AlertSeverity.CRITICAL: "🚨",
            }.get(severity, "📢")

            # Construct message
            text_content = f"{severity_emoji} **{title}**\n\n{message}\n\n时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"

            # Prepare payload
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": text_content,
                },
                "at": {
                    "atMobiles": at_mobiles or [],
                    "isAtAll": at_all,
                },
            }

            # Send request
            response = requests.post(
                self.dingtalk_webhook,
                json=payload,
                params=params,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print(f"[AlertService] DingTalk alert sent: {title}")
                    return True
                else:
                    print(f"[AlertService] DingTalk error: {result.get('errmsg')}")
                    return False
            else:
                print(f"[AlertService] DingTalk HTTP error: {response.status_code}")
                return False

        except Exception as e:
            print(f"[AlertService] Error sending DingTalk alert: {e}")
            return False

    # ==================== Feishu ====================

    def send_feishu_alert(
        self,
        title: str,
        message: str,
        severity: str = AlertSeverity.INFO,
    ) -> bool:
        """
        Send alert to Feishu (飞书)

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (info/warning/error/critical)

        Returns:
            True if successful, False otherwise
        """
        if not self.feishu_webhook:
            print("[AlertService] Feishu webhook not configured")
            return False

        try:
            # Severity color
            severity_color = {
                AlertSeverity.INFO: "blue",
                AlertSeverity.WARNING: "orange",
                AlertSeverity.ERROR: "red",
                AlertSeverity.CRITICAL: "red",
            }.get(severity, "blue")

            # Prepare payload (rich text format)
            payload = {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True,
                    },
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": title,
                        },
                        "template": severity_color,
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": message,
                            },
                        },
                        {
                            "tag": "div",
                            "text": {
                                "tag": "plain_text",
                                "content": f"时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
                            },
                        },
                    ],
                },
            }

            # Send request
            response = requests.post(
                self.feishu_webhook,
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('StatusCode') == 0 or result.get('code') == 0:
                    print(f"[AlertService] Feishu alert sent: {title}")
                    return True
                else:
                    print(f"[AlertService] Feishu error: {result.get('msg')}")
                    return False
            else:
                print(f"[AlertService] Feishu HTTP error: {response.status_code}")
                return False

        except Exception as e:
            print(f"[AlertService] Error sending Feishu alert: {e}")
            return False

    # ==================== Unified Alert Method ====================

    def send_alert(
        self,
        title: str,
        message: str,
        severity: str = AlertSeverity.INFO,
        platforms: Optional[list] = None,
        **kwargs,
    ) -> Dict[str, bool]:
        """
        Send alert to multiple platforms

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            platforms: List of platforms ('dingtalk', 'feishu'). If None, send to all configured.
            **kwargs: Platform-specific arguments

        Returns:
            Dict mapping platform name to success status
        """
        if platforms is None:
            platforms = []
            if self.dingtalk_webhook:
                platforms.append('dingtalk')
            if self.feishu_webhook:
                platforms.append('feishu')

        results = {}

        for platform in platforms:
            if platform == 'dingtalk':
                results['dingtalk'] = self.send_dingtalk_alert(
                    title, message, severity,
                    at_all=kwargs.get('at_all', False),
                    at_mobiles=kwargs.get('at_mobiles'),
                )
            elif platform == 'feishu':
                results['feishu'] = self.send_feishu_alert(
                    title, message, severity
                )

        return results


# ==================== Alert Templates ====================

class AlertTemplates:
    """Pre-defined alert templates"""

    @staticmethod
    def system_error(error_message: str, component: str) -> tuple:
        """System error alert"""
        title = f"🚨 系统错误 - {component}"
        message = f"**组件**: {component}\n\n**错误信息**:\n```\n{error_message}\n```\n\n请立即检查系统日志。"
        return title, message, AlertSeverity.CRITICAL

    @staticmethod
    def high_error_rate(error_rate: float, threshold: float) -> tuple:
        """High error rate alert"""
        title = "⚠️ 错误率告警"
        message = (
            f"**当前错误率**: {error_rate:.2f}%\n"
            f"**告警阈值**: {threshold:.2f}%\n\n"
            f"错误率超过阈值，请检查系统状态。"
        )
        return title, message, AlertSeverity.WARNING

    @staticmethod
    def low_retention(retention_rate: float, metric_name: str, threshold: float) -> tuple:
        """Low retention alert"""
        title = "⚠️ 留存率告警"
        message = (
            f"**指标**: {metric_name}\n"
            f"**当前留存率**: {retention_rate:.1f}%\n"
            f"**告警阈值**: {threshold:.1f}%\n\n"
            f"留存率低于目标，请检查用户体验和产品功能。"
        )
        return title, message, AlertSeverity.WARNING

    @staticmethod
    def api_slow_response(avg_duration: float, endpoint: str, threshold: float) -> tuple:
        """API slow response alert"""
        title = "⚠️ API响应缓慢"
        message = (
            f"**端点**: {endpoint}\n"
            f"**平均响应时间**: {avg_duration:.2f}s\n"
            f"**告警阈值**: {threshold:.2f}s\n\n"
            f"API响应时间过长，可能影响用户体验。"
        )
        return title, message, AlertSeverity.WARNING

    @staticmethod
    def database_connection_error(error_message: str) -> tuple:
        """Database connection error alert"""
        title = "🚨 数据库连接错误"
        message = (
            f"**错误信息**:\n```\n{error_message}\n```\n\n"
            f"数据库连接失败，服务可能中断。请立即检查数据库状态。"
        )
        return title, message, AlertSeverity.CRITICAL

    @staticmethod
    def high_ai_cost(cost: float, threshold: float, period: str = "daily") -> tuple:
        """High AI cost alert"""
        title = "💰 AI成本告警"
        message = (
            f"**周期**: {period}\n"
            f"**当前成本**: ¥{cost:.2f}\n"
            f"**预算阈值**: ¥{threshold:.2f}\n\n"
            f"AI调用成本超过预算，请检查使用情况。"
        )
        return title, message, AlertSeverity.WARNING

    @staticmethod
    def subscription_expiring_soon(count: int, days: int) -> tuple:
        """Subscriptions expiring soon alert"""
        title = "ℹ️ 订阅即将到期"
        message = (
            f"**即将到期订阅数**: {count}\n"
            f"**到期时间**: {days}天内\n\n"
            f"建议发送续费提醒通知。"
        )
        return title, message, AlertSeverity.INFO

    @staticmethod
    def daily_summary(
        dau: int,
        new_users: int,
        messages: int,
        errors: int,
        revenue: float,
    ) -> tuple:
        """Daily summary alert"""
        title = "📊 每日运营数据摘要"
        message = (
            f"**日活跃用户 (DAU)**: {dau}\n"
            f"**新增用户**: {new_users}\n"
            f"**消息总数**: {messages}\n"
            f"**错误次数**: {errors}\n"
            f"**当日收入**: ¥{revenue:.2f}\n\n"
            f"详细数据请查看运营仪表盘。"
        )
        return title, message, AlertSeverity.INFO

    @staticmethod
    def budget_exceeded(
        budget_type: str,
        period: str,
        usage_pct: float,
        current_cost: float,
        limit: float,
        provider: str = None
    ) -> tuple:
        """Budget exceeded alert (Story 10.3)"""
        severity = AlertSeverity.CRITICAL if usage_pct >= 100 else AlertSeverity.WARNING

        title_emoji = "🚨" if severity == AlertSeverity.CRITICAL else "⚠️"
        title = f"{title_emoji} AI成本预算{'超限' if usage_pct >= 100 else '告警'}"

        target_desc = f"Provider: {provider}" if provider else "全局"
        period_desc = "每日" if period == "daily" else "每月"

        message = (
            f"**预算类型**: {target_desc}\n"
            f"**周期**: {period_desc}\n"
            f"**当前成本**: ${current_cost:.2f}\n"
            f"**预算限额**: ${limit:.2f}\n"
            f"**使用率**: {usage_pct:.1f}%\n\n"
        )

        if usage_pct >= 100:
            message += "⛔ **预算已超限**，请立即采取措施：\n"
            message += "1. 暂停非必要AI调用\n"
            message += "2. 检查异常调用模式\n"
            message += "3. 考虑增加预算或优化成本\n"
        else:
            message += "⚠️ **预算使用率较高**，建议：\n"
            message += "1. 监控成本趋势\n"
            message += "2. 优化AI调用频率\n"
            message += "3. 考虑使用更经济的模型\n"

        return title, message, severity

    @staticmethod
    def cost_anomaly(
        current_cost: float,
        avg_cost: float,
        increase_pct: float,
        provider: str = None
    ) -> tuple:
        """Cost anomaly detected alert (Story 10.3)"""
        title = "📈 AI成本异常增长"

        target_desc = f"Provider: {provider}" if provider else "全局"

        message = (
            f"**检测范围**: {target_desc}\n"
            f"**当前成本**: ${current_cost:.2f}\n"
            f"**平均成本**: ${avg_cost:.2f}\n"
            f"**增长幅度**: +{increase_pct:.1f}%\n\n"
            f"检测到成本异常增长，可能原因：\n"
            f"1. 用户活跃度突然增加\n"
            f"2. AI模型配置变更\n"
            f"3. 异常调用模式\n\n"
            f"建议立即检查成本明细。"
        )
        return title, message, AlertSeverity.WARNING
