"""
Demo script for Step 18 - Creates a mock regenerated episode
This demonstrates the complete regeneration flow without requiring API access.
"""

import json
from pathlib import Path
from datetime import datetime


def demo_regeneration():
    """Create a complete mock regenerated episode"""
    print("=" * 70)
    print("Step 18 Demo: Complete Regeneration (Mock)")
    print("=" * 70)

    # Use the existing ai_trending episode as the source
    output_root = Path("output")
    original_episode_dir = output_root / "ai_trending"

    if not original_episode_dir.exists():
        print("\nError: Original episode 'ai_trending' not found")
        return

    print(f"\nOriginal episode: {original_episode_dir}")

    # Load original metadata
    original_metadata_path = original_episode_dir / "metadata.json"
    if not original_metadata_path.exists():
        print("Error: Original metadata not found")
        return

    original_metadata = json.loads(original_metadata_path.read_text(encoding="utf-8"))

    topic = original_metadata.get('topic', 'Unknown')
    tone = original_metadata.get('tone', 'educational')
    voice = original_metadata.get('voice', 'nova')
    length = original_metadata.get('length', 'medium')

    print(f"\nOriginal Settings:")
    print(f"  Topic: {topic}")
    print(f"  Tone: {tone}")
    print(f"  Voice: {voice}")
    print(f"  Length: {length}")

    # Create regenerated episode folder
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    safe_topic = topic.replace(" ", "_")
    new_episode_id = f"{safe_topic}_regenerated_demo_{timestamp}"
    new_episode_dir = output_root / new_episode_id

    print(f"\nCreating regenerated episode: {new_episode_id}")
    new_episode_dir.mkdir(parents=True, exist_ok=True)

    # Copy sources
    new_sources_dir = new_episode_dir / "sources"
    new_sources_dir.mkdir(exist_ok=True)

    original_sources_dir = original_episode_dir / "sources"
    source_count = 0
    for source_file in original_sources_dir.glob("*.txt"):
        dest_file = new_sources_dir / source_file.name
        dest_file.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")
        source_count += 1

    print(f"  Copied {source_count} source files")

    # Create mock script
    mock_script = f"""Regenerated Episode: {topic}

[This is a MOCK regenerated episode for demonstration purposes]

Welcome to this regenerated episode on {topic}!

This episode was regenerated from the original episode's metadata and sources.
The original episode was created on {original_metadata.get('created_at', 'unknown date')}.

In a real regeneration:
1. The LLM would read all source materials
2. Generate a fresh script using the same settings ({tone} tone, {length} length)
3. The script might be different from the original due to LLM variability
4. Audio would be generated with the {voice} voice

Main Talking Points:
- Point 1: This demonstrates the regeneration workflow
- Point 2: Source files are preserved and reused
- Point 3: New episode folder created with '_regenerated_' suffix

Conclusion:
Thank you for exploring Step 18! The regeneration feature allows you to recreate
episodes from saved metadata and sources.

[End of mock script]
"""

    script_file = new_episode_dir / "script.txt"
    script_file.write_text(mock_script, encoding="utf-8")
    print(f"  Created: script.txt")

    # Create mock show notes
    mock_show_notes = f"""Show Notes - Regenerated Episode: {topic}

Summary:
This is a demonstration of the Step 18 regeneration feature. It shows how
episodes can be recreated from their original metadata and source files.

Key Takeaways:
1. Episodes can be regenerated using saved metadata
2. Source files are preserved in the episode folder
3. Regeneration creates a new episode with '_regenerated_' suffix
4. Original episodes remain untouched

Original Episode:
- Created: {original_metadata.get('created_at', 'unknown')}
- Episode ID: {original_metadata.get('episode_id', original_metadata.get('topic', 'unknown'))}

Regenerated Episode:
- Created: {datetime.now().isoformat()}
- Episode ID: {new_episode_id}

[Demo show notes - Step 18]
"""

    show_notes_file = new_episode_dir / "show_notes.txt"
    show_notes_file.write_text(mock_show_notes, encoding="utf-8")
    print(f"  Created: show_notes.txt")

    # Create mock audio file (empty placeholder)
    audio_file = new_episode_dir / f"podcast_{voice}.mp3"
    audio_file.write_text("[Mock MP3 audio file - would contain actual audio in real regeneration]", encoding="utf-8")
    print(f"  Created: podcast_{voice}.mp3 (mock)")

    # Create metadata with regeneration info
    created_at = datetime.now().isoformat()

    new_metadata = {
        "created_at": created_at,
        "episode_id": new_episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": original_metadata.get('word_range_target', '500 to 700 words'),
        "regenerated_from": {
            "original_episode_id": original_metadata.get('episode_id', topic),
            "original_created_at": original_metadata.get('created_at'),
            "original_episode_dir": str(original_episode_dir)
        },
        "models": original_metadata.get('models', {}),
        "inputs": original_metadata.get('inputs', {}),
        "outputs": {
            "episode_dir": str(new_episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file)
        },
        "demo_mode": True,
        "note": "This is a demonstration episode created without API calls"
    }

    metadata_file = new_episode_dir / "metadata.json"
    metadata_file.write_text(json.dumps(new_metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Created: metadata.json")

    # Update episode index
    index_path = output_root / "episode_index.json"
    if index_path.exists():
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index_data = []

    episode_summary = {
        "created_at": created_at,
        "episode_id": new_episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "episode_dir": str(new_episode_dir),
        "metadata_file": str(metadata_file),
        "script_file": str(script_file),
        "show_notes_file": str(show_notes_file),
        "audio_file": str(audio_file),
        "regenerated": True,
        "regenerated_from": original_metadata.get('episode_id', topic),
        "demo_mode": True
    }

    index_data.append(episode_summary)
    index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Updated: episode_index.json")

    print("\n" + "=" * 70)
    print("Demo Regeneration Complete!")
    print("=" * 70)
    print(f"\nNew Episode ID: {new_episode_id}")
    print(f"Location: {new_episode_dir}")
    print(f"\nFiles created:")
    print(f"  - sources/ ({source_count} files)")
    print(f"  - script.txt")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3 (mock)")
    print(f"  - metadata.json")
    print(f"\nYou can now view this regenerated episode using:")
    print(f"  python step17_episode_browser.py")


if __name__ == "__main__":
    demo_regeneration()
