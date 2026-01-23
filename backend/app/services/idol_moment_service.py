"""
Idol Moment Service for managing idol social moments
Story 5.2: 偶像朋友圈系统
"""
import random
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.idol_moment import IdolMoment, IdolMomentLike
from app.models.idol import Idol
from app.models.user import User
from app.services.intimacy_service import IntimacyService


class IdolMomentService:
    """
    Service for managing idol moments (social posts)

    This service handles idol social moments similar to WeChat Moments,
    allowing idols to share their daily life with users.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_moments(
        self,
        idol_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[IdolMoment]:
        """
        Get moments for an idol

        Args:
            idol_id: Idol ID
            limit: Maximum number of moments to return
            offset: Offset for pagination

        Returns:
            List of IdolMoment objects, ordered by posted_at desc
        """
        moments = (
            self.db.query(IdolMoment)
            .filter(IdolMoment.idol_id == idol_id)
            .order_by(desc(IdolMoment.posted_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

        return moments

    def get_moment_by_id(self, moment_id: int) -> Optional[IdolMoment]:
        """
        Get a specific moment by ID

        Args:
            moment_id: Moment ID

        Returns:
            IdolMoment object or None
        """
        return (
            self.db.query(IdolMoment)
            .filter(IdolMoment.id == moment_id)
            .first()
        )

    def create_moment(
        self,
        idol_id: int,
        content: str,
        image_url: Optional[str] = None
    ) -> IdolMoment:
        """
        Create a new moment

        Args:
            idol_id: Idol ID
            content: Moment text content (max 300 chars)
            image_url: Optional image URL

        Returns:
            Created IdolMoment object

        Raises:
            ValueError: If content exceeds 300 characters
        """
        if len(content) > 300:
            raise ValueError("Moment content cannot exceed 300 characters")

        moment = IdolMoment(
            idol_id=idol_id,
            content=content,
            image_url=image_url,
            likes_count=0,
            posted_at=datetime.utcnow()
        )

        self.db.add(moment)
        self.db.commit()
        self.db.refresh(moment)

        return moment

    def delete_moment(self, moment_id: int) -> bool:
        """
        Delete a moment

        Args:
            moment_id: Moment ID

        Returns:
            True if deleted, False if not found
        """
        moment = self.get_moment_by_id(moment_id)

        if not moment:
            return False

        self.db.delete(moment)
        self.db.commit()

        return True

    def has_user_liked(self, moment_id: int, user_id: int) -> bool:
        """
        Check if user has liked a moment

        Args:
            moment_id: Moment ID
            user_id: User ID

        Returns:
            True if user has liked, False otherwise
        """
        like = (
            self.db.query(IdolMomentLike)
            .filter(
                IdolMomentLike.moment_id == moment_id,
                IdolMomentLike.user_id == user_id
            )
            .first()
        )

        return like is not None

    def like_moment(self, moment_id: int, user_id: int) -> Dict:
        """
        Like a moment (or unlike if already liked)

        Args:
            moment_id: Moment ID
            user_id: User ID

        Returns:
            Dictionary with action result:
            {
                'action': 'liked' or 'unliked',
                'likes_count': current like count
            }

        Raises:
            ValueError: If moment doesn't exist
        """
        moment = self.get_moment_by_id(moment_id)

        if not moment:
            raise ValueError(f"Moment {moment_id} not found")

        # Check if already liked
        existing_like = (
            self.db.query(IdolMomentLike)
            .filter(
                IdolMomentLike.moment_id == moment_id,
                IdolMomentLike.user_id == user_id
            )
            .first()
        )

        if existing_like:
            # Unlike: remove like record
            self.db.delete(existing_like)
            moment.decrement_likes()
            self.db.commit()

            return {
                'action': 'unliked',
                'likes_count': moment.likes_count
            }
        else:
            # Like: create like record
            like = IdolMomentLike(
                moment_id=moment_id,
                user_id=user_id,
                liked_at=datetime.utcnow()
            )

            self.db.add(like)
            moment.increment_likes()

            # Story 6.1: Add intimacy exp for liking moment (max 5 per day)
            intimacy_service = IntimacyService(self.db)
            intimacy_result = intimacy_service.add_like_moment_exp(user_id, moment.idol_id)

            self.db.commit()

            response = {
                'action': 'liked',
                'likes_count': moment.likes_count
            }

            # Include intimacy result if exp was awarded
            if intimacy_result:
                response['intimacy'] = intimacy_result

            return response

    def get_moments_with_like_status(
        self,
        idol_id: int,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get moments with user's like status

        Args:
            idol_id: Idol ID
            user_id: User ID
            limit: Maximum number of moments
            offset: Offset for pagination

        Returns:
            List of dictionaries with moment data and like status
        """
        moments = self.get_moments(idol_id, limit, offset)

        result = []
        for moment in moments:
            is_liked = self.has_user_liked(moment.id, user_id)

            result.append({
                'id': moment.id,
                'idol_id': moment.idol_id,
                'content': moment.content,
                'image_url': moment.image_url,
                'likes_count': moment.likes_count,
                'posted_at': moment.posted_at.isoformat() if moment.posted_at else None,
                'relative_time': moment.relative_time,
                'is_liked': is_liked
            })

        return result

    def get_moment_count(self, idol_id: int) -> int:
        """
        Get total moment count for an idol

        Args:
            idol_id: Idol ID

        Returns:
            Total number of moments
        """
        return (
            self.db.query(IdolMoment)
            .filter(IdolMoment.idol_id == idol_id)
            .count()
        )

    def get_moment_stats(self, idol_id: int) -> Dict:
        """
        Get moment statistics for an idol

        Args:
            idol_id: Idol ID

        Returns:
            Dictionary with stats
        """
        total_moments = self.get_moment_count(idol_id)

        total_likes = (
            self.db.query(IdolMoment)
            .filter(IdolMoment.idol_id == idol_id)
            .with_entities(IdolMoment.likes_count)
            .all()
        )

        total_likes_count = sum(likes for (likes,) in total_likes) if total_likes else 0

        return {
            'total_moments': total_moments,
            'total_likes': total_likes_count,
            'average_likes': round(total_likes_count / total_moments, 2) if total_moments > 0 else 0
        }
