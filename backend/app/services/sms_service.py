"""
SMS Verification Code Service
Handles verification code generation, storage in Redis, and sending
"""
import random
from typing import Optional
import redis

from app.config import settings

# Initialize Redis client
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def generate_verification_code() -> str:
    """
    Generate a 6-digit verification code

    Returns:
        6-digit numeric code as string
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def store_verification_code(phone: str, code: str, ttl: int = 300) -> bool:
    """
    Store verification code in Redis with TTL

    Args:
        phone: User's phone number
        code: 6-digit verification code
        ttl: Time to live in seconds (default: 300s = 5 minutes)

    Returns:
        True if stored successfully
    """
    try:
        key = f"sms:verify:{phone}"
        redis_client.setex(key, ttl, code)
        return True
    except Exception as e:
        print(f"Error storing verification code: {e}")
        return False


def verify_verification_code(phone: str, input_code: str) -> bool:
    """
    Verify if the input code matches the stored code in Redis

    Args:
        phone: User's phone number
        input_code: Code entered by user

    Returns:
        True if code matches and hasn't expired, False otherwise
    """
    try:
        key = f"sms:verify:{phone}"
        stored_code = redis_client.get(key)

        if stored_code is None:
            return False  # Code expired or doesn't exist

        # Delete the code after verification (one-time use)
        if stored_code == input_code:
            redis_client.delete(key)
            return True

        return False
    except Exception as e:
        print(f"Error verifying code: {e}")
        return False


def can_resend_code(phone: str) -> bool:
    """
    Check if user can resend verification code (rate limiting)

    Args:
        phone: User's phone number

    Returns:
        True if user can resend, False if still in cooldown period
    """
    try:
        key = f"sms:ratelimit:{phone}"
        return redis_client.get(key) is None
    except Exception as e:
        print(f"Error checking rate limit: {e}")
        return True  # Allow resend if error occurs


def set_resend_limit(phone: str, cooldown: int = 60) -> bool:
    """
    Set resend rate limit for a phone number

    Args:
        phone: User's phone number
        cooldown: Cooldown period in seconds (default: 60s)

    Returns:
        True if rate limit set successfully
    """
    try:
        key = f"sms:ratelimit:{phone}"
        redis_client.setex(key, cooldown, "1")
        return True
    except Exception as e:
        print(f"Error setting rate limit: {e}")
        return False


def send_sms_code(phone: str, code: str) -> bool:
    """
    Send SMS verification code to phone number
    MVP Stage: Console output only
    Production: Integrate with Aliyun SMS service

    Args:
        phone: User's phone number
        code: Verification code to send

    Returns:
        True if sent successfully
    """
    if settings.SMS_PROVIDER == "console":
        # MVP: Print to console instead of sending real SMS
        print(f"\n{'='*50}")
        print(f"[SMS] 发送验证码到手机号: {phone}")
        print(f"[SMS] 验证码: {code}")
        print(f"[SMS] 有效期: 5分钟")
        print(f"{'='*50}\n")
        return True

    elif settings.SMS_PROVIDER == "aliyun":
        # TODO: Implement Aliyun SMS API integration
        # from aliyunsdkcore.client import AcsClient
        # from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
        # ... Aliyun SMS implementation ...
        raise NotImplementedError("Aliyun SMS integration not implemented yet")

    else:
        raise ValueError(f"Unknown SMS provider: {settings.SMS_PROVIDER}")


# Password Reset Functions

def store_password_reset_code(phone: str, code: str, ttl: int = 600) -> bool:
    """
    Store password reset verification code in Redis

    Args:
        phone: User's phone number
        code: 6-digit verification code
        ttl: Time to live in seconds (default: 600s = 10 minutes)

    Returns:
        True if stored successfully
    """
    try:
        key = f"pwd:reset:{phone}"
        redis_client.setex(key, ttl, code)
        return True
    except Exception as e:
        print(f"Error storing password reset code: {e}")
        return False


def verify_password_reset_code(phone: str, input_code: str) -> bool:
    """
    Verify password reset code from Redis

    Args:
        phone: User's phone number
        input_code: Code entered by user

    Returns:
        True if code matches and hasn't expired, False otherwise
    """
    try:
        key = f"pwd:reset:{phone}"
        stored_code = redis_client.get(key)

        if stored_code is None:
            return False  # Code expired or doesn't exist

        # Delete the code after verification (one-time use)
        if stored_code == input_code:
            redis_client.delete(key)
            return True

        return False
    except Exception as e:
        print(f"Error verifying password reset code: {e}")
        return False
