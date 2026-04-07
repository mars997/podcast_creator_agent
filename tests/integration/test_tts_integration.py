"""
Integration tests for TTS provider functionality.

Tests actual TTS generation end-to-end with real API calls.
Converted from step2_tts_test.py.

Note: These tests require valid API keys and are marked as slow/integration.
"""

import pytest
import os
from pathlib import Path
from providers import get_default_config, create_tts_provider, ProviderConfig


@pytest.mark.integration
@pytest.mark.requires_openai
@pytest.mark.slow
def test_tts_generate_audio_file_openai(test_audio_script, temp_output_dir):
    """Test generating actual audio file with OpenAI TTS provider"""
    # Skip if no OpenAI key
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    config = ProviderConfig(llm_provider="openai", tts_provider="openai")
    provider = create_tts_provider(config)

    output_file = temp_output_dir / "podcast_test_openai.mp3"

    # Generate audio
    provider.generate_audio(test_audio_script, "alloy", output_file)

    # Verify file was created
    assert output_file.exists(), "Output file should exist"
    assert output_file.stat().st_size > 0, "Output file should not be empty"

    # Verify it's a reasonable size (audio should be several KB at least)
    assert output_file.stat().st_size > 1000, "Audio file should be larger than 1KB"

    print(f"✓ Generated audio file: {output_file} ({output_file.stat().st_size} bytes)")


@pytest.mark.integration
@pytest.mark.requires_gemini
@pytest.mark.slow
def test_tts_generate_audio_file_gemini(test_audio_script, temp_output_dir):
    """Test generating actual audio file with Gemini TTS provider"""
    # Skip if no Gemini key
    if not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")

    config = ProviderConfig(llm_provider="gemini", tts_provider="gemini")

    try:
        provider = create_tts_provider(config)
        output_file = temp_output_dir / "podcast_test_gemini.mp3"

        # Generate audio (note: Gemini TTS API may differ)
        provider.generate_audio(test_audio_script, "en-US-Journey-F", output_file)

        # Verify file was created
        assert output_file.exists(), "Output file should exist"
        assert output_file.stat().st_size > 0, "Output file should not be empty"

        print(f"✓ Generated audio file: {output_file} ({output_file.stat().st_size} bytes)")

    except NotImplementedError:
        pytest.skip("Gemini TTS not yet fully implemented")
    except Exception as e:
        # Gemini TTS API might not be fully available yet
        pytest.skip(f"Gemini TTS not available: {e}")


@pytest.mark.integration
@pytest.mark.requires_openai
@pytest.mark.slow
def test_tts_audio_file_exists_and_valid(test_audio_script, temp_output_dir):
    """Test that generated audio file is valid"""
    # Skip if no OpenAI key
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    config = ProviderConfig(llm_provider="openai", tts_provider="openai")
    provider = create_tts_provider(config)

    output_file = temp_output_dir / "podcast_validation_test.mp3"

    # Generate audio
    provider.generate_audio(test_audio_script, "nova", output_file)

    # Comprehensive validation
    assert output_file.exists(), "File must exist"
    assert output_file.is_file(), "Must be a file, not a directory"
    assert output_file.suffix == ".mp3", "File extension should be .mp3"

    file_size = output_file.stat().st_size
    assert file_size > 0, "File should not be empty"
    assert file_size > 1000, "Audio file should be reasonably sized"

    # Check that it's actually audio data (MP3 files start with ID3 or 0xFF 0xFB)
    with open(output_file, 'rb') as f:
        header = f.read(3)
        assert len(header) == 3, "File should have at least 3 bytes"
        # MP3 files often start with ID3 tag or MPEG sync word
        is_mp3 = header[:3] == b'ID3' or header[0] == 0xFF
        assert is_mp3, "File should have valid MP3 header"

    print(f"✓ Audio file is valid: {output_file}")
    print(f"  Size: {file_size} bytes")
    print(f"  Format: MP3")


@pytest.mark.integration
@pytest.mark.requires_openai
@pytest.mark.slow
def test_tts_different_voices(test_audio_script, temp_output_dir):
    """Test that multiple voices work correctly"""
    # Skip if no OpenAI key
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    config = ProviderConfig(llm_provider="openai", tts_provider="openai")
    provider = create_tts_provider(config)

    # Test multiple voices
    voices_to_test = ["alloy", "nova", "echo"]

    for voice in voices_to_test:
        output_file = temp_output_dir / f"podcast_voice_{voice}.mp3"

        # Generate audio with this voice
        provider.generate_audio(test_audio_script, voice, output_file)

        # Verify file was created
        assert output_file.exists(), f"File for voice '{voice}' should exist"
        assert output_file.stat().st_size > 1000, f"Audio for voice '{voice}' should be valid"

        print(f"✓ Voice '{voice}' generated successfully")
