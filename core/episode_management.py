"""
Episode lifecycle management utilities for podcast creation.

This module provides functions to manage podcast episodes including:
- Creating episode directories with unique IDs
- Saving and loading episode metadata
- Managing episode index
- Creating episode summaries
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

from core.file_utils import save_json, load_json
from core.validation import sanitize_filename


def create_episode_directory(
    output_root: Path,
    topic: str,
    timestamp_suffix: str = None
) -> Tuple[Path, str]:
    """
    Create a unique episode directory.

    Creates a directory with a sanitized topic name and optional timestamp
    to ensure uniqueness across multiple episode generations.

    Args:
        output_root: Root directory for all episodes
        topic: Episode topic (will be sanitized for filename)
        timestamp_suffix: Optional timestamp string. If None, generates current timestamp.

    Returns:
        Tuple of (episode_directory_path, episode_id)

    Examples:
        >>> episode_dir, episode_id = create_episode_directory(
        ...     Path("output"),
        ...     "AI Trends"
        ... )
        >>> # Returns: (Path("output/AI_Trends_2026-04-07_153045"), "AI_Trends_2026-04-07_153045")
    """
    safe_topic = sanitize_filename(topic)

    if timestamp_suffix is None:
        timestamp_suffix = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    episode_id = f"{safe_topic}_{timestamp_suffix}"

    output_root.mkdir(parents=True, exist_ok=True)
    episode_dir = output_root / episode_id
    episode_dir.mkdir(parents=True, exist_ok=True)

    return episode_dir, episode_id


def save_episode_metadata(episode_dir: Path, metadata: Dict[str, Any]) -> Path:
    """
    Save episode metadata to metadata.json file.

    Args:
        episode_dir: Episode directory path
        metadata: Metadata dictionary to save

    Returns:
        Path to the saved metadata file

    Examples:
        >>> metadata = {
        ...     "episode_id": "AI_Trends_2026-04-07_153045",
        ...     "topic": "AI Trends",
        ...     "tone": "educational"
        ... }
        >>> metadata_path = save_episode_metadata(Path("output/episode"), metadata)
    """
    metadata_file = episode_dir / "metadata.json"
    save_json(metadata, metadata_file)
    return metadata_file


def create_episode_summary(
    metadata: Dict[str, Any],
    episode_dir: Path,
    additional_fields: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a summary of episode information for the episode index.

    Extracts key fields from metadata and adds file paths for quick access.

    Args:
        metadata: Full episode metadata
        episode_dir: Episode directory path
        additional_fields: Optional additional fields to include in summary

    Returns:
        Dictionary containing episode summary

    Examples:
        >>> summary = create_episode_summary(
        ...     metadata,
        ...     Path("output/episode"),
        ...     {"num_sources": 3}
        ... )
    """
    summary = {
        "created_at": metadata.get("created_at"),
        "episode_id": metadata.get("episode_id"),
        "topic": metadata.get("topic"),
        "tone": metadata.get("tone"),
        "voice": metadata.get("voice"),
        "length": metadata.get("length"),
        "episode_dir": str(episode_dir),
        "metadata_file": str(episode_dir / "metadata.json"),
        "script_file": str(episode_dir / "script.txt"),
        "show_notes_file": str(episode_dir / "show_notes.txt"),
    }

    # Add audio file path if voice is specified
    if metadata.get("voice"):
        summary["audio_file"] = str(episode_dir / f"podcast_{metadata['voice']}.mp3")

    # Add any additional fields
    if additional_fields:
        summary.update(additional_fields)

    return summary


def update_episode_index(index_path: Path, episode_summary: Dict[str, Any]) -> None:
    """
    Update the global episode index with a new episode.

    Loads existing index (or creates new), appends the episode summary,
    and saves it back to the file.

    Args:
        index_path: Path to the episode index JSON file
        episode_summary: Episode summary to add to index

    Examples:
        >>> update_episode_index(
        ...     Path("output/episode_index.json"),
        ...     episode_summary
        ... )
    """
    if index_path.exists():
        try:
            index_data = load_json(index_path)
            if not isinstance(index_data, list):
                index_data = []
        except Exception:
            # If file is corrupted or invalid, start fresh
            index_data = []
    else:
        index_data = []

    index_data.append(episode_summary)
    save_json(index_data, index_path)


def load_episode_index(index_path: Path) -> List[Dict[str, Any]]:
    """
    Load the episode index from file.

    Args:
        index_path: Path to the episode index JSON file

    Returns:
        List of episode summaries

    Raises:
        FileNotFoundError: If index file doesn't exist

    Examples:
        >>> episodes = load_episode_index(Path("output/episode_index.json"))
        >>> len(episodes)
        5
    """
    if not index_path.exists():
        raise FileNotFoundError(f"Episode index not found: {index_path}")

    index_data = load_json(index_path)

    if not isinstance(index_data, list):
        raise ValueError(f"Invalid episode index format: expected list, got {type(index_data)}")

    return index_data


def load_episode_metadata(metadata_path: Path) -> Dict[str, Any]:
    """
    Load episode metadata from metadata.json file.

    Args:
        metadata_path: Path to the metadata JSON file

    Returns:
        Metadata dictionary

    Raises:
        FileNotFoundError: If metadata file doesn't exist
        ValueError: If metadata format is invalid

    Examples:
        >>> metadata = load_episode_metadata(Path("output/episode/metadata.json"))
        >>> metadata['topic']
        'AI Trends'
    """
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    try:
        metadata = load_json(metadata_path)
        return metadata
    except Exception as e:
        raise ValueError(f"Error loading metadata: {e}")
