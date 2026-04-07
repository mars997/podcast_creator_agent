"""
Pytest configuration and shared fixtures for podcast_creator_agent tests.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for tests"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_script():
    """Sample podcast script for testing"""
    return """
    Welcome to Tech Insights: AI Edition

    Hello and welcome to today's episode where we explore the fascinating world
    of artificial intelligence. Today, we're diving into how AI is transforming
    our daily lives in ways you might not even realize.

    Let's start with your smartphone. Every time you use voice commands,
    autocomplete, or even take a photo, AI is working behind the scenes.

    Moving on to healthcare, AI is helping doctors diagnose diseases earlier
    and more accurately than ever before.

    Finally, let's talk about climate. AI models are helping scientists predict
    weather patterns and understand climate change with unprecedented detail.

    Thanks for listening to Tech Insights. Until next time, stay curious!
    """.strip()


@pytest.fixture
def test_audio_script():
    """Short script for TTS testing (from step2_tts_test.py)"""
    return """
Welcome to my first AI-generated podcast.
This is a short test episode created with Python in Visual Studio Code.
If you can hear this audio clearly, then step two is working successfully.
""".strip()


@pytest.fixture
def sample_show_notes():
    """Sample show notes for testing"""
    return """
    Episode: AI in Everyday Life

    Summary:
    Explore how artificial intelligence is transforming our daily experiences,
    from smartphones to healthcare and climate science.

    Key Takeaways:
    - AI powers voice commands and photo enhancements on smartphones
    - Healthcare diagnostics are becoming more accurate with AI assistance
    - Climate scientists use AI to predict weather and understand climate change
    """.strip()


@pytest.fixture
def sample_metadata():
    """Sample episode metadata for testing"""
    return {
        "created_at": "2026-04-07T12:00:00",
        "episode_id": "ai_insights_2026-04-07_120000",
        "topic": "AI Insights",
        "tone": "educational",
        "voice": "nova",
        "length": "medium",
        "providers": {
            "llm_provider": "openai",
            "llm_model": "gpt-4.1-mini",
            "tts_provider": "openai",
            "tts_model": "gpt-4o-mini-tts"
        },
        "models": {
            "script_model": "gpt-4.1-mini",
            "tts_model": "gpt-4o-mini-tts"
        }
    }


@pytest.fixture
def mock_openai_llm_response():
    """Mock OpenAI LLM response"""
    mock = Mock()
    mock.output_text = "This is a generated podcast script about AI."
    return mock


@pytest.fixture
def mock_gemini_llm_response():
    """Mock Gemini LLM response"""
    mock = Mock()
    mock.text = "This is a generated podcast script from Gemini."
    return mock


@pytest.fixture
def mock_env_openai_only(monkeypatch):
    """Set environment to have only OpenAI key"""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)


@pytest.fixture
def mock_env_gemini_only(monkeypatch):
    """Set environment to have only Gemini key"""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "test-gemini-key")


@pytest.fixture
def mock_env_both_providers(monkeypatch):
    """Set environment to have both provider keys"""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-gemini-key")


@pytest.fixture
def mock_env_no_providers(monkeypatch):
    """Set environment to have no provider keys"""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing"""
    provider = Mock()
    provider.provider_name = "openai"
    provider.model_name = "gpt-4.1-mini"
    provider.generate_text = Mock(return_value="Generated script text")
    return provider


@pytest.fixture
def mock_tts_provider():
    """Mock TTS provider for testing"""
    provider = Mock()
    provider.provider_name = "openai"
    provider.model_name = "gpt-4o-mini-tts"
    provider.available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    provider.generate_audio = Mock()
    return provider


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory"""
    return Path(__file__).parent / "fixtures"


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_openai: marks tests that require OpenAI API key"
    )
    config.addinivalue_line(
        "markers", "requires_gemini: marks tests that require Gemini API key"
    )
