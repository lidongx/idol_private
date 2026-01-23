"""
Performance Tracking Middleware
Story 9.1: 性能优化（首屏加载<2秒）

Tracks API request performance metrics:
- Request duration
- Slow endpoint detection
- Performance statistics
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import statistics


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track API request performance

    Measures response time for all requests and logs slow endpoints.
    """

    # Slow request threshold (milliseconds)
    SLOW_REQUEST_THRESHOLD_MS = 200

    def __init__(self, app):
        super().__init__(app)

        # Performance metrics storage
        self.request_times = defaultdict(list)  # {endpoint: [duration_ms, ...]}
        self.request_counts = defaultdict(int)  # {endpoint: count}
        self.slow_requests = []  # List of slow request details

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track performance
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Track metrics
        endpoint = f"{request.method} {request.url.path}"
        self._record_request(endpoint, duration_ms)

        # Add performance header
        response.headers['X-Response-Time'] = f'{duration_ms:.2f}ms'

        # Log slow requests
        if duration_ms > self.SLOW_REQUEST_THRESHOLD_MS:
            self._log_slow_request(endpoint, duration_ms, request)

        # Log all requests in debug mode
        status_emoji = "✅" if response.status_code < 400 else "❌"
        print(f"[API] {status_emoji} {endpoint} - {response.status_code} - {duration_ms:.2f}ms")

        return response

    def _record_request(self, endpoint: str, duration_ms: float):
        """
        Record request metrics
        """
        self.request_times[endpoint].append(duration_ms)
        self.request_counts[endpoint] += 1

        # Keep only last 1000 requests per endpoint
        if len(self.request_times[endpoint]) > 1000:
            self.request_times[endpoint].pop(0)

    def _log_slow_request(self, endpoint: str, duration_ms: float, request: Request):
        """
        Log slow request details
        """
        slow_request = {
            'endpoint': endpoint,
            'duration_ms': duration_ms,
            'timestamp': time.time(),
            'query_params': dict(request.query_params),
        }

        self.slow_requests.append(slow_request)
        print(f"[Performance] ⚠️ SLOW REQUEST: {endpoint} took {duration_ms:.2f}ms")

        # Keep only last 100 slow requests
        if len(self.slow_requests) > 100:
            self.slow_requests.pop(0)

    def get_performance_stats(self) -> dict:
        """
        Get performance statistics for all endpoints

        Returns:
            dict: Performance stats by endpoint
        """
        stats = {}

        for endpoint, times in self.request_times.items():
            if not times:
                continue

            stats[endpoint] = {
                'count': self.request_counts[endpoint],
                'avg_ms': statistics.mean(times),
                'median_ms': statistics.median(times),
                'min_ms': min(times),
                'max_ms': max(times),
                'p95_ms': self._percentile(times, 0.95),
                'p99_ms': self._percentile(times, 0.99),
            }

        return stats

    def get_slow_requests(self, limit: int = 20) -> list:
        """
        Get recent slow requests

        Args:
            limit: Number of slow requests to return

        Returns:
            list: Recent slow requests
        """
        return self.slow_requests[-limit:]

    def _percentile(self, data: list, percentile: float) -> float:
        """
        Calculate percentile value

        Args:
            data: List of values
            percentile: Percentile (0.0 to 1.0)

        Returns:
            float: Percentile value
        """
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def print_performance_summary(self):
        """
        Print performance summary to console
        """
        stats = self.get_performance_stats()

        if not stats:
            print("[Performance] No requests recorded")
            return

        print("\n" + "=" * 80)
        print("API Performance Summary")
        print("=" * 80)

        # Sort by average response time (slowest first)
        sorted_stats = sorted(
            stats.items(),
            key=lambda x: x[1]['avg_ms'],
            reverse=True
        )

        for endpoint, metrics in sorted_stats:
            print(f"\n{endpoint}")
            print(f"  Requests: {metrics['count']}")
            print(f"  Average: {metrics['avg_ms']:.2f}ms")
            print(f"  Median: {metrics['median_ms']:.2f}ms")
            print(f"  Min: {metrics['min_ms']:.2f}ms")
            print(f"  Max: {metrics['max_ms']:.2f}ms")
            print(f"  P95: {metrics['p95_ms']:.2f}ms")
            print(f"  P99: {metrics['p99_ms']:.2f}ms")

            # Highlight slow endpoints
            if metrics['avg_ms'] > self.SLOW_REQUEST_THRESHOLD_MS:
                print(f"  ⚠️ WARNING: Average response time exceeds {self.SLOW_REQUEST_THRESHOLD_MS}ms threshold")

        print("\n" + "=" * 80)

        # Show slow requests summary
        slow_count = len(self.slow_requests)
        if slow_count > 0:
            print(f"\n⚠️ Total slow requests (>{self.SLOW_REQUEST_THRESHOLD_MS}ms): {slow_count}")
            print("\nRecent slow requests:")
            for req in self.get_slow_requests(10):
                print(f"  - {req['endpoint']}: {req['duration_ms']:.2f}ms")

        print("\n" + "=" * 80 + "\n")

    def clear_metrics(self):
        """
        Clear all performance metrics
        """
        self.request_times.clear()
        self.request_counts.clear()
        self.slow_requests.clear()
        print("[Performance] Metrics cleared")


# Global performance middleware instance
_performance_middleware = None


def get_performance_middleware() -> PerformanceMiddleware:
    """
    Get global performance middleware instance
    """
    global _performance_middleware
    return _performance_middleware


def set_performance_middleware(middleware: PerformanceMiddleware):
    """
    Set global performance middleware instance
    """
    global _performance_middleware
    _performance_middleware = middleware
