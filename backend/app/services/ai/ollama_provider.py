"""
Ollama AI Provider Implementation
Local AI model service (default: Qwen 7B)
"""
import httpx
from typing import List, Dict, Any, Optional

from app.services.ai.ai_provider import AIProvider


class OllamaProvider(AIProvider):
    """
    Ollama provider for local AI models

    Default configuration:
    - Base URL: http://localhost:11434
    - Model: qwen2:7b (or configured model)
    - Timeout: 30 seconds
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Ollama Provider

        Args:
            config: Optional config with:
                - base_url: Ollama API URL (default: http://localhost:11434)
                - model: Model name (default: qwen2:7b)
                - timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        self.base_url = self.config.get("base_url", "http://localhost:11434")
        self.model = self.config.get("model", "qwen2:7b")
        self.timeout = self.config.get("timeout", 30)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.8,
        max_tokens: int = 500
    ) -> str:
        """
        Generate response using Ollama API

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
            # Build prompt from messages
            prompt = self._build_prompt(messages)

            # Call Ollama API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        }
                    }
                )

                if response.status_code != 200:
                    raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

                result = response.json()
                return result.get("response", "").strip()

        except httpx.TimeoutException:
            raise Exception(f"Ollama API timeout after {self.timeout}s")
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")

    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Build prompt string from message history

        Args:
            messages: List of message dicts

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "ollama"
