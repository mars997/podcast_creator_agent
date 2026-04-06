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


topic = input("Enter podcast topic: ").strip()
tone = input("Choose tone (casual/professional/educational): ").strip().lower()
voice = input("Choose voice (alloy/echo/fable/onyx/nova/shimmer): ").strip().lower()
length = input("Choose length (short/medium/long): ").strip().lower()

if not topic:
    raise ValueError("Topic cannot be empty.")

if tone not in {"casual", "professional", "educational"}:
    raise ValueError("Tone must be casual, professional, or educational.")

if voice not in {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}:
    raise ValueError("Invalid voice selected.")

if length not in {"short", "medium", "long"}:
    raise ValueError("Length must be short, medium, or long.")

word_range = get_word_range(length)

safe_topic = sanitize_filename(topic)
episode_dir = Path("output") / safe_topic
episode_dir.mkdir(parents=True, exist_ok=True)

script_prompt = f"""
You are a podcast writer creating a solo-host podcast episode.

Topic: {topic}
Tone: {tone}
Length: {word_range}

Write a podcast episode script with the following:
- A catchy episode title on the first line
- A short welcome intro
- 3 clear main talking points
- A short conclusion
- Sound natural when spoken aloud
- No bullet points
- Beginner-friendly
- Smooth transitions between sections
"""

print("Generating podcast script...")

script_response = client.responses.create(
    model="gpt-4.1-mini",
    input=script_prompt
)

script = script_response.output_text.strip()

script_file = episode_dir / "script.txt"
with open(script_file, "w", encoding="utf-8") as f:
    f.write(script)

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
with open(show_notes_file, "w", encoding="utf-8") as f:
    f.write(show_notes)

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
print("Step 7 complete.")