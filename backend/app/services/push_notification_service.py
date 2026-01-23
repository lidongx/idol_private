"""
Push Notification Service
Story 9.3: 推送通知集成（Firebase Cloud Messaging）

Handles sending push notifications via Firebase Cloud Messaging (FCM).
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime

# TODO: Install firebase-admin package
# pip install firebase-admin
# from firebase_admin import messaging, credentials
# import firebase_admin


class PushNotificationService:
    """
    Push Notification Service using Firebase Cloud Messaging

    Handles sending push notifications to user devices.
    """

    def __init__(self, db: Session):
        self.db = db
        self._initialize_fcm()

    def _initialize_fcm(self):
        """
        Initialize Firebase Cloud Messaging

        TODO: In production, initialize with service account JSON:
        ```
        cred = credentials.Certificate('path/to/serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
        ```
        """
        # For MVP: FCM initialization placeholder
        print("[PushNotification] FCM service initialized (placeholder)")

    def send_notification(
        self,
        fcm_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> bool:
        """
        Send push notification to a single device

        Args:
            fcm_token: Device FCM token
            title: Notification title
            body: Notification body
            data: Additional data payload (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # TODO: Implement actual FCM sending
            # message = messaging.Message(
            #     notification=messaging.Notification(
            #         title=title,
            #         body=body,
            #     ),
            #     data=data or {},
            #     token=fcm_token,
            # )
            # response = messaging.send(message)

            # For MVP: Log notification instead of sending
            print(f"[PushNotification] Sending to {fcm_token[:20]}...")
            print(f"  Title: {title}")
            print(f"  Body: {body}")
            print(f"  Data: {data}")

            return True

        except Exception as e:
            print(f"[PushNotification] Error sending notification: {e}")
            return False

    def send_notification_to_user(
        self,
        user_id: int,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> Dict[str, int]:
        """
        Send push notification to all user's devices

        Args:
            user_id: User ID
            title: Notification title
            body: Notification body
            data: Additional data payload (optional)

        Returns:
            dict: {'sent': count, 'failed': count}
        """
        from app.models.user_device import UserDevice

        # Get all user's devices with FCM tokens
        devices = self.db.query(UserDevice).filter(
            UserDevice.user_id == user_id,
            UserDevice.fcm_token.isnot(None),
            UserDevice.fcm_token != ''
        ).all()

        sent_count = 0
        failed_count = 0

        for device in devices:
            success = self.send_notification(
                fcm_token=device.fcm_token,
                title=title,
                body=body,
                data=data
            )

            if success:
                sent_count += 1
            else:
                failed_count += 1

        print(f"[PushNotification] Sent to user {user_id}: {sent_count} sent, {failed_count} failed")

        return {
            'sent': sent_count,
            'failed': failed_count
        }

    def send_multicast_notification(
        self,
        fcm_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> Dict[str, int]:
        """
        Send push notification to multiple devices

        Args:
            fcm_tokens: List of FCM tokens
            title: Notification title
            body: Notification body
            data: Additional data payload (optional)

        Returns:
            dict: {'sent': count, 'failed': count}
        """
        if not fcm_tokens:
            return {'sent': 0, 'failed': 0}

        # TODO: Implement batch sending with FCM
        # multicast_message = messaging.MulticastMessage(
        #     notification=messaging.Notification(
        #         title=title,
        #         body=body,
        #     ),
        #     data=data or {},
        #     tokens=fcm_tokens,
        # )
        # response = messaging.send_multicast(multicast_message)

        # For MVP: Send individually
        sent_count = 0
        failed_count = 0

        for token in fcm_tokens:
            success = self.send_notification(token, title, body, data)
            if success:
                sent_count += 1
            else:
                failed_count += 1

        return {
            'sent': sent_count,
            'failed': failed_count
        }

    def register_device_token(
        self,
        user_id: int,
        device_id: str,
        fcm_token: str
    ) -> bool:
        """
        Register or update FCM token for a device

        Args:
            user_id: User ID
            device_id: Device identifier
            fcm_token: FCM device token

        Returns:
            bool: True if registered successfully
        """
        from app.models.user_device import UserDevice

        try:
            # Find existing device
            device = self.db.query(UserDevice).filter(
                UserDevice.user_id == user_id,
                UserDevice.device_id == device_id
            ).first()

            if device:
                # Update FCM token
                device.fcm_token = fcm_token
                device.updated_at = datetime.utcnow()
            else:
                # Create new device record
                device = UserDevice(
                    user_id=user_id,
                    device_id=device_id,
                    fcm_token=fcm_token,
                    device_name="Unknown Device",  # TODO: Get device name from client
                    last_login_at=datetime.utcnow()
                )
                self.db.add(device)

            self.db.commit()
            print(f"[PushNotification] Registered FCM token for user {user_id}, device {device_id}")

            return True

        except Exception as e:
            print(f"[PushNotification] Error registering device token: {e}")
            self.db.rollback()
            return False

    def unregister_device_token(
        self,
        user_id: int,
        device_id: str
    ) -> bool:
        """
        Unregister FCM token for a device

        Args:
            user_id: User ID
            device_id: Device identifier

        Returns:
            bool: True if unregistered successfully
        """
        from app.models.user_device import UserDevice

        try:
            device = self.db.query(UserDevice).filter(
                UserDevice.user_id == user_id,
                UserDevice.device_id == device_id
            ).first()

            if device:
                device.fcm_token = None
                device.updated_at = datetime.utcnow()
                self.db.commit()
                print(f"[PushNotification] Unregistered FCM token for user {user_id}, device {device_id}")

            return True

        except Exception as e:
            print(f"[PushNotification] Error unregistering device token: {e}")
            self.db.rollback()
            return False


# ==================== Notification Templates ====================

class NotificationTemplates:
    """
    Pre-defined notification templates for different scenarios
    """

    @staticmethod
    def idol_message(idol_name: str, message_preview: str) -> Dict[str, str]:
        """
        Notification for new idol message

        Args:
            idol_name: Name of the idol
            message_preview: Preview of the message (first 50 chars)

        Returns:
            dict: {'title': str, 'body': str}
        """
        return {
            'title': f'{idol_name}给你发来消息',
            'body': message_preview[:50] + ('...' if len(message_preview) > 50 else ''),
            'data': {
                'type': 'new_message',
                'idol_name': idol_name
            }
        }

    @staticmethod
    def intimacy_level_up(idol_name: str, new_level: int) -> Dict[str, str]:
        """
        Notification for intimacy level up

        Args:
            idol_name: Name of the idol
            new_level: New intimacy level

        Returns:
            dict: {'title': str, 'body': str}
        """
        return {
            'title': '亲密度提升！',
            'body': f'你与{idol_name}的亲密度达到了等级{new_level}！',
            'data': {
                'type': 'intimacy_level_up',
                'idol_name': idol_name,
                'level': str(new_level)
            }
        }

    @staticmethod
    def subscription_expiring(days_remaining: int) -> Dict[str, str]:
        """
        Notification for subscription expiring soon

        Args:
            days_remaining: Days until subscription expires

        Returns:
            dict: {'title': str, 'body': str}
        """
        return {
            'title': '订阅即将到期',
            'body': f'你的订阅将在{days_remaining}天后到期，请及时续费',
            'data': {
                'type': 'subscription_expiring',
                'days_remaining': str(days_remaining)
            }
        }

    @staticmethod
    def subscription_expired() -> Dict[str, str]:
        """
        Notification for subscription expired

        Returns:
            dict: {'title': str, 'body': str}
        """
        return {
            'title': '订阅已到期',
            'body': '你的订阅已到期，续费后可继续享受无限对话',
            'data': {
                'type': 'subscription_expired'
            }
        }

    @staticmethod
    def milestone_reminder(milestone_name: str, date: str) -> Dict[str, str]:
        """
        Notification for milestone reminder

        Args:
            milestone_name: Name of the milestone
            date: Milestone date

        Returns:
            dict: {'title': str, 'body': str}
        """
        return {
            'title': '纪念日提醒',
            'body': f'今天是"{milestone_name}"({date})，不要忘记庆祝哦',
            'data': {
                'type': 'milestone_reminder',
                'milestone_name': milestone_name,
                'date': date
            }
        }

    @staticmethod
    def achievement_unlocked(achievement_name: str) -> Dict[str, str]:
        """
        Notification for achievement unlocked

        Args:
            achievement_name: Name of the achievement

        Returns:
            dict: {'title': str, 'body': str}
        """
        return {
            'title': '成就解锁！',
            'body': f'恭喜你解锁成就：{achievement_name}',
            'data': {
                'type': 'achievement_unlocked',
                'achievement_name': achievement_name
            }
        }
