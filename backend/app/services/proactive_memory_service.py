"""
Proactive Memory Service for AI-initiated memory mentions
Story 4.6: 主动提及机制与记忆回顾
"""
from datetime import datetime, timedelta, date
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.memory import Memory
from app.models.proactive_mention import ProactiveMention
from app.models.user import User
from app.services.ai import AIProviderFactory


class ProactiveMemoryService:
    """
    Service for managing proactive memory mentions

    This service helps AI proactively bring up important memories that haven't
    been mentioned recently, making conversations feel more caring and attentive.
    """

    # Days threshold: mention memories not mentioned in last N days
    DAYS_THRESHOLD = 3

    # Daily limit: max proactive mentions per user per day
    DAILY_LIMIT = 1

    def __init__(self, db: Session):
        self.db = db
        self.ai_provider = AIProviderFactory.get_provider()

    def has_reached_daily_limit(self, user_id: int) -> bool:
        """
        Check if user has already received proactive mention today

        Args:
            user_id: User ID

        Returns:
            True if daily limit reached, False otherwise
        """
        today = date.today()

        count = (
            self.db.query(ProactiveMention)
            .filter(
                ProactiveMention.user_id == user_id,
                ProactiveMention.mention_date == today
            )
            .count()
        )

        return count >= self.DAILY_LIMIT

    def get_unmentioned_important_memories(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[Memory]:
        """
        Get important memories that haven't been mentioned recently

        Args:
            user_id: User ID
            limit: Maximum number of memories to return

        Returns:
            List of Memory objects
        """
        threshold_date = datetime.utcnow() - timedelta(days=self.DAYS_THRESHOLD)

        # Query for high importance memories that:
        # 1. Haven't been mentioned in last N days (or never mentioned)
        # 2. Are older than 1 day (avoid newly created memories)
        one_day_ago = datetime.utcnow() - timedelta(days=1)

        memories = (
            self.db.query(Memory)
            .filter(
                Memory.user_id == user_id,
                Memory.importance == 'high',
                Memory.created_at < one_day_ago,  # At least 1 day old
                (
                    (Memory.last_mentioned_at.is_(None)) |
                    (Memory.last_mentioned_at < threshold_date)
                )
            )
            .order_by(Memory.last_mentioned_at.asc().nullsfirst())
            .limit(limit)
            .all()
        )

        return memories

    def filter_recently_mentioned_proactively(
        self,
        memories: List[Memory],
        user_id: int
    ) -> List[Memory]:
        """
        Filter out memories that were proactively mentioned in last 7 days

        Args:
            memories: List of Memory objects
            user_id: User ID

        Returns:
            Filtered list of Memory objects
        """
        if not memories:
            return []

        seven_days_ago = date.today() - timedelta(days=7)

        # Get memory IDs that were proactively mentioned recently
        recent_mentions = (
            self.db.query(ProactiveMention.memory_id)
            .filter(
                ProactiveMention.user_id == user_id,
                ProactiveMention.mention_date >= seven_days_ago
            )
            .all()
        )

        recently_mentioned_ids = {memory_id for (memory_id,) in recent_mentions}

        # Filter out recently mentioned memories
        filtered = [m for m in memories if m.id not in recently_mentioned_ids]

        return filtered

    async def generate_proactive_question(self, memory_content: str) -> str:
        """
        Generate a natural proactive question about a memory using AI

        Args:
            memory_content: The memory content to ask about

        Returns:
            AI-generated proactive question
        """
        prompt = f"""你是一个温柔体贴的AI虚拟偶像"林雪晴"。你记得用户之前告诉你的一件重要的事情，你想主动关心一下他。

用户之前告诉你的记忆：
"{memory_content}"

请生成一句自然、温暖、关心的问候，主动提起这个话题。要求：
1. 语气温柔亲切，像朋友之间的关心
2. 不要直接复述记忆内容，要用自然的方式提起
3. 表达出你的关心和想了解进展的心情
4. 50字以内，简短自然
5. 可以用"对了"、"最近"等自然过渡词

只返回问候语，不要解释。"""

        try:
            response = await self.ai_provider.generate_response([
                {"role": "system", "content": "你是一个温柔体贴的AI助手。"},
                {"role": "user", "content": prompt}
            ])

            proactive_message = response.strip()

            # Remove quotes if present
            if proactive_message.startswith('"') and proactive_message.endswith('"'):
                proactive_message = proactive_message[1:-1]

            return proactive_message

        except Exception as e:
            # Fallback to template-based message
            return self._generate_template_question(memory_content)

    def _generate_template_question(self, memory_content: str) -> str:
        """
        Generate a template-based proactive question (fallback)

        Args:
            memory_content: The memory content

        Returns:
            Template-based question
        """
        templates = [
            f"对了，{memory_content}，最近怎么样了？",
            f"想起来了，{memory_content}，进展如何呀？",
            f"好久没听你说{memory_content}了，还好吗？",
            f"最近{memory_content}，有什么新进展吗？",
        ]

        # Simple hash to pick consistent template for same content
        template_index = len(memory_content) % len(templates)
        return templates[template_index]

    async def check_and_send_proactive_mention(
        self,
        user_id: int
    ) -> Optional[dict]:
        """
        Check if should send proactive mention and generate message

        Args:
            user_id: User ID

        Returns:
            Dictionary with proactive mention info, or None if no mention needed:
            {
                'memory_id': int,
                'proactive_message': str,
                'memory_content': str
            }
        """
        # Check daily limit
        if self.has_reached_daily_limit(user_id):
            return None

        # Get unmentioned important memories
        unmentioned = self.get_unmentioned_important_memories(user_id, limit=5)

        if not unmentioned:
            return None

        # Filter out recently proactively mentioned
        candidates = self.filter_recently_mentioned_proactively(unmentioned, user_id)

        if not candidates:
            return None

        # Pick the oldest unmentioned memory
        memory = candidates[0]

        # Generate proactive question
        proactive_message = await self.generate_proactive_question(memory.content)

        return {
            'memory_id': memory.id,
            'proactive_message': proactive_message,
            'memory_content': memory.content,
        }

    def record_proactive_mention(
        self,
        user_id: int,
        memory_id: int,
        proactive_message: str
    ) -> ProactiveMention:
        """
        Record a proactive mention in database

        Args:
            user_id: User ID
            memory_id: Memory ID
            proactive_message: The proactive message sent

        Returns:
            Created ProactiveMention object
        """
        today = date.today()

        # Check if already mentioned today (shouldn't happen but be safe)
        existing = (
            self.db.query(ProactiveMention)
            .filter(
                ProactiveMention.user_id == user_id,
                ProactiveMention.memory_id == memory_id,
                ProactiveMention.mention_date == today
            )
            .first()
        )

        if existing:
            return existing

        # Create new mention record
        mention = ProactiveMention(
            user_id=user_id,
            memory_id=memory_id,
            mention_date=today,
            proactive_message=proactive_message,
            was_replied=False
        )

        self.db.add(mention)
        self.db.commit()
        self.db.refresh(mention)

        # Also update memory's last_mentioned_at
        memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
        if memory:
            memory.mark_mentioned()
            self.db.commit()

        return mention

    def mark_proactive_mention_replied(
        self,
        mention_id: int
    ) -> Optional[ProactiveMention]:
        """
        Mark that user replied to a proactive mention

        Args:
            mention_id: ProactiveMention ID

        Returns:
            Updated ProactiveMention object or None
        """
        mention = (
            self.db.query(ProactiveMention)
            .filter(ProactiveMention.id == mention_id)
            .first()
        )

        if mention:
            mention.mark_replied()
            self.db.commit()
            self.db.refresh(mention)

        return mention

    def get_user_proactive_mentions(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[ProactiveMention]:
        """
        Get recent proactive mentions for a user

        Args:
            user_id: User ID
            limit: Maximum number to return

        Returns:
            List of ProactiveMention objects
        """
        return (
            self.db.query(ProactiveMention)
            .filter(ProactiveMention.user_id == user_id)
            .order_by(ProactiveMention.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_proactive_mention_stats(self, user_id: int) -> dict:
        """
        Get statistics about proactive mentions for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary with stats
        """
        total_mentions = (
            self.db.query(ProactiveMention)
            .filter(ProactiveMention.user_id == user_id)
            .count()
        )

        replied_mentions = (
            self.db.query(ProactiveMention)
            .filter(
                ProactiveMention.user_id == user_id,
                ProactiveMention.was_replied == True
            )
            .count()
        )

        reply_rate = (replied_mentions / total_mentions * 100) if total_mentions > 0 else 0

        today_mentions = (
            self.db.query(ProactiveMention)
            .filter(
                ProactiveMention.user_id == user_id,
                ProactiveMention.mention_date == date.today()
            )
            .count()
        )

        return {
            'total_proactive_mentions': total_mentions,
            'replied_mentions': replied_mentions,
            'reply_rate': round(reply_rate, 2),
            'mentions_today': today_mentions,
            'daily_limit_reached': today_mentions >= self.DAILY_LIMIT
        }
