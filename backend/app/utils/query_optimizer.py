"""
Database Query Optimizer
Story 9.1: 性能优化（首屏加载<2秒）

Provides utilities for optimizing database queries:
- Query performance monitoring
- Slow query detection
- Query result caching
- Pagination helpers
"""
import time
from typing import List, Optional, Type, TypeVar
from sqlalchemy.orm import Session, Query
from sqlalchemy.ext.declarative import DeclarativeMeta
from functools import wraps

T = TypeVar('T', bound=DeclarativeMeta)


class QueryOptimizer:
    """
    Database query optimizer with performance tracking
    """

    # Slow query threshold (milliseconds)
    SLOW_QUERY_THRESHOLD_MS = 100

    @staticmethod
    def execute_with_timing(query: Query, operation_name: str = "query") -> tuple:
        """
        Execute query and measure execution time

        Returns:
            tuple: (results, execution_time_ms)
        """
        start_time = time.time()
        results = query.all()
        elapsed_ms = (time.time() - start_time) * 1000

        # Log slow queries
        if elapsed_ms > QueryOptimizer.SLOW_QUERY_THRESHOLD_MS:
            print(f"[QueryOptimizer] ⚠️ SLOW QUERY: {operation_name} took {elapsed_ms:.2f}ms")
            print(f"[QueryOptimizer] Query: {query.statement}")
        else:
            print(f"[QueryOptimizer] ✅ {operation_name}: {elapsed_ms:.2f}ms")

        return results, elapsed_ms

    @staticmethod
    def paginate(
        query: Query,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100
    ) -> dict:
        """
        Paginate query results efficiently

        Args:
            query: SQLAlchemy query
            page: Page number (1-indexed)
            page_size: Items per page
            max_page_size: Maximum allowed page size

        Returns:
            dict with:
            - items: List of results
            - total: Total item count
            - page: Current page
            - page_size: Items per page
            - total_pages: Total page count
            - has_next: Whether there's a next page
            - has_prev: Whether there's a previous page
        """
        # Enforce page size limits
        page_size = min(page_size, max_page_size)
        page = max(page, 1)

        # Count total items (optimize by using count query)
        start_time = time.time()
        total = query.count()
        count_time_ms = (time.time() - start_time) * 1000

        # Calculate pagination
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        # Fetch page items
        start_time = time.time()
        items = query.limit(page_size).offset(offset).all()
        fetch_time_ms = (time.time() - start_time) * 1000

        total_time_ms = count_time_ms + fetch_time_ms

        if total_time_ms > QueryOptimizer.SLOW_QUERY_THRESHOLD_MS:
            print(f"[QueryOptimizer] ⚠️ SLOW PAGINATION: {total_time_ms:.2f}ms "
                  f"(count: {count_time_ms:.2f}ms, fetch: {fetch_time_ms:.2f}ms)")

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
        }

    @staticmethod
    def optimize_select_fields(
        query: Query,
        model: Type[T],
        fields: Optional[List[str]] = None
    ) -> Query:
        """
        Optimize query to select only specific fields

        Args:
            query: SQLAlchemy query
            model: Model class
            fields: List of field names to select (None = select all)

        Returns:
            Optimized query
        """
        if fields is None:
            return query

        # Build list of column objects
        columns = [getattr(model, field) for field in fields if hasattr(model, field)]

        if columns:
            return query.with_entities(*columns)

        return query

    @staticmethod
    def batch_fetch(
        db: Session,
        model: Type[T],
        ids: List[int],
        batch_size: int = 100
    ) -> List[T]:
        """
        Fetch multiple records by ID in batches

        More efficient than individual queries when fetching many records.

        Args:
            db: Database session
            model: Model class
            ids: List of IDs to fetch
            batch_size: Number of IDs per batch

        Returns:
            List of model instances
        """
        if not ids:
            return []

        results = []

        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]

            start_time = time.time()
            batch_results = db.query(model).filter(model.id.in_(batch_ids)).all()
            elapsed_ms = (time.time() - start_time) * 1000

            print(f"[QueryOptimizer] Batch fetch: {len(batch_results)} items in {elapsed_ms:.2f}ms")
            results.extend(batch_results)

        return results


def track_query_performance(operation_name: str):
    """
    Decorator to track query performance

    Usage:
    @track_query_performance("get_user_conversations")
    def get_user_conversations(db, user_id):
        return db.query(Conversation).filter(...).all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_ms = (time.time() - start_time) * 1000

            if elapsed_ms > QueryOptimizer.SLOW_QUERY_THRESHOLD_MS:
                print(f"[QueryPerf] ⚠️ SLOW: {operation_name} took {elapsed_ms:.2f}ms")
            else:
                print(f"[QueryPerf] ✅ {operation_name}: {elapsed_ms:.2f}ms")

            return result
        return wrapper
    return decorator


class OptimizedPagination:
    """
    Reusable pagination helper for consistent pagination across endpoints
    """

    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    @classmethod
    def paginate_query(
        cls,
        query: Query,
        page: int,
        page_size: Optional[int] = None
    ) -> dict:
        """
        Paginate a query with standard settings

        Returns standard pagination response format
        """
        page_size = page_size or cls.DEFAULT_PAGE_SIZE
        return QueryOptimizer.paginate(
            query=query,
            page=page,
            page_size=page_size,
            max_page_size=cls.MAX_PAGE_SIZE
        )


# ==================== Index Suggestions ====================

INDEX_SUGGESTIONS = """
Performance Optimization - Recommended Database Indexes
========================================================

Story 9.1: Based on common query patterns, add these indexes:

1. Conversations Table:
   CREATE INDEX idx_conversations_user_id ON conversations(user_id);
   CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
   CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);

2. Messages Table:
   CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
   CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
   CREATE INDEX idx_messages_conv_created ON messages(conversation_id, created_at DESC);

3. Memories Table:
   CREATE INDEX idx_memories_user_id ON memories(user_id);
   CREATE INDEX idx_memories_created_at ON memories(created_at DESC);

4. Intimacy Table:
   CREATE INDEX idx_intimacy_user_idol ON intimacy(user_id, idol_id);

5. Achievements Table:
   CREATE INDEX idx_achievements_user_id ON user_achievements(user_id);
   CREATE INDEX idx_achievements_unlocked ON user_achievements(unlocked_at DESC);

6. Devices Table:
   CREATE INDEX idx_devices_user_id ON user_devices(user_id);
   CREATE INDEX idx_devices_last_login ON user_devices(last_login_at DESC);

These indexes will significantly improve query performance for:
- Fetching user's conversations
- Loading conversation messages
- Querying user memories
- Checking intimacy levels
- Displaying achievements
- Device management

Run these indexes in a new migration file.
"""
