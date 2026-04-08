"""
Unit tests for core.content_generation module.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from core.content_generation import (
    build_script,
    build_show_notes,
    generate_audio,
)


class TestBuildScript:
    """Tests for build_script function."""

    def test_build_script_with_sources(self):
        """Test script generation with source material."""
        mock_llm = Mock()
        mock_llm.generate_text.return_value = "Generated Script"

        result = build_script(
            mock_llm,
            "AI Trends",
            "educational",
            "500 to 700 words",
            "Source 1: Article about AI..."
        )

        assert result == "Generated Script"
        mock_llm.generate_text.assert_called_once()

        # Check that the prompt includes all parameters
        prompt = mock_llm.generate_text.call_args[0][0]
        assert "AI Trends" in prompt
        assert "educational" in prompt
        assert "500 to 700 words" in prompt
        assert "Source 1: Article about AI..." in prompt

    def test_build_script_without_sources(self):
        """Test script generation without source material."""
        mock_llm = Mock()
        mock_llm.generate_text.return_value = "Generated Script"

        result = build_script(
            mock_llm,
            "Technology Overview",
            "casual",
            "300 to 450 words"
        )

        assert result == "Generated Script"
        mock_llm.generate_text.assert_called_once()

        # Check that the prompt doesn't include source material section
        prompt = mock_llm.generate_text.call_args[0][0]
        assert "Technology Overview" in prompt
        assert "casual" in prompt
        assert "300 to 450 words" in prompt
        assert "Source materials:" not in prompt

    def test_build_script_prompt_structure(self):
        """Test that prompt includes required elements."""
        mock_llm = Mock()
        mock_llm.generate_text.return_value = "Script"

        build_script(
            mock_llm,
            "Test Topic",
            "professional",
            "500 to 700 words",
            "Test sources"
        )

        prompt = mock_llm.generate_text.call_args[0][0]

        # Check for key prompt elements
        assert "podcast writer" in prompt.lower()
        assert "episode title" in prompt.lower()
        assert "main talking points" in prompt.lower()
        assert "conclusion" in prompt.lower()

    def test_build_script_with_different_tones(self):
        """Test script generation with different tones."""
        mock_llm = Mock()
        mock_llm.generate_text.return_value = "Script"

        for tone in ["casual", "professional", "educational"]:
            build_script(mock_llm, "Topic", tone, "500 to 700 words")
            prompt = mock_llm.generate_text.call_args[0][0]
            assert tone in prompt

    def test_build_script_with_different_lengths(self):
        """Test script generation with different word ranges."""
        mock_llm = Mock()
        mock_llm.generate_text.return_value = "Script"

        for word_range in ["300 to 450 words", "500 to 700 words", "800 to 1100 words"]:
            build_script(mock_llm, "Topic", "casual", word_range)
            prompt = mock_llm.generate_text.call_args[0][0]
            assert word_range in prompt


class TestBuildShowNotes:
    """Tests for build_show_notes function."""

    def test_build_show_notes_basic(self):
        """Test basic show notes generation."""
        mock_llm = Mock()
        mock_llm.generate_text.return_value = "Generated Show Notes"

        script = "Episode Title\n\nWelcome to the podcast...\n\nConclusion."

        result = build_show_notes(mock_llm, script)

        assert result == "Generated Show Notes"
        mock_llm.generate_text.assert_called_once()

        # Check that script is in the prompt
        prompt = mock_llm.generate_text.call_args[0][0]
        assert script in prompt

    def test_build_show_notes_prompt_requirements(self):
        """Test that prompt includes required elements."""
        mock_llm = Mock()
        mock_llm.generate_text.return_value = "Notes"

        build_show_notes(mock_llm, "Test script")

        prompt = mock_llm.generate_text.call_args[0][0]

        # Check for key requirements
        assert "episode title" in prompt.lower()
        assert "summary" in prompt.lower()
        assert "key takeaways" in prompt.lower()

    def test_build_show_notes_with_long_script(self):
        """Test show notes generation with longer script."""
        mock_llm = Mock()
        mock_llm.generate_text.return_value = "Notes"

        long_script = "Title\n" + "\n".join([f"Point {i}" for i in range(100)])

        result = build_show_notes(mock_llm, long_script)

        assert result == "Notes"
        prompt = mock_llm.generate_text.call_args[0][0]
        assert long_script in prompt

    def test_build_show_notes_with_special_characters(self):
        """Test show notes with special characters in script."""
        mock_llm = Mock()
        mock_llm.generate_text.return_value = "Notes"

        script = "Episode: AI & ML\n\nHello! This is a test... with special chars: @#$"

        result = build_show_notes(mock_llm, script)

        assert result == "Notes"
        prompt = mock_llm.generate_text.call_args[0][0]
        assert script in prompt


class TestGenerateAudio:
    """Tests for generate_audio function."""

    def test_generate_audio_basic(self, tmp_path):
        """Test basic audio generation."""
        mock_tts = Mock()
        audio_path = tmp_path / "podcast.mp3"

        generate_audio(
            mock_tts,
            "Welcome to my podcast...",
            "nova",
            audio_path
        )

        mock_tts.generate_audio.assert_called_once_with(
            "Welcome to my podcast...",
            "nova",
            audio_path
        )

    def test_generate_audio_with_different_voices(self, tmp_path):
        """Test audio generation with different voices."""
        mock_tts = Mock()
        audio_path = tmp_path / "podcast.mp3"

        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        for voice in voices:
            mock_tts.reset_mock()
            generate_audio(mock_tts, "Script", voice, audio_path)

            mock_tts.generate_audio.assert_called_once()
            call_args = mock_tts.generate_audio.call_args[0]
            assert call_args[1] == voice

    def test_generate_audio_with_long_script(self, tmp_path):
        """Test audio generation with long script."""
        mock_tts = Mock()
        audio_path = tmp_path / "podcast.mp3"

        long_script = "Welcome. " * 1000  # Very long script

        generate_audio(mock_tts, long_script, "nova", audio_path)

        mock_tts.generate_audio.assert_called_once()
        call_args = mock_tts.generate_audio.call_args[0]
        assert call_args[0] == long_script

    def test_generate_audio_path_handling(self, tmp_path):
        """Test that audio path is passed correctly."""
        mock_tts = Mock()

        # Test with different path types
        audio_path = tmp_path / "output" / "episode" / "podcast_nova.mp3"

        generate_audio(mock_tts, "Script", "nova", audio_path)

        call_args = mock_tts.generate_audio.call_args[0]
        assert call_args[2] == audio_path

    def test_generate_audio_with_special_characters(self, tmp_path):
        """Test audio generation with special characters in script."""
        mock_tts = Mock()
        audio_path = tmp_path / "podcast.mp3"

        script_with_special = "Hello! This costs $10. Let's discuss AI & ML... Questions?"

        generate_audio(mock_tts, script_with_special, "nova", audio_path)

        mock_tts.generate_audio.assert_called_once()
        call_args = mock_tts.generate_audio.call_args[0]
        assert call_args[0] == script_with_special


class TestIntegration:
    """Integration tests for content generation workflow."""

    def test_full_content_generation_workflow(self, tmp_path):
        """Test complete workflow: script -> show notes -> audio."""
        mock_llm = Mock()
        mock_tts = Mock()

        # Generate script
        mock_llm.generate_text.return_value = "Episode Title\n\nWelcome to the podcast..."
        script = build_script(
            mock_llm,
            "AI Trends",
            "educational",
            "500 to 700 words",
            "Source: Article about AI"
        )

        assert "Episode Title" in script

        # Generate show notes from script
        mock_llm.generate_text.return_value = "# Episode Title\n\nSummary...\n\nKey takeaways..."
        show_notes = build_show_notes(mock_llm, script)

        assert "Summary" in show_notes

        # Generate audio from script
        audio_path = tmp_path / "podcast.mp3"
        generate_audio(mock_tts, script, "nova", audio_path)

        # Verify all components were called
        assert mock_llm.generate_text.call_count == 2  # Script + show notes
        assert mock_tts.generate_audio.call_count == 1

    def test_workflow_with_minimal_content(self, tmp_path):
        """Test workflow with minimal content."""
        mock_llm = Mock()
        mock_tts = Mock()

        mock_llm.generate_text.return_value = "Short"
        script = build_script(mock_llm, "Topic", "casual", "300 to 450 words")

        show_notes = build_show_notes(mock_llm, script)

        audio_path = tmp_path / "test.mp3"
        generate_audio(mock_tts, script, "alloy", audio_path)

        assert mock_llm.generate_text.call_count == 2
        assert mock_tts.generate_audio.call_count == 1
