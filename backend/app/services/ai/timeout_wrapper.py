"""
AI Provider Timeout Wrapper
Adds timeout handling to AI generation requests
"""
import asyncio
from typing import List, Dict
from app.services.ai.ai_provider import AIProvider
from app.core.exceptions import AITimeoutException


# Default AI generation timeout (30 seconds)
DEFAULT_AI_TIMEOUT = 30


async def generate_with_timeout(
    provider: AIProvider,
    messages: List[Dict[str, str]],
    temperature: float = 0.8,
    max_tokens: int = 500,
    timeout: int = DEFAULT_AI_TIMEOUT
) -> str:
    """
    Generate AI response with timeout protection

    Args:
        provider: AI provider instance
        messages: Conversation messages
        temperature: Generation temperature
        max_tokens: Maximum tokens
        timeout: Timeout in seconds (default 30)

    Returns:
        Generated response text

    Raises:
        AITimeoutException: If generation exceeds timeout
        Exception: If generation fails for other reasons
    """
    try:
        # Wrap AI generation with timeout
        response = await asyncio.wait_for(
            provider.generate_response(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            ),
            timeout=timeout
        )
        return response

    except asyncio.TimeoutError:
        # AI generation exceeded timeout
        provider_name = provider.get_provider_name()
        error_msg = f"{provider_name}思考时间有点长，请稍后重试~"
        raise AITimeoutException(message=error_msg)

    except Exception as e:
        # Re-raise other exceptions
        raise e


async def generate_with_retry(
    provider: AIProvider,
    messages: List[Dict[str, str]],
    temperature: float = 0.8,
    max_tokens: int = 500,
    timeout: int = DEFAULT_AI_TIMEOUT,
    max_retries: int = 1
) -> str:
    """
    Generate AI response with timeout and automatic retry

    Retries once on timeout, then raises exception

    Args:
        provider: AI provider instance
        messages: Conversation messages
        temperature: Generation temperature
        max_tokens: Maximum tokens
        timeout: Timeout in seconds (default 30)
        max_retries: Maximum retry attempts (default 1)

    Returns:
        Generated response text

    Raises:
        AITimeoutException: If all retries fail
        Exception: If generation fails for other reasons
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            response = await generate_with_timeout(
                provider=provider,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )
            return response

        except AITimeoutException as e:
            last_exception = e
            if attempt < max_retries:
                # Retry on timeout
                print(f"[AI Timeout] Retry attempt {attempt + 1}/{max_retries}")
                continue
            else:
                # Final retry failed
                raise e

        except Exception as e:
            # Don't retry on other errors
            raise e

    # Should not reach here, but just in case
    if last_exception:
        raise last_exception
    else:
        raise AITimeoutException()
