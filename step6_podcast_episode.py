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

topic = input("Enter a podcast topic: ").strip()

if not topic:
    raise ValueError("Topic cannot be empty.")

safe_topic = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in topic).strip()
safe_topic = safe_topic.replace(" ", "_")

episode_dir = Path("output") / safe_topic
episode_dir.mkdir(parents=True, exist_ok=True)

script_prompt = f"""
You are a podcast writer creating a short solo-host episode.

Topic: {topic}

Write a podcast episode script with the following:
- A catchy episode title on the first line
- A short welcome intro
- 3 clear main talking points
- A short conclusion
- Around 500 to 700 words
- Conversational, warm, and engaging
- Beginner-friendly
- No bullet points
- Output as a spoken script
"""

print("Generating podcast script...")

script = llm_provider.generate_text(script_prompt)

script_file = episode_dir / "script.txt"
with open(script_file, "w", encoding="utf-8") as f:
    f.write(script)

print(f"Script saved to: {script_file.resolve()}")

show_notes_prompt = f"""
Based on the following podcast script, write short show notes.

Requirements:
- Include episode title
- Include a 2 to 4 sentence summary
- Include 3 key takeaways
- Keep it clean and simple

Podcast script:
{script}
"""

print("Generating show notes...")

show_notes = llm_provider.generate_text(show_notes_prompt)

show_notes_file = episode_dir / "show_notes.txt"
with open(show_notes_file, "w", encoding="utf-8") as f:
    f.write(show_notes)

print(f"Show notes saved to: {show_notes_file.resolve()}")

audio_file = episode_dir / "podcast.mp3"

print("Generating audio...")

tts_provider.generate_audio(script, "alloy", audio_file)

print(f"Audio saved to: {audio_file.resolve()}")
print("Step 6 complete.")