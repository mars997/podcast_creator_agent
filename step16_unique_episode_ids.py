from datetime import datetime
from pathlib import Path

from core.provider_setup import initialize_providers, get_provider_info
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file, ensure_directory
from core.source_management import parse_csv_input, save_sources_to_directory
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


# Initialize providers
llm_provider, tts_provider = initialize_providers()

# Configuration
DEFAULT_TONE = config.DEFAULT_TONE
DEFAULT_VOICE = config.PROVIDER_MODELS.get(tts_provider.provider_name, {}).get("default_voice", "nova")
DEFAULT_LENGTH = config.DEFAULT_LENGTH
OUTPUT_ROOT = config.OUTPUT_ROOT
EPISODE_INDEX_FILE = "episode_index.json"

VALID_TONES = config.VALID_TONES
VALID_VOICES = set(tts_provider.available_voices)
VALID_LENGTHS = config.VALID_LENGTHS


def main():
    url_input = input("Enter article URLs separated by commas (or leave blank): ").strip()
    file_input = input("Enter text file paths separated by commas (or leave blank): ").strip()

    topic = input("Enter episode topic/title: ").strip()
    tone = get_user_input("Choose tone (casual/professional/educational)", DEFAULT_TONE)
    voice = get_user_input("Choose voice (alloy/echo/fable/onyx/nova/shimmer)", DEFAULT_VOICE)
    length = get_user_input("Choose length (short/medium/long)", DEFAULT_LENGTH)

    if not url_input and not file_input:
        raise ValueError("You must provide at least one URL or one file.")

    if not topic:
        raise ValueError("Topic cannot be empty.")

    # Validate inputs
    tone = validate_choice(tone, VALID_TONES, "tone")
    voice = validate_choice(voice, VALID_VOICES, "voice")
    length = validate_choice(length, VALID_LENGTHS, "length")

    word_range = get_word_range(length)

    # Create unique episode directory using core module (Step 16 feature)
    output_root = Path(OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"Created episode directory: {episode_dir}")
    print(f"Episode ID: {episode_id}")

    sources_dir = ensure_directory(episode_dir / "sources")

    # Parse and fetch sources
    all_sources = []
    urls = parse_csv_input(url_input) if url_input else None
    file_paths = [Path(p) for p in parse_csv_input(file_input)] if file_input else None

    successful, failed = save_sources_to_directory(
        sources_dir,
        all_sources,
        urls=urls,
        files=file_paths
    )

    if not all_sources:
        raise ValueError("No usable source content could be retrieved.")

    combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(all_sources)

    # Generate content
    print("Generating podcast script...")
    script = build_script(llm_provider, topic, tone, word_range, combined_source_text)

    script_file = episode_dir / "script.txt"
    save_text_file(script, script_file)
    print(f"Script saved to: {script_file.resolve()}")

    print("Generating show notes...")
    show_notes = build_show_notes(llm_provider, script)

    show_notes_file = episode_dir / "show_notes.txt"
    save_text_file(show_notes, show_notes_file)
    print(f"Show notes saved to: {show_notes_file.resolve()}")

    audio_file = episode_dir / f"podcast_{voice}.mp3"

    print("Generating audio...")
    generate_audio(tts_provider, script, voice, audio_file)
    print(f"Audio saved to: {audio_file.resolve()}")

    # Create and save metadata with unique episode ID
    created_at = datetime.now().isoformat()
    provider_info = get_provider_info(llm_provider, tts_provider)

    # Separate successful/failed by type
    successful_urls = [s for s in successful if s.get("type") == "url"]
    successful_files = [s for s in successful if s.get("type") == "file"]
    failed_urls = [f for f in failed if f.get("type") == "url"]
    failed_files = [f for f in failed if f.get("type") == "file"]

    metadata = {
        "created_at": created_at,
        "episode_id": episode_id,  # Step 16: unique episode ID
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "providers": provider_info,
        "models": {
            "script_model": llm_provider.model_name,
            "tts_model": tts_provider.model_name
        },
        "inputs": {
            "requested_urls": urls or [],
            "requested_files": [str(f) for f in file_paths] if file_paths else [],
            "successful_urls": successful_urls,
            "failed_urls": failed_urls,
            "successful_files": successful_files,
            "failed_files": failed_files
        },
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file)
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"Metadata saved to: {metadata_file.resolve()}")

    # Create and update episode index
    episode_summary = create_episode_summary(
        metadata,
        episode_dir,
        {
            "num_successful_urls": len(successful_urls),
            "num_successful_files": len(successful_files),
            "num_failed_urls": len(failed_urls),
            "num_failed_files": len(failed_files)
        }
    )

    index_file = output_root / EPISODE_INDEX_FILE
    update_episode_index(index_file, episode_summary)
    print(f"Episode index updated: {index_file}")

    print("Step 16 complete.")


