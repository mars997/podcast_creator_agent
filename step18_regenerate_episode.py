import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# =========================
# CONFIG
# =========================
OUTPUT_ROOT = "output"
EPISODE_INDEX_FILE = "episode_index.json"

# Default models (can be overridden by metadata)
DEFAULT_SCRIPT_MODEL = "gpt-4.1-mini"
DEFAULT_TTS_MODEL = "gpt-4o-mini-tts"


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)


def sanitize_filename(text: str) -> str:
    """Sanitize text for use in filenames"""
    cleaned = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in text).strip()
    return cleaned.replace(" ", "_")


def get_word_range(length_choice: str) -> str:
    """Get word range based on length choice"""
    mapping = {
        "short": "300 to 450 words",
        "medium": "500 to 700 words",
        "long": "800 to 1100 words",
    }
    return mapping.get(length_choice.lower(), "500 to 700 words")


def load_episode_index(index_path: Path) -> list[dict]:
    """Load the episode index from JSON file"""
    if not index_path.exists():
        print(f"Episode index not found: {index_path}")
        return []

    try:
        content = index_path.read_text(encoding="utf-8")
        episodes = json.loads(content)
        if not isinstance(episodes, list):
            return []
        return episodes
    except Exception as e:
        print(f"Error loading episode index: {e}")
        return []


def load_metadata(metadata_path: Path) -> dict:
    """Load episode metadata from JSON file"""
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    try:
        content = metadata_path.read_text(encoding="utf-8")
        metadata = json.loads(content)
        return metadata
    except Exception as e:
        raise ValueError(f"Error loading metadata: {e}")


def load_source_files(sources_dir: Path) -> list[str]:
    """Load all source text files from sources directory"""
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
                print(f"  Loaded: {source_file.name}")
        except Exception as e:
            print(f"  Warning: Could not read {source_file.name}: {e}")

    return all_sources


def build_script(topic: str, tone: str, word_range: str, source_material: str, model: str) -> str:
    """Generate podcast script using LLM"""
    prompt = f"""
You are a podcast writer creating a solo-host podcast episode.

Episode topic: {topic}
Tone: {tone}
Target length: {word_range}

Use the source materials below to write the episode.
Combine the ideas clearly and naturally.
Stay grounded in the sources and do not invent specific facts not supported by them.

Requirements:
- A catchy episode title on the first line
- A short welcome intro
- 3 clear main talking points
- A short conclusion
- Sound natural when spoken aloud
- No bullet points
- Beginner-friendly
- Smooth transitions between sections

Source materials:
{source_material}
"""

    response = client.responses.create(
        model=model,
        input=prompt
    )
    return response.output_text.strip()


def build_show_notes(script: str, model: str) -> str:
    """Generate show notes from script"""
    prompt = f"""
Based on the following podcast script, create show notes.

Requirements:
- Include the episode title
- Include a short summary
- Include 3 key takeaways
- Clean and readable format

Podcast script:
{script}
"""

    response = client.responses.create(
        model=model,
        input=prompt
    )
    return response.output_text.strip()


def generate_audio(script: str, voice: str, audio_path: Path, model: str) -> None:
    """Generate audio file from script using TTS"""
    with client.audio.speech.with_streaming_response.create(
        model=model,
        voice=voice,
        input=script,
    ) as response:
        response.stream_to_file(audio_path)


def save_json(data: dict | list, file_path: Path) -> None:
    """Save data to JSON file"""
    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def update_episode_index(index_path: Path, episode_summary: dict) -> None:
    """Update the global episode index"""
    if index_path.exists():
        try:
            index_data = json.loads(index_path.read_text(encoding="utf-8"))
            if not isinstance(index_data, list):
                index_data = []
        except Exception:
            index_data = []
    else:
        index_data = []

    index_data.append(episode_summary)
    save_json(index_data, index_path)


def display_episode_list(episodes: list[dict]) -> None:
    """Display episodes for selection"""
    print("\n" + "=" * 70)
    print(f"Available Episodes ({len(episodes)} total)")
    print("=" * 70)

    for i, episode in enumerate(episodes, start=1):
        topic = episode.get('topic', 'Unknown')
        episode_id = episode.get('episode_id', topic)
        created_at = episode.get('created_at', 'Unknown date')

        try:
            dt = datetime.fromisoformat(created_at)
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            date_str = created_at

        print(f"[{i}] {topic}")
        print(f"    Episode ID: {episode_id}")
        print(f"    Created: {date_str}")
        print()


