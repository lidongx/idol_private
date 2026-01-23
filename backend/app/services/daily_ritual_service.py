"""
DailyRitualService - Service for managing daily rituals
Story 5.3: 每日仪式（早安/运势/晚安）
"""
import json
import random
from datetime import datetime, date, time
from typing import Dict, Optional, List
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.daily_ritual import DailyRitual
from app.models.user import User
from app.models.idol import Idol
from app.models.conversation import Conversation
from app.services.intimacy_service import IntimacyService


class DailyRitualService:
    """Service for managing daily rituals (morning, fortune, night)"""

    def __init__(self, db: Session):
        self.db = db
        self._load_templates()

    def _load_templates(self):
        """Load ritual templates from JSON configuration"""
        config_path = Path(__file__).parent.parent / "config" / "ritual_templates.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)

    def check_ritual_status(self, user_id: int, ritual_date: date = None) -> Dict:
        """
        Check ritual completion status for a user on a specific date

        Args:
            user_id: User ID
            ritual_date: Date to check (default: today)

        Returns:
            {
                'date': str,
                'morning_greeting': {'completed': bool, 'completed_at': str, 'can_complete': bool, 'in_time_window': bool},
                'fortune': {'completed': bool, 'completed_at': str, 'can_complete': bool},
                'night_greeting': {'completed': bool, 'completed_at': str, 'can_complete': bool, 'in_time_window': bool}
            }
        """
        if ritual_date is None:
            ritual_date = date.today()

        # Get all rituals for this user on this date
        rituals = self.db.query(DailyRitual).filter(
            DailyRitual.user_id == user_id,
            DailyRitual.ritual_date == ritual_date
        ).all()

        # Create ritual lookup
        rituals_dict = {r.ritual_type: r for r in rituals}

        # Get current time for time window checks
        current_time = datetime.now().time()
        current_hour = current_time.hour

        # Check morning greeting time window (7:00-9:00)
        morning_window = self.templates['time_windows']['morning_greeting']
        in_morning_window = morning_window['start_hour'] <= current_hour < morning_window['end_hour']

        # Check night greeting time window (22:00-24:00)
        night_window = self.templates['time_windows']['night_greeting']
        in_night_window = night_window['start_hour'] <= current_hour < night_window['end_hour']

        # Check if it's today (can't complete rituals for past/future dates)
        is_today = ritual_date == date.today()

        # Build status response
        status = {
            'date': ritual_date.isoformat(),
            'morning_greeting': {
                'completed': DailyRitual.MORNING_GREETING in rituals_dict,
                'completed_at': rituals_dict[DailyRitual.MORNING_GREETING].completed_at.isoformat() if DailyRitual.MORNING_GREETING in rituals_dict else None,
                'can_complete': is_today and in_morning_window and DailyRitual.MORNING_GREETING not in rituals_dict,
                'in_time_window': in_morning_window,
                'time_window': f"{morning_window['start_hour']}:00-{morning_window['end_hour']}:00"
            },
            'fortune': {
                'completed': DailyRitual.FORTUNE in rituals_dict,
                'completed_at': rituals_dict[DailyRitual.FORTUNE].completed_at.isoformat() if DailyRitual.FORTUNE in rituals_dict else None,
                'can_complete': is_today and DailyRitual.FORTUNE not in rituals_dict,
                'time_window': '全天'
            },
            'night_greeting': {
                'completed': DailyRitual.NIGHT_GREETING in rituals_dict,
                'completed_at': rituals_dict[DailyRitual.NIGHT_GREETING].completed_at.isoformat() if DailyRitual.NIGHT_GREETING in rituals_dict else None,
                'can_complete': is_today and in_night_window and DailyRitual.NIGHT_GREETING not in rituals_dict,
                'in_time_window': in_night_window,
                'time_window': f"{night_window['start_hour']}:00-{night_window['end_hour']}:00"
            }
        }

        return status

    def complete_morning_greeting(self, user_id: int, idol_id: int) -> Dict:
        """
        Complete morning greeting ritual

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            {
                'success': bool,
                'message': str,
                'greeting': str,
                'exp_reward': int,
                'ritual_id': int
            }

        Raises:
            ValueError: If not in time window or already completed
        """
        # Check time window
        current_hour = datetime.now().hour
        morning_window = self.templates['time_windows']['morning_greeting']

        if not (morning_window['start_hour'] <= current_hour < morning_window['end_hour']):
            raise ValueError(f"早安问候只能在 {morning_window['start_hour']}:00-{morning_window['end_hour']}:00 完成")

        # Check if already completed today
        today = date.today()
        existing = self.db.query(DailyRitual).filter(
            DailyRitual.user_id == user_id,
            DailyRitual.ritual_type == DailyRitual.MORNING_GREETING,
            DailyRitual.ritual_date == today
        ).first()

        if existing:
            raise ValueError("今天已经完成早安问候啦~")

        # Select random greeting
        greeting = random.choice(self.templates['morning_greetings'])

        # Create ritual record
        ritual = DailyRitual(
            user_id=user_id,
            idol_id=idol_id,
            ritual_type=DailyRitual.MORNING_GREETING,
            ritual_date=today,
            completed_at=datetime.utcnow()
        )
        self.db.add(ritual)
        self.db.commit()
        self.db.refresh(ritual)

        # Get exp reward
        exp_reward = DailyRitual.get_ritual_exp_reward(DailyRitual.MORNING_GREETING)

        # Story 6.1: Add intimacy exp for morning greeting
        conversation = self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.idol_id == idol_id
        ).first()

        intimacy_result = None
        if conversation:
            intimacy_service = IntimacyService(self.db)
            intimacy_result = intimacy_service.add_morning_greeting_exp(conversation.id)

        return {
            'success': True,
            'message': '早安问候完成！',
            'greeting': greeting,
            'exp_reward': exp_reward,
            'ritual_id': ritual.id,
            'intimacy': intimacy_result
        }

    def complete_night_greeting(self, user_id: int, idol_id: int) -> Dict:
        """
        Complete night greeting ritual

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            {
                'success': bool,
                'message': str,
                'greeting': str,
                'exp_reward': int,
                'ritual_id': int
            }

        Raises:
            ValueError: If not in time window or already completed
        """
        # Check time window
        current_hour = datetime.now().hour
        night_window = self.templates['time_windows']['night_greeting']

        if not (night_window['start_hour'] <= current_hour < night_window['end_hour']):
            raise ValueError(f"晚安问候只能在 {night_window['start_hour']}:00-{night_window['end_hour']}:00 完成")

        # Check if already completed today
        today = date.today()
        existing = self.db.query(DailyRitual).filter(
            DailyRitual.user_id == user_id,
            DailyRitual.ritual_type == DailyRitual.NIGHT_GREETING,
            DailyRitual.ritual_date == today
        ).first()

        if existing:
            raise ValueError("今天已经完成晚安问候啦~")

        # Select random greeting
        greeting = random.choice(self.templates['night_greetings'])

        # Create ritual record
        ritual = DailyRitual(
            user_id=user_id,
            idol_id=idol_id,
            ritual_type=DailyRitual.NIGHT_GREETING,
            ritual_date=today,
            completed_at=datetime.utcnow()
        )
        self.db.add(ritual)
        self.db.commit()
        self.db.refresh(ritual)

        # Get exp reward
        exp_reward = DailyRitual.get_ritual_exp_reward(DailyRitual.NIGHT_GREETING)

        # Story 6.1: Add intimacy exp for night greeting
        conversation = self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.idol_id == idol_id
        ).first()

        intimacy_result = None
        if conversation:
            intimacy_service = IntimacyService(self.db)
            intimacy_result = intimacy_service.add_night_greeting_exp(conversation.id)

        return {
            'success': True,
            'message': '晚安问候完成！',
            'greeting': greeting,
            'exp_reward': exp_reward,
            'ritual_id': ritual.id,
            'intimacy': intimacy_result
        }

    def get_user_ritual_history(self, user_id: int, limit: int = 30) -> List[Dict]:
        """
        Get user's ritual history

        Args:
            user_id: User ID
            limit: Number of days to retrieve

        Returns:
            List of ritual records with date and completion status
        """
        rituals = self.db.query(DailyRitual).filter(
            DailyRitual.user_id == user_id
        ).order_by(DailyRitual.ritual_date.desc()).limit(limit * 3).all()  # *3 because max 3 rituals per day

        # Group by date
        history_by_date = {}
        for ritual in rituals:
            date_str = ritual.ritual_date.isoformat()
            if date_str not in history_by_date:
                history_by_date[date_str] = {
                    'date': date_str,
                    'rituals': []
                }

            history_by_date[date_str]['rituals'].append({
                'type': ritual.ritual_type,
                'type_display': ritual.ritual_display_name,
                'completed_at': ritual.completed_at.isoformat(),
                'exp_reward': DailyRitual.get_ritual_exp_reward(ritual.ritual_type)
            })

        # Convert to sorted list
        history = sorted(history_by_date.values(), key=lambda x: x['date'], reverse=True)

        return history[:limit]

    def get_ritual_stats(self, user_id: int) -> Dict:
        """
        Get ritual statistics for a user

        Args:
            user_id: User ID

        Returns:
            {
                'total_rituals': int,
                'morning_greetings': int,
                'fortunes': int,
                'night_greetings': int,
                'total_exp_earned': int,
                'current_streak': int,
                'longest_streak': int
            }
        """
        # Get all rituals for user
        rituals = self.db.query(DailyRitual).filter(
            DailyRitual.user_id == user_id
        ).order_by(DailyRitual.ritual_date.desc()).all()

        # Count by type
        type_counts = {
            DailyRitual.MORNING_GREETING: 0,
            DailyRitual.FORTUNE: 0,
            DailyRitual.NIGHT_GREETING: 0
        }

        for ritual in rituals:
            if ritual.ritual_type in type_counts:
                type_counts[ritual.ritual_type] += 1

        # Calculate total exp
        total_exp = sum(
            DailyRitual.get_ritual_exp_reward(ritual.ritual_type)
            for ritual in rituals
        )

        # Calculate streaks (days with at least one ritual)
        dates_with_rituals = sorted(set(r.ritual_date for r in rituals), reverse=True)

        current_streak = 0
        longest_streak = 0
        temp_streak = 0

        if dates_with_rituals:
            # Check current streak
            expected_date = date.today()
            for ritual_date in dates_with_rituals:
                if ritual_date == expected_date:
                    current_streak += 1
                    temp_streak += 1
                    expected_date = date.fromordinal(expected_date.toordinal() - 1)
                else:
                    break

            # Calculate longest streak
            temp_streak = 1
            longest_streak = 1
            for i in range(1, len(dates_with_rituals)):
                prev_date = dates_with_rituals[i - 1]
                curr_date = dates_with_rituals[i]
                if (prev_date.toordinal() - curr_date.toordinal()) == 1:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 1

        return {
            'total_rituals': len(rituals),
            'morning_greetings': type_counts[DailyRitual.MORNING_GREETING],
            'fortunes': type_counts[DailyRitual.FORTUNE],
            'night_greetings': type_counts[DailyRitual.NIGHT_GREETING],
            'total_exp_earned': total_exp,
            'current_streak': current_streak,
            'longest_streak': longest_streak
        }
