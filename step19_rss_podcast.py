from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from core.provider_setup import initialize_providers, get_provider_info
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file, ensure_directory, save_json
from core.source_management import fetch_article_text
from core.episode_management import save_episode_metadata, create_episode_summary, update_episode_index
from core.rss_utils import parse_rss_feed, save_rss_info
import config


# Initialize providers
llm_provider, tts_provider = initialize_providers()

# Configuration
DEFAULT_TONE = config.DEFAULT_TONE
DEFAULT_VOICE = config.PROVIDER_MODELS.get(tts_provider.provider_name, {}).get("default_voice", "nova")
DEFAULT_LENGTH = config.DEFAULT_LENGTH
DEFAULT_NUM_ARTICLES = 3
OUTPUT_ROOT = config.OUTPUT_ROOT

VALID_TONES = config.VALID_TONES
VALID_VOICES = set(tts_provider.available_voices)
VALID_LENGTHS = config.VALID_LENGTHS


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

    # Parse RSS feed using core module
    articles = parse_rss_feed(feed_url, max_items=num_articles * 2)

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
    episode_dir = ensure_directory(output_root / unique_episode_id)
    sources_dir = ensure_directory(episode_dir / "sources")

    # Save RSS feed info using core module
    rss_info = {
        'feed_url': feed_url,
        'fetched_at': datetime.now().isoformat(),
        'num_articles_requested': num_articles,
        'num_articles_successful': len(successful_articles),
        'articles': successful_articles
    }
    rss_info_file = save_rss_info(sources_dir, rss_info)
    print(f"\n  RSS info saved: {rss_info_file.name}")

    # Save article sources
    for i, article_info in enumerate(successful_articles, start=1):
        article_url = article_info['url']
        domain = urlparse(article_url).netloc.replace(".", "_")
        source_file = sources_dir / f"article_{i}_{domain}.txt"

        if i <= len(all_sources):
            save_text_file(all_sources[i-1], source_file)
            print(f"  Saved article {i}: {source_file.name}")

    combined_source_text = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(all_sources)

    # Generate script
    print("\nGenerating podcast script...")
    script = build_script(llm_provider, topic, tone, word_range, combined_source_text)

    script_file = episode_dir / "script.txt"
    save_text_file(script, script_file)
    print(f"  Script saved: {script_file.name}")

    # Generate show notes
    print("\nGenerating show notes...")
    show_notes = build_show_notes(llm_provider, script)

    show_notes_file = episode_dir / "show_notes.txt"
    save_text_file(show_notes, show_notes_file)
    print(f"  Show notes saved: {show_notes_file.name}")

    # Generate audio
    audio_file = episode_dir / f"podcast_{voice}.mp3"

    print("\nGenerating audio...")
    generate_audio(tts_provider, script, voice, audio_file)
    print(f"  Audio saved: {audio_file.name}")

    # Save metadata
    created_at = datetime.now().isoformat()
    provider_info = get_provider_info(llm_provider, tts_provider)

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
        "providers": provider_info,
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

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"  Metadata saved: {metadata_file.name}")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "num_successful_urls": len(successful_articles),
            "num_successful_files": 0,
            "num_failed_urls": len(failed_articles),
            "num_failed_files": 0,
            "source_type": "rss_feed",
            "num_rss_articles": len(successful_articles),
            "rss_feed_url": feed_url
        }
    )

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
