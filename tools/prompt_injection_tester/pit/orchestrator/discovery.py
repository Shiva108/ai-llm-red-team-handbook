"""
Auto-discovery functionality for LLM endpoints.

Provides smart detection of models and API capabilities.
"""

from typing import Optional
from urllib.parse import urlparse

# Handle optional imports
try:
    import aiohttp
except ImportError:
    aiohttp = None  # type: ignore


class AutoDiscovery:
    """
    Auto-discovery for LLM endpoints.

    Attempts to detect model identifiers and API capabilities.
    """

    def __init__(self, target_url: str):
        """
        Initialize auto-discovery.

        Args:
            target_url: Target API endpoint URL
        """
        self.target_url = target_url
        self.parsed_url = urlparse(target_url)

    async def discover_model(self, hint: Optional[str] = None) -> str:
        """
        Discover the model identifier.

        Args:
            hint: Optional model hint from user

        Returns:
            Discovered or default model identifier
        """
        if hint:
            return hint

        # Try to discover from endpoint
        discovered = await self._probe_for_model()
        if discovered:
            return discovered

        # Default models based on port/URL
        return self._guess_model_from_url()

    async def _probe_for_model(self) -> Optional[str]:
        """
        Probe the endpoint for model information.

        Returns:
            Model identifier if discovered, None otherwise
        """
        if not aiohttp:
            return None

        try:
            # Try Ollama tags endpoint
            if "11434" in self.target_url:
                tags_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}/api/tags"
                async with aiohttp.ClientSession() as session:
                    async with session.get(tags_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if "models" in data and len(data["models"]) > 0:
                                return data["models"][0].get("name", "")
        except Exception:
            pass

        return None

    def _guess_model_from_url(self) -> str:
        """
        Guess model based on URL patterns.

        Returns:
            Best guess for model identifier
        """
        url_lower = self.target_url.lower()

        # Ollama default
        if "11434" in url_lower or "ollama" in url_lower:
            return "llama3:latest"

        # OpenAI
        if "openai" in url_lower or "api.openai.com" in url_lower:
            return "gpt-4"

        # Anthropic
        if "anthropic" in url_lower or "claude" in url_lower:
            return "claude-3-5-sonnet-20241022"

        # LocalAI
        if "8080" in url_lower or "localai" in url_lower:
            return "gpt-3.5-turbo"

        # Default
        return "gpt-3.5-turbo"

    async def discover_capabilities(self) -> dict:
        """
        Discover API capabilities.

        Returns:
            Dictionary of discovered capabilities
        """
        capabilities = {
            "streaming": False,
            "tool_use": False,
            "vision": False,
            "embeddings": False,
        }

        # This could be expanded with actual probing
        return capabilities
