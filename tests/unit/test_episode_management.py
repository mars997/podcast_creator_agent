"""
Unit tests for core.episode_management module.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index,
    load_episode_index,
    load_episode_metadata,
)


class TestCreateEpisodeDirectory:
    """Tests for create_episode_directory function."""

    def test_create_basic_directory(self, tmp_path):
        """Test creating a basic episode directory."""
        output_root = tmp_path / "output"

        episode_dir, episode_id = create_episode_directory(
            output_root,
            "AI Trends"
        )

        assert episode_dir.exists()
        assert episode_dir.is_dir()
        assert "AI_Trends" in episode_id
        assert "_" in episode_id  # Should have timestamp

    def test_create_with_custom_timestamp(self, tmp_path):
        """Test creating directory with custom timestamp."""
        output_root = tmp_path / "output"

        episode_dir, episode_id = create_episode_directory(
            output_root,
            "Test Topic",
            timestamp_suffix="2026-04-07_120000"
        )

        assert episode_id == "Test_Topic_2026-04-07_120000"
        assert episode_dir.name == "Test_Topic_2026-04-07_120000"

    def test_sanitizes_topic_name(self, tmp_path):
        """Test that topic name is sanitized for directory."""
        output_root = tmp_path / "output"

        episode_dir, episode_id = create_episode_directory(
            output_root,
            "AI & ML: The Future!",
            timestamp_suffix="2026-04-07_120000"
        )

        # Should have special characters removed
        assert "AI__ML_The_Future" in episode_id
        assert "&" not in episode_id
        assert ":" not in episode_id

    def test_creates_parent_directories(self, tmp_path):
        """Test that parent directories are created if needed."""
        output_root = tmp_path / "level1" / "level2" / "output"

        episode_dir, episode_id = create_episode_directory(
            output_root,
            "Test",
            timestamp_suffix="2026-04-07_120000"
        )

        assert output_root.exists()
        assert episode_dir.exists()

    def test_unique_ids_for_same_topic(self, tmp_path):
        """Test that different timestamps create unique IDs."""
        output_root = tmp_path / "output"

        _, id1 = create_episode_directory(
            output_root,
            "Same Topic",
            timestamp_suffix="2026-04-07_120000"
        )

        _, id2 = create_episode_directory(
            output_root,
            "Same Topic",
            timestamp_suffix="2026-04-07_120001"
        )

        assert id1 != id2

    @patch('core.episode_management.datetime')
    def test_auto_generates_timestamp(self, mock_datetime, tmp_path):
        """Test automatic timestamp generation."""
        mock_now = datetime(2026, 4, 7, 15, 30, 45)
        mock_datetime.now.return_value = mock_now

        output_root = tmp_path / "output"

        episode_dir, episode_id = create_episode_directory(
            output_root,
            "Test"
        )

        assert "2026-04-07_153045" in episode_id


class TestSaveEpisodeMetadata:
    """Tests for save_episode_metadata function."""

    def test_save_metadata_basic(self, tmp_path):
        """Test basic metadata saving."""
        episode_dir = tmp_path / "episode"
        episode_dir.mkdir()

        metadata = {
            "episode_id": "Test_2026-04-07_120000",
            "topic": "Test Topic",
            "tone": "educational"
        }

        metadata_path = save_episode_metadata(episode_dir, metadata)

        assert metadata_path.exists()
        assert metadata_path.name == "metadata.json"

        loaded = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert loaded == metadata

    def test_save_complex_metadata(self, tmp_path):
        """Test saving complex metadata structure."""
        episode_dir = tmp_path / "episode"
        episode_dir.mkdir()

        metadata = {
            "episode_id": "Complex_2026-04-07_120000",
            "topic": "Complex Topic",
            "inputs": {
                "urls": ["url1", "url2"],
                "files": ["file1.txt"]
            },
            "outputs": {
                "script_file": "script.txt",
                "audio_file": "podcast.mp3"
            }
        }

        metadata_path = save_episode_metadata(episode_dir, metadata)

        loaded = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert loaded["inputs"]["urls"] == ["url1", "url2"]
        assert loaded["outputs"]["script_file"] == "script.txt"


class TestCreateEpisodeSummary:
    """Tests for create_episode_summary function."""

    def test_create_basic_summary(self, tmp_path):
        """Test creating basic episode summary."""
        episode_dir = tmp_path / "episode"
        episode_dir.mkdir()

        metadata = {
            "created_at": "2026-04-07T15:30:00",
            "episode_id": "Test_2026-04-07_153000",
            "topic": "Test Topic",
            "tone": "casual",
            "voice": "nova",
            "length": "medium"
        }

        summary = create_episode_summary(metadata, episode_dir)

        assert summary["created_at"] == "2026-04-07T15:30:00"
        assert summary["episode_id"] == "Test_2026-04-07_153000"
        assert summary["topic"] == "Test Topic"
        assert summary["tone"] == "casual"
        assert summary["voice"] == "nova"
        assert summary["length"] == "medium"

    def test_summary_includes_file_paths(self, tmp_path):
        """Test that summary includes file paths."""
        episode_dir = tmp_path / "episode"
        episode_dir.mkdir()

        metadata = {
            "episode_id": "Test",
            "topic": "Test",
            "voice": "nova"
        }

        summary = create_episode_summary(metadata, episode_dir)

        assert "metadata_file" in summary
        assert "script_file" in summary
        assert "show_notes_file" in summary
        assert "audio_file" in summary
        assert "podcast_nova.mp3" in summary["audio_file"]

    def test_summary_with_additional_fields(self, tmp_path):
        """Test summary with additional fields."""
        episode_dir = tmp_path / "episode"
        episode_dir.mkdir()

        metadata = {"episode_id": "Test", "topic": "Test"}
        additional = {
            "num_sources": 3,
            "duration": 600
        }

        summary = create_episode_summary(metadata, episode_dir, additional)

        assert summary["num_sources"] == 3
        assert summary["duration"] == 600

    def test_summary_without_voice(self, tmp_path):
        """Test summary creation when voice is not specified."""
        episode_dir = tmp_path / "episode"
        episode_dir.mkdir()

        metadata = {
            "episode_id": "Test",
            "topic": "Test"
            # No voice specified
        }

        summary = create_episode_summary(metadata, episode_dir)

        # Should not have audio_file if no voice
        assert "audio_file" not in summary


class TestUpdateEpisodeIndex:
    """Tests for update_episode_index function."""

    def test_create_new_index(self, tmp_path):
        """Test creating a new index file."""
        index_path = tmp_path / "episode_index.json"

        episode_summary = {
            "episode_id": "Test_001",
            "topic": "Test Topic"
        }

        update_episode_index(index_path, episode_summary)

        assert index_path.exists()
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        assert len(index_data) == 1
        assert index_data[0]["episode_id"] == "Test_001"

    def test_append_to_existing_index(self, tmp_path):
        """Test appending to existing index."""
        index_path = tmp_path / "episode_index.json"

        # Create initial index
        initial_data = [
            {"episode_id": "Test_001", "topic": "Topic 1"}
        ]
        index_path.write_text(json.dumps(initial_data), encoding="utf-8")

        # Add new episode
        new_summary = {
            "episode_id": "Test_002",
            "topic": "Topic 2"
        }

        update_episode_index(index_path, new_summary)

        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        assert len(index_data) == 2
        assert index_data[1]["episode_id"] == "Test_002"

    def test_handle_corrupted_index(self, tmp_path):
        """Test handling corrupted index file."""
        index_path = tmp_path / "episode_index.json"

        # Create corrupted index
        index_path.write_text("{ invalid json }", encoding="utf-8")

        # Should create fresh index
        new_summary = {"episode_id": "Test_001"}
        update_episode_index(index_path, new_summary)

        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        assert len(index_data) == 1

    def test_handle_non_list_index(self, tmp_path):
        """Test handling index that's not a list."""
        index_path = tmp_path / "episode_index.json"

        # Create index as dict instead of list
        index_path.write_text(json.dumps({"wrong": "type"}), encoding="utf-8")

        # Should create fresh list
        new_summary = {"episode_id": "Test_001"}
        update_episode_index(index_path, new_summary)

        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        assert isinstance(index_data, list)
        assert len(index_data) == 1


