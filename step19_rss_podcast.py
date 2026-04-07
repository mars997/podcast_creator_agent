import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import feedparser
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
DEFAULT_NUM_ARTICLES = 3
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
    """Sanitize text for use in filenames"""
    cleaned = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in text).strip()
    return cleaned.replace(" ", "_")


def get_word_range(length_choice: str) -> str:
    """Get word range based on length choice"""
    mapping = {
        "short": "300 to 450 words",
        "medium": "500 to 700 words",
        "long": "800 to 1100 words",
    }
    return mapping.get(length_choice.lower(), "500 to 700 words")


def get_user_input(prompt_text: str, default_value: str) -> str:
    """Get user input with default value"""
    user_value = input(f"{prompt_text} [{default_value}]: ").strip().lower()
    return user_value if user_value else default_value


def validate_choice(value: str, valid_set: set, field_name: str) -> str:
    """Validate user choice against valid set"""
    if value not in valid_set:
        raise ValueError(f"Invalid {field_name}: {value}")
    return value


def parse_rss_feed(feed_url: str, max_items: int = 10) -> list[dict]:
    """Parse RSS feed and extract article information"""
    print(f"\nFetching RSS feed: {feed_url}")

    try:
        feed = feedparser.parse(feed_url)

        if feed.bozo and not feed.entries:
            raise ValueError(f"Failed to parse RSS feed: {feed.get('bozo_exception', 'Unknown error')}")

        if not feed.entries:
            raise ValueError("No entries found in RSS feed")

        print(f"  Feed title: {feed.feed.get('title', 'Unknown')}")
        print(f"  Total entries: {len(feed.entries)}")

        articles = []
        for entry in feed.entries[:max_items]:
            article = {
                'title': entry.get('title', 'Untitled'),
                'link': entry.get('link', ''),
                'description': entry.get('description', '') or entry.get('summary', ''),
                'published': entry.get('published', '') or entry.get('updated', ''),
                'author': entry.get('author', ''),
            }
            articles.append(article)

        return articles

    except Exception as e:
        raise ValueError(f"Error parsing RSS feed: {e}")


def fetch_article_text(url: str) -> str:
    """Fetch article content from URL"""
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


def build_script(topic: str, tone: str, word_range: str, source_material: str) -> str:
    """Generate podcast script using LLM"""
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
    """Generate show notes from script"""
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
    """Generate audio file from script using TTS"""
    tts_provider.generate_audio(script, voice, audio_path)


