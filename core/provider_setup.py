"""
Provider initialization utilities for podcast creation.

This module centralizes the initialization of LLM and TTS providers,
loading environment variables and creating provider instances.
"""

from typing import Tuple, Dict
from dotenv import load_dotenv
from providers import get_default_config, create_llm_provider, create_tts_provider


def initialize_providers(verbose: bool = True) -> Tuple:
    """
    Initialize LLM and TTS providers with default configuration.

    Loads environment variables, gets default provider configuration,
    and creates LLM and TTS provider instances.

    Args:
        verbose: If True, prints provider information to console

    Returns:
        Tuple of (llm_provider, tts_provider)

    Examples:
        >>> llm, tts = initialize_providers()
        [Provider Info]
          LLM: OPENAI (gpt-4.1-mini)
          TTS: OPENAI (gpt-4o-mini-tts)
        >>> llm, tts = initialize_providers(verbose=False)
    """
    # Load environment variables
    load_dotenv()

    # Get provider configuration (auto-detects available providers)
    provider_config = get_default_config()

    # Create LLM and TTS providers
    llm_provider = create_llm_provider(provider_config)
    tts_provider = create_tts_provider(provider_config)

    # Display active providers if verbose
    if verbose:
        print(f"\n[Provider Info]")
        print(f"  LLM: {llm_provider.provider_name.upper()} ({llm_provider.model_name})")
        print(f"  TTS: {tts_provider.provider_name.upper()} ({tts_provider.model_name})")
        print()

    return llm_provider, tts_provider


def get_provider_info(llm_provider, tts_provider) -> Dict[str, Dict[str, str]]:
    """
    Get provider information as a dictionary.

    Args:
        llm_provider: The LLM provider instance
        tts_provider: The TTS provider instance

    Returns:
        Dictionary with 'llm' and 'tts' keys containing provider info

    Examples:
        >>> llm, tts = initialize_providers(verbose=False)
        >>> info = get_provider_info(llm, tts)
        >>> info['llm']['provider_name']
        'openai'
        >>> info['llm']['model_name']
        'gpt-4.1-mini'
    """
    return {
        "llm": {
            "provider_name": llm_provider.provider_name,
            "model_name": llm_provider.model_name,
        },
        "tts": {
            "provider_name": tts_provider.provider_name,
            "model_name": tts_provider.model_name,
            "available_voices": list(tts_provider.available_voices),
        }
    }