class TestLoadEpisodeIndex:
    """Tests for load_episode_index function."""

    def test_load_existing_index(self, tmp_path):
        """Test loading an existing index."""
        index_path = tmp_path / "episode_index.json"

        index_data = [
            {"episode_id": "Test_001", "topic": "Topic 1"},
            {"episode_id": "Test_002", "topic": "Topic 2"}
        ]
        index_path.write_text(json.dumps(index_data), encoding="utf-8")

        loaded = load_episode_index(index_path)

        assert len(loaded) == 2
        assert loaded[0]["episode_id"] == "Test_001"
        assert loaded[1]["episode_id"] == "Test_002"

    def test_load_empty_index(self, tmp_path):
        """Test loading an empty index."""
        index_path = tmp_path / "episode_index.json"
        index_path.write_text(json.dumps([]), encoding="utf-8")

        loaded = load_episode_index(index_path)

        assert loaded == []

    def test_load_nonexistent_index(self, tmp_path):
        """Test loading non-existent index raises error."""
        index_path = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            load_episode_index(index_path)

    def test_load_invalid_format(self, tmp_path):
        """Test loading invalid format raises error."""
        index_path = tmp_path / "episode_index.json"
        index_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

        with pytest.raises(ValueError) as exc_info:
            load_episode_index(index_path)

        assert "Invalid episode index format" in str(exc_info.value)


