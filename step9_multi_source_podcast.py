import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)


def sanitize_filename(text: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in text).strip()
    return cleaned.replace(" ", "_")


def get_word_range(length_choice: str) -> str:
    mapping = {
        "short": "300 to 450 words",
        "medium": "500 to 700 words",
        "long": "800 to 1100 words",
    }
    return mapping.get(length_choice.lower(), "500 to 700 words")


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

script_response = client.responses.create(
    model="gpt-4.1-mini",
    input=script_prompt
)

script = script_response.output_text.strip()

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

notes_response = client.responses.create(
    model="gpt-4.1-mini",
    input=show_notes_prompt
)

show_notes = notes_response.output_text.strip()

show_notes_file = episode_dir / "show_notes.txt"
show_notes_file.write_text(show_notes, encoding="utf-8")

print(f"Show notes saved to: {show_notes_file.resolve()}")

audio_file = episode_dir / f"podcast_{voice}.mp3"

print("Generating audio...")

with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice=voice,
    input=script,
) as response:
    response.stream_to_file(audio_file)

print(f"Audio saved to: {audio_file.resolve()}")
print("Step 9 complete.")