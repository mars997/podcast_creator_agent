"""
High-level tests for the provider abstraction system.
"""

import pytest
from providers import (
    BaseLLMProvider,
    BaseTTSProvider,
    ProviderConfig,
    detect_available_providers,
)


def test_provider_config_creation():
    """Test ProviderConfig dataclass creation"""
    config = ProviderConfig(
        llm_provider="openai",
        tts_provider="openai",
        llm_model="gpt-4.1-mini",
        tts_model="gpt-4o-mini-tts"
    )

    assert config.llm_provider == "openai"
    assert config.tts_provider == "openai"
    assert config.llm_model == "gpt-4.1-mini"
    assert config.tts_model == "gpt-4o-mini-tts"


def test_provider_config_optional_models():
    """Test ProviderConfig with optional model parameters"""
    config = ProviderConfig(
        llm_provider="gemini",
        tts_provider="openai"
    )

    assert config.llm_provider == "gemini"
    assert config.tts_provider == "openai"
    assert config.llm_model is None
    assert config.tts_model is None


def test_detect_available_providers_with_no_keys(mock_env_no_providers):
    """Test provider detection with no API keys"""
    available = detect_available_providers()
    assert available == {}


def test_detect_available_providers_with_openai(mock_env_openai_only):
    """Test provider detection with only OpenAI key"""
    available = detect_available_providers()
    assert "openai" in available
    assert "gemini" not in available


def test_detect_available_providers_with_gemini(mock_env_gemini_only):
    """Test provider detection with only Gemini key"""
    available = detect_available_providers()
    assert "gemini" in available
    assert "openai" not in available


def test_detect_available_providers_with_both(mock_env_both_providers):
    """Test provider detection with both API keys"""
    available = detect_available_providers()
    assert "openai" in available
    assert "gemini" in available


def test_base_llm_provider_is_abstract():
    """Test that BaseLLMProvider cannot be instantiated"""
    with pytest.raises(TypeError):
        BaseLLMProvider()


def test_base_tts_provider_is_abstract():
    """Test that BaseTTSProvider cannot be instantiated"""
    with pytest.raises(TypeError):
        BaseTTSProvider()


def test_base_llm_provider_has_required_methods():
    """Test that BaseLLMProvider defines required abstract methods"""
    required_methods = ["generate_text", "model_name", "provider_name"]

    for method in required_methods:
        assert hasattr(BaseLLMProvider, method)


def test_base_tts_provider_has_required_methods():
    """Test that BaseTTSProvider defines required abstract methods"""
    required_methods = ["generate_audio", "available_voices", "model_name", "provider_name"]

    for method in required_methods:
        assert hasattr(BaseTTSProvider, method)