if __name__ == "__main__":
    main()
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
# Import provider abstraction (Step 21+)
from providers import get_default_config, create_llm_provider, create_tts_provider
import config


# =========================
# CONFIG
# =========================
DEFAULT_TONE = "educational"
DEFAULT_VOICE = config.PROVIDER_MODELS.get(tts_provider.provider_name, {}).get("default_voice", "nova")
DEFAULT_LENGTH = "medium"
OUTPUT_ROOT = "output"

SCRIPT_MODEL = "gpt-4.1-mini"
TTS_MODEL = "gpt-4o-mini-tts"

VALID_TONES = {"casual", "professional", "educational"}
VALID_VOICES = set(tts_provider.available_voices)
VALID_LENGTHS = {"short", "medium", "long"}


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


def get_user_input(prompt_text: str, default_value: str) -> str:
    user_value = input(f"{prompt_text} [{default_value}]: ").strip().lower()
    return user_value if user_value else default_value


def validate_choice(value: str, valid_set: set, field_name: str) -> str:
    if value not in valid_set:
        raise ValueError(f"Invalid {field_name}: {value}")
    return value


def fetch_article_text(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else "Untitled"

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p) > 40]

    article_text = "\n".join(paragraphs[:80]).strip()

    if not article_text:
        raise ValueError(f"Could not extract article text from: {url}")

    return f"Title: {title}\nURL: {url}\n\n{article_text}"


def read_text_file(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = file_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"File is empty: {file_path}")

    return f"File: {file_path.name}\n\n{content}"


def build_script(topic: str, tone: str, word_range: str, source_material: str) -> str:
    prompt = f"""
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
{source_material}
"""

    return llm_provider.generate_text(prompt)


def build_show_notes(script: str) -> str:
    prompt = f"""
Based on the following podcast script, create show notes.

Requirements:
- Include the episode title
- Include a short summary
- Include 3 key takeaways
- Clean and readable format

Podcast script:
{script}
"""

    return llm_provider.generate_text(prompt)


def generate_audio(script: str, voice: str, audio_path: Path) -> None:
    tts_provider.generate_audio(script, voice, audio_path)


def parse_csv_input(raw_text: str) -> list[str]:
    return [item.strip() for item in raw_text.split(",") if item.strip()]


def save_json(data: dict | list, file_path: Path) -> None:
    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def update_episode_index(index_path: Path, episode_summary: dict) -> None:
    if index_path.exists():
        try:
            index_data = json.loads(index_path.read_text(encoding="utf-8"))
            if not isinstance(index_data, list):
                index_data = []
        except Exception:
            index_data = []
    else:
        index_data = []

    index_data.append(episode_summary)
    save_json(index_data, index_path)


