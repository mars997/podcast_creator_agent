import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "podcast_test.mp3"

script_text = """
Welcome to my first AI-generated podcast.
This is a short test episode created with Python in Visual Studio Code.
If you can hear this audio clearly, then step two is working successfully.
"""

with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=script_text,
) as response:
    response.stream_to_file(output_file)

print(f"Audio saved to: {output_file.resolve()}")