"""
Emotion Analysis Service
Detects user emotion from message content and adjusts AI response strategy
"""
import re
from typing import Dict, Tuple, Optional
from app.services.ai import AIProviderFactory


class EmotionAnalyzer:
    """
    Analyzes user message emotion and provides response strategies

    Emotion Categories:
    - happy: 开心、愉快、兴奋
    - sad: 难过、伤心、失落
    - angry: 生气、愤怒、不满
    - anxious: 焦虑、担心、紧张
    - tired: 疲惫、累、困
    - lonely: 孤独、寂寞
    - excited: 激动、期待
    - neutral: 中性、日常对话
    """

    # Keyword-based emotion detection (fast path)
    EMOTION_KEYWORDS = {
        "happy": [
            "开心", "高兴", "快乐", "哈哈", "嘿嘿", "嘻嘻",
            "太好了", "棒", "赞", "不错", "喜欢", "爱",
            "😄", "😊", "😁", "🎉", "❤️"
        ],
        "sad": [
            "难过", "伤心", "失落", "沮丧", "郁闷", "不开心",
            "哭", "呜呜", "唉", "心情不好", "糟糕", "痛苦",
            "😢", "😭", "😔", "💔"
        ],
        "angry": [
            "生气", "愤怒", "气死了", "烦", "讨厌", "混蛋",
            "可恶", "该死", "烦死了", "受够了", "不爽",
            "😡", "😠", "💢"
        ],
        "anxious": [
            "焦虑", "担心", "紧张", "害怕", "不安", "忐忑",
            "恐惧", "慌", "怎么办", "着急", "压力大",
            "😰", "😨", "😟"
        ],
        "tired": [
            "累", "疲惫", "困", "想睡", "乏", "没精神",
            "撑不住", "好累", "筋疲力尽", "打哈欠",
            "😴", "😪", "🥱"
        ],
        "lonely": [
            "孤独", "寂寞", "孤单", "没人陪", "一个人",
            "空虚", "无聊", "想你", "陪我",
            "😞", "🥺"
        ],
        "excited": [
            "激动", "兴奋", "期待", "好奇", "迫不及待",
            "太棒了", "厉害", "哇", "酷", "震惊",
            "😍", "🤩", "✨", "🔥"
        ]
    }

    # Response strategies based on emotion
    RESPONSE_STRATEGIES = {
        "happy": {
            "tone": "分享快乐，表达共鸣",
            "prompt_addition": "用户现在心情很好，请用轻松愉快的语气回应，分享ta的快乐，可以适当使用活泼的表情和语气词（如：呀、呢、哦）。"
        },
        "sad": {
            "tone": "温柔安慰，情感支持",
            "prompt_addition": "用户现在心情低落，请用温柔体贴的语气安慰ta，表达理解和支持，避免说教，多倾听。可以说一些暖心的话或转移注意力。"
        },
        "angry": {
            "tone": "理解情绪，冷静回应",
            "prompt_addition": "用户现在有些生气或烦躁，请先理解和认可ta的情绪，避免火上浇油。用平和的语气回应，帮助ta冷静下来。"
        },
        "anxious": {
            "tone": "舒缓焦虑，给予安全感",
            "prompt_addition": "用户现在有些焦虑或担心，请用温和的语气安抚ta，给予安全感和信心。可以提供具体的建议或转移注意力。"
        },
        "tired": {
            "tone": "关心休息，减少负担",
            "prompt_addition": "用户现在很累或疲惫，请用轻柔关心的语气回应，建议ta休息，避免长篇大论，保持简洁温暖。"
        },
        "lonely": {
            "tone": "温暖陪伴，主动关心",
            "prompt_addition": "用户现在感到孤独或寂寞，请用温暖的语气陪伴ta，主动表达关心，让ta感受到你的存在和重视。"
        },
        "excited": {
            "tone": "呼应激动，共享兴奋",
            "prompt_addition": "用户现在很激动或兴奋，请用热情的语气呼应ta的情绪，分享ta的期待和喜悦，可以用感叹词和表情增强互动。"
        },
        "neutral": {
            "tone": "自然对话，保持性格",
            "prompt_addition": "这是日常对话，请保持你的性格特点，自然回应即可。"
        }
    }

    def __init__(self):
        """Initialize emotion analyzer"""
        self.ai_provider = None  # Lazy load for AI-based detection

    def detect_emotion(self, message: str, use_ai: bool = False) -> Tuple[str, float]:
        """
        Detect emotion from user message

        Args:
            message: User message content
            use_ai: Whether to use AI for emotion detection (slower but more accurate)

        Returns:
            Tuple of (emotion_label, confidence_score)
            emotion_label: One of the emotion categories
            confidence_score: 0.0-1.0 confidence
        """
        # First try keyword-based detection (fast)
        emotion, confidence = self._keyword_based_detection(message)

        if confidence >= 0.7:
            # High confidence from keywords, use it
            return emotion, confidence

        if use_ai and confidence < 0.5:
            # Low confidence, use AI for better detection
            emotion_ai, confidence_ai = self._ai_based_detection(message)
            if confidence_ai > confidence:
                return emotion_ai, confidence_ai

        return emotion, confidence

    def _keyword_based_detection(self, message: str) -> Tuple[str, float]:
        """
        Fast keyword-based emotion detection

        Args:
            message: User message

        Returns:
            Tuple of (emotion, confidence)
        """
        message_lower = message.lower()
        emotion_scores = {}

        # Count keyword matches for each emotion
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
            if score > 0:
                emotion_scores[emotion] = score

        # No keyword matches
        if not emotion_scores:
            return "neutral", 0.3

        # Get emotion with highest score
        best_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[best_emotion]

        # Calculate confidence (normalize by number of matches)
        # 1 match = 0.5, 2 matches = 0.7, 3+ matches = 0.9
        if max_score == 1:
            confidence = 0.5
        elif max_score == 2:
            confidence = 0.7
        else:
            confidence = 0.9

        return best_emotion, confidence

    async def _ai_based_detection(self, message: str) -> Tuple[str, float]:
        """
        AI-based emotion detection (more accurate but slower)

        Args:
            message: User message

        Returns:
            Tuple of (emotion, confidence)
        """
        if not self.ai_provider:
            self.ai_provider = AIProviderFactory.get_provider()

        # Build prompt for emotion analysis
        analysis_prompt = [
            {
                "role": "system",
                "content": """你是一个情感分析专家。分析用户消息的情感状态，从以下类别中选择一个：

happy - 开心、愉快、兴奋
sad - 难过、伤心、失落
angry - 生气、愤怒、不满
anxious - 焦虑、担心、紧张
tired - 疲惫、累、困
lonely - 孤独、寂寞
excited - 激动、期待
neutral - 中性、日常对话

只返回情感标签，不要解释。"""
            },
            {
                "role": "user",
                "content": f"分析这条消息的情感：{message}"
            }
        ]

        try:
            response = await self.ai_provider.generate_response(
                messages=analysis_prompt,
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=10
            )

            # Parse response
            emotion = response.strip().lower()

            # Validate emotion label
            if emotion in self.EMOTION_KEYWORDS:
                return emotion, 0.8  # High confidence from AI
            else:
                return "neutral", 0.5

        except Exception as e:
            print(f"[Emotion] AI detection error: {e}")
            return "neutral", 0.3

    def get_response_strategy(self, emotion: str) -> Dict[str, str]:
        """
        Get response strategy for given emotion

        Args:
            emotion: Detected emotion label

        Returns:
            Dictionary with tone and prompt_addition
        """
        return self.RESPONSE_STRATEGIES.get(emotion, self.RESPONSE_STRATEGIES["neutral"])

    def enhance_prompt_with_emotion(
        self,
        base_prompt: str,
        emotion: str,
        confidence: float
    ) -> str:
        """
        Enhance AI prompt with emotion-aware instructions

        Args:
            base_prompt: Base personality prompt
            emotion: Detected emotion
            confidence: Confidence score

        Returns:
            Enhanced prompt with emotion guidance
        """
        if confidence < 0.4:
            # Low confidence, don't add emotion guidance
            return base_prompt

        strategy = self.get_response_strategy(emotion)
        emotion_guidance = strategy["prompt_addition"]

        enhanced = f"""{base_prompt}

【当前用户情感状态】
{emotion_guidance}"""

        return enhanced


# Global emotion analyzer instance
emotion_analyzer = EmotionAnalyzer()
