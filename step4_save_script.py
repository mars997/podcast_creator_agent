from pathlib import Path

from core.provider_setup import initialize_providers
from core.content_generation import build_script
from core.validation import sanitize_filename
from core.file_utils import save_text_file, ensure_directory

# Initialize providers
llm_provider, _ = initialize_providers()

topic = input("Enter a podcast topic: ").strip()

if not topic:
    raise ValueError("Topic cannot be empty.")

# Generate script using core module
script = build_script(
    llm_provider,
    topic,
    tone="casual",
    word_range="300 to 500 words"
)

# Prepare output directory and filename
output_dir = ensure_directory(Path("output"))
safe_topic = sanitize_filename(topic)
file_path = output_dir / f"{safe_topic}_script.txt"

# Save script
save_text_file(script, file_path)

print("\nScript saved successfully.")
print(f"File path: {file_path.resolve()}")