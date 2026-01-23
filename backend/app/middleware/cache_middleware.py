"""
Response Caching Middleware
Story 9.1: 性能优化（首屏加载<2秒）

Caches API responses in Redis to reduce response time and database load.

Features:
- Cache GET requests by default
- Configurable cache TTL per endpoint
- Cache invalidation on data updates
- Performance metrics tracking
"""
import json
import hashlib
from typing import Optional, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
import time


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Cache middleware for API responses

    Caches GET requests to reduce database queries and improve response time.
    Uses Redis as the caching backend.
    """

    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis = redis_client

        # Default cache TTL (seconds)
        self.default_ttl = 60

        # Cache TTL by route pattern
        self.route_ttl = {
            # User profile: 5 minutes (changes infrequently)
            '/api/v1/users/me': 300,

            # Idol info: 10 minutes (static data)
            '/api/v1/idols': 600,

            # Conversation list: 1 minute (updated frequently)
            '/api/v1/conversations': 60,

            # Moments: 2 minutes
            '/api/v1/moments': 120,

            # Achievements: 5 minutes
            '/api/v1/achievements': 300,

            # Intimacy stats: 2 minutes
            '/api/v1/intimacy': 120,
        }

        # Routes to exclude from caching
        self.exclude_routes = {
            '/docs',
            '/redoc',
            '/openapi.json',
            '/health',
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and handle caching
        """
        # Only cache GET requests
        if request.method != 'GET':
            return await call_next(request)

        # Skip excluded routes
        if any(request.url.path.startswith(route) for route in self.exclude_routes):
            return await call_next(request)

        # Generate cache key
        cache_key = self._generate_cache_key(request)

        # Try to get cached response
        start_time = time.time()
        cached_response = self._get_cached_response(cache_key)

        if cached_response is not None:
            # Cache hit - return cached response
            elapsed_ms = (time.time() - start_time) * 1000
            print(f"[Cache] HIT: {request.url.path} ({elapsed_ms:.2f}ms)")

            return JSONResponse(
                content=cached_response,
                headers={
                    'X-Cache-Status': 'HIT',
                    'X-Cache-Time': f'{elapsed_ms:.2f}ms'
                }
            )

        # Cache miss - proceed with request
        response = await call_next(request)

        # Only cache successful responses
        if response.status_code == 200:
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            try:
                response_data = json.loads(response_body.decode())

                # Cache the response
                ttl = self._get_ttl_for_route(request.url.path)
                self._cache_response(cache_key, response_data, ttl)

                elapsed_ms = (time.time() - start_time) * 1000
                print(f"[Cache] MISS: {request.url.path} ({elapsed_ms:.2f}ms, cached for {ttl}s)")

                # Return response with cache headers
                return JSONResponse(
                    content=response_data,
                    headers={
                        'X-Cache-Status': 'MISS',
                        'X-Cache-TTL': str(ttl),
                        'X-Response-Time': f'{elapsed_ms:.2f}ms'
                    }
                )
            except Exception as e:
                print(f"[Cache] Error caching response: {e}")
                # Return original response if caching fails
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )

        return response

    def _generate_cache_key(self, request: Request) -> str:
        """
        Generate cache key based on URL path, query params, and user
        """
        # Extract user ID from auth header (if present)
        user_id = "anonymous"
        auth_header = request.headers.get('Authorization')
        if auth_header:
            # Simple hash of auth token to identify user
            token_hash = hashlib.md5(auth_header.encode()).hexdigest()[:8]
            user_id = f"user_{token_hash}"

        # Build cache key components
        path = request.url.path
        query = str(sorted(request.query_params.items()))

        # Create hash of key components
        key_string = f"{user_id}:{path}:{query}"
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]

        return f"api_cache:{key_hash}"

    def _get_cached_response(self, cache_key: str) -> Optional[dict]:
        """
        Get cached response from Redis
        """
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"[Cache] Error reading from cache: {e}")

        return None

    def _cache_response(self, cache_key: str, response_data: dict, ttl: int):
        """
        Cache response in Redis
        """
        try:
            self.redis.setex(
                cache_key,
                ttl,
                json.dumps(response_data)
            )
        except Exception as e:
            print(f"[Cache] Error writing to cache: {e}")

    def _get_ttl_for_route(self, path: str) -> int:
        """
        Get cache TTL for a specific route
        """
        for route_pattern, ttl in self.route_ttl.items():
            if path.startswith(route_pattern):
                return ttl

        return self.default_ttl

    def invalidate_cache(self, pattern: str = "*"):
        """
        Invalidate cache entries matching pattern

        Examples:
        - invalidate_cache("api_cache:*") - Clear all API cache
        - invalidate_cache("api_cache:user_123:*") - Clear cache for specific user
        """
        try:
            keys = self.redis.keys(f"api_cache:{pattern}")
            if keys:
                deleted = self.redis.delete(*keys)
                print(f"[Cache] Invalidated {deleted} cache entries matching '{pattern}'")
                return deleted
        except Exception as e:
            print(f"[Cache] Error invalidating cache: {e}")

        return 0


def invalidate_cache_on_update(redis_client: redis.Redis, pattern: str):
    """
    Decorator to invalidate cache when data is updated

    Usage:
    @router.post("/conversations")
    @invalidate_cache_on_update(redis_client, "conversations:*")
    async def create_conversation(...):
        ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Invalidate cache after successful update
            try:
                keys = redis_client.keys(f"api_cache:*{pattern}")
                if keys:
                    redis_client.delete(*keys)
                    print(f"[Cache] Invalidated {len(keys)} entries for pattern '{pattern}'")
            except Exception as e:
                print(f"[Cache] Error invalidating cache: {e}")

            return result
        return wrapper
    return decorator
