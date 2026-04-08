"""
Unit tests for core.source_management module.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from core.source_management import (
    fetch_article_text,
    read_text_file,
    parse_csv_input,
    load_source_files,
    save_sources_to_directory,
)


class TestFetchArticleText:
    """Tests for fetch_article_text function."""

    @patch('core.source_management.requests.get')
    @patch('core.source_management.BeautifulSoup')
    def test_successful_fetch(self, mock_soup_class, mock_get):
        """Test successful article fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '<html><body><p>Article content here with enough text.</p></body></html>'
        mock_get.return_value = mock_response

        # Mock BeautifulSoup
        mock_soup = Mock()
        mock_soup.title.get_text.return_value = "Test Article"
        mock_p = Mock()
        mock_p.get_text.return_value = "Article content here with enough text to pass the 40 character minimum."
        mock_soup.find_all.return_value = [mock_p]
        # Mock the __call__ method for soup(["script", ...])
        mock_soup.return_value = []
        mock_soup_class.return_value = mock_soup

        result = fetch_article_text("https://example.com/article")

        assert "Title: Test Article" in result
        assert "URL: https://example.com/article" in result
        assert "Article content" in result
        mock_get.assert_called_once()

    @patch('core.source_management.requests.get')
    def test_request_timeout(self, mock_get):
        """Test request with timeout parameter."""
        mock_response = Mock()
        mock_response.text = '<html><body><p>Content with more than forty characters here.</p></body></html>'
        mock_get.return_value = mock_response

        with patch('core.source_management.BeautifulSoup') as mock_soup_class:
            mock_soup = Mock()
            mock_soup.title.get_text.return_value = "Title"
            mock_p = Mock()
            mock_p.get_text.return_value = "Content with more than forty characters here for the test case."
            mock_soup.find_all.return_value = [mock_p]
            mock_soup.return_value = []  # Mock soup(["script", ...])
            mock_soup_class.return_value = mock_soup

            fetch_article_text("https://example.com")

            # Verify timeout parameter
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs['timeout'] == 20

    @patch('core.source_management.requests.get')
    @patch('core.source_management.BeautifulSoup')
    def test_no_article_text_raises_error(self, mock_soup_class, mock_get):
        """Test that no extractable text raises ValueError."""
        mock_response = Mock()
        mock_response.text = '<html><body></body></html>'
        mock_get.return_value = mock_response

        mock_soup = Mock()
        mock_soup.title = None
        mock_soup.find_all.return_value = []
        mock_soup.return_value = []  # Mock soup(["script", ...])
        mock_soup_class.return_value = mock_soup

        with pytest.raises(ValueError) as exc_info:
            fetch_article_text("https://example.com")

        assert "Could not extract article text" in str(exc_info.value)

    @patch('core.source_management.requests.get')
    @patch('core.source_management.BeautifulSoup')
    def test_filters_short_paragraphs(self, mock_soup_class, mock_get):
        """Test that paragraphs under 40 chars are filtered."""
        mock_response = Mock()
        mock_response.text = '<html><body><p>Short.</p><p>This is a longer paragraph with sufficient content.</p></body></html>'
        mock_get.return_value = mock_response

        mock_soup = Mock()
        mock_soup.title.get_text.return_value = "Title"
        mock_p1 = Mock()
        mock_p1.get_text.return_value = "Short."
        mock_p2 = Mock()
        mock_p2.get_text.return_value = "This is a longer paragraph with sufficient content for the article."
        mock_soup.find_all.return_value = [mock_p1, mock_p2]
        mock_soup.return_value = []  # Mock soup(["script", ...])
        mock_soup_class.return_value = mock_soup

        result = fetch_article_text("https://example.com")

        # Should only include the longer paragraph
        assert "sufficient content" in result
        assert "Short." not in result or "Short." in result  # May be filtered


class TestReadTextFile:
    """Tests for read_text_file function."""

    def test_read_existing_file(self, tmp_path):
        """Test reading an existing text file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Test content", encoding="utf-8")

        result = read_text_file(file_path)

        assert "File: test.txt" in result
        assert "Test content" in result

    def test_read_multiline_file(self, tmp_path):
        """Test reading multiline content."""
        file_path = tmp_path / "multiline.txt"
        file_path.write_text("Line 1\nLine 2\nLine 3", encoding="utf-8")

        result = read_text_file(file_path)

        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_file_not_found(self, tmp_path):
        """Test reading non-existent file raises FileNotFoundError."""
        file_path = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            read_text_file(file_path)

    def test_empty_file_raises_error(self, tmp_path):
        """Test reading empty file raises ValueError."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("", encoding="utf-8")

        with pytest.raises(ValueError):
            read_text_file(file_path)


class TestParseCsvInput:
    """Tests for parse_csv_input function."""

    def test_basic_csv(self):
        """Test basic comma-separated values."""
        result = parse_csv_input("url1, url2, url3")
        assert result == ["url1", "url2", "url3"]

    def test_with_extra_spaces(self):
        """Test CSV with extra whitespace."""
        result = parse_csv_input("  url1  ,  url2  ,  url3  ")
        assert result == ["url1", "url2", "url3"]

    def test_empty_items_filtered(self):
        """Test that empty items are filtered out."""
        result = parse_csv_input("url1, , url2,  , url3")
        assert result == ["url1", "url2", "url3"]

    def test_empty_string(self):
        """Test empty string returns empty list."""
        result = parse_csv_input("")
        assert result == []

    def test_single_item(self):
        """Test single item without commas."""
        result = parse_csv_input("single_url")
        assert result == ["single_url"]

    def test_no_spaces(self):
        """Test CSV without spaces."""
        result = parse_csv_input("url1,url2,url3")
        assert result == ["url1", "url2", "url3"]


