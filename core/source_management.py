"""
Source management utilities for podcast creation.

This module provides functions to:
- Fetch article text from URLs
- Read text from local files
- Parse comma-separated inputs
- Load and save source materials
"""

from pathlib import Path
from typing import List, Tuple, Dict, Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from core.file_utils import save_text_file, read_text_file as _read_text_file


def fetch_article_text(url: str) -> str:
    """
    Fetch and extract article text from a URL.

    Args:
        url: The URL to fetch

    Returns:
        Formatted text with title, URL, and article content

    Raises:
        requests.HTTPError: If the request fails
        ValueError: If no article text could be extracted

    Examples:
        >>> text = fetch_article_text("https://example.com/article")
        >>> # Returns: "Title: Article Title\\nURL: https://...\\n\\nArticle content..."
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else "Untitled"

    # Extract paragraphs
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p) > 40]

    article_text = "\n".join(paragraphs[:80]).strip()

    if not article_text:
        raise ValueError(f"Could not extract article text from: {url}")

    return f"Title: {title}\nURL: {url}\n\n{article_text}"


def read_text_file(file_path: Path) -> str:
    """
    Read text from a file and format for podcast source.

    This is a wrapper around core.file_utils.read_text_file that
    adds the filename to the output.

    Args:
        file_path: Path to the text file

    Returns:
        Formatted text with filename and content

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty
    """
    content = _read_text_file(file_path)
    return f"File: {file_path.name}\n\n{content}"


def parse_csv_input(raw_text: str) -> List[str]:
    """
    Parse comma-separated input into a list of items.

    Strips whitespace from each item and filters out empty items.

    Args:
        raw_text: Comma-separated string

    Returns:
        List of non-empty, stripped items

    Examples:
        >>> parse_csv_input("url1, url2, url3")
        ['url1', 'url2', 'url3']
        >>> parse_csv_input("file1,  , file2")
        ['file1', 'file2']
        >>> parse_csv_input("")
        []
    """
    return [item.strip() for item in raw_text.split(",") if item.strip()]


def load_source_files(sources_dir: Path) -> List[str]:
    """
    Load all source text files from a directory.

    Reads all .txt files in the directory and formats them as
    numbered sources.

    Args:
        sources_dir: Directory containing source .txt files

    Returns:
        List of formatted source texts

    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If no source files found

    Examples:
        >>> sources = load_source_files(Path("output/episode/sources"))
        >>> # Returns: ["Source 1:\\nContent...", "Source 2:\\nContent..."]
    """
    if not sources_dir.exists():
        raise FileNotFoundError(f"Sources directory not found: {sources_dir}")

    source_files = sorted(sources_dir.glob("*.txt"))
    if not source_files:
        raise ValueError(f"No source files found in: {sources_dir}")

    all_sources = []
    for i, source_file in enumerate(source_files, start=1):
        try:
            content = source_file.read_text(encoding="utf-8").strip()
            if content:
                all_sources.append(f"Source {i}:\n{content}")
        except Exception as e:
            # Skip files that can't be read
            print(f"  Warning: Could not read {source_file.name}: {e}")

    return all_sources


def save_sources_to_directory(
    sources_dir: Path,
    sources: List[str],
    urls: List[str] = None,
    files: List[Path] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fetch/read sources and save them to a directory.

    Fetches articles from URLs and/or reads local files, saves them
    to the sources directory, and returns metadata about successful
    and failed operations.

    Args:
        sources_dir: Directory where sources should be saved
        sources: List to append formatted source texts to (modified in place)
        urls: Optional list of URLs to fetch
        files: Optional list of file paths to read

    Returns:
        Tuple of (successful_sources, failed_sources) where each is a list of dicts

    Examples:
        >>> sources = []
        >>> success, failed = save_sources_to_directory(
        ...     Path("output/episode/sources"),
        ...     sources,
        ...     urls=["https://example.com/article"],
        ...     files=[Path("local.txt")]
        ... )
    """
    sources_dir.mkdir(parents=True, exist_ok=True)

    successful_sources = []
    failed_sources = []
    source_counter = 1

    # Fetch URLs
    if urls:
        print("Fetching article content...")
        for url in urls:
            try:
                article_text = fetch_article_text(url)
                sources.append(f"Source {source_counter}:\n{article_text}")

                domain = urlparse(url).netloc.replace(".", "_")
                source_file = sources_dir / f"source_{source_counter}_{domain}.txt"
                save_text_file(article_text, source_file)
                print(f"Saved URL source {source_counter}: {source_file.resolve()}")

                successful_sources.append({
                    "type": "url",
                    "source": url,
                    "saved_file": str(source_file)
                })
                source_counter += 1
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                failed_sources.append({
                    "type": "url",
                    "source": url,
                    "error": str(e)
                })

    # Read local files
    if files:
        print("Reading local text files...")
        for file_path in files:
            try:
                file_text = read_text_file(file_path)
                sources.append(f"Source {source_counter}:\n{file_text}")

                copied_file = sources_dir / f"source_{source_counter}_{file_path.name}"
                save_text_file(
                    file_path.read_text(encoding="utf-8"),
                    copied_file
                )
                print(f"Copied file source {source_counter}: {copied_file.resolve()}")

                successful_sources.append({
                    "type": "file",
                    "source": str(file_path),
                    "saved_file": str(copied_file)
                })
                source_counter += 1
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")
                failed_sources.append({
                    "type": "file",
                    "source": str(file_path),
                    "error": str(e)
                })

    return successful_sources, failed_sources
