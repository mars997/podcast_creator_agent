from pathlib import Path

from core.provider_setup import initialize_providers
from core.content_generation import build_script, generate_audio
from core.validation import sanitize_filename
from core.file_utils import save_text_file, ensure_directory

# Initialize providers
llm_provider, tts_provider = initialize_providers()

topic = input("Enter a podcast topic: ").strip()

if not topic:
    raise ValueError("Topic cannot be empty.")

print("Generating script...")

# Generate script using core module
script = build_script(
    llm_provider,
    topic,
    tone="casual",
    word_range="300 to 500 words"
)

# Prepare output directory and filenames
output_dir = ensure_directory(Path("output"))
safe_topic = sanitize_filename(topic)

script_file = output_dir / f"{safe_topic}_script.txt"
audio_file = output_dir / f"{safe_topic}_podcast.mp3"

# Save script
save_text_file(script, script_file)
print(f"Script saved to: {script_file.resolve()}")

print("Generating audio...")

# Generate audio using core module
generate_audio(tts_provider, script, "alloy", audio_file)

print(f"Audio saved to: {audio_file.resolve()}")
print("Podcast generation complete.")