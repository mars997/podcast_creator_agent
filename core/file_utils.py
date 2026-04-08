"""
File operation utilities for podcast creation.

This module provides common file operations including:
- JSON file saving
- Text file saving
- Directory creation
"""

import json
from pathlib import Path
from typing import Union, Dict, List, Any


def save_json(data: Union[Dict[str, Any], List[Any]], file_path: Path) -> None:
    """
    Save data to a JSON file with proper formatting.

    Args:
        data: Dictionary or list to save as JSON
        file_path: Path where the JSON file should be saved

    Examples:
        >>> save_json({"title": "My Podcast"}, Path("metadata.json"))
        >>> save_json([{"id": 1}, {"id": 2}], Path("index.json"))
    """
    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def save_text_file(content: str, file_path: Path) -> None:
    """
    Save text content to a file.

    Args:
        content: Text content to save
        file_path: Path where the text file should be saved

    Examples:
        >>> save_text_file("Episode script...", Path("script.txt"))
    """
    file_path.write_text(content, encoding="utf-8")


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory

    Returns:
        The path object (for chaining)

    Examples:
        >>> episode_dir = ensure_directory(Path("output/my_episode"))
        >>> sources_dir = ensure_directory(episode_dir / "sources")
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_text_file(file_path: Path) -> str:
    """
    Read text content from a file with validation.

    Args:
        file_path: Path to the text file

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is empty

    Examples:
        >>> content = read_text_file(Path("source.txt"))
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = file_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"File is empty: {file_path}")

    return content


def load_json(file_path: Path) -> Union[Dict[str, Any], List[Any]]:
    """
    Load data from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data (dict or list)

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON

    Examples:
        >>> metadata = load_json(Path("metadata.json"))
        >>> episodes = load_json(Path("episode_index.json"))
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return json.loads(file_path.read_text(encoding="utf-8"))
