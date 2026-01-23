"""
SpecialEventService - Service for managing special events and easter eggs
Story 5.5: 特殊事件与互动彩蛋
"""
import json
import random
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.special_event import SpecialEvent, UserSpecialEvent
from app.models.user import User
from app.models.message import Message
from app.models.daily_ritual import DailyRitual


class SpecialEventService:
    """Service for managing special events"""

    def __init__(self, db: Session):
        self.db = db
        self._load_templates()

    def _load_templates(self):
        """Load event templates from JSON configuration"""
        config_path = Path(__file__).parent.parent / "config" / "event_templates.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)

    def _has_triggered_recently(
        self,
        user_id: int,
        event_name: str,
        hours: int
    ) -> bool:
        """
        Check if event was triggered recently for this user

        Args:
            user_id: User ID
            event_name: Event name
            hours: Hours to check back

        Returns:
            True if event was triggered within the time window
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Find event by name
        event = self.db.query(SpecialEvent).filter(
            SpecialEvent.event_name == event_name
        ).first()

        if not event:
            return False

        recent_trigger = self.db.query(UserSpecialEvent).filter(
            UserSpecialEvent.user_id == user_id,
            UserSpecialEvent.event_id == event.id,
            UserSpecialEvent.triggered_at >= cutoff_time
        ).first()

        return recent_trigger is not None

    def _has_triggered_this_year(
        self,
        user_id: int,
        event_name: str
    ) -> bool:
        """
        Check if event was triggered this year

        Args:
            user_id: User ID
            event_name: Event name

        Returns:
            True if event was triggered this year
        """
        current_year = datetime.now().year
        year_start = datetime(current_year, 1, 1)

        event = self.db.query(SpecialEvent).filter(
            SpecialEvent.event_name == event_name
        ).first()

        if not event:
            return False

        year_trigger = self.db.query(UserSpecialEvent).filter(
            UserSpecialEvent.user_id == user_id,
            UserSpecialEvent.event_id == event.id,
            UserSpecialEvent.triggered_at >= year_start
        ).first()

        return year_trigger is not None

    def _get_user_message_count(self, user_id: int) -> int:
        """Get total message count for user"""
        count = self.db.query(func.count(Message.id)).filter(
            Message.user_id == user_id,
            Message.sender_type == 'user'
        ).scalar()
        return count or 0

    def _get_user_login_streak(self, user_id: int) -> int:
        """
        Calculate user's current login streak

        Simplified version: count consecutive days with daily rituals
        """
        # Get all unique ritual dates for user
        ritual_dates = self.db.query(
            func.date(DailyRitual.ritual_date).label('date')
        ).filter(
            DailyRitual.user_id == user_id
        ).distinct().order_by(func.date(DailyRitual.ritual_date).desc()).all()

        if not ritual_dates:
            return 0

        # Calculate streak
        streak = 0
        expected_date = date.today()

        for (ritual_date,) in ritual_dates:
            if ritual_date == expected_date:
                streak += 1
                expected_date = expected_date - timedelta(days=1)
            else:
                break

        return streak

    def check_random_events(self, user_id: int, idol_id: int) -> Optional[Dict]:
        """
        Check and trigger random events (5% probability)

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            Event info dict if triggered, None otherwise
        """
        # Check daily event limit
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        events_today = self.db.query(func.count(UserSpecialEvent.id)).filter(
            UserSpecialEvent.user_id == user_id,
            UserSpecialEvent.triggered_at >= today_start
        ).scalar()

        max_events = self.templates['event_settings']['max_events_per_day']
        if events_today >= max_events:
            return None

        # Random probability check
        probability = self.templates['event_settings']['random_event_probability']
        if random.random() >= probability:
            return None

        # Select eligible random events (not on cooldown)
        eligible_events = []
        for event_template in self.templates['random_events']:
            cooldown_hours = event_template.get('cooldown_hours', 24)
            if not self._has_triggered_recently(user_id, event_template['event_name'], cooldown_hours):
                eligible_events.append(event_template)

        if not eligible_events:
            return None

        # Select random event
        selected_template = random.choice(eligible_events)

        # Process template variables
        content = selected_template['content_template']
        if '{quote}' in content:
            quote = random.choice(self.templates['quote_pool'])
            content = content.replace('{quote}', quote)
        if '{song_name}' in content:
            song = random.choice(self.templates['song_pool'])
            content = content.replace('{song_name}', song)

        # Trigger event
        return self._trigger_event(
            user_id=user_id,
            idol_id=idol_id,
            event_template=selected_template,
            content=content
        )

    def check_holiday_events(self, user_id: int, idol_id: int) -> Optional[Dict]:
        """
        Check and trigger holiday events based on current date

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            Event info dict if triggered, None otherwise
        """
        today = date.today()

        for event_template in self.templates['holiday_events']:
            date_info = event_template.get('date')
            if not date_info:
                continue

            # Check if today matches the holiday (simplified, ignoring lunar calendar)
            if date_info.get('lunar'):
                continue  # Skip lunar calendar for MVP

            if (date_info['month'] == today.month and
                date_info['day'] == today.day):

                # Check if already triggered this year
                if event_template.get('once_per_year') and \
                   self._has_triggered_this_year(user_id, event_template['event_name']):
                    continue

                # Process template
                content = event_template['content_template']

                # Trigger event
                return self._trigger_event(
                    user_id=user_id,
                    idol_id=idol_id,
                    event_template=event_template,
                    content=content
                )

        return None

    def check_achievement_events(self, user_id: int, idol_id: int) -> Optional[Dict]:
        """
        Check and trigger achievement-based events

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            Event info dict if triggered, None otherwise
        """
        for event_template in self.templates['achievement_events']:
            trigger_condition = event_template.get('trigger_condition', {})

            # Check if one-time-only and already triggered
            if event_template.get('one_time_only'):
                if self._has_triggered_recently(user_id, event_template['event_name'], hours=365*24):
                    continue

            # Check message count achievements
            if 'message_count' in trigger_condition:
                required_count = trigger_condition['message_count']
                actual_count = self._get_user_message_count(user_id)

                if actual_count == required_count:
                    content = event_template['content_template']
                    return self._trigger_event(
                        user_id=user_id,
                        idol_id=idol_id,
                        event_template=event_template,
                        content=content
                    )

            # Check login streak achievements
            if 'login_streak' in trigger_condition:
                required_streak = trigger_condition['login_streak']
                actual_streak = self._get_user_login_streak(user_id)

                if actual_streak == required_streak:
                    content = event_template['content_template']
                    return self._trigger_event(
                        user_id=user_id,
                        idol_id=idol_id,
                        event_template=event_template,
                        content=content
                    )

            # Check daily rituals completed
            if 'daily_rituals_completed' in trigger_condition:
                required_count = trigger_condition['daily_rituals_completed']
                today = date.today()
                rituals_today = self.db.query(func.count(DailyRitual.id)).filter(
                    DailyRitual.user_id == user_id,
                    DailyRitual.ritual_date == today
                ).scalar()

                if rituals_today == required_count:
                    # Check if already triggered today
                    if not self._has_triggered_recently(user_id, event_template['event_name'], hours=24):
                        content = event_template['content_template']
                        return self._trigger_event(
                            user_id=user_id,
                            idol_id=idol_id,
                            event_template=event_template,
                            content=content
                        )

        return None

    def _trigger_event(
        self,
        user_id: int,
        idol_id: int,
        event_template: Dict,
        content: str
    ) -> Dict:
        """
        Trigger an event and create database records

        Args:
            user_id: User ID
            idol_id: Idol ID
            event_template: Event template dict
            content: Processed content string

        Returns:
            Event info dict
        """
        # Get or create SpecialEvent record
        event = self.db.query(SpecialEvent).filter(
            SpecialEvent.event_name == event_template['event_name']
        ).first()

        if not event:
            event = SpecialEvent(
                event_name=event_template['event_name'],
                event_type=event_template['event_type'],
                trigger_condition=event_template.get('trigger_condition'),
                content_template=event_template['content_template'],
                image_url=event_template.get('image_url'),
                reward_exp=event_template.get('reward_exp', 0),
                is_active=True
            )
            self.db.add(event)
            self.db.flush()

        # Create UserSpecialEvent record
        user_event = UserSpecialEvent(
            user_id=user_id,
            idol_id=idol_id,
            event_id=event.id,
            event_content=content,
            exp_awarded=event_template.get('reward_exp', 0),
            triggered_at=datetime.utcnow()
        )
        self.db.add(user_event)
        self.db.commit()
        self.db.refresh(user_event)

        return {
            'event_id': event.id,
            'event_name': event.event_name,
            'event_type': event.event_type,
            'content': content,
            'image_url': event_template.get('image_url'),
            'reward_exp': event_template.get('reward_exp', 0),
            'user_event_id': user_event.id
        }

    def check_all_events(self, user_id: int, idol_id: int) -> Optional[Dict]:
        """
        Check all event types and trigger if conditions met

        Priority: holiday > achievement > random

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            Event info dict if any event triggered, None otherwise
        """
        # Check holiday events first (highest priority)
        holiday_event = self.check_holiday_events(user_id, idol_id)
        if holiday_event:
            return holiday_event

        # Check achievement events
        achievement_event = self.check_achievement_events(user_id, idol_id)
        if achievement_event:
            return achievement_event

        # Check random events (lowest priority)
        random_event = self.check_random_events(user_id, idol_id)
        if random_event:
            return random_event

        return None

    def get_user_event_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """
        Get user's event history

        Args:
            user_id: User ID
            limit: Number of records to retrieve

        Returns:
            List of event records
        """
        user_events = self.db.query(UserSpecialEvent).filter(
            UserSpecialEvent.user_id == user_id
        ).order_by(UserSpecialEvent.triggered_at.desc()).limit(limit).all()

        return [
            {
                'id': ue.id,
                'event_name': ue.event.event_name if ue.event else 'Unknown',
                'event_type': ue.event.type_display_name if ue.event else 'Unknown',
                'content': ue.event_content,
                'image_url': ue.event.image_url if ue.event else None,
                'exp_awarded': ue.exp_awarded,
                'triggered_at': ue.triggered_at.isoformat(),
                'was_interacted': ue.was_interacted
            }
            for ue in user_events
        ]

    def get_event_stats(self, user_id: int) -> Dict:
        """
        Get event statistics for user

        Args:
            user_id: User ID

        Returns:
            Event statistics
        """
        user_events = self.db.query(UserSpecialEvent).filter(
            UserSpecialEvent.user_id == user_id
        ).all()

        # Count by type
        by_type = {
            SpecialEvent.TYPE_RANDOM: 0,
            SpecialEvent.TYPE_HOLIDAY: 0,
            SpecialEvent.TYPE_ACHIEVEMENT: 0,
            SpecialEvent.TYPE_WEATHER: 0
        }

        total_exp = 0
        interacted_count = 0

        for ue in user_events:
            if ue.event and ue.event.event_type in by_type:
                by_type[ue.event.event_type] += 1
            total_exp += ue.exp_awarded
            if ue.was_interacted:
                interacted_count += 1

        return {
            'total_events': len(user_events),
            'by_type': by_type,
            'total_exp_from_events': total_exp,
            'interaction_rate': round(interacted_count / len(user_events), 2) if user_events else 0.0
        }
