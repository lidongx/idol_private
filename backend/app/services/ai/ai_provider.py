"""
AI Provider Abstract Base Class
Defines interface for AI conversation providers using Strategy Pattern
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class AIProvider(ABC):
    """
    Abstract base class for AI providers

    Supports multiple AI backends: Ollama, Deepseek, Claude
    Implements Strategy Pattern for easy switching
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AI Provider

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.8,
        max_tokens: int = 500
    ) -> str:
        """
        Generate AI response from conversation messages

        Args:
            messages: List of message dicts with 'role' and 'content'
                      Example: [
                          {"role": "system", "content": "You are..."},
                          {"role": "user", "content": "Hello"},
                          {"role": "assistant", "content": "Hi!"}
                      ]
            temperature: Randomness (0.0-1.0). Higher = more creative
            max_tokens: Maximum tokens in response

        Returns:
            Generated response text

        Raises:
            Exception: If AI generation fails
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get provider name for logging and monitoring

        Returns:
            Provider name (e.g., "ollama", "deepseek", "claude")
        """
        pass

    async def health_check(self) -> bool:
        """
        Check if provider is available and healthy

        Returns:
            True if provider is available, False otherwise
        """
        try:
            # Simple test generation
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'OK'"}
            ]
            response = await self.generate_response(test_messages, temperature=0.1, max_tokens=10)
            return len(response) > 0
        except Exception as e:
            print(f"[{self.get_provider_name()}] Health check failed: {e}")
            return False
