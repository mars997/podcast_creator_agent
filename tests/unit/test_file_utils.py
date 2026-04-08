"""
Unit tests for core.file_utils module.
"""

import json
import pytest
from pathlib import Path
from core.file_utils import (
    save_json,
    save_text_file,
    ensure_directory,
    read_text_file,
    load_json,
)


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


class TestSaveJson:
    """Tests for save_json function."""

    def test_save_dict(self, temp_dir):
        """Test saving a dictionary to JSON."""
        data = {"title": "My Podcast", "episodes": 5}
        file_path = temp_dir / "metadata.json"

        save_json(data, file_path)

        assert file_path.exists()
        loaded = json.loads(file_path.read_text(encoding="utf-8"))
        assert loaded == data

    def test_save_list(self, temp_dir):
        """Test saving a list to JSON."""
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        file_path = temp_dir / "episodes.json"

        save_json(data, file_path)

        assert file_path.exists()
        loaded = json.loads(file_path.read_text(encoding="utf-8"))
        assert loaded == data

    def test_save_nested_structure(self, temp_dir):
        """Test saving nested data structures."""
        data = {
            "episode": {
                "title": "AI Trends",
                "metadata": {
                    "duration": 600,
                    "tags": ["ai", "tech"]
                }
            }
        }
        file_path = temp_dir / "complex.json"

        save_json(data, file_path)

        loaded = json.loads(file_path.read_text(encoding="utf-8"))
        assert loaded == data

    def test_save_unicode_content(self, temp_dir):
        """Test saving unicode content."""
        data = {"title": "Café ☕ Podcast", "author": "José"}
        file_path = temp_dir / "unicode.json"

        save_json(data, file_path)

        content = file_path.read_text(encoding="utf-8")
        assert "Café" in content
        assert "José" in content

    def test_formatted_output(self, temp_dir):
        """Test that JSON is formatted with indentation."""
        data = {"a": 1, "b": 2}
        file_path = temp_dir / "formatted.json"

        save_json(data, file_path)

        content = file_path.read_text(encoding="utf-8")
        # Check for indentation (formatted JSON has newlines)
        assert "\n" in content

    def test_overwrite_existing_file(self, temp_dir):
        """Test that existing files are overwritten."""
        file_path = temp_dir / "overwrite.json"

        save_json({"old": "data"}, file_path)
        save_json({"new": "data"}, file_path)

        loaded = json.loads(file_path.read_text(encoding="utf-8"))
        assert loaded == {"new": "data"}