def regenerate_episode(original_metadata: dict, episode_dir_path: Path) -> None:
    """Regenerate episode from metadata and sources"""
    print("\n" + "=" * 70)
    print("Regenerating Episode")
    print("=" * 70)

    # Extract settings from metadata
    topic = original_metadata.get('topic', 'Regenerated Episode')
    tone = original_metadata.get('tone', 'educational')
    voice = original_metadata.get('voice', 'nova')
    length = original_metadata.get('length', 'medium')
    word_range = original_metadata.get('word_range_target', get_word_range(length))

    # Get models from metadata or use defaults
    models = original_metadata.get('models', {})
    script_model = models.get('script_model', DEFAULT_SCRIPT_MODEL)
    tts_model = models.get('tts_model', DEFAULT_TTS_MODEL)

    print(f"\nOriginal Episode Settings:")
    print(f"  Topic: {topic}")
    print(f"  Tone: {tone}")
    print(f"  Voice: {voice}")
    print(f"  Length: {length} ({word_range})")
    print(f"  Script Model: {script_model}")
    print(f"  TTS Model: {tts_model}")

    # Load sources from original episode
    sources_dir = episode_dir_path / "sources"
    print(f"\nLoading sources from: {sources_dir}")

    all_sources = load_source_files(sources_dir)

    if not all_sources:
        raise ValueError("No source content could be loaded")

    print(f"  Total sources loaded: {len(all_sources)}")

    combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(all_sources)

    # Create new episode folder with timestamp
    safe_topic = sanitize_filename(topic)
    timestamp_suffix = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    unique_episode_id = f"{safe_topic}_regenerated_{timestamp_suffix}"

    output_root = Path(OUTPUT_ROOT)
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
        dest_file.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"  Copied {len(list(new_sources_dir.glob('*.txt')))} source files")

    # Generate script
    print("\nGenerating new podcast script...")
    script = build_script(topic, tone, word_range, combined_source_text, script_model)

    script_file = new_episode_dir / "script.txt"
    script_file.write_text(script, encoding="utf-8")
    print(f"  Script saved: {script_file.name}")

    # Generate show notes
    print("\nGenerating show notes...")
    show_notes = build_show_notes(script, script_model)

    show_notes_file = new_episode_dir / "show_notes.txt"
    show_notes_file.write_text(show_notes, encoding="utf-8")
    print(f"  Show notes saved: {show_notes_file.name}")

    # Generate audio
    audio_file = new_episode_dir / f"podcast_{voice}.mp3"

    print("\nGenerating audio...")
    generate_audio(script, voice, audio_file, tts_model)
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
        "models": {
            "script_model": script_model,
            "tts_model": tts_model
        },
        "inputs": original_metadata.get('inputs', {}),
        "outputs": {
            "episode_dir": str(new_episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file)
        }
    }

    metadata_file = new_episode_dir / "metadata.json"
    save_json(new_metadata, metadata_file)
    print(f"  Metadata saved: {metadata_file.name}")

    # Update episode index
    episode_summary = {
        "created_at": created_at,
        "episode_id": unique_episode_id,
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
        "regenerated_from": original_metadata.get('episode_id', topic)
    }

    index_file = output_root / EPISODE_INDEX_FILE
    update_episode_index(index_file, episode_summary)
    print(f"\nEpisode index updated: {index_file}")

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


def main():
    """Main entry point for episode regeneration"""
    print("\n" + "=" * 70)
    print("Step 18: Regenerate Episode from Metadata")
    print("=" * 70)

    output_root = Path(OUTPUT_ROOT)
    index_path = output_root / EPISODE_INDEX_FILE

    # Load episode index
    print(f"\nLoading episode index from: {index_path}")
    episodes = load_episode_index(index_path)

    if not episodes:
        print("\nNo episodes found. Create episodes first using step16_unique_episode_ids.py")
        return

    print(f"Found {len(episodes)} episode(s)")

    # Display episodes for selection
    display_episode_list(episodes)

    # Get user selection
    try:
        choice = int(input(f"Select episode to regenerate (1-{len(episodes)}): ").strip())
        if choice < 1 or choice > len(episodes):
            print(f"Invalid choice. Must be 1-{len(episodes)}")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    selected_episode = episodes[choice - 1]

    # Load metadata
    metadata_file = selected_episode.get('metadata_file')
    if not metadata_file:
        print("Error: Episode does not have metadata_file path")
        return

    metadata_path = Path(metadata_file)
    print(f"\nLoading metadata from: {metadata_path}")

    try:
        metadata = load_metadata(metadata_path)
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return

    # Get episode directory
    episode_dir = selected_episode.get('episode_dir')
    if not episode_dir:
        print("Error: Episode does not have episode_dir path")
        return

    episode_dir_path = Path(episode_dir)
    if not episode_dir_path.exists():
        print(f"Error: Episode directory not found: {episode_dir_path}")
        return

    # Confirm regeneration
    print(f"\nYou are about to regenerate episode: {selected_episode.get('topic')}")
    confirm = input("This will create a NEW episode with the same sources. Continue? (y/n): ").strip().lower()

    if confirm != 'y':
        print("Regeneration cancelled.")
        return

    # Regenerate episode
    try:
        regenerate_episode(metadata, episode_dir_path)
        print("\nStep 18 complete.")
    except Exception as e:
        print(f"\nError during regeneration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
