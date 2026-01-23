"""
Deepseek AI Provider Implementation
Chinese commercial AI API service
"""
import httpx
from typing import List, Dict, Any, Optional

from app.services.ai.ai_provider import AIProvider


class DeepseekProvider(AIProvider):
    """
    Deepseek provider for commercial AI API

    Configuration required:
    - api_key: Deepseek API key
    - model: Model name (default: deepseek-chat)
    - base_url: API endpoint (default: https://api.deepseek.com)

    Pricing: ~¥0.001 per 1K tokens
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Deepseek Provider

        Args:
            config: Required config with:
                - api_key: Deepseek API key
                - model: Model name (default: deepseek-chat)
                - base_url: API URL (default: https://api.deepseek.com)
                - timeout: Request timeout (default: 30)
        """
        super().__init__(config)
        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise ValueError("Deepseek API key is required")

        self.base_url = self.config.get("base_url", "https://api.deepseek.com")
        self.model = self.config.get("model", "deepseek-chat")
        self.timeout = self.config.get("timeout", 30)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.8,
        max_tokens: int = 500
    ) -> str:
        """
        Generate response using Deepseek API

        Args:
            messages: Conversation history with role and content
            temperature: Response randomness (0.0-1.0)
            max_tokens: Maximum response length

        Returns:
            Generated response text

        Raises:
            Exception: If API call fails or times out
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": False
                    }
                )

                if response.status_code != 200:
                    raise Exception(f"Deepseek API error: {response.status_code} - {response.text}")

                result = response.json()
                if "choices" not in result or len(result["choices"]) == 0:
                    raise Exception("Deepseek API returned no choices")

                message_content = result["choices"][0]["message"]["content"]
                return message_content.strip()

        except httpx.TimeoutException:
            raise Exception(f"Deepseek API timeout after {self.timeout}s")
        except Exception as e:
            raise Exception(f"Deepseek generation failed: {str(e)}")

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "deepseek"
