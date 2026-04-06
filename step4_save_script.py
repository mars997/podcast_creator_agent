import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

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

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt
)

script = response.output_text

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

safe_topic = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in topic).strip()
safe_topic = safe_topic.replace(" ", "_")

file_path = output_dir / f"{safe_topic}_script.txt"

with open(file_path, "w", encoding="utf-8") as f:
    f.write(script)

print("\nScript saved successfully.")
print(f"File path: {file_path.resolve()}")