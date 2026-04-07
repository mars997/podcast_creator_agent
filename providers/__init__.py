"""
Provider abstraction layer for podcast creator.

Supports multiple LLM and TTS providers including OpenAI and Google Gemini.
"""

from .base import BaseLLMProvider, BaseTTSProvider
from .factory import (
    ProviderConfig,
    create_llm_provider,
    create_tts_provider,
    get_default_config,
    detect_available_providers,
)

__all__ = [
    "BaseLLMProvider",
    "BaseTTSProvider",
    "ProviderConfig",
    "create_llm_provider",
    "create_tts_provider",
    "get_default_config",
    "detect_available_providers",
]
