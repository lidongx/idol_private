"""
IntimacyService - Service for managing intimacy exp and level progression
Story 6.1: 亲密度等级系统与经验值计算
"""
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.conversation import Conversation
from app.models.intimacy_log import IntimacyLog
from app.models.idol_moment import IdolMomentLike
from app.services.reward_service import RewardService


class IntimacyService:
    """Service for managing intimacy system"""

    # Exp rewards configuration
    EXP_SEND_MESSAGE = 5
    EXP_SEND_VOICE = 8
    EXP_SEND_IMAGE = 8
    EXP_MORNING_GREETING = 10
    EXP_NIGHT_GREETING = 10
    EXP_CHECK_FORTUNE = 5
    EXP_LIKE_MOMENT = 3
    EXP_LOGIN_STREAK_7 = 50

    # Daily limits
    MAX_LIKE_EXP_PER_DAY = 5  # Max 5 likes count towards exp per day

    # Level title ranges
    LEVEL_TITLES = {
        (1, 10): "新朋友",
        (11, 20): "好朋友",
        (21, 30): "亲密朋友",
        (31, 50): "特别的人",
        (51, 70): "恋人",
        (71, 90): "深度恋人",
        (91, 100): "灵魂伴侣",
    }

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def get_required_exp(level: int) -> int:
        """
        Calculate required exp for a given level

        Args:
            level: Current level (1-100)

        Returns:
            Required exp to reach next level (level * 100)
        """
        return level * 100

    @staticmethod
    def get_level_title(level: int) -> str:
        """
        Get title/label for a given intimacy level

        Args:
            level: Intimacy level (1-100)

        Returns:
            Level title (e.g., "新朋友", "恋人")
        """
        for (min_level, max_level), title in IntimacyService.LEVEL_TITLES.items():
            if min_level <= level <= max_level:
                return title
        return "灵魂伴侣"  # Default for level > 100

    def add_intimacy_exp(
        self,
        conversation_id: int,
        exp: int,
        reason: str
    ) -> Dict:
        """
        Add intimacy exp to a conversation and handle level ups

        Args:
            conversation_id: Conversation ID
            exp: Exp points to add
            reason: Reason for exp gain

        Returns:
            {
                'success': bool,
                'exp_added': int,
                'old_level': int,
                'new_level': int,
                'old_exp': int,
                'new_exp': int,
                'level_up': bool,
                'required_exp_for_next': int
            }
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        old_level = conversation.intimacy_level
        old_exp = conversation.intimacy_exp

        # Add exp
        conversation.intimacy_exp += exp

        # Check for level up
        level_up = False
        required_exp = self.get_required_exp(conversation.intimacy_level)

        while conversation.intimacy_exp >= required_exp and conversation.intimacy_level < 100:
            # Level up!
            conversation.intimacy_exp -= required_exp
            conversation.intimacy_level += 1
            level_up = True

            # Get required exp for next level
            required_exp = self.get_required_exp(conversation.intimacy_level)

        # Save conversation
        self.db.commit()
        self.db.refresh(conversation)

        # Story 6.3: Check and unlock rewards if leveled up
        unlocked_rewards = []
        if level_up:
            reward_service = RewardService(self.db)
            unlocked_rewards = reward_service.check_and_unlock_rewards(
                user_id=conversation.user_id,
                conversation_id=conversation_id,
                new_level=conversation.intimacy_level
            )

        # Create intimacy log
        log = IntimacyLog(
            conversation_id=conversation_id,
            exp_change=exp,
            reason=reason,
            new_level=conversation.intimacy_level,
            new_exp=conversation.intimacy_exp
        )
        self.db.add(log)
        self.db.commit()

        result = {
            'success': True,
            'exp_added': exp,
            'old_level': old_level,
            'new_level': conversation.intimacy_level,
            'old_exp': old_exp,
            'new_exp': conversation.intimacy_exp,
            'level_up': level_up,
            'required_exp_for_next': self.get_required_exp(conversation.intimacy_level)
        }

        # Include unlocked rewards in response
        if unlocked_rewards:
            reward_service = RewardService(self.db)
            result['unlocked_rewards'] = [
                {
                    'reward_id': ur.reward_id,
                    'reward_type': ur.reward.reward_type,
                    'description': ur.reward.description,
                    'unlock_message': reward_service.get_reward_unlock_message(ur.reward)
                }
                for ur in unlocked_rewards
            ]

        return result

    def add_message_exp(self, conversation_id: int) -> Dict:
        """Add exp for sending a message"""
        return self.add_intimacy_exp(
            conversation_id,
            self.EXP_SEND_MESSAGE,
            IntimacyLog.REASON_SEND_MESSAGE
        )

    def add_voice_exp(self, conversation_id: int) -> Dict:
        """Add exp for sending a voice message"""
        return self.add_intimacy_exp(
            conversation_id,
            self.EXP_SEND_VOICE,
            IntimacyLog.REASON_SEND_VOICE
        )

    def add_image_exp(self, conversation_id: int) -> Dict:
        """Add exp for sending an image"""
        return self.add_intimacy_exp(
            conversation_id,
            self.EXP_SEND_IMAGE,
            IntimacyLog.REASON_SEND_IMAGE
        )

    def add_morning_greeting_exp(self, conversation_id: int) -> Dict:
        """Add exp for completing morning greeting ritual"""
        return self.add_intimacy_exp(
            conversation_id,
            self.EXP_MORNING_GREETING,
            IntimacyLog.REASON_MORNING_GREETING
        )

    def add_night_greeting_exp(self, conversation_id: int) -> Dict:
        """Add exp for completing night greeting ritual"""
        return self.add_intimacy_exp(
            conversation_id,
            self.EXP_NIGHT_GREETING,
            IntimacyLog.REASON_NIGHT_GREETING
        )

    def add_fortune_exp(self, conversation_id: int) -> Dict:
        """Add exp for checking daily fortune"""
        return self.add_intimacy_exp(
            conversation_id,
            self.EXP_CHECK_FORTUNE,
            IntimacyLog.REASON_CHECK_FORTUNE
        )

    def add_like_moment_exp(self, user_id: int, idol_id: int) -> Optional[Dict]:
        """
        Add exp for liking idol's moment (max 5 per day)

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            Exp result dict or None if daily limit reached
        """
        # Get conversation
        conversation = self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.idol_id == idol_id
        ).first()

        if not conversation:
            return None

        # Check daily like exp limit
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        today_like_exp_count = self.db.query(func.count(IntimacyLog.id)).filter(
            IntimacyLog.conversation_id == conversation.id,
            IntimacyLog.reason == IntimacyLog.REASON_LIKE_MOMENT,
            IntimacyLog.created_at >= today_start
        ).scalar()

        if today_like_exp_count >= self.MAX_LIKE_EXP_PER_DAY:
            return None  # Daily limit reached

        return self.add_intimacy_exp(
            conversation.id,
            self.EXP_LIKE_MOMENT,
            IntimacyLog.REASON_LIKE_MOMENT
        )

    def get_intimacy_info(self, conversation_id: int) -> Dict:
        """
        Get intimacy information for a conversation

        Args:
            conversation_id: Conversation ID

        Returns:
            {
                'conversation_id': int,
                'current_level': int,
                'current_exp': int,
                'required_exp_for_next': int,
                'progress_percentage': float,
                'level_title': str,
                'total_exp_earned': int
            }
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        required_exp = self.get_required_exp(conversation.intimacy_level)
        progress = (conversation.intimacy_exp / required_exp * 100) if required_exp > 0 else 100

        # Calculate total exp earned
        total_exp_earned = sum(
            self.get_required_exp(i)
            for i in range(1, conversation.intimacy_level)
        ) + conversation.intimacy_exp

        return {
            'conversation_id': conversation_id,
            'current_level': conversation.intimacy_level,
            'current_exp': conversation.intimacy_exp,
            'required_exp_for_next': required_exp,
            'progress_percentage': round(progress, 1),
            'level_title': self.get_level_title(conversation.intimacy_level),
            'total_exp_earned': total_exp_earned
        }

    def get_intimacy_history(
        self,
        conversation_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get intimacy exp change history

        Args:
            conversation_id: Conversation ID
            limit: Number of records to retrieve

        Returns:
            List of intimacy log records
        """
        logs = self.db.query(IntimacyLog).filter(
            IntimacyLog.conversation_id == conversation_id
        ).order_by(IntimacyLog.created_at.desc()).limit(limit).all()

        return [
            {
                'id': log.id,
                'exp_change': log.exp_change,
                'reason': log.reason,
                'reason_display': log.reason_display_name,
                'new_level': log.new_level,
                'new_exp': log.new_exp,
                'created_at': log.created_at.isoformat()
            }
            for log in logs
        ]

    def get_intimacy_stats(self, conversation_id: int) -> Dict:
        """
        Get intimacy statistics

        Args:
            conversation_id: Conversation ID

        Returns:
            {
                'total_exp_gained': int,
                'exp_by_reason': dict,
                'level_ups': int,
                'days_active': int
            }
        """
        logs = self.db.query(IntimacyLog).filter(
            IntimacyLog.conversation_id == conversation_id
        ).all()

        # Calculate stats
        total_exp = sum(log.exp_change for log in logs)
        exp_by_reason = {}

        for log in logs:
            reason_display = log.reason_display_name
            if reason_display not in exp_by_reason:
                exp_by_reason[reason_display] = 0
            exp_by_reason[reason_display] += log.exp_change

        # Count level ups (find highest level - 1)
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        level_ups = conversation.intimacy_level - 1 if conversation else 0

        # Count active days
        if logs:
            dates = set(log.created_at.date() for log in logs)
            days_active = len(dates)
        else:
            days_active = 0

        return {
            'total_exp_gained': total_exp,
            'exp_by_reason': exp_by_reason,
            'level_ups': level_ups,
            'days_active': days_active
        }

    def apply_intimacy_decay(
        self,
        conversation_id: int,
        decay_amount: int,
        reason: str
    ) -> Dict:
        """
        Apply intimacy decay to a conversation (Story 6.5)

        Args:
            conversation_id: Conversation ID
            decay_amount: Amount to decay (positive number, will be subtracted)
            reason: Reason for decay

        Returns:
            {
                'success': bool,
                'decay_applied': int,
                'intimacy_exp_before': int,
                'intimacy_exp_after': int,
                'level': int
            }
        """
        from app.models.intimacy_decay_log import IntimacyDecayLog

        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Check if decay is disabled for this conversation
        if conversation.decay_disabled:
            return {
                'success': False,
                'reason': 'decay_disabled',
                'message': 'Decay is disabled for this conversation'
            }

        intimacy_exp_before = conversation.intimacy_exp

        # Apply decay (don't go below 0)
        actual_decay = min(decay_amount, conversation.intimacy_exp)
        conversation.intimacy_exp -= actual_decay

        intimacy_exp_after = conversation.intimacy_exp

        # Save conversation
        self.db.commit()
        self.db.refresh(conversation)

        # Create decay log
        log = IntimacyDecayLog(
            conversation_id=conversation_id,
            decay_amount=-actual_decay,  # Store as negative value
            reason=reason,
            intimacy_exp_before=intimacy_exp_before,
            intimacy_exp_after=intimacy_exp_after
        )
        self.db.add(log)
        self.db.commit()

        return {
            'success': True,
            'decay_applied': actual_decay,
            'intimacy_exp_before': intimacy_exp_before,
            'intimacy_exp_after': intimacy_exp_after,
            'level': conversation.intimacy_level
        }

    def check_and_apply_decay(self) -> List[Dict]:
        """
        Check all conversations for decay and apply if needed (Story 6.5)

        Called by daily background task

        Returns:
            List of decay results
        """
        from app.models.intimacy_decay_log import IntimacyDecayLog
        from datetime import datetime, timedelta

        # Get conversations inactive for 7+ days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        inactive_conversations = self.db.query(Conversation).filter(
            and_(
                Conversation.last_message_at < seven_days_ago,
                Conversation.decay_disabled == False,
                Conversation.intimacy_exp > 0  # Only apply to conversations with exp
            )
        ).all()

        results = []

        for conv in inactive_conversations:
            # Calculate days inactive
            days_inactive = (datetime.utcnow() - conv.last_message_at).days

            # Determine decay amount and reason
            if days_inactive >= 30:
                decay_amount = 10  # Faster decay after 30 days
                reason = IntimacyDecayLog.REASON_INACTIVE_30DAYS
            elif days_inactive >= 14:
                decay_amount = 7  # Medium decay after 14 days
                reason = IntimacyDecayLog.REASON_INACTIVE_14DAYS
            else:  # 7-13 days
                decay_amount = 5  # Gentle decay
                reason = IntimacyDecayLog.REASON_INACTIVE_7DAYS

            # Apply decay
            result = self.apply_intimacy_decay(conv.id, decay_amount, reason)
            result['conversation_id'] = conv.id
            result['days_inactive'] = days_inactive
            results.append(result)

        return results

    def toggle_decay(self, conversation_id: int, disabled: bool) -> Dict:
        """
        Enable or disable decay for a conversation (Story 6.5)

        Args:
            conversation_id: Conversation ID
            disabled: True to disable decay, False to enable

        Returns:
            Updated conversation info
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        conversation.decay_disabled = disabled
        self.db.commit()
        self.db.refresh(conversation)

        return {
            'conversation_id': conversation_id,
            'decay_disabled': conversation.decay_disabled,
            'message': f"Decay {'disabled' if disabled else 'enabled'} successfully"
        }

    def give_comeback_bonus(self, conversation_id: int) -> Dict:
        """
        Give comeback bonus to user returning after inactivity (Story 6.5)

        Args:
            conversation_id: Conversation ID

        Returns:
            Exp addition result
        """
        from datetime import datetime, timedelta

        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Check if user has received comeback bonus recently (within 30 days)
        if conversation.last_comeback_bonus_at:
            days_since_last_bonus = (datetime.utcnow() - conversation.last_comeback_bonus_at).days
            if days_since_last_bonus < 30:
                return {
                    'success': False,
                    'reason': 'too_soon',
                    'message': f"Comeback bonus available in {30 - days_since_last_bonus} days",
                    'days_until_available': 30 - days_since_last_bonus
                }

        # Check if user was actually inactive (7+ days)
        if conversation.last_message_at:
            days_inactive = (datetime.utcnow() - conversation.last_message_at).days
            if days_inactive < 7:
                return {
                    'success': False,
                    'reason': 'not_inactive',
                    'message': 'User was not inactive long enough for comeback bonus'
                }

        # Give comeback bonus
        COMEBACK_BONUS_EXP = 50
        exp_result = self.add_intimacy_exp(
            conversation_id,
            COMEBACK_BONUS_EXP,
            'comeback_bonus'
        )

        # Update last comeback bonus time
        conversation.last_comeback_bonus_at = datetime.utcnow()
        self.db.commit()

        exp_result['is_comeback_bonus'] = True
        exp_result['message'] = "欢迎回来！这是给你的回归礼包~"

        return exp_result

    def get_decay_history(
        self,
        conversation_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get intimacy decay history for a conversation

        Args:
            conversation_id: Conversation ID
            limit: Number of records to retrieve

        Returns:
            List of decay log records
        """
        from app.models.intimacy_decay_log import IntimacyDecayLog

        logs = self.db.query(IntimacyDecayLog).filter(
            IntimacyDecayLog.conversation_id == conversation_id
        ).order_by(IntimacyDecayLog.created_at.desc()).limit(limit).all()

        return [log.to_dict() for log in logs]