def save_json(data: dict | list, file_path: Path) -> None:
    """Save data to JSON file"""
    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def update_episode_index(index_path: Path, episode_summary: dict) -> None:
    """Update the global episode index"""
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
    """Main entry point for RSS podcast generation"""
    print("\n" + "=" * 70)
    print("Step 19: RSS Feed Podcast Generator")
    print("=" * 70)

    # Get RSS feed URL
    feed_url = input("\nEnter RSS feed URL: ").strip()
    if not feed_url:
        raise ValueError("RSS feed URL cannot be empty")

    # Get number of articles to include
    num_articles_str = input(f"Number of articles to include [{DEFAULT_NUM_ARTICLES}]: ").strip()
    num_articles = int(num_articles_str) if num_articles_str else DEFAULT_NUM_ARTICLES

    if num_articles < 1 or num_articles > 10:
        raise ValueError("Number of articles must be between 1 and 10")

    # Get podcast settings
    topic = input("Enter episode topic/title: ").strip()
    tone = get_user_input("Choose tone (casual/professional/educational)", DEFAULT_TONE)
    voice = get_user_input("Choose voice (alloy/echo/fable/onyx/nova/shimmer)", DEFAULT_VOICE)
    length = get_user_input("Choose length (short/medium/long)", DEFAULT_LENGTH)

    if not topic:
        raise ValueError("Topic cannot be empty")

    tone = validate_choice(tone, VALID_TONES, "tone")
    voice = validate_choice(voice, VALID_VOICES, "voice")
    length = validate_choice(length, VALID_LENGTHS, "length")

    word_range = get_word_range(length)

    # Parse RSS feed
    articles = parse_rss_feed(feed_url, max_items=num_articles * 2)  # Fetch extra in case some fail

    if not articles:
        raise ValueError("No articles found in RSS feed")

    print(f"\n  Found {len(articles)} articles")

    # Display articles
    print("\n  Latest articles:")
    for i, article in enumerate(articles[:num_articles], start=1):
        print(f"    [{i}] {article['title']}")
        if article['published']:
            print(f"        Published: {article['published']}")

    # Fetch article content
    all_sources = []
    successful_articles = []
    failed_articles = []

    print(f"\nFetching content from {num_articles} articles...")

    for i, article in enumerate(articles[:num_articles], start=1):
        article_url = article['link']
        article_title = article['title']

        try:
            print(f"  [{i}] Fetching: {article_title[:60]}...")
            article_text = fetch_article_text(article_url)
            all_sources.append(f"Source {i}:\n{article_text}")

            successful_articles.append({
                'title': article_title,
                'url': article_url,
                'published': article['published'],
                'author': article['author']
            })
            print(f"      Success")
        except Exception as e:
            print(f"      Failed: {e}")
            failed_articles.append({
                'title': article_title,
                'url': article_url,
                'error': str(e)
            })

    if not all_sources:
        raise ValueError("Could not fetch any article content")

    print(f"\n  Successfully fetched: {len(successful_articles)} articles")
    if failed_articles:
        print(f"  Failed to fetch: {len(failed_articles)} articles")

    # Create episode folder
    safe_topic = sanitize_filename(topic)
    timestamp_suffix = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    unique_episode_id = f"{safe_topic}_{timestamp_suffix}"

    output_root = Path(OUTPUT_ROOT)
    output_root.mkdir(parents=True, exist_ok=True)

    episode_dir = output_root / unique_episode_id
    episode_dir.mkdir(parents=True, exist_ok=True)

    sources_dir = episode_dir / "sources"
    sources_dir.mkdir(exist_ok=True)

    # Save RSS feed info
    rss_info_file = sources_dir / "rss_feed_info.json"
    rss_info = {
        'feed_url': feed_url,
        'fetched_at': datetime.now().isoformat(),
        'num_articles_requested': num_articles,
        'num_articles_successful': len(successful_articles),
        'articles': successful_articles
    }
    save_json(rss_info, rss_info_file)
    print(f"\n  RSS info saved: {rss_info_file.name}")

    # Save article sources
    for i, article_info in enumerate(successful_articles, start=1):
        article_url = article_info['url']
        domain = urlparse(article_url).netloc.replace(".", "_")
        source_file = sources_dir / f"article_{i}_{domain}.txt"

        # Find the corresponding source text
        if i <= len(all_sources):
            source_file.write_text(all_sources[i-1], encoding="utf-8")
            print(f"  Saved article {i}: {source_file.name}")

    combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(all_sources)

    # Generate script
    print("\nGenerating podcast script...")
    script = build_script(topic, tone, word_range, combined_source_text)

    script_file = episode_dir / "script.txt"
    script_file.write_text(script, encoding="utf-8")
    print(f"  Script saved: {script_file.name}")

    # Generate show notes
    print("\nGenerating show notes...")
    show_notes = build_show_notes(script)

    show_notes_file = episode_dir / "show_notes.txt"
    show_notes_file.write_text(show_notes, encoding="utf-8")
    print(f"  Show notes saved: {show_notes_file.name}")

    # Generate audio
    audio_file = episode_dir / f"podcast_{voice}.mp3"

    print("\nGenerating audio...")
    generate_audio(script, voice, audio_file)
    print(f"  Audio saved: {audio_file.name}")

    # Save metadata
    created_at = datetime.now().isoformat()

    metadata = {
        "created_at": created_at,
        "episode_id": unique_episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "source_type": "rss_feed",
        "rss_feed": {
            "feed_url": feed_url,
            "num_articles_requested": num_articles,
            "num_articles_successful": len(successful_articles),
            "num_articles_failed": len(failed_articles),
            "articles": successful_articles,
            "failed_articles": failed_articles
        },
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
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file),
            "rss_info_file": str(rss_info_file)
        }
    }

    metadata_file = episode_dir / "metadata.json"
    save_json(metadata, metadata_file)
    print(f"  Metadata saved: {metadata_file.name}")

    # Update episode index
    episode_summary = {
        "created_at": created_at,
        "episode_id": unique_episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "source_type": "rss_feed",
        "episode_dir": str(episode_dir),
        "metadata_file": str(metadata_file),
        "script_file": str(script_file),
        "show_notes_file": str(show_notes_file),
        "audio_file": str(audio_file),
        "num_rss_articles": len(successful_articles),
        "rss_feed_url": feed_url
    }

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)
    print(f"\nEpisode index updated: {index_file}")

    print("\n" + "=" * 70)
    print("Step 19 Complete!")
    print("=" * 70)
    print(f"\nEpisode ID: {unique_episode_id}")
    print(f"Location: {episode_dir}")
    print(f"\nRSS Feed: {feed_url}")
    print(f"Articles included: {len(successful_articles)}")
    print(f"\nFiles generated:")
    print(f"  - sources/rss_feed_info.json")
    print(f"  - sources/article_*.txt ({len(successful_articles)} files)")
    print(f"  - script.txt")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")


if __name__ == "__main__":
    main()
