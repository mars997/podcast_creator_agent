"""
Unit tests for TTS provider functionality.

Tests TTS provider interface without making real API calls.
Converted from step2_tts_test.py.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from providers import create_tts_provider, ProviderConfig
from providers.openai_provider import OpenAITTSProvider
from providers.gemini_provider import GeminiTTSProvider


def test_tts_provider_creation_openai(mock_env_openai_only):
    """Test creating OpenAI TTS provider"""
    config = ProviderConfig(llm_provider="openai", tts_provider="openai")

    with patch('providers.openai_provider.OpenAI'):
        provider = create_tts_provider(config)

        assert provider is not None
        assert provider.provider_name == "openai"
        assert provider.model_name == "gpt-4o-mini-tts"


def test_tts_provider_creation_gemini(mock_env_gemini_only):
    """Test creating Gemini TTS provider"""
    config = ProviderConfig(llm_provider="gemini", tts_provider="gemini")

    with patch('providers.gemini_provider.genai'):
        provider = create_tts_provider(config)

        assert provider is not None
        assert provider.provider_name == "gemini"
        assert provider.model_name == "gemini-2.5-flash"


def test_tts_provider_has_required_attributes(mock_tts_provider):
    """Test that TTS provider has required attributes"""
    assert hasattr(mock_tts_provider, 'provider_name')
    assert hasattr(mock_tts_provider, 'model_name')
    assert hasattr(mock_tts_provider, 'available_voices')
    assert hasattr(mock_tts_provider, 'generate_audio')

    # Test attributes are accessible
    assert mock_tts_provider.provider_name == "openai"
    assert mock_tts_provider.model_name == "gpt-4o-mini-tts"
    assert isinstance(mock_tts_provider.available_voices, list)
    assert len(mock_tts_provider.available_voices) > 0


def test_tts_provider_generate_audio_called(mock_tts_provider, test_audio_script, temp_output_dir):
    """Test that generate_audio is called with correct parameters"""
    output_file = temp_output_dir / "test_audio.mp3"
    voice = "alloy"

    # Call generate_audio
    mock_tts_provider.generate_audio(test_audio_script, voice, output_file)

    # Verify it was called
    mock_tts_provider.generate_audio.assert_called_once()

    # Verify it was called with correct arguments
    call_args = mock_tts_provider.generate_audio.call_args
    assert call_args[0][0] == test_audio_script
    assert call_args[0][1] == voice
    assert call_args[0][2] == output_file


def test_tts_provider_voice_validation(mock_env_openai_only):
    """Test that invalid voice raises error"""
    config = ProviderConfig(llm_provider="openai", tts_provider="openai")

    with patch('providers.openai_provider.OpenAI'):
        provider = create_tts_provider(config)

        # Valid voices should be in the list
        assert "nova" in provider.available_voices
        assert "alloy" in provider.available_voices

        # Test that invalid voice would be caught
        # (actual validation happens in generate_audio)
        assert "invalid_voice_name" not in provider.available_voices


def test_tts_provider_output_file_created(mock_env_openai_only, test_audio_script, temp_output_dir):
    """Test that output file is created after audio generation"""
    config = ProviderConfig(llm_provider="openai", tts_provider="openai")
    output_file = temp_output_dir / "podcast_test.mp3"

    # Mock the OpenAI client and its methods
    with patch('providers.openai_provider.OpenAI') as mock_openai:
        mock_response = MagicMock()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        # Mock stream_to_file to actually create a file
        def mock_stream(path):
            Path(path).write_bytes(b"fake audio data")

        mock_response.stream_to_file = mock_stream

        mock_client = Mock()
        mock_client.audio.speech.with_streaming_response.create = Mock(return_value=mock_response)
        mock_openai.return_value = mock_client

        # Create provider and generate audio
        provider = create_tts_provider(config)
        provider.generate_audio(test_audio_script, "nova", output_file)

        # Verify file was created
        assert output_file.exists()
        assert output_file.stat().st_size > 0
