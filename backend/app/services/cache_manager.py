"""
Redis Cache Manager Service
Implements three-layer caching strategy for conversation optimization
"""
import json
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime
import redis
from redis import Redis

from app.config import settings


class CacheManager:
    """
    Three-layer cache architecture:
    - L1: Conversation context cache (15 min TTL)
    - L2: Common question cache (24 hour TTL)
    - L3: Vector search result cache (10 min TTL)
    """

    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client: Redis = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )

    # ========== L1: Conversation Context Cache ==========

    def get_conversation_context(self, conversation_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get conversation context from L1 cache

        Args:
            conversation_id: Conversation ID

        Returns:
            List of message dicts or None if cache miss
        """
        key = f"conv:context:{conversation_id}"
        try:
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"[Cache] L1 get error: {e}")
            return None

    def set_conversation_context(
        self,
        conversation_id: int,
        messages: List[Dict[str, Any]],
        ttl: int = 900  # 15 minutes
    ) -> bool:
        """
        Set conversation context in L1 cache

        Args:
            conversation_id: Conversation ID
            messages: List of message dicts
            ttl: Time to live in seconds (default: 900s = 15min)

        Returns:
            True if successful, False otherwise
        """
        key = f"conv:context:{conversation_id}"
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(messages, ensure_ascii=False)
            )
            return True
        except Exception as e:
            print(f"[Cache] L1 set error: {e}")
            return False

    def invalidate_conversation_context(self, conversation_id: int) -> bool:
        """
        Invalidate conversation context cache

        Args:
            conversation_id: Conversation ID

        Returns:
            True if successful
        """
        key = f"conv:context:{conversation_id}"
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"[Cache] L1 invalidate error: {e}")
            return False

    # ========== L2: Common Question Cache ==========

    def get_common_response(self, question: str) -> Optional[str]:
        """
        Get cached response for common question from L2 cache

        Args:
            question: User question text

        Returns:
            Cached response or None if cache miss
        """
        key = self._hash_question(question)
        full_key = f"conv:common:{key}"
        try:
            cached = self.redis_client.get(full_key)
            return cached
        except Exception as e:
            print(f"[Cache] L2 get error: {e}")
            return None

    def set_common_response(
        self,
        question: str,
        response: str,
        ttl: int = 86400  # 24 hours
    ) -> bool:
        """
        Set cached response for common question in L2 cache

        Args:
            question: User question text
            response: AI response text
            ttl: Time to live in seconds (default: 86400s = 24h)

        Returns:
            True if successful
        """
        key = self._hash_question(question)
        full_key = f"conv:common:{key}"
        try:
            self.redis_client.setex(full_key, ttl, response)
            return True
        except Exception as e:
            print(f"[Cache] L2 set error: {e}")
            return False

    def _hash_question(self, question: str) -> str:
        """
        Generate hash key for question

        Args:
            question: Question text

        Returns:
            MD5 hash of normalized question
        """
        # Normalize: lowercase, strip whitespace
        normalized = question.lower().strip()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()[:16]

    # ========== L3: Vector Search Cache (for Epic 4) ==========

    def get_memory_search_results(
        self,
        user_id: int,
        query: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached memory search results from L3 cache

        Args:
            user_id: User ID
            query: Search query text

        Returns:
            List of memory dicts or None if cache miss
        """
        query_hash = self._hash_question(query)
        key = f"memory:search:{user_id}:{query_hash}"
        try:
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"[Cache] L3 get error: {e}")
            return None

    def set_memory_search_results(
        self,
        user_id: int,
        query: str,
        results: List[Dict[str, Any]],
        ttl: int = 600  # 10 minutes
    ) -> bool:
        """
        Set cached memory search results in L3 cache

        Args:
            user_id: User ID
            query: Search query text
            results: List of memory search results
            ttl: Time to live in seconds (default: 600s = 10min)

        Returns:
            True if successful
        """
        query_hash = self._hash_question(query)
        key = f"memory:search:{user_id}:{query_hash}"
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(results, ensure_ascii=False)
            )
            return True
        except Exception as e:
            print(f"[Cache] L3 set error: {e}")
            return False

    # ========== Utility Methods ==========

    def health_check(self) -> bool:
        """
        Check if Redis connection is healthy

        Returns:
            True if Redis is available
        """
        try:
            return self.redis_client.ping()
        except Exception as e:
            print(f"[Cache] Health check failed: {e}")
            return False

    def clear_all_caches(self) -> bool:
        """
        Clear all conversation caches (dev/testing only)

        Returns:
            True if successful
        """
        try:
            # Clear L1 caches
            for key in self.redis_client.scan_iter("conv:context:*"):
                self.redis_client.delete(key)

            # Clear L2 caches
            for key in self.redis_client.scan_iter("conv:common:*"):
                self.redis_client.delete(key)

            # Clear L3 caches
            for key in self.redis_client.scan_iter("memory:search:*"):
                self.redis_client.delete(key)

            return True
        except Exception as e:
            print(f"[Cache] Clear all error: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring

        Returns:
            Dictionary with cache stats
        """
        try:
            info = self.redis_client.info()
            return {
                "redis_version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            print(f"[Cache] Stats error: {e}")
            return {"error": str(e)}


# Global cache manager instance
cache_manager = CacheManager()
