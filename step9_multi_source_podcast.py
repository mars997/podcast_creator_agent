from pathlib import Path

from core.provider_setup import initialize_providers
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_tone, validate_voice, validate_length, get_word_range
from core.file_utils import save_text_file, ensure_directory, read_text_file
from core.source_management import parse_csv_input

# Initialize providers
llm_provider, tts_provider = initialize_providers()

source_input = input("Enter source text file paths separated by commas: ").strip()
topic = input("Enter episode topic/title: ").strip()
tone = input("Choose tone (casual/professional/educational): ").strip().lower()
voice = input("Choose voice (alloy/echo/fable/onyx/nova/shimmer): ").strip().lower()
length = input("Choose length (short/medium/long): ").strip().lower()

if not source_input:
    raise ValueError("You must provide at least one source file path.")

# Parse comma-separated input using core module
source_file_paths = parse_csv_input(source_input)
if not source_file_paths:
    raise ValueError("No valid source file paths were provided.")

source_files = [Path(p) for p in source_file_paths]

# Validate all files exist
for file_path in source_files:
    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

if not topic:
    raise ValueError("Topic cannot be empty.")

# Validate inputs using core validation module
tone = validate_tone(tone)
voice = validate_voice(voice)
length = validate_length(length)

# Read all source files
source_texts = []
for idx, file_path in enumerate(source_files, start=1):
    content = read_text_file(file_path)
    source_texts.append(f"Source {idx} ({file_path.name}):\n{content}")

combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(source_texts)
word_range = get_word_range(length)

# Create episode directory
safe_topic = sanitize_filename(topic)
episode_dir = ensure_directory(Path("output") / safe_topic)

sources_dir = ensure_directory(episode_dir / "sources")

# Copy source files to episode directory
for file_path in source_files:
    copied_path = sources_dir / file_path.name
    save_text_file(file_path.read_text(encoding="utf-8"), copied_path)

print("Generating podcast script from multiple sources...")

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
print("Step 9 complete.")