"""
Milestone Service for anniversary tracking and milestone messages
Story 4.5: 周年纪念与主动回顾
"""
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.milestone import Milestone
from app.models.user import User
from app.models.conversation import Conversation


class MilestoneService:
    """Service for managing user milestones and anniversaries"""

    # Milestone types in order
    MILESTONE_TYPES = ['days_7', 'days_30', 'days_100', 'days_365']

    # Days for each milestone type
    MILESTONE_DAYS = {
        'days_7': 7,
        'days_30': 30,
        'days_100': 100,
        'days_365': 365,
    }

    def __init__(self, db: Session):
        self.db = db

    def get_user_first_conversation_date(self, user_id: int) -> Optional[date]:
        """
        Get the date of user's first conversation (relationship start date)

        Args:
            user_id: User ID

        Returns:
            Date of first conversation or None
        """
        first_conversation = (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.asc())
            .first()
        )

        if first_conversation:
            return first_conversation.created_at.date()
        return None

    def calculate_days_since_first_conversation(self, user_id: int) -> Optional[int]:
        """
        Calculate how many days since user's first conversation

        Args:
            user_id: User ID

        Returns:
            Number of days or None if no conversations
        """
        first_date = self.get_user_first_conversation_date(user_id)
        if not first_date:
            return None

        today = date.today()
        days_since = (today - first_date).days
        return days_since

    def get_milestone_by_type(self, user_id: int, milestone_type: str) -> Optional[Milestone]:
        """
        Get a specific milestone for user

        Args:
            user_id: User ID
            milestone_type: Milestone type (e.g., 'days_7')

        Returns:
            Milestone object or None
        """
        return (
            self.db.query(Milestone)
            .filter(
                Milestone.user_id == user_id,
                Milestone.milestone_type == milestone_type
            )
            .first()
        )

    def has_milestone(self, user_id: int, milestone_type: str) -> bool:
        """
        Check if user already has a specific milestone

        Args:
            user_id: User ID
            milestone_type: Milestone type

        Returns:
            True if milestone exists, False otherwise
        """
        return self.get_milestone_by_type(user_id, milestone_type) is not None

    def get_user_milestones(self, user_id: int) -> List[Milestone]:
        """
        Get all milestones for a user

        Args:
            user_id: User ID

        Returns:
            List of Milestone objects
        """
        return (
            self.db.query(Milestone)
            .filter(Milestone.user_id == user_id)
            .order_by(Milestone.triggered_at.desc())
            .all()
        )

    def create_milestone(
        self,
        user_id: int,
        milestone_type: str,
        message_content: Optional[str] = None,
        special_reward: Optional[str] = None
    ) -> Milestone:
        """
        Create a new milestone for user

        Args:
            user_id: User ID
            milestone_type: Milestone type
            message_content: Optional custom message
            special_reward: Optional special reward

        Returns:
            Created Milestone object

        Raises:
            ValueError: If milestone already exists
        """
        # Check if milestone already exists
        if self.has_milestone(user_id, milestone_type):
            raise ValueError(f"Milestone {milestone_type} already exists for user {user_id}")

        # Get user for personalization
        user = self.db.query(User).filter(User.id == user_id).first()
        user_name = None  # Can be extracted from memory tags if available

        # Generate message if not provided
        if not message_content:
            message_content = Milestone.get_milestone_message(milestone_type, user_name)

        # Get special reward if not provided
        if not special_reward:
            special_reward = Milestone.get_special_reward(milestone_type)

        # Create milestone
        milestone = Milestone(
            user_id=user_id,
            milestone_type=milestone_type,
            message_content=message_content,
            special_reward=special_reward,
            triggered_at=datetime.utcnow(),
            is_claimed=False
        )

        self.db.add(milestone)
        self.db.commit()
        self.db.refresh(milestone)

        return milestone

    def check_and_create_milestones_for_user(self, user_id: int) -> List[Milestone]:
        """
        Check if user has reached any new milestones and create them

        Args:
            user_id: User ID

        Returns:
            List of newly created Milestone objects (empty if none)
        """
        # Calculate days since first conversation
        days_since = self.calculate_days_since_first_conversation(user_id)

        if days_since is None:
            return []  # No conversations yet

        newly_created = []

        # Check each milestone type
        for milestone_type in self.MILESTONE_TYPES:
            required_days = self.MILESTONE_DAYS[milestone_type]

            # If user has reached this milestone and doesn't have it yet
            if days_since >= required_days and not self.has_milestone(user_id, milestone_type):
                try:
                    milestone = self.create_milestone(user_id, milestone_type)
                    newly_created.append(milestone)
                except ValueError:
                    # Milestone already exists (race condition)
                    pass

        return newly_created

    def check_all_users_milestones(self) -> dict:
        """
        Check milestones for ALL active users (for daily cron job)

        Returns:
            Dictionary with statistics:
            {
                'users_checked': int,
                'milestones_created': int,
                'milestone_details': [...]
            }
        """
        # Get all users who have at least one conversation
        users_with_conversations = (
            self.db.query(User.id)
            .join(Conversation, User.id == Conversation.user_id)
            .group_by(User.id)
            .all()
        )

        user_ids = [user_id for (user_id,) in users_with_conversations]

        total_milestones_created = 0
        milestone_details = []

        for user_id in user_ids:
            newly_created = self.check_and_create_milestones_for_user(user_id)
            total_milestones_created += len(newly_created)

            for milestone in newly_created:
                milestone_details.append({
                    'user_id': user_id,
                    'milestone_type': milestone.milestone_type,
                    'milestone_name': milestone.milestone_display_name,
                    'message': milestone.message_content,
                    'special_reward': milestone.special_reward,
                })

        return {
            'users_checked': len(user_ids),
            'milestones_created': total_milestones_created,
            'milestone_details': milestone_details,
        }

    def get_unclaimed_milestones(self, user_id: int) -> List[Milestone]:
        """
        Get all unclaimed milestones for a user

        Args:
            user_id: User ID

        Returns:
            List of unclaimed Milestone objects
        """
        return (
            self.db.query(Milestone)
            .filter(
                Milestone.user_id == user_id,
                Milestone.is_claimed == False
            )
            .order_by(Milestone.triggered_at.desc())
            .all()
        )

    def claim_milestone(self, milestone_id: int) -> Optional[Milestone]:
        """
        Mark a milestone as claimed

        Args:
            milestone_id: Milestone ID

        Returns:
            Updated Milestone object or None
        """
        milestone = self.db.query(Milestone).filter(Milestone.id == milestone_id).first()

        if milestone:
            milestone.claim()
            self.db.commit()
            self.db.refresh(milestone)

        return milestone

    def get_next_milestone_info(self, user_id: int) -> Optional[dict]:
        """
        Get information about the next milestone user will reach

        Args:
            user_id: User ID

        Returns:
            Dictionary with next milestone info or None
        """
        days_since = self.calculate_days_since_first_conversation(user_id)

        if days_since is None:
            return None

        # Find next unreached milestone
        for milestone_type in self.MILESTONE_TYPES:
            required_days = self.MILESTONE_DAYS[milestone_type]

            if days_since < required_days:
                days_remaining = required_days - days_since
                return {
                    'milestone_type': milestone_type,
                    'milestone_name': Milestone(milestone_type=milestone_type).milestone_display_name,
                    'required_days': required_days,
                    'current_days': days_since,
                    'days_remaining': days_remaining,
                }

        # All milestones reached
        return None
