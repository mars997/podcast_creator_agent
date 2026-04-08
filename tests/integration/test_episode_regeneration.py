"""
Integration tests for episode regeneration workflow.

These tests verify the regeneration of episodes from existing metadata and sources.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock
from datetime import datetime

from core.episode_regenerator import regenerate_episode


@pytest.fixture
def mock_providers():
    """Create mock LLM and TTS providers"""
    llm_provider = Mock()
    llm_provider.provider_name = "openai"
    llm_provider.model_name = "gpt-4"
    llm_provider.generate_text.return_value = "Regenerated podcast script"

    tts_provider = Mock()
    tts_provider.provider_name = "openai"
    tts_provider.model_name = "tts-1"
    tts_provider.available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    tts_provider.generate_audio.return_value = None

    return llm_provider, tts_provider


@pytest.fixture
def original_episode(tmp_path):
    """Create an original episode to regenerate from"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    episode_dir = output_dir / "Test_Episode_2024-01-01_120000"
    episode_dir.mkdir()

    sources_dir = episode_dir / "sources"
    sources_dir.mkdir()

    # Create source files
    source1 = sources_dir / "source_1.txt"
    source1.write_text("Source 1: Original content", encoding="utf-8")

    source2 = sources_dir / "source_2.txt"
    source2.write_text("Source 2: More original content", encoding="utf-8")

    # Create metadata
    metadata = {
        "created_at": "2024-01-01T12:00:00",
        "episode_id": "Test_Episode_2024-01-01_120000",
        "topic": "Test Episode",
        "tone": "casual",
        "voice": "nova",
        "length": "medium",
        "word_range_target": "500 to 700 words",
        "models": {
            "script_model": "gpt-4",
            "tts_model": "tts-1"
        },
        "inputs": {
            "requested_urls": [],
            "requested_files": ["source1.txt", "source2.txt"]
        }
    }

    metadata_file = episode_dir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    index_file = output_dir / "episode_index.json"

    return {
        "episode_dir": episode_dir,
        "metadata": metadata,
        "output_root": output_dir,
        "index_file": index_file
    }


class TestEpisodeRegeneration:
    """Test episode regeneration workflow"""

    def test_regenerate_basic_episode(self, mock_providers, original_episode):
        """Test basic episode regeneration"""
        llm_provider, tts_provider = mock_providers

        new_episode_dir, new_episode_id = regenerate_episode(
            original_episode["metadata"],
            original_episode["episode_dir"],
            llm_provider,
            tts_provider,
            original_episode["output_root"],
            original_episode["index_file"]
        )

        # Verify new episode directory created
        assert new_episode_dir.exists()
        assert new_episode_dir != original_episode["episode_dir"]

        # Verify new episode ID includes "regenerated"
        assert "regenerated" in new_episode_id

        # Verify metadata file created
        metadata_file = new_episode_dir / "metadata.json"
        assert metadata_file.exists()
        new_metadata = json.loads(metadata_file.read_text())

        # Verify metadata references original episode
        assert "regenerated_from" in new_metadata
        assert new_metadata["regenerated_from"]["original_episode_id"] == "Test_Episode_2024-01-01_120000"

        # Verify settings preserved
        assert new_metadata["topic"] == "Test Episode"
        assert new_metadata["tone"] == "casual"
        assert new_metadata["voice"] == "nova"
        assert new_metadata["length"] == "medium"

    def test_regenerate_copies_sources(self, mock_providers, original_episode):
        """Test that source files are copied to new episode"""
        llm_provider, tts_provider = mock_providers

        new_episode_dir, new_episode_id = regenerate_episode(
            original_episode["metadata"],
            original_episode["episode_dir"],
            llm_provider,
            tts_provider,
            original_episode["output_root"],
            original_episode["index_file"]
        )

        # Verify sources directory exists
        new_sources_dir = new_episode_dir / "sources"
        assert new_sources_dir.exists()

        # Verify source files copied
        source_files = list(new_sources_dir.glob("*.txt"))
        assert len(source_files) == 2

        # Verify content matches
        source1_content = (new_sources_dir / "source_1.txt").read_text()
        assert "Original content" in source1_content

    def test_regenerate_creates_new_files(self, mock_providers, original_episode):
        """Test that new script, show notes, and audio files are created"""
        llm_provider, tts_provider = mock_providers

        new_episode_dir, new_episode_id = regenerate_episode(
            original_episode["metadata"],
            original_episode["episode_dir"],
            llm_provider,
            tts_provider,
            original_episode["output_root"],
            original_episode["index_file"]
        )

        # Verify script file created
        script_file = new_episode_dir / "script.txt"
        assert script_file.exists()
        assert script_file.read_text() == "Regenerated podcast script"

        # Verify show notes file created
        show_notes_file = new_episode_dir / "show_notes.txt"
        assert show_notes_file.exists()

        # Verify LLM was called for script and show notes
        assert llm_provider.generate_text.call_count == 2

        # Verify TTS was called for audio
        assert tts_provider.generate_audio.called

    def test_regenerate_updates_episode_index(self, mock_providers, original_episode):
        """Test that episode index is updated with regenerated episode"""
        llm_provider, tts_provider = mock_providers

        new_episode_dir, new_episode_id = regenerate_episode(
            original_episode["metadata"],
            original_episode["episode_dir"],
            llm_provider,
            tts_provider,
            original_episode["output_root"],
            original_episode["index_file"]
        )

        # Verify episode index exists
        index_file = original_episode["index_file"]
        assert index_file.exists()

        # Verify index contains regenerated episode
        index_data = json.loads(index_file.read_text())
        assert len(index_data) == 1

        regenerated_entry = index_data[0]
        assert "regenerated" in regenerated_entry["episode_id"]

    def test_regenerate_without_sources_raises_error(self, mock_providers, original_episode):
        """Test that regeneration fails if sources directory is missing"""
        llm_provider, tts_provider = mock_providers

        # Delete sources directory
        sources_dir = original_episode["episode_dir"] / "sources"
        for file in sources_dir.glob("*.txt"):
            file.unlink()
        sources_dir.rmdir()

        # Attempt regeneration should raise error
        with pytest.raises(FileNotFoundError, match="Sources directory not found"):
            regenerate_episode(
                original_episode["metadata"],
                original_episode["episode_dir"],
                llm_provider,
                tts_provider,
                original_episode["output_root"],
                original_episode["index_file"]
            )

    def test_regenerate_with_empty_sources_raises_error(self, mock_providers, original_episode):
        """Test that regeneration fails if sources directory is empty"""
        llm_provider, tts_provider = mock_providers

        # Delete all source files
        sources_dir = original_episode["episode_dir"] / "sources"
        for file in sources_dir.glob("*.txt"):
            file.unlink()

        # Attempt regeneration should raise error
        with pytest.raises(ValueError, match="No source files found"):
            regenerate_episode(
                original_episode["metadata"],
                original_episode["episode_dir"],
                llm_provider,
                tts_provider,
                original_episode["output_root"],
                original_episode["index_file"]
            )
