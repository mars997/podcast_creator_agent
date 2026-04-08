from datetime import datetime
from pathlib import Path

from core.provider_setup import initialize_providers, get_provider_info
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file, ensure_directory
from core.source_management import parse_csv_input, save_sources_to_directory
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


# Initialize providers
llm_provider, tts_provider = initialize_providers()

# Configuration
DEFAULT_TONE = config.DEFAULT_TONE
DEFAULT_VOICE = config.PROVIDER_MODELS.get(tts_provider.provider_name, {}).get("default_voice", "nova")
DEFAULT_LENGTH = config.DEFAULT_LENGTH
OUTPUT_ROOT = config.OUTPUT_ROOT
EPISODE_INDEX_FILE = "episode_index.json"

VALID_TONES = config.VALID_TONES
VALID_VOICES = set(tts_provider.available_voices)
VALID_LENGTHS = config.VALID_LENGTHS


def main():
    url_input = input("Enter article URLs separated by commas (or leave blank): ").strip()
    file_input = input("Enter text file paths separated by commas (or leave blank): ").strip()

    topic = input("Enter episode topic/title: ").strip()
    tone = get_user_input("Choose tone (casual/professional/educational)", DEFAULT_TONE)
    voice = get_user_input("Choose voice (alloy/echo/fable/onyx/nova/shimmer)", DEFAULT_VOICE)
    length = get_user_input("Choose length (short/medium/long)", DEFAULT_LENGTH)

    if not url_input and not file_input:
        raise ValueError("You must provide at least one URL or one file.")

    if not topic:
        raise ValueError("Topic cannot be empty.")

    # Validate inputs
    tone = validate_choice(tone, VALID_TONES, "tone")
    voice = validate_choice(voice, VALID_VOICES, "voice")
    length = validate_choice(length, VALID_LENGTHS, "length")

    word_range = get_word_range(length)

    # Create unique episode directory using core module (Step 16 feature)
    output_root = Path(OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"Created episode directory: {episode_dir}")
    print(f"Episode ID: {episode_id}")

    sources_dir = ensure_directory(episode_dir / "sources")

    # Parse and fetch sources
    all_sources = []
    urls = parse_csv_input(url_input) if url_input else None
    file_paths = [Path(p) for p in parse_csv_input(file_input)] if file_input else None

    successful, failed = save_sources_to_directory(
        sources_dir,
        all_sources,
        urls=urls,
        files=file_paths
    )

    if not all_sources:
        raise ValueError("No usable source content could be retrieved.")

    combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(all_sources)

    # Generate content
    print("Generating podcast script...")
    script = build_script(llm_provider, topic, tone, word_range, combined_source_text)

    script_file = episode_dir / "script.txt"
    save_text_file(script, script_file)
    print(f"Script saved to: {script_file.resolve()}")

    print("Generating show notes...")
    show_notes = build_show_notes(llm_provider, script)

    show_notes_file = episode_dir / "show_notes.txt"
    save_text_file(show_notes, show_notes_file)
    print(f"Show notes saved to: {show_notes_file.resolve()}")

    audio_file = episode_dir / f"podcast_{voice}.mp3"

    print("Generating audio...")
    generate_audio(tts_provider, script, voice, audio_file)
    print(f"Audio saved to: {audio_file.resolve()}")

    # Create and save metadata with unique episode ID
    created_at = datetime.now().isoformat()
    provider_info = get_provider_info(llm_provider, tts_provider)

    # Separate successful/failed by type
    successful_urls = [s for s in successful if s.get("type") == "url"]
    successful_files = [s for s in successful if s.get("type") == "file"]
    failed_urls = [f for f in failed if f.get("type") == "url"]
    failed_files = [f for f in failed if f.get("type") == "file"]

    metadata = {
        "created_at": created_at,
        "episode_id": episode_id,  # Step 16: unique episode ID
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "providers": provider_info,
        "models": {
            "script_model": llm_provider.model_name,
            "tts_model": tts_provider.model_name
        },
        "inputs": {
            "requested_urls": urls or [],
            "requested_files": [str(f) for f in file_paths] if file_paths else [],
            "successful_urls": successful_urls,
            "failed_urls": failed_urls,
            "successful_files": successful_files,
            "failed_files": failed_files
        },
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file)
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"Metadata saved to: {metadata_file.resolve()}")

    # Create and update episode index
    episode_summary = create_episode_summary(
        metadata,
        episode_dir,
        {
            "num_successful_urls": len(successful_urls),
            "num_successful_files": len(successful_files),
            "num_failed_urls": len(failed_urls),
            "num_failed_files": len(failed_files)
        }
    )

    index_file = output_root / EPISODE_INDEX_FILE
    update_episode_index(index_file, episode_summary)
    print(f"Episode index updated: {index_file}")

    print("Step 16 complete.")


if __name__ == "__main__":
    main()
