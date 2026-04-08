"""
RSS feed parsing utilities for podcast creation.

This module provides functions to parse RSS feeds and extract article information.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import feedparser

from core.file_utils import save_json


def parse_rss_feed(feed_url: str, max_items: int = 10) -> List[Dict[str, str]]:
    """
    Parse an RSS feed and extract article information.

    Args:
        feed_url: URL of the RSS feed
        max_items: Maximum number of items to extract (default: 10)

    Returns:
        List of article dictionaries with keys: title, link, description, published, author

    Raises:
        ValueError: If feed cannot be parsed or contains no entries

    Examples:
        >>> articles = parse_rss_feed("https://example.com/feed.rss", max_items=5)
        >>> len(articles)
        5
        >>> articles[0]['title']
        'Article Title'
    """
    print(f"\nFetching RSS feed: {feed_url}")

    try:
        feed = feedparser.parse(feed_url)

        # Check for parsing errors
        if feed.bozo and not feed.entries:
            error_msg = feed.get('bozo_exception', 'Unknown error')
            raise ValueError(f"Failed to parse RSS feed: {error_msg}")

        if not feed.entries:
            raise ValueError("No entries found in RSS feed")

        # Display feed information
        feed_title = feed.feed.get('title', 'Unknown')
        print(f"  Feed title: {feed_title}")
        print(f"  Total entries: {len(feed.entries)}")

        # Extract article information
        articles = []
        for entry in feed.entries[:max_items]:
            article = {
                'title': entry.get('title', 'Untitled'),
                'link': entry.get('link', ''),
                'description': entry.get('description', '') or entry.get('summary', ''),
                'published': entry.get('published', '') or entry.get('updated', ''),
                'author': entry.get('author', ''),
            }
            articles.append(article)

        return articles

    except Exception as e:
        raise ValueError(f"Error parsing RSS feed: {e}")


def save_rss_info(
    sources_dir: Path,
    feed_url: str,
    articles: List[Dict[str, Any]]
) -> Path:
    """
    Save RSS feed information to a JSON file.

    Creates an rss_feed_info.json file in the sources directory containing
    metadata about the RSS feed and the articles fetched.

    Args:
        sources_dir: Directory where RSS info should be saved
        feed_url: URL of the RSS feed
        articles: List of article information dictionaries

    Returns:
        Path to the saved RSS info file

    Examples:
        >>> articles = [
        ...     {'title': 'Article 1', 'url': 'http://example.com/1'},
        ...     {'title': 'Article 2', 'url': 'http://example.com/2'}
        ... ]
        >>> rss_info_path = save_rss_info(
        ...     Path("output/episode/sources"),
        ...     "https://example.com/feed.rss",
        ...     articles
        ... )
    """
    sources_dir.mkdir(parents=True, exist_ok=True)

    rss_info_file = sources_dir / "rss_feed_info.json"

    rss_info = {
        'feed_url': feed_url,
        'fetched_at': datetime.now().isoformat(),
        'num_articles': len(articles),
        'articles': articles
    }

    save_json(rss_info, rss_info_file)
    print(f"\n  RSS info saved: {rss_info_file.name}")

    return rss_info_file
