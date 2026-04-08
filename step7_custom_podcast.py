from pathlib import Path

from core.provider_setup import initialize_providers
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_tone, validate_voice, validate_length, get_word_range
from core.file_utils import save_text_file, ensure_directory

# Initialize providers
llm_provider, tts_provider = initialize_providers()

topic = input("Enter podcast topic: ").strip()
tone = input("Choose tone (casual/professional/educational): ").strip().lower()
voice = input("Choose voice (alloy/echo/fable/onyx/nova/shimmer): ").strip().lower()
length = input("Choose length (short/medium/long): ").strip().lower()

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

print("Generating podcast script...")

# Generate script using core module
script = build_script(llm_provider, topic, tone, word_range)

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
print("Step 7 complete.")