class TestSaveTextFile:
    """Tests for save_text_file function."""

    def test_save_basic_text(self, temp_dir):
        """Test saving basic text content."""
        content = "This is a podcast script."
        file_path = temp_dir / "script.txt"

        save_text_file(content, file_path)

        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content

    def test_save_multiline_text(self, temp_dir):
        """Test saving multiline text."""
        content = "Line 1\nLine 2\nLine 3"
        file_path = temp_dir / "multiline.txt"

        save_text_file(content, file_path)

        assert file_path.read_text(encoding="utf-8") == content

    def test_save_unicode_text(self, temp_dir):
        """Test saving unicode text."""
        content = "Hello 世界 🌍"
        file_path = temp_dir / "unicode.txt"

        save_text_file(content, file_path)

        assert file_path.read_text(encoding="utf-8") == content

    def test_save_empty_string(self, temp_dir):
        """Test saving empty string."""
        file_path = temp_dir / "empty.txt"

        save_text_file("", file_path)

        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == ""

    def test_overwrite_existing(self, temp_dir):
        """Test overwriting existing text file."""
        file_path = temp_dir / "overwrite.txt"

        save_text_file("old content", file_path)
        save_text_file("new content", file_path)

        assert file_path.read_text(encoding="utf-8") == "new content"


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_create_directory(self, temp_dir):
        """Test creating a new directory."""
        new_dir = temp_dir / "new_directory"

        result = ensure_directory(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()
        assert result == new_dir

    def test_create_nested_directories(self, temp_dir):
        """Test creating nested directories."""
        nested_dir = temp_dir / "level1" / "level2" / "level3"

        result = ensure_directory(nested_dir)

        assert nested_dir.exists()
        assert nested_dir.is_dir()
        assert result == nested_dir

    def test_existing_directory(self, temp_dir):
        """Test with existing directory (should not error)."""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()

        result = ensure_directory(existing_dir)

        assert existing_dir.exists()
        assert result == existing_dir

    def test_returns_path_for_chaining(self, temp_dir):
        """Test that function returns path for method chaining."""
        new_dir = temp_dir / "chainable"

        result = ensure_directory(new_dir)

        # Should be able to use result directly
        file_path = result / "test.txt"
        file_path.write_text("test")
        assert file_path.exists()


class TestReadTextFile:
    """Tests for read_text_file function."""

    def test_read_existing_file(self, temp_dir):
        """Test reading an existing text file."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("Test content", encoding="utf-8")

        content = read_text_file(file_path)

        assert content == "Test content"

    def test_read_multiline_file(self, temp_dir):
        """Test reading multiline content."""
        file_path = temp_dir / "multiline.txt"
        file_path.write_text("Line 1\nLine 2\nLine 3", encoding="utf-8")

        content = read_text_file(file_path)

        assert content == "Line 1\nLine 2\nLine 3"

    def test_read_unicode_file(self, temp_dir):
        """Test reading unicode content."""
        file_path = temp_dir / "unicode.txt"
        file_path.write_text("Café ☕", encoding="utf-8")

        content = read_text_file(file_path)

        assert content == "Café ☕"

    def test_strips_whitespace(self, temp_dir):
        """Test that leading/trailing whitespace is stripped."""
        file_path = temp_dir / "whitespace.txt"
        file_path.write_text("  \n  Content  \n  ", encoding="utf-8")

        content = read_text_file(file_path)

        assert content == "Content"

    def test_file_not_found(self, temp_dir):
        """Test reading non-existent file raises FileNotFoundError."""
        file_path = temp_dir / "nonexistent.txt"

        with pytest.raises(FileNotFoundError) as exc_info:
            read_text_file(file_path)

        assert "not found" in str(exc_info.value).lower()

    def test_empty_file_raises_error(self, temp_dir):
        """Test reading empty file raises ValueError."""
        file_path = temp_dir / "empty.txt"
        file_path.write_text("", encoding="utf-8")

        with pytest.raises(ValueError) as exc_info:
            read_text_file(file_path)

        assert "empty" in str(exc_info.value).lower()

    def test_whitespace_only_file_raises_error(self, temp_dir):
        """Test file with only whitespace raises ValueError."""
        file_path = temp_dir / "whitespace_only.txt"
        file_path.write_text("   \n  \n  ", encoding="utf-8")

        with pytest.raises(ValueError):
            read_text_file(file_path)


class TestLoadJson:
    """Tests for load_json function."""

    def test_load_dict(self, temp_dir):
        """Test loading a JSON dictionary."""
        data = {"title": "My Podcast", "episodes": 5}
        file_path = temp_dir / "metadata.json"
        file_path.write_text(json.dumps(data), encoding="utf-8")

        loaded = load_json(file_path)

        assert loaded == data

    def test_load_list(self, temp_dir):
        """Test loading a JSON list."""
        data = [{"id": 1}, {"id": 2}]
        file_path = temp_dir / "episodes.json"
        file_path.write_text(json.dumps(data), encoding="utf-8")

        loaded = load_json(file_path)

        assert loaded == data

    def test_load_nested_structure(self, temp_dir):
        """Test loading nested JSON structure."""
        data = {
            "episode": {
                "metadata": {
                    "tags": ["ai", "tech"]
                }
            }
        }
        file_path = temp_dir / "complex.json"
        file_path.write_text(json.dumps(data), encoding="utf-8")

        loaded = load_json(file_path)

        assert loaded == data

    def test_load_unicode_content(self, temp_dir):
        """Test loading unicode JSON content."""
        data = {"title": "Café ☕"}
        file_path = temp_dir / "unicode.json"
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        loaded = load_json(file_path)

        assert loaded["title"] == "Café ☕"

    def test_file_not_found(self, temp_dir):
        """Test loading non-existent file raises FileNotFoundError."""
        file_path = temp_dir / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            load_json(file_path)

    def test_invalid_json(self, temp_dir):
        """Test loading invalid JSON raises JSONDecodeError."""
        file_path = temp_dir / "invalid.json"
        file_path.write_text("{ invalid json }", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            load_json(file_path)


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_save_and_load_json_roundtrip(self, temp_dir):
        """Test saving and loading JSON preserves data."""
        original_data = {
            "title": "AI Podcast",
            "episodes": [
                {"id": 1, "title": "Intro to AI"},
                {"id": 2, "title": "Deep Learning"}
            ]
        }
        file_path = temp_dir / "roundtrip.json"

        save_json(original_data, file_path)
        loaded_data = load_json(file_path)

        assert loaded_data == original_data

    def test_save_and_read_text_roundtrip(self, temp_dir):
        """Test saving and reading text preserves content."""
        original_content = "This is a test script.\nWith multiple lines."
        file_path = temp_dir / "roundtrip.txt"

        save_text_file(original_content, file_path)
        loaded_content = read_text_file(file_path)

        assert loaded_content == original_content

    def test_ensure_directory_and_save_file(self, temp_dir):
        """Test creating directory and saving file in one workflow."""
        episode_dir = temp_dir / "episode_001"
        ensure_directory(episode_dir)

        script_path = episode_dir / "script.txt"
        save_text_file("Episode script", script_path)

        assert episode_dir.exists()
        assert script_path.exists()
        assert read_text_file(script_path) == "Episode script"
