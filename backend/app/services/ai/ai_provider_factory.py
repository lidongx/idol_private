"""
AI Provider Factory
Creates AI provider instances based on configuration using Factory Pattern
"""
from typing import Optional, Dict, Any

from app.services.ai.ai_provider import AIProvider
from app.services.ai.ollama_provider import OllamaProvider
from app.services.ai.deepseek_provider import DeepseekProvider
from app.services.ai.claude_provider import ClaudeProvider
from app.config import settings


class AIProviderFactory:
    """
    Factory for creating AI provider instances

    Supports:
    - ollama: Local Ollama service
    - deepseek: Deepseek commercial API
    - claude: Anthropic Claude API
    """

    # Registry of available providers
    _providers = {
        "ollama": OllamaProvider,
        "deepseek": DeepseekProvider,
        "claude": ClaudeProvider,
    }

    @classmethod
    def get_provider(
        cls,
        provider_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> AIProvider:
        """
        Get AI provider instance

        Args:
            provider_name: Provider name (ollama/deepseek/claude)
                          If None, uses AI_PROVIDER from settings
            config: Optional provider-specific configuration
                   If None, uses default configuration from settings

        Returns:
            AIProvider instance

        Raises:
            ValueError: If provider name is invalid or not supported
        """
        # Use configured provider if not specified
        if provider_name is None:
            provider_name = settings.AI_PROVIDER

        # Normalize provider name
        provider_name = provider_name.lower().strip()

        # Check if provider is supported
        if provider_name not in cls._providers:
            raise ValueError(
                f"Unsupported AI provider: {provider_name}. "
                f"Supported providers: {', '.join(cls._providers.keys())}"
            )

        # Get provider config if not provided
        if config is None:
            config = cls._get_default_config(provider_name)

        # Create and return provider instance
        provider_class = cls._providers[provider_name]
        return provider_class(config)

    @classmethod
    def _get_default_config(cls, provider_name: str) -> Dict[str, Any]:
        """
        Get default configuration for provider from settings

        Args:
            provider_name: Provider name

        Returns:
            Configuration dictionary
        """
        if provider_name == "ollama":
            return {
                "base_url": getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434"),
                "model": getattr(settings, "OLLAMA_MODEL", "qwen2:7b"),
                "timeout": 30
            }
        elif provider_name == "deepseek":
            return {
                "api_key": getattr(settings, "DEEPSEEK_API_KEY", None),
                "model": getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat"),
                "base_url": "https://api.deepseek.com",
                "timeout": 30
            }
        elif provider_name == "claude":
            return {
                "api_key": getattr(settings, "CLAUDE_API_KEY", None),
                "model": getattr(settings, "CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
                "base_url": "https://api.anthropic.com",
                "timeout": 30
            }
        else:
            return {}

    @classmethod
    def list_providers(cls) -> list:
        """
        Get list of supported provider names

        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
