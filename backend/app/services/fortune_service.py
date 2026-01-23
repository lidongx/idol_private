"""
FortuneService - Service for generating daily fortune
Story 5.3: 每日仪式（早安/运势/晚安）
"""
import json
import random
from datetime import datetime, date
from typing import Dict, Optional
from pathlib import Path
from sqlalchemy.orm import Session
import anthropic
import os

from app.models.daily_ritual import DailyRitual
from app.models.user import User
from app.models.idol import Idol
from app.models.conversation import Conversation
from app.services.intimacy_service import IntimacyService


class FortuneService:
    """Service for generating and managing daily fortune"""

    def __init__(self, db: Session):
        self.db = db
        self._load_templates()
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def _load_templates(self):
        """Load fortune templates from JSON configuration"""
        config_path = Path(__file__).parent.parent / "config" / "ritual_templates.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)

    def _get_fortune_level(self, score: int) -> Dict:
        """
        Get fortune level based on score

        Args:
            score: Fortune score (0-100)

        Returns:
            Level info dict with range, level name, emoji, and templates
        """
        for level_key, level_data in self.templates['fortune_scores'].items():
            min_score, max_score = level_data['range']
            if min_score <= score <= max_score:
                return level_data

        # Default to average if not found
        return self.templates['fortune_scores']['average']

    def _generate_fortune_score(self, user_id: int, fortune_date: date) -> int:
        """
        Generate fortune score (0-100) based on user_id and date

        Uses a pseudo-random algorithm for consistency:
        same user on same date always gets same score

        Args:
            user_id: User ID
            fortune_date: Date for fortune

        Returns:
            Fortune score (0-100)
        """
        # Create seed from user_id and date for consistency
        seed = user_id * 10000 + fortune_date.toordinal()
        random.seed(seed)

        # Generate weighted random score
        # 60% chance for good fortune (60-100)
        # 30% chance for average fortune (40-59)
        # 10% chance for poor fortune (0-39)
        rand = random.random()
        if rand < 0.6:
            score = random.randint(60, 100)
        elif rand < 0.9:
            score = random.randint(40, 59)
        else:
            score = random.randint(0, 39)

        # Reset random seed
        random.seed()

        return score

    def _select_lucky_elements(self, user_id: int, fortune_date: date) -> Dict:
        """
        Select lucky elements for the day

        Args:
            user_id: User ID
            fortune_date: Date for fortune

        Returns:
            {
                'color': str,
                'number': int,
                'direction': str,
                'item': str
            }
        """
        # Create seed for consistency
        seed = user_id * 10000 + fortune_date.toordinal()
        random.seed(seed)

        lucky_elements = {
            'color': random.choice(self.templates['lucky_elements']['colors']),
            'number': random.choice(self.templates['lucky_elements']['numbers']),
            'direction': random.choice(self.templates['lucky_elements']['directions']),
            'item': random.choice(self.templates['lucky_elements']['items'])
        }

        # Reset random seed
        random.seed()

        return lucky_elements

    def _select_fortune_advice(self, user_id: int, fortune_date: date) -> Dict:
        """
        Select fortune advice for different aspects

        Args:
            user_id: User ID
            fortune_date: Date for fortune

        Returns:
            {
                'career': str,
                'love': str,
                'health': str,
                'wealth': str
            }
        """
        # Create seed for consistency
        seed = user_id * 10000 + fortune_date.toordinal()
        random.seed(seed)

        advice = {
            'career': random.choice(self.templates['fortune_advice']['career']),
            'love': random.choice(self.templates['fortune_advice']['love']),
            'health': random.choice(self.templates['fortune_advice']['health']),
            'wealth': random.choice(self.templates['fortune_advice']['wealth'])
        }

        # Reset random seed
        random.seed()

        return advice

    async def _generate_fortune_description_with_ai(
        self,
        user_name: str,
        idol_name: str,
        score: int,
        level_info: Dict,
        lucky_elements: Dict
    ) -> str:
        """
        Generate personalized fortune description using AI

        Args:
            user_name: User's name
            idol_name: Idol's name
            score: Fortune score
            level_info: Fortune level information
            lucky_elements: Lucky elements (color, number, direction, item)

        Returns:
            Fortune description text
        """
        # Select a template from level info
        template_description = random.choice(level_info['templates'])

        # Create prompt for AI
        prompt = f"""你是温柔体贴的AI偶像 {idol_name}，正在为 {user_name} 生成今日运势。

今日运势信息：
- 运势评分：{score}/100
- 运势等级：{level_info['level']} {level_info['emoji']}
- 幸运颜色：{lucky_elements['color']}
- 幸运数字：{lucky_elements['number']}
- 幸运方位：{lucky_elements['direction']}
- 幸运物品：{lucky_elements['item']}

参考模板："{template_description}"

要求：
1. 用温暖、鼓励的语气
2. 自然融入幸运元素
3. 保持50-80字
4. 不要使用emoji（已有等级emoji）
5. 让 {user_name} 感受到你的关心

生成今日运势描述："""

        try:
            # Call AI to generate description
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0.8,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            description = response.content[0].text.strip()

            # Fallback to template if AI response is too long
            if len(description) > 100:
                description = template_description

            return description

        except Exception as e:
            # Fallback to template on error
            print(f"Error generating fortune description with AI: {e}")
            return template_description

    async def generate_fortune(self, user_id: int, idol_id: int) -> Dict:
        """
        Generate daily fortune for user

        Args:
            user_id: User ID
            idol_id: Idol ID

        Returns:
            {
                'success': bool,
                'message': str,
                'fortune': {
                    'score': int,
                    'level': str,
                    'level_emoji': str,
                    'description': str,
                    'lucky_color': str,
                    'lucky_number': int,
                    'lucky_direction': str,
                    'lucky_item': str,
                    'advice': {
                        'career': str,
                        'love': str,
                        'health': str,
                        'wealth': str
                    }
                },
                'exp_reward': int,
                'ritual_id': int
            }

        Raises:
            ValueError: If fortune already generated today
        """
        # Check if already generated today
        today = date.today()
        existing = self.db.query(DailyRitual).filter(
            DailyRitual.user_id == user_id,
            DailyRitual.ritual_type == DailyRitual.FORTUNE,
            DailyRitual.ritual_date == today
        ).first()

        if existing:
            # Return existing fortune
            return {
                'success': True,
                'message': '今天已经查看过运势啦~',
                'fortune': existing.fortune_data,
                'exp_reward': 0,  # No exp for viewing again
                'ritual_id': existing.id,
                'already_checked': True
            }

        # Get user and idol info
        user = self.db.query(User).filter(User.id == user_id).first()
        idol = self.db.query(Idol).filter(Idol.id == idol_id).first()

        if not user or not idol:
            raise ValueError("用户或偶像不存在")

        # Generate fortune score
        score = self._generate_fortune_score(user_id, today)

        # Get fortune level
        level_info = self._get_fortune_level(score)

        # Select lucky elements
        lucky_elements = self._select_lucky_elements(user_id, today)

        # Select fortune advice
        advice = self._select_fortune_advice(user_id, today)

        # Generate AI description
        description = await self._generate_fortune_description_with_ai(
            user.username,
            idol.name,
            score,
            level_info,
            lucky_elements
        )

        # Build fortune data
        fortune_data = {
            'score': score,
            'level': level_info['level'],
            'level_emoji': level_info['emoji'],
            'description': description,
            'lucky_color': lucky_elements['color'],
            'lucky_number': lucky_elements['number'],
            'lucky_direction': lucky_elements['direction'],
            'lucky_item': lucky_elements['item'],
            'advice': advice
        }

        # Create ritual record
        ritual = DailyRitual(
            user_id=user_id,
            idol_id=idol_id,
            ritual_type=DailyRitual.FORTUNE,
            ritual_date=today,
            completed_at=datetime.utcnow(),
            fortune_data=fortune_data
        )
        self.db.add(ritual)
        self.db.commit()
        self.db.refresh(ritual)

        # Get exp reward
        exp_reward = DailyRitual.get_ritual_exp_reward(DailyRitual.FORTUNE)

        # Story 6.1: Add intimacy exp for checking fortune
        conversation = self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.idol_id == idol_id
        ).first()

        intimacy_result = None
        if conversation:
            intimacy_service = IntimacyService(self.db)
            intimacy_result = intimacy_service.add_fortune_exp(conversation.id)

        return {
            'success': True,
            'message': '运势生成成功！',
            'fortune': fortune_data,
            'exp_reward': exp_reward,
            'ritual_id': ritual.id,
            'already_checked': False,
            'intimacy': intimacy_result
        }

    def get_fortune_for_date(self, user_id: int, fortune_date: date) -> Optional[Dict]:
        """
        Get fortune for a specific date (if it exists)

        Args:
            user_id: User ID
            fortune_date: Date to check

        Returns:
            Fortune data or None if not found
        """
        ritual = self.db.query(DailyRitual).filter(
            DailyRitual.user_id == user_id,
            DailyRitual.ritual_type == DailyRitual.FORTUNE,
            DailyRitual.ritual_date == fortune_date
        ).first()

        if ritual:
            return {
                'date': ritual.ritual_date.isoformat(),
                'fortune': ritual.fortune_data,
                'completed_at': ritual.completed_at.isoformat()
            }

        return None
