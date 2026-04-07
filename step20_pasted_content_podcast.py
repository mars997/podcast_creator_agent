import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Import provider abstraction (Step 21+)
from providers import get_default_config, create_llm_provider, create_tts_provider
import config


# =========================
# LOAD CONFIGURATION
# =========================
load_dotenv()

# Get provider configuration (auto-detects available providers)
provider_config = get_default_config()

# Create LLM and TTS providers
llm_provider = create_llm_provider(provider_config)
tts_provider = create_tts_provider(provider_config)

# Display active providers
print(f"\n[Provider Info]")
print(f"  LLM: {llm_provider.provider_name.upper()} ({llm_provider.model_name})")
print(f"  TTS: {tts_provider.provider_name.upper()} ({tts_provider.model_name})")
print()

# Use config module for settings
DEFAULT_TONE = config.DEFAULT_TONE
DEFAULT_VOICE = config.PROVIDER_MODELS.get(tts_provider.provider_name, {}).get("default_voice", "nova")
DEFAULT_LENGTH = config.DEFAULT_LENGTH
OUTPUT_ROOT = config.OUTPUT_ROOT

VALID_TONES = config.VALID_TONES
VALID_VOICES = set(tts_provider.available_voices)
VALID_LENGTHS = config.VALID_LENGTHS


def sanitize_filename(text: str) -> str:
    """Sanitize text for use in filenames"""
    cleaned = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in text).strip()
    return cleaned.replace(" ", "_")


def get_word_range(length_choice: str) -> str:
    """Get word range based on length choice"""
    return config.get_word_range(length_choice)


def get_user_input(prompt_text: str, default_value: str) -> str:
    """Get user input with default value"""
    user_value = input(f"{prompt_text} [{default_value}]: ").strip().lower()
    return user_value if user_value else default_value


def validate_choice(value: str, valid_set: set, field_name: str) -> str:
    """Validate user choice against valid set"""
    if value not in valid_set:
        raise ValueError(f"Invalid {field_name}: {value}")
    return value


def read_multiline_input() -> str:
    """Read multi-line text input from user"""
    print("\nPaste your content below.")
    print("When finished, enter '###END###' on a new line and press Enter:")
    print("-" * 70)

    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "###END###":
                break
            lines.append(line)
        except EOFError:
            break

    content = "\n".join(lines).strip()
    return content


def read_text_from_file(file_path: Path) -> str:
    """Read text content from a file"""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = file_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"File is empty: {file_path}")

    return content


def build_script(topic: str, tone: str, word_range: str, source_material: str) -> str:
    """Generate podcast script using LLM provider"""
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

    return llm_provider.generate_text(prompt)


def build_show_notes(script: str) -> str:
    """Generate show notes from script using LLM provider"""
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

    return llm_provider.generate_text(prompt)


def generate_audio(script: str, voice: str, audio_path: Path) -> None:
    """Generate audio file from script using TTS provider"""
    tts_provider.generate_audio(script, voice, audio_path)


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


