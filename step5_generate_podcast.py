import os
from pathlib import Path
from dotenv import load_dotenv

# Import provider abstraction (Step 21+)
from providers import get_default_config, create_llm_provider, create_tts_provider

load_dotenv()

# Get provider configuration
provider_config = get_default_config()
llm_provider = create_llm_provider(provider_config)
tts_provider = create_tts_provider(provider_config)

print(f"LLM: {llm_provider.provider_name.upper()} ({llm_provider.model_name})")
print(f"TTS: {tts_provider.provider_name.upper()} ({tts_provider.model_name})")

topic = input("Enter a podcast topic: ").strip()

if not topic:
    raise ValueError("Topic cannot be empty.")

prompt = f"""
You are a podcast writer.

Write a short podcast script about this topic: {topic}

Requirements:
- Keep it around 300 to 500 words
- Make it sound natural and conversational
- Include:
  1. A short title
  2. An intro hook
  3. 2 to 3 key points
  4. A short closing
- Tone: clear, engaging, beginner-friendly
- Do not use bullet points
- Format it like a script for a solo podcast host
"""

print("Generating script...")

# Use LLM provider
script = llm_provider.generate_text(prompt)

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

safe_topic = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in topic).strip()
safe_topic = safe_topic.replace(" ", "_")

script_file = output_dir / f"{safe_topic}_script.txt"
audio_file = output_dir / f"{safe_topic}_podcast.mp3"

with open(script_file, "w", encoding="utf-8") as f:
    f.write(script)

print(f"Script saved to: {script_file.resolve()}")
print("Generating audio...")

# Use TTS provider
tts_provider.generate_audio(script, "alloy", audio_file)

print(f"Audio saved to: {audio_file.resolve()}")
print("Podcast generation complete.")