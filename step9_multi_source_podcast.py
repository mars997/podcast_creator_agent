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


source_input = input("Enter source text file paths separated by commas: ").strip()
topic = input("Enter episode topic/title: ").strip()
tone = input("Choose tone (casual/professional/educational): ").strip().lower()
voice = input("Choose voice (alloy/echo/fable/onyx/nova/shimmer): ").strip().lower()
length = input("Choose length (short/medium/long): ").strip().lower()

if not source_input:
    raise ValueError("You must provide at least one source file path.")

source_files = [Path(p.strip()) for p in source_input.split(",") if p.strip()]
if not source_files:
    raise ValueError("No valid source file paths were provided.")

for file_path in source_files:
    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

if not topic:
    raise ValueError("Topic cannot be empty.")

if tone not in {"casual", "professional", "educational"}:
    raise ValueError("Tone must be casual, professional, or educational.")

if voice not in {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}:
    raise ValueError("Invalid voice selected.")

if length not in {"short", "medium", "long"}:
    raise ValueError("Length must be short, medium, or long.")

source_texts = []
for idx, file_path in enumerate(source_files, start=1):
    content = file_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"Source file is empty: {file_path}")
    source_texts.append(f"Source {idx} ({file_path.name}):\n{content}")

combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(source_texts)
word_range = get_word_range(length)

safe_topic = sanitize_filename(topic)
episode_dir = Path("output") / safe_topic
episode_dir.mkdir(parents=True, exist_ok=True)

sources_dir = episode_dir / "sources"
sources_dir.mkdir(exist_ok=True)

for file_path in source_files:
    copied_path = sources_dir / file_path.name
    copied_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")

script_prompt = f"""
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
{combined_source_text}
"""

print("Generating podcast script from multiple sources...")

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
print("Step 9 complete.")