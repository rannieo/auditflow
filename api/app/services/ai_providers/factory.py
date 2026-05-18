"""Pick an AI provider from current Settings."""

import httpx

from app.config import Settings

from . import AiProvider
from .mock_provider import MockProvider


def get_provider(
    settings: Settings, *, http_client_factory=None
) -> AiProvider:
    """Return the provider matching ``settings.ai_provider``.

    ``http_client_factory`` is a hook for tests to inject an httpx client
    with a MockTransport. Production code passes ``None`` and the provider
    builds its own client.
    """
    if settings.ai_provider == "ollama":
        from .ollama_provider import OllamaProvider

        return OllamaProvider(
            api_key=settings.ollama_api_key,
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout=settings.ollama_timeout_seconds,
            http_client_factory=http_client_factory,
        )
    return MockProvider()


# httpx is re-exported so route/test code can build MockTransports without
# importing httpx itself in two places.
__all__ = ["get_provider", "httpx"]
