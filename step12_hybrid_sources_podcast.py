import os
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


def main():
    source_mode = input("Choose source type (url/file): ").strip().lower()

    if source_mode not in {"url", "file"}:
        raise ValueError("Source type must be 'url' or 'file'.")

    if source_mode == "url":
        source_input = input("Enter article URLs separated by commas: ").strip()
    else:
        source_input = input("Enter text file paths separated by commas: ").strip()

    topic = input("Enter episode topic/title: ").strip()
    tone = get_user_input("Choose tone (casual/professional/educational)", DEFAULT_TONE)
    voice = get_user_input("Choose voice (alloy/echo/fable/onyx/nova/shimmer)", DEFAULT_VOICE)
    length = get_user_input("Choose length (short/medium/long)", DEFAULT_LENGTH)

    if not source_input:
        raise ValueError("You must provide at least one source.")

    if not topic:
        raise ValueError("Topic cannot be empty.")

    tone = validate_choice(tone, VALID_TONES, "tone")
    voice = validate_choice(voice, VALID_VOICES, "voice")
    length = validate_choice(length, VALID_LENGTHS, "length")

    word_range = get_word_range(length)
    safe_topic = sanitize_filename(topic)

    episode_dir = Path(OUTPUT_ROOT) / safe_topic
    episode_dir.mkdir(parents=True, exist_ok=True)

    sources_dir = episode_dir / "sources"
    sources_dir.mkdir(exist_ok=True)

    all_sources = []

    if source_mode == "url":
        urls = [u.strip() for u in source_input.split(",") if u.strip()]
        if not urls:
            raise ValueError("No valid URLs were provided.")

        print("Fetching article content...")
        for idx, url in enumerate(urls, start=1):
            try:
                article_text = fetch_article_text(url)
                all_sources.append(f"Source {idx}:\n{article_text}")

                domain = urlparse(url).netloc.replace(".", "_")
                source_file = sources_dir / f"source_{idx}_{domain}.txt"
                source_file.write_text(article_text, encoding="utf-8")
                print(f"Saved source {idx}: {source_file.resolve()}")
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")

    else:
        file_paths = [Path(p.strip()) for p in source_input.split(",") if p.strip()]
        if not file_paths:
            raise ValueError("No valid file paths were provided.")

        print("Reading local text files...")
        for idx, file_path in enumerate(file_paths, start=1):
            try:
                file_text = read_text_file(file_path)
                all_sources.append(f"Source {idx}:\n{file_text}")

                copied_file = sources_dir / file_path.name
                copied_file.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
                print(f"Copied source {idx}: {copied_file.resolve()}")
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")

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
    print("Step 12 complete.")


if __name__ == "__main__":
    main()