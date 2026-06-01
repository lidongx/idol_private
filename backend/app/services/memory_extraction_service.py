"""
Memory extraction service for automatically extracting key information from conversations
"""
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.conversation import Conversation
from app.models.message import Message
from app.services.memory_service import MemoryService
from app.services.ai.ai_provider import AIProvider


# Memory extraction prompt template
MEMORY_EXTRACTION_PROMPT = """你是一个专业的信息提取助手。请从以下对话中提取用户分享的关键信息。

提取规则：
1. 只提取用户（User）明确表达的事实性信息
2. 不要提取AI的回复内容
3. 不要推测或猜测用户未明确说明的信息
4. 每条记忆应该是独立、完整的陈述
5. 记忆类型：hobby（爱好）、work（工作）、family（家人）、feeling（情感）、goal（目标）、preference（偏好）、event（事件）
6. 重要性：high（关键信息）、medium（一般信息）、low（次要信息）

对话内容：
{conversation_text}

请以JSON格式返回提取的记忆，格式如下：
{{
  "memories": [
    {{"content": "用户喜欢打篮球", "type": "hobby", "importance": "medium"}},
    {{"content": "用户在字节跳动工作", "type": "work", "importance": "high"}},
    {{"content": "用户有一个妹妹在上大学", "type": "family", "importance": "medium"}}
  ]
}}

如果没有提取到任何记忆，返回空数组：
{{
  "memories": []
}}
"""


class MemoryExtractionService:
    """
    Service for extracting memories from conversations

    Features:
    - Extract key information from conversation history
    - Deduplicate similar memories
    - Schedule automatic extraction after idle periods
    """

    def __init__(self, db: Session):
        self.db = db
        self.memory_service = MemoryService(db)
        self.ai_provider = AIProvider()

    def format_messages_for_extraction(self, messages: List[Message]) -> str:
        """
        Format messages into a readable text for extraction

        Args:
            messages: List of Message objects

        Returns:
            Formatted conversation text
        """
        lines = []
        for msg in messages:
            sender = "User" if msg.sender_type == "user" else "AI"
            lines.append(f"{sender}: {msg.content}")

        return "\n".join(lines)

    async def extract_memories_from_conversation(
        self,
        conversation_id: int,
        message_limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Extract memories from a conversation

        Args:
            conversation_id: Conversation ID
            message_limit: Number of recent messages to analyze (default: 20)

        Returns:
            List of extracted memories with metadata
        """
        # 1. Get conversation and check if exists
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # 2. Get recent messages
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(message_limit).all()

        if not messages:
            print(f"[MemoryExtraction] No messages found for conversation {conversation_id}")
            return []

        # Reverse to chronological order
        messages = list(reversed(messages))

        # 3. Format conversation text
        conversation_text = self.format_messages_for_extraction(messages)

        # 4. Build extraction prompt
        prompt = MEMORY_EXTRACTION_PROMPT.format(conversation_text=conversation_text)

        try:
            # 5. Call AI to extract memories
            response = await self.ai_provider.generate_text(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temperature for more consistent extraction
            )

            # 6. Parse JSON response
            result = self._parse_extraction_result(response)

            if not result or 'memories' not in result:
                print(f"[MemoryExtraction] Failed to parse extraction result")
                return []

            extracted_memories = result['memories']
            print(f"[MemoryExtraction] Extracted {len(extracted_memories)} memories")

            # 7. Save memories with deduplication
            saved_memories = []
            for mem_data in extracted_memories:
                try:
                    # Check for duplicates
                    if await self._is_duplicate_memory(
                        conversation.user_id,
                        mem_data['content']
                    ):
                        print(f"[MemoryExtraction] Skipping duplicate: {mem_data['content'][:50]}...")
                        continue

                    # Save memory
                    memory = await self.memory_service.add_memory(
                        user_id=conversation.user_id,
                        content=mem_data['content'],
                        memory_type=mem_data.get('type', 'general'),
                        importance=mem_data.get('importance', 'medium'),
                        source_message_id=messages[-1].id if messages else None,
                    )

                    saved_memories.append({
                        "memory_id": memory.id,
                        "content": memory.content,
                        "type": memory.memory_type,
                        "importance": memory.importance,
                    })

                except Exception as e:
                    print(f"[MemoryExtraction] Failed to save memory: {e}")
                    continue

            print(f"[MemoryExtraction] Saved {len(saved_memories)}/{len(extracted_memories)} memories")
            return saved_memories

        except Exception as e:
            print(f"[MemoryExtraction] Extraction failed: {e}")
            return []

    def _parse_extraction_result(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse AI response to extract JSON

        Args:
            response: AI response text

        Returns:
            Parsed JSON dict or None
        """
        try:
            # Try to parse directly
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_text = response[start:end].strip()
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass

            # Try to extract JSON between { and }
            if "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_text = response[start:end]
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass

            print(f"[MemoryExtraction] Failed to parse JSON from response")
            return None

    async def _is_duplicate_memory(
        self,
        user_id: int,
        content: str,
        similarity_threshold: float = 0.90,
    ) -> bool:
        """
        Check if memory is duplicate using vector similarity

        Args:
            user_id: User ID
            content: Memory content
            similarity_threshold: Similarity threshold (0.90 = 90%)

        Returns:
            True if duplicate found
        """
        try:
            # Search for similar memories
            similar_memories = await self.memory_service.search_memories(
                user_id=user_id,
                query=content,
                limit=1,
            )

            if similar_memories and len(similar_memories) > 0:
                similarity = similar_memories[0]['similarity']
                if similarity >= similarity_threshold:
                    print(f"[MemoryExtraction] Duplicate found (similarity: {similarity:.2f})")
                    return True

            return False

        except Exception as e:
            print(f"[MemoryExtraction] Duplicate check failed: {e}")
            return False

    def get_conversations_needing_extraction(
        self,
        idle_minutes: int = 5,
    ) -> List[Conversation]:
        """
        Get conversations that need memory extraction

        Criteria:
        - Last message was at least idle_minutes ago
        - Has messages that haven't been extracted yet

        Args:
            idle_minutes: Minimum idle time in minutes (default: 5)

        Returns:
            List of Conversation objects
        """
        idle_threshold = datetime.utcnow() - timedelta(minutes=idle_minutes)

        # Find conversations with recent activity but now idle
        conversations = self.db.query(Conversation).filter(
            Conversation.last_active_at <= idle_threshold,
            Conversation.last_active_at >= datetime.utcnow() - timedelta(hours=24),  # Within last 24h
        ).all()

        # TODO: Add logic to track which conversations have been extracted
        # For MVP, we'll extract every time (could be optimized later)

        return conversations
