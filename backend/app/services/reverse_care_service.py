"""
ReverseCareService - Service for managing idol's proactive care actions
Story 5.4: 反向陪伴机制
"""
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.models.reverse_care import ReverseCare
from app.models.user import User
from app.models.idol import Idol
from app.models.message import Message


class ReverseCareService:
    """Service for managing reverse care (idol reaching out to users)"""

    def __init__(self, db: Session):
        self.db = db
        self._load_templates()

    def _load_templates(self):
        """Load care message templates from JSON configuration"""
        config_path = Path(__file__).parent.parent / "config" / "care_message_templates.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)

    def _has_recent_care_log(
        self,
        user_id: int,
        care_type: str,
        cooldown_days: int
    ) -> bool:
        """
        Check if user has received this type of care message recently

        Args:
            user_id: User ID
            care_type: Type of care message
            cooldown_days: Number of days for cooldown period

        Returns:
            True if recent care log exists, False otherwise
        """
        cutoff_time = datetime.utcnow() - timedelta(days=cooldown_days)

        recent_log = self.db.query(ReverseCare).filter(
            ReverseCare.user_id == user_id,
            ReverseCare.care_type == care_type,
            ReverseCare.triggered_at >= cutoff_time
        ).first()

        return recent_log is not None

    def check_inactive_users(self) -> List[Dict]:
        """
        Check for users who haven't been active for 3+ days

        Returns:
            List of users who need care with their details
        """
        settings = self.templates['care_settings']['inactive_3days']
        min_days = settings['min_days_inactive']
        cooldown_days = settings['cooldown_days']

        # Find users inactive for min_days
        cutoff_time = datetime.utcnow() - timedelta(days=min_days)

        inactive_users = self.db.query(User).filter(
            User.last_active_at < cutoff_time
        ).all()

        users_needing_care = []
        for user in inactive_users:
            # Check if already sent care message recently
            if not self._has_recent_care_log(user.id, ReverseCare.INACTIVE_3DAYS, cooldown_days):
                users_needing_care.append({
                    'user_id': user.id,
                    'user_phone': user.phone,
                    'last_active_at': user.last_active_at,
                    'days_inactive': (datetime.utcnow() - user.last_active_at).days
                })

        return users_needing_care

    def send_inactive_care_message(self, user_id: int, idol_id: int) -> Dict:
        """
        Send care message to inactive user

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            {
                'success': bool,
                'message': str,
                'care_log_id': int,
                'send_push': bool
            }
        """
        # Select random care message
        messages = self.templates['inactive_3days']['messages']
        message_content = random.choice(messages)

        # Create care log
        care_log = ReverseCare(
            user_id=user_id,
            idol_id=idol_id,
            care_type=ReverseCare.INACTIVE_3DAYS,
            message_content=message_content,
            triggered_at=datetime.utcnow()
        )
        self.db.add(care_log)
        self.db.commit()
        self.db.refresh(care_log)

        # Note: Actual message sending would happen in conversation service
        # This just creates the care log for tracking

        return {
            'success': True,
            'message': message_content,
            'care_log_id': care_log.id,
            'send_push': self.templates['care_settings']['inactive_3days']['send_push_notification'],
            'push_title': self.templates['inactive_3days']['push_notification_title'],
            'push_body': self.templates['inactive_3days']['push_notification_body']
        }

    def check_late_night_activity(self, user_id: int) -> bool:
        """
        Check if current time is late night (1:00-3:00 AM)
        and if user hasn't received late night care today

        Args:
            user_id: User ID

        Returns:
            True if care message should be sent, False otherwise
        """
        current_hour = datetime.now().hour
        time_window = self.templates['late_night']['time_window']

        # Check if current time is in late night window
        if not (time_window['start_hour'] <= current_hour < time_window['end_hour']):
            return False

        # Check if already sent care message today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        recent_log = self.db.query(ReverseCare).filter(
            ReverseCare.user_id == user_id,
            ReverseCare.care_type == ReverseCare.LATE_NIGHT,
            ReverseCare.triggered_at >= today_start
        ).first()

        return recent_log is None

    def send_late_night_care_message(self, user_id: int, idol_id: int) -> Dict:
        """
        Send late night care message to user

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            {
                'success': bool,
                'message': str,
                'care_log_id': int
            }
        """
        # Select random late night care message
        messages = self.templates['late_night']['messages']
        message_content = random.choice(messages)

        # Create care log
        care_log = ReverseCare(
            user_id=user_id,
            idol_id=idol_id,
            care_type=ReverseCare.LATE_NIGHT,
            message_content=message_content,
            triggered_at=datetime.utcnow()
        )
        self.db.add(care_log)
        self.db.commit()
        self.db.refresh(care_log)

        return {
            'success': True,
            'message': message_content,
            'care_log_id': care_log.id
        }

    def check_low_mood_users(self) -> List[Dict]:
        """
        Check for users with low mood for 3+ consecutive days

        Returns:
            List of users who need emotional care
        """
        settings = self.templates['low_mood_3days']['trigger_condition']
        min_days = settings['consecutive_days']
        mood_types = settings['mood_types']
        cooldown_days = self.templates['care_settings']['low_mood_3days']['cooldown_days']

        # Get messages from last 3 days for all users
        three_days_ago = datetime.utcnow() - timedelta(days=3)

        # Query users with consecutive low mood messages
        # This is a simplified approach - in production, you'd want more sophisticated analysis
        low_mood_users = []

        # Get all users
        users = self.db.query(User).all()

        for user in users:
            # Check if already sent care message recently
            if self._has_recent_care_log(user.id, ReverseCare.LOW_MOOD_3DAYS, cooldown_days):
                continue

            # Get user's messages from last 3 days
            recent_messages = self.db.query(Message).filter(
                Message.user_id == user.id,
                Message.sender_type == 'user',
                Message.created_at >= three_days_ago
            ).order_by(Message.created_at.desc()).limit(10).all()

            if len(recent_messages) < 3:
                continue

            # Check if majority of messages have low mood
            low_mood_count = sum(
                1 for msg in recent_messages
                if msg.emotion and msg.emotion.lower() in mood_types
            )

            # If 60%+ messages show low mood, trigger care
            if low_mood_count >= len(recent_messages) * 0.6:
                low_mood_users.append({
                    'user_id': user.id,
                    'user_phone': user.phone,
                    'low_mood_ratio': low_mood_count / len(recent_messages),
                    'recent_messages_count': len(recent_messages)
                })

        return low_mood_users

    def send_low_mood_care_message(self, user_id: int, idol_id: int) -> Dict:
        """
        Send emotional care message to user with low mood

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            {
                'success': bool,
                'message': str,
                'care_log_id': int
            }
        """
        # Select random low mood care message
        messages = self.templates['low_mood_3days']['messages']
        message_content = random.choice(messages)

        # Create care log
        care_log = ReverseCare(
            user_id=user_id,
            idol_id=idol_id,
            care_type=ReverseCare.LOW_MOOD_3DAYS,
            message_content=message_content,
            triggered_at=datetime.utcnow()
        )
        self.db.add(care_log)
        self.db.commit()
        self.db.refresh(care_log)

        return {
            'success': True,
            'message': message_content,
            'care_log_id': care_log.id
        }

    def mark_care_as_responded(self, care_log_id: int) -> bool:
        """
        Mark a care message as responded by user

        Args:
            care_log_id: Care log ID

        Returns:
            True if successful, False otherwise
        """
        care_log = self.db.query(ReverseCare).filter(
            ReverseCare.id == care_log_id
        ).first()

        if not care_log:
            return False

        care_log.mark_as_responded()
        self.db.commit()

        return True

    def get_user_care_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """
        Get care history for a user

        Args:
            user_id: User ID
            limit: Number of records to retrieve

        Returns:
            List of care log records
        """
        care_logs = self.db.query(ReverseCare).filter(
            ReverseCare.user_id == user_id
        ).order_by(ReverseCare.triggered_at.desc()).limit(limit).all()

        return [
            {
                'id': log.id,
                'care_type': log.care_type,
                'care_type_display': log.care_display_name,
                'message': log.message_content,
                'triggered_at': log.triggered_at.isoformat(),
                'was_responded': log.was_responded,
                'responded_at': log.responded_at.isoformat() if log.responded_at else None
            }
            for log in care_logs
        ]

    def get_care_stats(self, user_id: int) -> Dict:
        """
        Get care statistics for a user

        Args:
            user_id: User ID

        Returns:
            {
                'total_care_messages': int,
                'by_type': {
                    'inactive_3days': int,
                    'late_night': int,
                    'low_mood_3days': int
                },
                'response_rate': float,
                'last_care_at': str
            }
        """
        # Get all care logs for user
        care_logs = self.db.query(ReverseCare).filter(
            ReverseCare.user_id == user_id
        ).all()

        # Count by type
        by_type = {
            ReverseCare.INACTIVE_3DAYS: 0,
            ReverseCare.LATE_NIGHT: 0,
            ReverseCare.LOW_MOOD_3DAYS: 0
        }

        responded_count = 0
        for log in care_logs:
            if log.care_type in by_type:
                by_type[log.care_type] += 1
            if log.was_responded:
                responded_count += 1

        # Calculate response rate
        response_rate = responded_count / len(care_logs) if care_logs else 0.0

        # Get last care time
        last_log = self.db.query(ReverseCare).filter(
            ReverseCare.user_id == user_id
        ).order_by(ReverseCare.triggered_at.desc()).first()

        return {
            'total_care_messages': len(care_logs),
            'by_type': by_type,
            'response_rate': round(response_rate, 2),
            'last_care_at': last_log.triggered_at.isoformat() if last_log else None
        }

    def process_all_care_checks(self) -> Dict:
        """
        Process all care checks (inactive users and low mood users)

        This is called by the background task

        Returns:
            Summary of care actions taken
        """
        results = {
            'inactive_users_checked': 0,
            'inactive_care_sent': 0,
            'low_mood_users_checked': 0,
            'low_mood_care_sent': 0,
            'errors': []
        }

        try:
            # Check inactive users
            inactive_users = self.check_inactive_users()
            results['inactive_users_checked'] = len(inactive_users)

            for user_info in inactive_users:
                try:
                    # Default idol_id = 1 (林雪晴)
                    self.send_inactive_care_message(user_info['user_id'], idol_id=1)
                    results['inactive_care_sent'] += 1
                except Exception as e:
                    results['errors'].append(f"Failed to send inactive care to user {user_info['user_id']}: {str(e)}")

        except Exception as e:
            results['errors'].append(f"Failed to check inactive users: {str(e)}")

        try:
            # Check low mood users
            low_mood_users = self.check_low_mood_users()
            results['low_mood_users_checked'] = len(low_mood_users)

            for user_info in low_mood_users:
                try:
                    # Default idol_id = 1 (林雪晴)
                    self.send_low_mood_care_message(user_info['user_id'], idol_id=1)
                    results['low_mood_care_sent'] += 1
                except Exception as e:
                    results['errors'].append(f"Failed to send low mood care to user {user_info['user_id']}: {str(e)}")

        except Exception as e:
            results['errors'].append(f"Failed to check low mood users: {str(e)}")

        return results
