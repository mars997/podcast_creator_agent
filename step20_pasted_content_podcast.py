from datetime import datetime
from pathlib import Path

from core.provider_setup import initialize_providers, get_provider_info
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input, read_multiline_input
from core.file_utils import save_text_file, ensure_directory, read_text_file
from core.episode_management import save_episode_metadata, create_episode_summary, update_episode_index
import config


# Initialize providers
llm_provider, tts_provider = initialize_providers()

# Configuration
DEFAULT_TONE = config.DEFAULT_TONE
DEFAULT_VOICE = config.PROVIDER_MODELS.get(tts_provider.provider_name, {}).get("default_voice", "nova")
DEFAULT_LENGTH = config.DEFAULT_LENGTH
OUTPUT_ROOT = config.OUTPUT_ROOT

VALID_TONES = config.VALID_TONES
VALID_VOICES = set(tts_provider.available_voices)
VALID_LENGTHS = config.VALID_LENGTHS


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
        # Multi-line pasted input using core module
        content = read_multiline_input()
        content_source = "pasted_text"

        if not content:
            raise ValueError("No content was provided")

        print(f"\n  Received {len(content)} characters")
        print(f"  Approximately {len(content.split())} words")

    elif choice == "2":
        # File path input using core module
        file_path_str = input("\nEnter text file path: ").strip()
        file_path = Path(file_path_str)

        content = read_text_file(file_path)
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
    episode_dir = ensure_directory(output_root / unique_episode_id)
    sources_dir = ensure_directory(episode_dir / "sources")

    # Save pasted content as source file
    source_file = sources_dir / "pasted_content.txt"
    save_text_file(content, source_file)
    print(f"\n  Content saved to: sources/pasted_content.txt")

    # Prepare source material for script generation
    source_material = f"Source Content:\n\n{content}"

    # Generate script
    print("\nGenerating podcast script...")
    script = build_script(llm_provider, topic, tone, word_range, source_material)

    script_file = episode_dir / "script.txt"
    save_text_file(script, script_file)
    print(f"  Script saved: {script_file.name}")

    # Generate show notes
    print("\nGenerating show notes...")
    show_notes = build_show_notes(llm_provider, script)

    show_notes_file = episode_dir / "show_notes.txt"
    save_text_file(show_notes, show_notes_file)
    print(f"  Show notes saved: {show_notes_file.name}")

    # Generate audio
    audio_file = episode_dir / f"podcast_{voice}.mp3"

    print("\nGenerating audio...")
    generate_audio(tts_provider, script, voice, audio_file)
    print(f"  Audio saved: {audio_file.name}")

    # Save metadata
    created_at = datetime.now().isoformat()
    provider_info = get_provider_info(llm_provider, tts_provider)

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
        "providers": provider_info,
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

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"  Metadata saved: {metadata_file.name}")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "num_successful_urls": 0,
            "num_successful_files": 1,
            "num_failed_urls": 0,
            "num_failed_files": 0,
            "source_type": "pasted_content",
            "content_word_count": len(content.split())
        }
    )

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
