"""
Message Broadcast Service for Real-time Message Sync
Story 8.2: 实时消息同步（SSE）
"""
import json
from typing import Dict, Any
from app.redis_client import get_redis_client


class MessageBroadcastService:
    """
    Service for broadcasting messages to all user's devices via Redis pub/sub
    """

    def __init__(self):
        self.redis_client = get_redis_client()

    def get_user_channel(self, user_id: int) -> str:
        """
        Get the Redis channel name for a user's devices

        Args:
            user_id: User ID

        Returns:
            str: Channel name (e.g., "user:123:messages")
        """
        return f"user:{user_id}:messages"

    def broadcast_message(self, user_id: int, message_data: Dict[str, Any]) -> int:
        """
        Broadcast a message to all of user's devices

        Args:
            user_id: User ID
            message_data: Message data to broadcast (dict)

        Returns:
            int: Number of subscribers that received the message
        """
        channel = self.get_user_channel(user_id)
        message_json = json.dumps(message_data, ensure_ascii=False)

        # Publish message to Redis channel
        # Returns number of subscribers that received the message
        num_subscribers = self.redis_client.publish(channel, message_json)

        return num_subscribers

    def broadcast_new_message(self, user_id: int, message_id: int,
                             conversation_id: int, content: str,
                             sender_type: str, created_at: str) -> int:
        """
        Broadcast a new message event

        Args:
            user_id: User ID
            message_id: Message ID
            conversation_id: Conversation ID
            content: Message content
            sender_type: 'user' or 'idol'
            created_at: Message creation timestamp (ISO format)

        Returns:
            int: Number of subscribers
        """
        message_data = {
            "event": "new_message",
            "data": {
                "id": message_id,
                "conversation_id": conversation_id,
                "content": content,
                "sender_type": sender_type,
                "created_at": created_at,
            }
        }

        return self.broadcast_message(user_id, message_data)

    def broadcast_typing_indicator(self, user_id: int, conversation_id: int,
                                   is_typing: bool, sender_type: str) -> int:
        """
        Broadcast typing indicator event

        Args:
            user_id: User ID
            conversation_id: Conversation ID
            is_typing: Whether user is typing
            sender_type: 'user' or 'idol'

        Returns:
            int: Number of subscribers
        """
        message_data = {
            "event": "typing_indicator",
            "data": {
                "conversation_id": conversation_id,
                "is_typing": is_typing,
                "sender_type": sender_type,
            }
        }

        return self.broadcast_message(user_id, message_data)

    def broadcast_message_status(self, user_id: int, message_id: int,
                                 status: str) -> int:
        """
        Broadcast message status change event

        Args:
            user_id: User ID
            message_id: Message ID
            status: New status ('sent', 'delivered', 'read')

        Returns:
            int: Number of subscribers
        """
        message_data = {
            "event": "message_status",
            "data": {
                "message_id": message_id,
                "status": status,
            }
        }

        return self.broadcast_message(user_id, message_data)