def main():
    """Main entry point for pasted content podcast generation"""
    print("\n" + "=" * 70)
    print("Step 20: Pasted Content Podcast Generator")
    print("=" * 70)

    # Choose input method
    print("\nHow would you like to provide content?")
    print("1. Paste text directly (multi-line input)")
    print("2. Provide a text file path")

    choice = input("\nEnter choice (1 or 2): ").strip()

    content = ""
    content_source = ""

    if choice == "1":
        # Multi-line pasted input
        content = read_multiline_input()
        content_source = "pasted_text"

        if not content:
            raise ValueError("No content was provided")

        print(f"\n  Received {len(content)} characters")
        print(f"  Approximately {len(content.split())} words")

    elif choice == "2":
        # File path input
        file_path_str = input("\nEnter text file path: ").strip()
        file_path = Path(file_path_str)

        content = read_text_from_file(file_path)
        content_source = f"file:{file_path.name}"

        print(f"\n  Read {len(content)} characters from {file_path.name}")
        print(f"  Approximately {len(content.split())} words")

    else:
        raise ValueError("Invalid choice. Please enter 1 or 2")

    # Get podcast settings
    topic = input("\nEnter episode topic/title: ").strip()
    tone = get_user_input("Choose tone (casual/professional/educational)", DEFAULT_TONE)
    voice = get_user_input("Choose voice (alloy/echo/fable/onyx/nova/shimmer)", DEFAULT_VOICE)
    length = get_user_input("Choose length (short/medium/long)", DEFAULT_LENGTH)

    if not topic:
        raise ValueError("Topic cannot be empty")

    tone = validate_choice(tone, VALID_TONES, "tone")
    voice = validate_choice(voice, VALID_VOICES, "voice")
    length = validate_choice(length, VALID_LENGTHS, "length")

    word_range = get_word_range(length)

    # Create episode folder
    safe_topic = sanitize_filename(topic)
    timestamp_suffix = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    unique_episode_id = f"{safe_topic}_{timestamp_suffix}"

    output_root = Path(OUTPUT_ROOT)
    output_root.mkdir(parents=True, exist_ok=True)

    episode_dir = output_root / unique_episode_id
    episode_dir.mkdir(parents=True, exist_ok=True)

    sources_dir = episode_dir / "sources"
    sources_dir.mkdir(exist_ok=True)

    # Save pasted content as source file
    source_file = sources_dir / "pasted_content.txt"
    source_file.write_text(content, encoding="utf-8")
    print(f"\n  Content saved to: sources/pasted_content.txt")

    # Prepare source material for script generation
    source_material = f"Source Content:\n\n{content}"

    # Generate script
    print("\nGenerating podcast script...")
    script = build_script(topic, tone, word_range, source_material)

    script_file = episode_dir / "script.txt"
    script_file.write_text(script, encoding="utf-8")
    print(f"  Script saved: {script_file.name}")

    # Generate show notes
    print("\nGenerating show notes...")
    show_notes = build_show_notes(script)

    show_notes_file = episode_dir / "show_notes.txt"
    show_notes_file.write_text(show_notes, encoding="utf-8")
    print(f"  Show notes saved: {show_notes_file.name}")

    # Generate audio
    audio_file = episode_dir / f"podcast_{voice}.mp3"

    print("\nGenerating audio...")
    generate_audio(script, voice, audio_file)
    print(f"  Audio saved: {audio_file.name}")

    # Save metadata
    created_at = datetime.now().isoformat()

    metadata = {
        "created_at": created_at,
        "episode_id": unique_episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "source_type": "pasted_content",
        "content_info": {
            "source": content_source,
            "character_count": len(content),
            "word_count": len(content.split()),
            "input_method": "paste" if choice == "1" else "file"
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
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file),
            "source_file": str(source_file)
        }
    }

    metadata_file = episode_dir / "metadata.json"
    save_json(metadata, metadata_file)
    print(f"  Metadata saved: {metadata_file.name}")

    # Update episode index
    episode_summary = {
        "created_at": created_at,
        "episode_id": unique_episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "source_type": "pasted_content",
        "episode_dir": str(episode_dir),
        "metadata_file": str(metadata_file),
        "script_file": str(script_file),
        "show_notes_file": str(show_notes_file),
        "audio_file": str(audio_file),
        "content_word_count": len(content.split())
    }

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)
    print(f"\nEpisode index updated: {index_file}")

    print("\n" + "=" * 70)
    print("Step 20 Complete!")
    print("=" * 70)
    print(f"\nEpisode ID: {unique_episode_id}")
    print(f"Location: {episode_dir}")
    print(f"\nContent source: {content_source}")
    print(f"Word count: {len(content.split())}")
    print(f"\nFiles generated:")
    print(f"  - sources/pasted_content.txt")
    print(f"  - script.txt")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")


if __name__ == "__main__":
    main()