def main():
    url_input = input("Enter article URLs separated by commas (or leave blank): ").strip()
    file_input = input("Enter text file paths separated by commas (or leave blank): ").strip()

    topic = input("Enter episode topic/title: ").strip()
    tone = get_user_input("Choose tone (casual/professional/educational)", DEFAULT_TONE)
    voice = get_user_input("Choose voice (alloy/echo/fable/onyx/nova/shimmer)", DEFAULT_VOICE)
    length = get_user_input("Choose length (short/medium/long)", DEFAULT_LENGTH)

    if not url_input and not file_input:
        raise ValueError("You must provide at least one URL or one file.")

    if not topic:
        raise ValueError("Topic cannot be empty.")

    tone = validate_choice(tone, VALID_TONES, "tone")
    voice = validate_choice(voice, VALID_VOICES, "voice")
    length = validate_choice(length, VALID_LENGTHS, "length")

    word_range = get_word_range(length)
    safe_topic = sanitize_filename(topic)

    # Step 16: Add timestamp to create unique episode ID
    timestamp_suffix = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    unique_episode_id = f"{safe_topic}_{timestamp_suffix}"

    output_root = Path(OUTPUT_ROOT)
    output_root.mkdir(parents=True, exist_ok=True)

    # Step 16: Use unique episode ID for folder name
    episode_dir = output_root / unique_episode_id
    episode_dir.mkdir(parents=True, exist_ok=True)

    sources_dir = episode_dir / "sources"
    sources_dir.mkdir(exist_ok=True)

    all_sources = []
    source_counter = 1

    urls = parse_csv_input(url_input)
    files = parse_csv_input(file_input)

    successful_urls = []
    failed_urls = []
    successful_files = []
    failed_files = []

    if urls:
        print("Fetching article content...")
        for url in urls:
            try:
                article_text = fetch_article_text(url)
                all_sources.append(f"Source {source_counter}:\n{article_text}")

                domain = urlparse(url).netloc.replace(".", "_")
                source_file = sources_dir / f"source_{source_counter}_{domain}.txt"
                source_file.write_text(article_text, encoding="utf-8")
                print(f"Saved URL source {source_counter}: {source_file.resolve()}")

                successful_urls.append({
                    "url": url,
                    "saved_source_file": str(source_file)
                })
                source_counter += 1
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                failed_urls.append({
                    "url": url,
                    "error": str(e)
                })

    if files:
        print("Reading local text files...")
        for file_str in files:
            file_path = Path(file_str)
            try:
                file_text = read_text_file(file_path)
                all_sources.append(f"Source {source_counter}:\n{file_text}")

                copied_file = sources_dir / f"source_{source_counter}_{file_path.name}"
                copied_file.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
                print(f"Copied file source {source_counter}: {copied_file.resolve()}")

                successful_files.append({
                    "original_file": str(file_path),
                    "saved_source_file": str(copied_file)
                })
                source_counter += 1
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")
                failed_files.append({
                    "file": str(file_path),
                    "error": str(e)
                })

    if not all_sources:
        raise ValueError("No usable source content could be retrieved.")

    combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(all_sources)

    print("Generating podcast script...")
    script = build_script(topic, tone, word_range, combined_source_text)

    script_file = episode_dir / "script.txt"
    script_file.write_text(script, encoding="utf-8")
    print(f"Script saved to: {script_file.resolve()}")

    print("Generating show notes...")
    show_notes = build_show_notes(script)

    show_notes_file = episode_dir / "show_notes.txt"
    show_notes_file.write_text(show_notes, encoding="utf-8")
    print(f"Show notes saved to: {show_notes_file.resolve()}")

    audio_file = episode_dir / f"podcast_{voice}.mp3"

    print("Generating audio...")
    generate_audio(script, voice, audio_file)
    print(f"Audio saved to: {audio_file.resolve()}")

    created_at = datetime.now().isoformat()

    metadata = {
        "created_at": created_at,
        "episode_id": unique_episode_id,  # Step 16: Add unique episode ID to metadata
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "providers": {
            "llm_provider": llm_provider.provider_name,
            "llm_model": llm_provider.model_name,
            "tts_provider": tts_provider.provider_name,
            "tts_model": tts_provider.model_name
        },
        "models": {
            "script_model": llm_provider.model_name,
            "tts_model": tts_provider.model_name
        },
        "inputs": {
            "requested_urls": urls,
            "requested_files": files,
            "successful_urls": successful_urls,
            "failed_urls": failed_urls,
            "successful_files": successful_files,
            "failed_files": failed_files
        },
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file)
        }
    }

    metadata_file = episode_dir / "metadata.json"
    save_json(metadata, metadata_file)
    print(f"Metadata saved to: {metadata_file.resolve()}")

    episode_summary = {
        "created_at": created_at,
        "episode_id": unique_episode_id,  # Step 16: Add unique episode ID to index
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "episode_dir": str(episode_dir),
        "metadata_file": str(metadata_file),
        "script_file": str(script_file),
        "show_notes_file": str(show_notes_file),
        "audio_file": str(audio_file),
        "num_successful_urls": len(successful_urls),
        "num_successful_files": len(successful_files),
        "num_failed_urls": len(failed_urls),
        "num_failed_files": len(failed_files)
    }

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)
    print(f"Episode index updated: {index_file.resolve()}")

    print(f"\nStep 16 complete. Episode ID: {unique_episode_id}")


if __name__ == "__main__":
    main()
