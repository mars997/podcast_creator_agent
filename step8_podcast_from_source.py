import os
from pathlib import Path
from dotenv import load_dotenv
# Import provider abstraction (Step 21+)
from providers import get_default_config, create_llm_provider, create_tts_provider
import config

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


def sanitize_filename(text: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in text).strip()
    return cleaned.replace(" ", "_")


def get_word_range(length_choice: str) -> str:
    return config.get_word_range(length_choice)


source_file = input("Enter source text file path (example: source.txt): ").strip()
topic = input("Enter episode topic/title: ").strip()
tone = input("Choose tone (casual/professional/educational): ").strip().lower()
voice = input("Choose voice (alloy/echo/fable/onyx/nova/shimmer): ").strip().lower()
length = input("Choose length (short/medium/long): ").strip().lower()

if not source_file:
    raise ValueError("Source file path cannot be empty.")

if not Path(source_file).exists():
    raise FileNotFoundError(f"Source file not found: {source_file}")

if not topic:
    raise ValueError("Topic cannot be empty.")

if tone not in {"casual", "professional", "educational"}:
    raise ValueError("Tone must be casual, professional, or educational.")

if voice not in {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}:
    raise ValueError("Invalid voice selected.")

if length not in {"short", "medium", "long"}:
    raise ValueError("Length must be short, medium, or long.")

source_text = Path(source_file).read_text(encoding="utf-8")
if not source_text.strip():
    raise ValueError("Source file is empty.")

word_range = get_word_range(length)

safe_topic = sanitize_filename(topic)
episode_dir = Path("output") / safe_topic
episode_dir.mkdir(parents=True, exist_ok=True)

source_copy_file = episode_dir / "source.txt"
source_copy_file.write_text(source_text, encoding="utf-8")

script_prompt = f"""
You are a podcast writer creating a solo-host podcast episode.

Episode topic: {topic}
Tone: {tone}
Target length: {word_range}

Use the source material below to write the episode.
Stay grounded in the source content and do not invent specific facts that are not supported by the source.

Requirements:
- A catchy episode title on the first line
- A short welcome intro
- 3 clear main talking points
- A short conclusion
- Sound natural when spoken aloud
- No bullet points
- Beginner-friendly
- Smooth transitions between sections

Source material:
{source_text}
"""

print("Generating podcast script from source...")

script = llm_provider.generate_text(script_prompt)

script_file = episode_dir / "script.txt"
script_file.write_text(script, encoding="utf-8")

print(f"Script saved to: {script_file.resolve()}")

show_notes_prompt = f"""
Based on the following podcast script, create show notes.

Requirements:
- Include the episode title
- Include a short summary
- Include 3 key takeaways
- Clean and readable format

Podcast script:
{script}
"""

print("Generating show notes...")

show_notes = llm_provider.generate_text(show_notes_prompt)

show_notes_file = episode_dir / "show_notes.txt"
show_notes_file.write_text(show_notes, encoding="utf-8")

print(f"Show notes saved to: {show_notes_file.resolve()}")

audio_file = episode_dir / f"podcast_{voice}.mp3"

print("Generating audio...")

tts_provider.generate_audio(script, voice, audio_file)

print(f"Audio saved to: {audio_file.resolve()}")
print("Step 8 complete.")