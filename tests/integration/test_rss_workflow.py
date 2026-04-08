"""
Integration tests for RSS feed workflow.

These tests verify the RSS feed parsing and podcast generation workflow.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from core.rss_utils import parse_rss_feed, save_rss_info
from core.source_management import save_sources_to_directory
from core.episode_management import create_episode_directory


@pytest.fixture
def mock_rss_feed():
    """Create a mock RSS feed response"""
    mock_feed = MagicMock()
    mock_feed.bozo = False

    # Mock feed metadata
    mock_feed.feed.title = "Tech News Feed"

    # Create mock entries using MagicMock with get() method support
    mock_entry1 = MagicMock()
    mock_entry1.get = lambda k, default='': {
        'title': 'Article 1: AI Advances',
        'link': 'https://example.com/article1',
        'description': 'Summary of AI advances',
        'summary': '',
        'published': '2024-01-01T10:00:00Z',
        'updated': '',
        'author': 'John Doe'
    }.get(k, default)

    mock_entry2 = MagicMock()
    mock_entry2.get = lambda k, default='': {
        'title': 'Article 2: Machine Learning',
        'link': 'https://example.com/article2',
        'description': 'Machine learning trends',
        'summary': '',
        'published': '2024-01-02T11:00:00Z',
        'updated': '',
        'author': 'Jane Smith'
    }.get(k, default)

    mock_entry3 = MagicMock()
    mock_entry3.get = lambda k, default='': {
        'title': 'Article 3: Data Science',
        'link': 'https://example.com/article3',
        'description': '',
        'summary': 'Data science overview',  # Using summary instead of description
        'published': '2024-01-03T12:00:00Z',
        'updated': '',
        'author': ''
    }.get(k, default)

    mock_feed.entries = [mock_entry1, mock_entry2, mock_entry3]

    return mock_feed


class TestRSSWorkflow:
    """Test RSS feed parsing and podcast generation workflow"""

    def test_parse_rss_feed_basic(self, mock_rss_feed):
        """Test basic RSS feed parsing"""
        with patch('feedparser.parse', return_value=mock_rss_feed):
            articles = parse_rss_feed('https://example.com/feed.xml', max_items=10)

        assert len(articles) == 3
        assert articles[0]['title'] == 'Article 1: AI Advances'
        assert articles[0]['link'] == 'https://example.com/article1'
        assert articles[0]['description'] == 'Summary of AI advances'
        assert articles[0]['published'] == '2024-01-01T10:00:00Z'
        assert articles[0]['author'] == 'John Doe'

    def test_parse_rss_feed_with_limit(self, mock_rss_feed):
        """Test RSS feed parsing with max_items limit"""
        with patch('feedparser.parse', return_value=mock_rss_feed):
            articles = parse_rss_feed('https://example.com/feed.xml', max_items=2)

        assert len(articles) == 2
        assert articles[0]['title'] == 'Article 1: AI Advances'
        assert articles[1]['title'] == 'Article 2: Machine Learning'

    def test_parse_rss_feed_handles_summary_field(self, mock_rss_feed):
        """Test that RSS parser handles 'summary' field when 'description' is missing"""
        with patch('feedparser.parse', return_value=mock_rss_feed):
            articles = parse_rss_feed('https://example.com/feed.xml', max_items=10)

        # Third article uses 'summary' instead of 'description'
        assert articles[2]['description'] == 'Data science overview'

    def test_parse_rss_feed_handles_missing_author(self, mock_rss_feed):
        """Test that RSS parser handles missing author field"""
        with patch('feedparser.parse', return_value=mock_rss_feed):
            articles = parse_rss_feed('https://example.com/feed.xml', max_items=10)

        # Third article has empty author
        assert articles[2]['author'] == ''

    def test_parse_rss_feed_empty_feed(self):
        """Test handling of empty RSS feed"""
        mock_empty_feed = MagicMock()
        mock_empty_feed.bozo = False
        mock_empty_feed.entries = []

        with patch('feedparser.parse', return_value=mock_empty_feed):
            with pytest.raises(ValueError, match="No entries found in RSS feed"):
                parse_rss_feed('https://example.com/feed.xml')

    def test_parse_rss_feed_malformed(self):
        """Test handling of malformed RSS feed"""
        mock_bad_feed = MagicMock()
        mock_bad_feed.bozo = True
        mock_bad_feed.entries = []
        mock_bad_feed.get = lambda k, default=None: Exception("Parse error") if k == 'bozo_exception' else default

        with patch('feedparser.parse', return_value=mock_bad_feed):
            with pytest.raises(ValueError, match="Failed to parse RSS feed"):
                parse_rss_feed('https://example.com/feed.xml')

    def test_save_rss_info(self, tmp_path):
        """Test saving RSS feed information"""
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        feed_url = 'https://example.com/feed.xml'
        articles = [
            {'title': 'Article 1', 'link': 'https://example.com/1'},
            {'title': 'Article 2', 'link': 'https://example.com/2'}
        ]

        rss_file = save_rss_info(sources_dir, feed_url, articles)

        assert rss_file.exists()
        assert rss_file.name == "rss_feed_info.json"

        saved_data = json.loads(rss_file.read_text())
        assert saved_data['feed_url'] == 'https://example.com/feed.xml'
        assert saved_data['num_articles'] == 2
        assert len(saved_data['articles']) == 2

    def test_rss_to_episode_workflow(self, mock_rss_feed, tmp_path):
        """Test complete workflow from RSS feed to episode creation"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Parse RSS feed
        with patch('feedparser.parse', return_value=mock_rss_feed):
            articles = parse_rss_feed('https://example.com/feed.xml', max_items=2)

        assert len(articles) == 2

        # Create episode directory
        topic = "Tech News Roundup"
        episode_dir, episode_id = create_episode_directory(output_dir, topic)

        sources_dir = episode_dir / "sources"
        sources_dir.mkdir()

        # Save RSS info
        feed_url = 'https://example.com/feed.xml'
        rss_file = save_rss_info(sources_dir, feed_url, articles)
        assert rss_file.exists()

        # Fetch article content
        all_sources = []
        with patch('core.source_management.fetch_article_text') as mock_fetch:
            mock_fetch.side_effect = [
                "Full content of article 1",
                "Full content of article 2"
            ]

            urls = [article['link'] for article in articles]
            successful, failed = save_sources_to_directory(
                sources_dir,
                all_sources,
                urls=urls
            )

        assert len(successful) == 2
        assert len(failed) == 0
        assert len(all_sources) == 2

        # Verify source files saved
        source_files = list(sources_dir.glob("source_*.txt"))
        assert len(source_files) == 2

    def test_rss_partial_fetch_failure(self, mock_rss_feed, tmp_path):
        """Test handling when some RSS articles fail to fetch"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Parse RSS feed
        with patch('feedparser.parse', return_value=mock_rss_feed):
            articles = parse_rss_feed('https://example.com/feed.xml', max_items=3)

        assert len(articles) == 3

        # Create episode directory
        episode_dir, episode_id = create_episode_directory(output_dir, "Test")
        sources_dir = episode_dir / "sources"
        sources_dir.mkdir()

        # Fetch articles with some failures
        all_sources = []
        with patch('core.source_management.fetch_article_text') as mock_fetch:
            mock_fetch.side_effect = [
                "Content 1",
                Exception("404 Not Found"),
                "Content 3"
            ]

            urls = [article['link'] for article in articles]
            successful, failed = save_sources_to_directory(
                sources_dir,
                all_sources,
                urls=urls
            )

        assert len(successful) == 2
        assert len(failed) == 1
        assert len(all_sources) == 2

        # Verify successful articles saved
        assert "Content 1" in all_sources[0]
        assert "Content 3" in all_sources[1]

        # Verify failed article recorded
        assert failed[0]['source'] == 'https://example.com/article2'
        assert "404 Not Found" in failed[0]['error']

    def test_rss_feed_with_special_characters(self):
        """Test RSS feed parsing with special characters in content"""
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.feed.title = "Tech News"

        mock_entry = MagicMock()
        mock_entry.get = lambda k, default='': {
            'title': 'AI & ML: The Future™',
            'link': 'https://example.com/article',
            'description': 'Exploring AI & ML technologies™ in 2024',
            'summary': '',
            'published': '2024-01-01T10:00:00Z',
            'updated': '',
            'author': 'O\'Brien'
        }.get(k, default)

        mock_feed.entries = [mock_entry]

        with patch('feedparser.parse', return_value=mock_feed):
            articles = parse_rss_feed('https://example.com/feed.xml')

        assert articles[0]['title'] == 'AI & ML: The Future™'
        assert articles[0]['description'] == 'Exploring AI & ML technologies™ in 2024'
        assert articles[0]['author'] == 'O\'Brien'
