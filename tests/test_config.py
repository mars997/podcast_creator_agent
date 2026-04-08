"""
Tests for the config module.
"""

import pytest
import config


def test_config_has_required_constants():
    """Test that config module has all required constants"""
    assert hasattr(config, "DEFAULT_PROVIDER")
    assert hasattr(config, "PROVIDER_MODELS")
    assert hasattr(config, "DEFAULT_TONE")
    assert hasattr(config, "DEFAULT_LENGTH")
    assert hasattr(config, "OUTPUT_ROOT")
    assert hasattr(config, "VALID_TONES")
    assert hasattr(config, "VALID_LENGTHS")
    assert hasattr(config, "WORD_RANGES")


def test_provider_models_structure():
    """Test that PROVIDER_MODELS has expected structure"""
    assert "openai" in config.PROVIDER_MODELS
    assert "gemini" in config.PROVIDER_MODELS

    # Check OpenAI config
    openai_config = config.PROVIDER_MODELS["openai"]
    assert "llm_model" in openai_config
    assert "tts_model" in openai_config
    assert "api_key_env" in openai_config
    assert "voices" in openai_config
    assert "default_voice" in openai_config

    # Check Gemini config
    gemini_config = config.PROVIDER_MODELS["gemini"]
    assert "llm_model" in gemini_config
    assert "api_key_env" in gemini_config


def test_valid_tones():
    """Test that valid tones are defined correctly"""
    assert isinstance(config.VALID_TONES, set)
    assert "casual" in config.VALID_TONES
    assert "professional" in config.VALID_TONES
    assert "educational" in config.VALID_TONES


def test_valid_lengths():
    """Test that valid lengths are defined correctly"""
    assert isinstance(config.VALID_LENGTHS, set)
    assert "short" in config.VALID_LENGTHS
    assert "medium" in config.VALID_LENGTHS
    assert "long" in config.VALID_LENGTHS


def test_word_ranges():
    """Test that word ranges are defined for all lengths"""
    assert "short" in config.WORD_RANGES
    assert "medium" in config.WORD_RANGES
    assert "long" in config.WORD_RANGES


def test_get_word_range_function():
    """Test the get_word_range function"""
    assert config.get_word_range("short") == "300 to 450 words"
    assert config.get_word_range("medium") == "500 to 700 words"
    assert config.get_word_range("long") == "800 to 1100 words"

    # Test case insensitivity
    assert config.get_word_range("SHORT") == "300 to 450 words"
    assert config.get_word_range("Medium") == "500 to 700 words"

    # Test default fallback
    assert config.get_word_range("invalid") == "500 to 700 words"


def test_default_provider():
    """Test that default provider is OpenAI for backward compatibility"""
    assert config.DEFAULT_PROVIDER == "openai"


def test_output_root():
    """Test that output root is defined"""
    assert config.OUTPUT_ROOT == "output"
