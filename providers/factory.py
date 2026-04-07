"""
Provider factory for instantiating LLM and TTS providers.

Includes smart fallback logic and provider detection.
"""

import os
from dataclasses import dataclass
from typing import Optional

from .base import BaseLLMProvider, BaseTTSProvider
from .gemini_provider import GeminiLLMProvider, GeminiTTSProvider
from .openai_provider import OpenAILLMProvider, OpenAITTSProvider


@dataclass
class ProviderConfig:
    """Configuration for provider selection"""

    llm_provider: str  # "openai" or "gemini"
    tts_provider: str  # "openai" or "gemini"
    llm_model: Optional[str] = None
    tts_model: Optional[str] = None


def detect_available_providers() -> dict:
    """
    Detect which providers have valid API keys.

    Returns:
        dict: Dictionary with provider names as keys and True as values
              Example: {"openai": True, "gemini": True}
    """
    available = {}

    if os.getenv("OPENAI_API_KEY"):
        available["openai"] = True

    if os.getenv("GOOGLE_API_KEY"):
        available["gemini"] = True

    return available


def create_llm_provider(config: ProviderConfig) -> BaseLLMProvider:
    """
    Factory function to create LLM provider.

    Args:
        config: ProviderConfig with llm_provider and optional llm_model

    Returns:
        BaseLLMProvider: Configured LLM provider instance

    Raises:
        ValueError: If provider is unknown
    """
    if config.llm_provider == "openai":
        return OpenAILLMProvider(model=config.llm_model or "gpt-4.1-mini")
    elif config.llm_provider == "gemini":
        return GeminiLLMProvider(model=config.llm_model or "gemini-1.5-flash")
    else:
        raise ValueError(
            f"Unknown LLM provider: {config.llm_provider}\n"
            f"Supported providers: openai, gemini"
        )


def create_tts_provider(config: ProviderConfig) -> BaseTTSProvider:
    """
    Factory function to create TTS provider.

    Args:
        config: ProviderConfig with tts_provider and optional tts_model

    Returns:
        BaseTTSProvider: Configured TTS provider instance

    Raises:
        ValueError: If provider is unknown
    """
    if config.tts_provider == "openai":
        return OpenAITTSProvider(model=config.tts_model or "gpt-4o-mini-tts")
    elif config.tts_provider == "gemini":
        return GeminiTTSProvider(model=config.tts_model or "gemini-2.5-flash")
    else:
        raise ValueError(
            f"Unknown TTS provider: {config.tts_provider}\n"
            f"Supported providers: openai, gemini"
        )


def get_default_config() -> ProviderConfig:
    """
    Get default provider config with smart fallback.

    Behavior:
    - Checks environment variables for preferred providers
    - Falls back to available providers if preferred not available
    - Defaults to OpenAI for backward compatibility
    - Raises clear error if no API keys found

    Returns:
        ProviderConfig: Configuration with selected providers

    Raises:
        ValueError: If no API keys are available
    """
    available = detect_available_providers()

    if not available:
        raise ValueError(
            "No API keys found. Please set at least one of:\n"
            "  - OPENAI_API_KEY for OpenAI (get from: https://platform.openai.com/api-keys)\n"
            "  - GOOGLE_API_KEY for Gemini (get from: https://makersuite.google.com/app/apikey)\n\n"
            "Add the key to your .env file."
        )

    # Default to OpenAI for backward compatibility
    llm_provider = os.getenv("PODCAST_LLM_PROVIDER", "openai")
    tts_provider = os.getenv("PODCAST_TTS_PROVIDER", "openai")

    # Fallback if preferred not available
    if llm_provider not in available:
        llm_provider = list(available.keys())[0]
        print(
            f"⚠️  Preferred LLM provider not available, using {llm_provider.upper()}"
        )

    if tts_provider not in available:
        tts_provider = list(available.keys())[0]
        print(
            f"⚠️  Preferred TTS provider not available, using {tts_provider.upper()}"
        )

    # If using Gemini TTS, warn about potential issues
    if tts_provider == "gemini":
        print(
            "ℹ️  Using Gemini TTS (experimental). If you encounter issues, "
            "set PODCAST_TTS_PROVIDER=openai in .env"
        )

    return ProviderConfig(
        llm_provider=llm_provider,
        tts_provider=tts_provider,
        llm_model=os.getenv("PODCAST_LLM_MODEL"),
        tts_model=os.getenv("PODCAST_TTS_MODEL"),
    )
