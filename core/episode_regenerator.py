"""
Episode regeneration utilities for podcast creation.

This module provides functions to regenerate podcast episodes from
existing metadata and source materials.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index,
)
from core.source_management import load_source_files
from core.content_generation import build_script, build_show_notes, generate_audio
from core.file_utils import save_text_file
from core.validation import sanitize_filename, get_word_range


def regenerate_episode(
    original_metadata: Dict[str, Any],
    episode_dir_path: Path,
    llm_provider,
    tts_provider,
    output_root: Path,
    index_path: Path
) -> Tuple[Path, str]:
    """
    Regenerate a podcast episode from existing metadata and sources.

    Creates a new episode with "_regenerated_" suffix using the same
    settings and sources as the original episode.

    Args:
        original_metadata: Metadata dictionary from the original episode
        episode_dir_path: Path to the original episode directory
        llm_provider: LLM provider instance for script generation
        tts_provider: TTS provider instance for audio generation
        output_root: Root directory for output
        index_path: Path to the episode index file

    Returns:
        Tuple of (new_episode_directory, new_episode_id)

    Examples:
        >>> new_dir, new_id = regenerate_episode(
        ...     original_metadata,
        ...     Path("output/AI_Trends_2026-04-07_153000"),
        ...     llm_provider,
        ...     tts_provider,
        ...     Path("output"),
        ...     Path("output/episode_index.json")
        ... )
        >>> print(new_id)
        'AI_Trends_regenerated_2026-04-07_160000'
    """
    print("\n" + "=" * 70)
    print("Regenerating Episode")
    print("=" * 70)

    # Extract settings from metadata
    topic = original_metadata.get('topic', 'Regenerated Episode')
    tone = original_metadata.get('tone', 'educational')
    voice = original_metadata.get('voice', 'nova')
    length = original_metadata.get('length', 'medium')
    word_range = original_metadata.get('word_range_target', get_word_range(length))

    # Get models from metadata (for reference)
    models = original_metadata.get('models', {})
    original_script_model = models.get('script_model', 'N/A')
    original_tts_model = models.get('tts_model', 'N/A')

    print(f"\nOriginal Episode Settings:")
    print(f"  Topic: {topic}")
    print(f"  Tone: {tone}")
    print(f"  Voice: {voice}")
    print(f"  Length: {length} ({word_range})")
    print(f"  Original Script Model: {original_script_model}")
    print(f"  Original TTS Model: {original_tts_model}")

    # Load sources from original episode
    sources_dir = episode_dir_path / "sources"
    print(f"\nLoading sources from: {sources_dir}")

    all_sources = load_source_files(sources_dir)

    if not all_sources:
        raise ValueError("No source content could be loaded")

    print(f"  Total sources loaded: {len(all_sources)}")

    combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(all_sources)

    # Create new episode folder with timestamp and "regenerated" marker
    safe_topic = sanitize_filename(topic)
    timestamp_suffix = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    unique_episode_id = f"{safe_topic}_regenerated_{timestamp_suffix}"

    output_root.mkdir(parents=True, exist_ok=True)

    new_episode_dir = output_root / unique_episode_id
    new_episode_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nNew episode folder: {new_episode_dir}")

    # Copy sources to new episode folder
    new_sources_dir = new_episode_dir / "sources"
    new_sources_dir.mkdir(exist_ok=True)

    original_sources_dir = episode_dir_path / "sources"
    for source_file in original_sources_dir.glob("*.txt"):
        dest_file = new_sources_dir / source_file.name
        save_text_file(
            source_file.read_text(encoding="utf-8"),
            dest_file
        )

    num_sources_copied = len(list(new_sources_dir.glob('*.txt')))
    print(f"  Copied {num_sources_copied} source files")

    # Generate script
    print("\nGenerating new podcast script...")
    script = build_script(llm_provider, topic, tone, word_range, combined_source_text)

    script_file = new_episode_dir / "script.txt"
    save_text_file(script, script_file)
    print(f"  Script saved: {script_file.name}")

    # Generate show notes
    print("\nGenerating show notes...")
    show_notes = build_show_notes(llm_provider, script)

    show_notes_file = new_episode_dir / "show_notes.txt"
    save_text_file(show_notes, show_notes_file)
    print(f"  Show notes saved: {show_notes_file.name}")

    # Generate audio
    audio_file = new_episode_dir / f"podcast_{voice}.mp3"

    print("\nGenerating audio...")
    generate_audio(tts_provider, script, voice, audio_file)
    print(f"  Audio saved: {audio_file.name}")

    # Save metadata
    created_at = datetime.now().isoformat()

    new_metadata = {
        "created_at": created_at,
        "episode_id": unique_episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "regenerated_from": {
            "original_episode_id": original_metadata.get('episode_id', topic),
            "original_created_at": original_metadata.get('created_at'),
            "original_episode_dir": str(episode_dir_path)
        },
        "providers": {
            "llm_provider": llm_provider.provider_name,
            "llm_model": llm_provider.model_name,
            "tts_provider": tts_provider.provider_name,
            "tts_model": tts_provider.model_name
        },
        "models": {
            "script_model": llm_provider.model_name,
            "tts_model": tts_provider.model_name
        },
        "inputs": original_metadata.get('inputs', {}),
        "outputs": {
            "episode_dir": str(new_episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file)
        }
    }

    metadata_file = save_episode_metadata(new_episode_dir, new_metadata)
    print(f"  Metadata saved: {metadata_file.name}")

    # Create and save episode summary
    episode_summary = create_episode_summary(
        new_metadata,
        new_episode_dir,
        {
            "regenerated": True,
            "regenerated_from": original_metadata.get('episode_id', topic)
        }
    )

    update_episode_index(index_path, episode_summary)
    print(f"\nEpisode index updated: {index_path}")

    print("\n" + "=" * 70)
    print(f"Regeneration Complete!")
    print("=" * 70)
    print(f"\nNew Episode ID: {unique_episode_id}")
    print(f"Location: {new_episode_dir}")
    print(f"\nFiles generated:")
    print(f"  - {script_file.name}")
    print(f"  - {show_notes_file.name}")
    print(f"  - {audio_file.name}")
    print(f"  - {metadata_file.name}")

    return new_episode_dir, unique_episode_id
