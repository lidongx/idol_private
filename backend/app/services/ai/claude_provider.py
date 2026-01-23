"""
Claude AI Provider Implementation
Anthropic's Claude API service
"""
import httpx
from typing import List, Dict, Any, Optional

from app.services.ai.ai_provider import AIProvider


class ClaudeProvider(AIProvider):
    """
    Claude provider for Anthropic's AI API

    Configuration required:
    - api_key: Anthropic API key
    - model: Model name (default: claude-3-5-sonnet-20241022)
    - base_url: API endpoint (default: https://api.anthropic.com)

    Pricing: Variable by model tier
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Claude Provider

        Args:
            config: Required config with:
                - api_key: Anthropic API key
                - model: Model name (default: claude-3-5-sonnet-20241022)
                - base_url: API URL (default: https://api.anthropic.com)
                - timeout: Request timeout (default: 30)
        """
        super().__init__(config)
        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise ValueError("Claude API key is required")

        self.base_url = self.config.get("base_url", "https://api.anthropic.com")
        self.model = self.config.get("model", "claude-3-5-sonnet-20241022")
        self.timeout = self.config.get("timeout", 30)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.8,
        max_tokens: int = 500
    ) -> str:
        """
        Generate response using Claude API

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
            # Extract system message if present
            system_message = None
            conversation_messages = []

            for msg in messages:
                if msg.get("role") == "system":
                    system_message = msg.get("content", "")
                else:
                    conversation_messages.append(msg)

            # Build request
            request_body = {
                "model": self.model,
                "messages": conversation_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            if system_message:
                request_body["system"] = system_message

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json=request_body
                )

                if response.status_code != 200:
                    raise Exception(f"Claude API error: {response.status_code} - {response.text}")

                result = response.json()
                if "content" not in result or len(result["content"]) == 0:
                    raise Exception("Claude API returned no content")

                # Extract text from first content block
                first_content = result["content"][0]
                if first_content.get("type") == "text":
                    return first_content.get("text", "").strip()
                else:
                    raise Exception(f"Unexpected content type: {first_content.get('type')}")

        except httpx.TimeoutException:
            raise Exception(f"Claude API timeout after {self.timeout}s")
        except Exception as e:
            raise Exception(f"Claude generation failed: {str(e)}")

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "claude"