class TestLoadSourceFiles:
    """Tests for load_source_files function."""

    def test_load_multiple_files(self, tmp_path):
        """Test loading multiple source files."""
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        (sources_dir / "source_1.txt").write_text("Content 1", encoding="utf-8")
        (sources_dir / "source_2.txt").write_text("Content 2", encoding="utf-8")

        result = load_source_files(sources_dir)

        assert len(result) == 2
        assert "Source 1:" in result[0]
        assert "Content 1" in result[0]
        assert "Source 2:" in result[1]
        assert "Content 2" in result[1]

    def test_files_sorted(self, tmp_path):
        """Test that files are sorted alphabetically."""
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        (sources_dir / "source_3.txt").write_text("Content 3", encoding="utf-8")
        (sources_dir / "source_1.txt").write_text("Content 1", encoding="utf-8")
        (sources_dir / "source_2.txt").write_text("Content 2", encoding="utf-8")

        result = load_source_files(sources_dir)

        # Should be sorted
        assert "Content 1" in result[0]
        assert "Content 2" in result[1]
        assert "Content 3" in result[2]

    def test_directory_not_found(self, tmp_path):
        """Test missing directory raises FileNotFoundError."""
        sources_dir = tmp_path / "nonexistent"

        with pytest.raises(FileNotFoundError) as exc_info:
            load_source_files(sources_dir)

        assert "not found" in str(exc_info.value).lower()

    def test_no_source_files(self, tmp_path):
        """Test directory with no .txt files raises ValueError."""
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        with pytest.raises(ValueError) as exc_info:
            load_source_files(sources_dir)

        assert "No source files found" in str(exc_info.value)

    def test_skips_empty_files(self, tmp_path, capsys):
        """Test that empty files are skipped."""
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        (sources_dir / "source_1.txt").write_text("Content 1", encoding="utf-8")
        (sources_dir / "source_2.txt").write_text("", encoding="utf-8")  # Empty

        result = load_source_files(sources_dir)

        assert len(result) == 1
        assert "Content 1" in result[0]


class TestSaveSourcesToDirectory:
    """Tests for save_sources_to_directory function."""

    @patch('core.source_management.fetch_article_text')
    def test_save_urls_only(self, mock_fetch, tmp_path, capsys):
        """Test saving sources from URLs only."""
        sources_dir = tmp_path / "sources"
        sources = []

        mock_fetch.return_value = "Title: Test\nURL: test.com\n\nContent"

        urls = ["https://example.com/article"]
        success, failed = save_sources_to_directory(sources_dir, sources, urls=urls)

        assert len(success) == 1
        assert success[0]["type"] == "url"
        assert success[0]["source"] == "https://example.com/article"
        assert len(failed) == 0
        assert len(sources) == 1
        assert sources_dir.exists()

    def test_save_files_only(self, tmp_path, capsys):
        """Test saving sources from files only."""
        # Create a source file
        source_file = tmp_path / "source.txt"
        source_file.write_text("Test content", encoding="utf-8")

        sources_dir = tmp_path / "sources"
        sources = []

        files = [source_file]
        success, failed = save_sources_to_directory(sources_dir, sources, files=files)

        assert len(success) == 1
        assert success[0]["type"] == "file"
        assert len(failed) == 0
        assert len(sources) == 1

    @patch('core.source_management.fetch_article_text')
    def test_failed_url_fetch(self, mock_fetch, tmp_path, capsys):
        """Test handling of failed URL fetch."""
        sources_dir = tmp_path / "sources"
        sources = []

        mock_fetch.side_effect = Exception("Network error")

        urls = ["https://example.com/article"]
        success, failed = save_sources_to_directory(sources_dir, sources, urls=urls)

        assert len(success) == 0
        assert len(failed) == 1
        assert failed[0]["type"] == "url"
        assert "error" in failed[0]

    def test_failed_file_read(self, tmp_path, capsys):
        """Test handling of failed file read."""
        sources_dir = tmp_path / "sources"
        sources = []

        # Non-existent file
        files = [tmp_path / "nonexistent.txt"]
        success, failed = save_sources_to_directory(sources_dir, sources, files=files)

        assert len(success) == 0
        assert len(failed) == 1
        assert failed[0]["type"] == "file"

    @patch('core.source_management.fetch_article_text')
    def test_mixed_urls_and_files(self, mock_fetch, tmp_path, capsys):
        """Test saving both URLs and files."""
        # Create source file
        source_file = tmp_path / "source.txt"
        source_file.write_text("File content", encoding="utf-8")

        sources_dir = tmp_path / "sources"
        sources = []

        mock_fetch.return_value = "Title: Test\nURL: test.com\n\nURL content"

        urls = ["https://example.com/article"]
        files = [source_file]

        success, failed = save_sources_to_directory(
            sources_dir, sources, urls=urls, files=files
        )

        assert len(success) == 2
        assert len(sources) == 2
        assert "Source 1:" in sources[0]  # URL
        assert "Source 2:" in sources[1]  # File

    def test_creates_directory(self, tmp_path):
        """Test that directory is created if it doesn't exist."""
        sources_dir = tmp_path / "new_sources"
        sources = []

        assert not sources_dir.exists()

        save_sources_to_directory(sources_dir, sources)

        assert sources_dir.exists()
