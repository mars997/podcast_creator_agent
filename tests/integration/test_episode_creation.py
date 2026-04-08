"""
Integration tests for episode creation workflow.

These tests verify the full episode creation process from sources to outputs.
They use mocked providers to avoid API calls but test the actual workflow.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from core.content_generation import build_script, build_show_notes, generate_audio
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
from core.source_management import save_sources_to_directory
from core.validation import sanitize_filename, get_word_range


@pytest.fixture
def mock_providers():
    """Create mock LLM and TTS providers"""
    llm_provider = Mock()
    llm_provider.provider_name = "openai"
    llm_provider.model_name = "gpt-4"
    llm_provider.generate_text.return_value = "Test podcast script content"

    tts_provider = Mock()
    tts_provider.provider_name = "openai"
    tts_provider.model_name = "tts-1"
    tts_provider.available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    tts_provider.generate_audio.return_value = None

    return llm_provider, tts_provider


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


class TestEpisodeCreationWorkflow:
    """Test complete episode creation workflow"""

    def test_create_episode_with_url_sources(self, mock_providers, temp_output_dir, tmp_path):
        """Test creating episode from URL sources"""
        llm_provider, tts_provider = mock_providers

        topic = "AI Technology"
        tone = "educational"
        voice = "nova"
        length = "medium"
        word_range = get_word_range(length)

        # Create episode directory
        episode_dir, episode_id = create_episode_directory(temp_output_dir, topic)

        assert episode_dir.exists()
        assert episode_id.startswith("AI_Technology_")

        # Mock source content
        sources_dir = episode_dir / "sources"
        sources_dir.mkdir()

        all_sources = []
        with patch('core.source_management.fetch_article_text') as mock_fetch:
            mock_fetch.return_value = "Article content from URL"

            urls = ["https://example.com/article1", "https://example.com/article2"]
            successful, failed = save_sources_to_directory(
                sources_dir,
                all_sources,
                urls=urls
            )

        assert len(successful) == 2
        assert len(failed) == 0
        assert len(all_sources) == 2

        # Generate script
        combined_source = "\n\n".join(all_sources)
        script = build_script(llm_provider, topic, tone, word_range, combined_source)

        assert script == "Test podcast script content"
        assert llm_provider.generate_text.called

        # Generate show notes
        show_notes = build_show_notes(llm_provider, script)

        assert show_notes == "Test podcast script content"

        # Save files
        script_file = episode_dir / "script.txt"
        script_file.write_text(script, encoding="utf-8")

        show_notes_file = episode_dir / "show_notes.txt"
        show_notes_file.write_text(show_notes, encoding="utf-8")

        audio_file = episode_dir / f"podcast_{voice}.mp3"

        # Generate audio
        generate_audio(tts_provider, script, voice, audio_file)

        assert tts_provider.generate_audio.called

        # Save metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "episode_id": episode_id,
            "topic": topic,
            "tone": tone,
            "voice": voice,
            "length": length,
            "word_range_target": word_range,
        }

        metadata_file = save_episode_metadata(episode_dir, metadata)

        assert metadata_file.exists()
        saved_metadata = json.loads(metadata_file.read_text())
        assert saved_metadata["topic"] == topic
        assert saved_metadata["episode_id"] == episode_id

    def test_create_episode_with_file_sources(self, mock_providers, temp_output_dir, tmp_path):
        """Test creating episode from file sources"""
        llm_provider, tts_provider = mock_providers

        # Create source files
        source_file1 = tmp_path / "source1.txt"
        source_file1.write_text("Content from file 1", encoding="utf-8")

        source_file2 = tmp_path / "source2.txt"
        source_file2.write_text("Content from file 2", encoding="utf-8")

        topic = "Test Topic"
        episode_dir, episode_id = create_episode_directory(temp_output_dir, topic)

        sources_dir = episode_dir / "sources"
        sources_dir.mkdir()

        all_sources = []
        file_paths = [source_file1, source_file2]

        successful, failed = save_sources_to_directory(
            sources_dir,
            all_sources,
            files=file_paths
        )

        assert len(successful) == 2
        assert len(failed) == 0
        assert len(all_sources) == 2
        assert "Content from file 1" in all_sources[0]
        assert "Content from file 2" in all_sources[1]

    def test_episode_index_update(self, mock_providers, temp_output_dir):
        """Test episode index updates correctly"""
        llm_provider, tts_provider = mock_providers

        index_file = temp_output_dir / "episode_index.json"

        # Create first episode
        episode_dir1, episode_id1 = create_episode_directory(temp_output_dir, "Topic 1")

        metadata1 = {
            "created_at": datetime.now().isoformat(),
            "episode_id": episode_id1,
            "topic": "Topic 1",
            "tone": "casual",
            "voice": "nova",
            "length": "short"
        }

        summary1 = create_episode_summary(metadata1, episode_dir1)
        update_episode_index(index_file, summary1)

        # Create second episode
        episode_dir2, episode_id2 = create_episode_directory(temp_output_dir, "Topic 2")

        metadata2 = {
            "created_at": datetime.now().isoformat(),
            "episode_id": episode_id2,
            "topic": "Topic 2",
            "tone": "professional",
            "voice": "alloy",
            "length": "long"
        }

        summary2 = create_episode_summary(metadata2, episode_dir2)
        update_episode_index(index_file, summary2)

        # Verify index has both episodes
        index_data = json.loads(index_file.read_text())

        assert len(index_data) == 2
        assert index_data[0]["topic"] == "Topic 1"
        assert index_data[1]["topic"] == "Topic 2"
        assert index_data[0]["episode_id"] == episode_id1
        assert index_data[1]["episode_id"] == episode_id2

    def test_failed_source_handling(self, mock_providers, temp_output_dir):
        """Test handling of failed source fetches"""
        llm_provider, tts_provider = mock_providers

        episode_dir, episode_id = create_episode_directory(temp_output_dir, "Test")
        sources_dir = episode_dir / "sources"
        sources_dir.mkdir()

        all_sources = []

        with patch('core.source_management.fetch_article_text') as mock_fetch:
            # First URL succeeds, second fails
            mock_fetch.side_effect = [
                "Article content",
                Exception("Connection timeout")
            ]

            urls = ["https://example.com/success", "https://example.com/fail"]
            successful, failed = save_sources_to_directory(
                sources_dir,
                all_sources,
                urls=urls
            )

        assert len(successful) == 1
        assert len(failed) == 1
        assert successful[0]["source"] == "https://example.com/success"
        assert failed[0]["source"] == "https://example.com/fail"
        assert "Connection timeout" in failed[0]["error"]

    def test_unique_episode_ids(self, mock_providers, temp_output_dir):
        """Test that multiple episodes with same topic get unique IDs"""
        llm_provider, tts_provider = mock_providers

        topic = "Same Topic"

        # Create multiple episodes with same topic with slight delays to ensure unique timestamps
        import time
        episode_dir1, episode_id1 = create_episode_directory(temp_output_dir, topic)
        time.sleep(1)  # Ensure different timestamps
        episode_dir2, episode_id2 = create_episode_directory(temp_output_dir, topic)
        time.sleep(1)
        episode_dir3, episode_id3 = create_episode_directory(temp_output_dir, topic)

        # All IDs should be different
        assert episode_id1 != episode_id2
        assert episode_id2 != episode_id3
        assert episode_id1 != episode_id3

        # All should start with sanitized topic
        safe_topic = sanitize_filename(topic)
        assert episode_id1.startswith(safe_topic)
        assert episode_id2.startswith(safe_topic)
        assert episode_id3.startswith(safe_topic)

        # All directories should exist
        assert episode_dir1.exists()
        assert episode_dir2.exists()
        assert episode_dir3.exists()
