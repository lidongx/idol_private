"""
Authentication Service
Handles login attempt tracking and account locking
"""
import redis
from app.config import settings

# Initialize Redis client
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# Login attempt limits
MAX_LOGIN_ATTEMPTS = 5
LOCK_DURATION = 1800  # 30 minutes in seconds


def check_account_locked(phone: str) -> bool:
    """
    Check if an account is locked due to too many failed login attempts

    Args:
        phone: User's phone number

    Returns:
        True if account is locked, False otherwise
    """
    try:
        key = f"auth:locked:{phone}"
        return redis_client.exists(key) > 0
    except Exception as e:
        print(f"Error checking account lock: {e}")
        return False


def get_login_attempts(phone: str) -> int:
    """
    Get the number of failed login attempts for a phone number

    Args:
        phone: User's phone number

    Returns:
        Number of failed attempts
    """
    try:
        key = f"auth:attempts:{phone}"
        attempts = redis_client.get(key)
        return int(attempts) if attempts else 0
    except Exception as e:
        print(f"Error getting login attempts: {e}")
        return 0


def increment_login_attempts(phone: str) -> int:
    """
    Increment failed login attempts counter

    Args:
        phone: User's phone number

    Returns:
        New attempt count
    """
    try:
        key = f"auth:attempts:{phone}"
        attempts = redis_client.incr(key)

        # Set expiry on first attempt (30 minutes)
        if attempts == 1:
            redis_client.expire(key, LOCK_DURATION)

        # Lock account if max attempts reached
        if attempts >= MAX_LOGIN_ATTEMPTS:
            lock_key = f"auth:locked:{phone}"
            redis_client.setex(lock_key, LOCK_DURATION, "1")

        return attempts
    except Exception as e:
        print(f"Error incrementing login attempts: {e}")
        return 0


def clear_login_attempts(phone: str) -> bool:
    """
    Clear failed login attempts after successful login

    Args:
        phone: User's phone number

    Returns:
        True if cleared successfully
    """
    try:
        attempt_key = f"auth:attempts:{phone}"
        lock_key = f"auth:locked:{phone}"
        redis_client.delete(attempt_key, lock_key)
        return True
    except Exception as e:
        print(f"Error clearing login attempts: {e}")
        return False


def get_remaining_attempts(phone: str) -> int:
    """
    Get remaining login attempts before account lock

    Args:
        phone: User's phone number

    Returns:
        Number of remaining attempts (0 if locked)
    """
    if check_account_locked(phone):
        return 0

    attempts = get_login_attempts(phone)
    remaining = MAX_LOGIN_ATTEMPTS - attempts
    return max(0, remaining)


def get_lock_time_remaining(phone: str) -> int:
    """
    Get remaining time until account is unlocked (in seconds)

    Args:
        phone: User's phone number

    Returns:
        Seconds until unlock, 0 if not locked
    """
    try:
        key = f"auth:locked:{phone}"
        ttl = redis_client.ttl(key)
        return ttl if ttl > 0 else 0
    except Exception as e:
        print(f"Error getting lock time: {e}")
        return 0
