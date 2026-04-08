from pathlib import Path

from core.provider_setup import initialize_providers
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_tone, validate_voice, validate_length, get_word_range
from core.file_utils import save_text_file, ensure_directory
from core.source_management import parse_csv_input, save_sources_to_directory

# Initialize providers
llm_provider, tts_provider = initialize_providers()

url_input = input("Enter article URLs separated by commas: ").strip()
topic = input("Enter episode topic/title: ").strip()
tone = input("Choose tone (casual/professional/educational): ").strip().lower()
voice = input("Choose voice (alloy/echo/fable/onyx/nova/shimmer): ").strip().lower()
length = input("Choose length (short/medium/long): ").strip().lower()

if not url_input:
    raise ValueError("You must provide at least one URL.")

# Parse comma-separated URLs using core module
urls = parse_csv_input(url_input)
if not urls:
    raise ValueError("No valid URLs were provided.")

if not topic:
    raise ValueError("Topic cannot be empty.")

# Validate inputs using core validation module
tone = validate_tone(tone)
voice = validate_voice(voice)
length = validate_length(length)

word_range = get_word_range(length)

# Create episode directory
safe_topic = sanitize_filename(topic)
episode_dir = ensure_directory(Path("output") / safe_topic)

sources_dir = ensure_directory(episode_dir / "sources")

# Fetch and save sources using core module
all_sources = []
successful, failed = save_sources_to_directory(sources_dir, all_sources, urls=urls)

if not all_sources:
    raise ValueError("No article content could be retrieved from the provided URLs.")

combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(all_sources)

print("Generating podcast script...")

# Generate script using core module with source material
script = build_script(llm_provider, topic, tone, word_range, combined_source_text)

script_file = episode_dir / "script.txt"
save_text_file(script, script_file)
print(f"Script saved to: {script_file.resolve()}")

print("Generating show notes...")

# Generate show notes using core module
show_notes = build_show_notes(llm_provider, script)

show_notes_file = episode_dir / "show_notes.txt"
save_text_file(show_notes, show_notes_file)
print(f"Show notes saved to: {show_notes_file.resolve()}")

audio_file = episode_dir / f"podcast_{voice}.mp3"

print("Generating audio...")

# Generate audio using core module
generate_audio(tts_provider, script, voice, audio_file)

print(f"Audio saved to: {audio_file.resolve()}")
print("Step 10 complete.")