class TestLoadEpisodeMetadata:
    """Tests for load_episode_metadata function."""

    def test_load_existing_metadata(self, tmp_path):
        """Test loading existing metadata."""
        metadata_path = tmp_path / "metadata.json"

        metadata = {
            "episode_id": "Test_001",
            "topic": "Test Topic",
            "tone": "casual"
        }
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

        loaded = load_episode_metadata(metadata_path)

        assert loaded["episode_id"] == "Test_001"
        assert loaded["topic"] == "Test Topic"
        assert loaded["tone"] == "casual"

    def test_load_nonexistent_metadata(self, tmp_path):
        """Test loading non-existent metadata raises error."""
        metadata_path = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            load_episode_metadata(metadata_path)

    def test_load_invalid_metadata(self, tmp_path):
        """Test loading invalid metadata raises error."""
        metadata_path = tmp_path / "metadata.json"
        metadata_path.write_text("{ invalid json }", encoding="utf-8")

        with pytest.raises(ValueError) as exc_info:
            load_episode_metadata(metadata_path)

        assert "Error loading metadata" in str(exc_info.value)


class TestIntegration:
    """Integration tests for episode management workflow."""

    def test_full_episode_lifecycle(self, tmp_path):
        """Test complete episode lifecycle."""
        output_root = tmp_path / "output"
        index_path = output_root / "episode_index.json"

        # Create episode directory
        episode_dir, episode_id = create_episode_directory(
            output_root,
            "AI Trends",
            timestamp_suffix="2026-04-07_153000"
        )

        # Save metadata
        metadata = {
            "created_at": "2026-04-07T15:30:00",
            "episode_id": episode_id,
            "topic": "AI Trends",
            "tone": "educational",
            "voice": "nova",
            "length": "medium"
        }
        metadata_path = save_episode_metadata(episode_dir, metadata)

        # Create and save summary
        summary = create_episode_summary(metadata, episode_dir)
        update_episode_index(index_path, summary)

        # Load and verify
        loaded_index = load_episode_index(index_path)
        assert len(loaded_index) == 1
        assert loaded_index[0]["episode_id"] == episode_id

        loaded_metadata = load_episode_metadata(metadata_path)
        assert loaded_metadata["topic"] == "AI Trends"

    def test_multiple_episodes(self, tmp_path):
        """Test managing multiple episodes."""
        output_root = tmp_path / "output"
        index_path = output_root / "episode_index.json"

        # Create three episodes
        for i in range(3):
            episode_dir, episode_id = create_episode_directory(
                output_root,
                f"Topic {i}",
                timestamp_suffix=f"2026-04-07_15300{i}"
            )

            metadata = {
                "created_at": f"2026-04-07T15:30:0{i}",
                "episode_id": episode_id,
                "topic": f"Topic {i}"
            }

            save_episode_metadata(episode_dir, metadata)
            summary = create_episode_summary(metadata, episode_dir)
            update_episode_index(index_path, summary)

        # Verify all episodes in index
        loaded_index = load_episode_index(index_path)
        assert len(loaded_index) == 3

        for i, episode in enumerate(loaded_index):
            assert f"Topic_{i}" in episode["episode_id"]
