from pathlib import Path

from core.provider_setup import initialize_providers
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file, ensure_directory
from core.source_management import parse_csv_input, save_sources_to_directory
import config


# Initialize providers (FIXED: was trying to use tts_provider before creation)
llm_provider, tts_provider = initialize_providers()

# Configuration (FIXED: now providers are available)
DEFAULT_TONE = config.DEFAULT_TONE
DEFAULT_VOICE = config.PROVIDER_MODELS.get(tts_provider.provider_name, {}).get("default_voice", "nova")
DEFAULT_LENGTH = config.DEFAULT_LENGTH
OUTPUT_ROOT = config.OUTPUT_ROOT

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

    # Validate inputs using core module
    tone = validate_choice(tone, VALID_TONES, "tone")
    voice = validate_choice(voice, VALID_VOICES, "voice")
    length = validate_choice(length, VALID_LENGTHS, "length")

    word_range = get_word_range(length)

    # Create episode directory
    safe_topic = sanitize_filename(topic)
    episode_dir = ensure_directory(Path(OUTPUT_ROOT) / safe_topic)

    sources_dir = ensure_directory(episode_dir / "sources")

    # Parse inputs using core module
    urls = parse_csv_input(url_input) if url_input else None
    file_paths = [Path(p) for p in parse_csv_input(file_input)] if file_input else None

    # Fetch and save sources using core module
    all_sources = []
    successful, failed = save_sources_to_directory(
        sources_dir,
        all_sources,
        urls=urls,
        files=file_paths
    )

    if not all_sources:
        raise ValueError("No usable source content could be retrieved.")

    combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(all_sources)

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
    print("Step 12 complete.")


if __name__ == "__main__":
    main()