"""
Redis client for caching and pub/sub
Story 8.2: 实时消息同步（SSE）
"""
import redis
from app.config import settings


# Global Redis client instance
_redis_client = None


def get_redis_client() -> redis.Redis:
    """
    Get Redis client instance (singleton pattern)

    Returns:
        redis.Redis: Redis client instance
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,  # Auto-decode bytes to strings
            encoding="utf-8"
        )

    return _redis_client


def get_redis_pubsub() -> redis.client.PubSub:
    """
    Get Redis pub/sub instance for message broadcasting

    Returns:
        redis.client.PubSub: Redis pub/sub instance
    """
    client = get_redis_client()
    return client.pubsub()
