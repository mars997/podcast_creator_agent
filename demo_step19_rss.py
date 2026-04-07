"""
Demo script for Step 19 - RSS Feed Podcast
Creates a demo episode from RSS feed without requiring full API access.
"""

import json
from pathlib import Path
from datetime import datetime
import feedparser


def demo_rss_podcast():
    """Create a demo RSS-based episode"""
    print("=" * 70)
    print("Step 19 Demo: RSS Feed Podcast (Mock)")
    print("=" * 70)

    # Use a real RSS feed for demonstration
    feed_url = "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
    print(f"\nDemo RSS feed: {feed_url}")

    # Parse feed
    print("\nParsing RSS feed...")
    feed = feedparser.parse(feed_url)

    if not feed.entries:
        print("Error: Could not fetch RSS feed")
        return

    print(f"  Feed title: {feed.feed.get('title', 'Unknown')}")
    print(f"  Total entries: {len(feed.entries)}")

    # Get first 3 articles
    num_articles = min(3, len(feed.entries))
    articles = []

    print(f"\n  Latest {num_articles} articles:")
    for i, entry in enumerate(feed.entries[:num_articles], start=1):
        article = {
            'title': entry.get('title', 'Untitled'),
            'link': entry.get('link', ''),
            'description': entry.get('description', '') or entry.get('summary', ''),
            'published': entry.get('published', '') or entry.get('updated', ''),
            'author': entry.get('author', ''),
        }
        articles.append(article)

        print(f"    [{i}] {article['title']}")
        if article['published']:
            print(f"        Published: {article['published']}")

    # Create episode folder
    topic = "tech_news_from_rss"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    episode_id = f"{topic}_{timestamp}"

    output_root = Path("output")
    episode_dir = output_root / episode_id
    episode_dir.mkdir(parents=True, exist_ok=True)

    sources_dir = episode_dir / "sources"
    sources_dir.mkdir(exist_ok=True)

    print(f"\nCreating demo episode: {episode_id}")

    # Save RSS feed info
    rss_info = {
        'feed_url': feed_url,
        'feed_title': feed.feed.get('title', 'Unknown'),
        'fetched_at': datetime.now().isoformat(),
        'num_articles': num_articles,
        'articles': articles
    }

    rss_info_file = sources_dir / "rss_feed_info.json"
    rss_info_file.write_text(json.dumps(rss_info, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Created: sources/rss_feed_info.json")

    # Create mock article files
    for i, article in enumerate(articles, start=1):
        article_content = f"""Title: {article['title']}
URL: {article['link']}
Published: {article['published']}
Author: {article['author']}

Description:
{article['description']}

[This is a demo - in real RSS podcast, the full article would be fetched from the URL]
"""
        article_file = sources_dir / f"article_{i}_mock.txt"
        article_file.write_text(article_content, encoding="utf-8")
        print(f"  Created: sources/article_{i}_mock.txt")

    # Create mock script
    article_titles = "\n".join([f"- {a['title']}" for a in articles])

    mock_script = f"""Tech News Roundup from RSS Feed

[This is a MOCK episode for demonstration purposes]

Welcome to today's tech news roundup! I've gathered the latest stories from {feed.feed.get('title', 'the RSS feed')}
to keep you updated on what's happening in technology.

Today we're covering {num_articles} key stories:
{article_titles}

Story 1: {articles[0]['title']}
{articles[0]['description'][:200]}...

In a real RSS-generated podcast:
- The full article would be fetched from each URL
- The LLM would analyze all {num_articles} articles
- A cohesive script would be generated combining all sources
- Audio would be generated with natural transitions

This demonstrates how RSS feeds can automatically provide fresh content
for podcast episodes without manual article selection.

[End of mock script]
"""

    script_file = episode_dir / "script.txt"
    script_file.write_text(mock_script, encoding="utf-8")
    print(f"  Created: script.txt")

    # Create mock show notes
    mock_show_notes = f"""Show Notes - Tech News from RSS Feed

Summary:
This episode covers the latest technology news from {feed.feed.get('title', 'RSS feed')}.

Articles covered:
"""
    for i, article in enumerate(articles, start=1):
        mock_show_notes += f"\n{i}. {article['title']}\n   {article['link']}\n   Published: {article['published']}\n"

    mock_show_notes += f"""
Key Takeaways:
1. RSS feeds provide automatic content discovery
2. Multiple articles can be combined into one episode
3. Source attribution is preserved in metadata

RSS Feed: {feed_url}
Generated: {datetime.now().isoformat()}

[Demo show notes - Step 19]
"""

    show_notes_file = episode_dir / "show_notes.txt"
    show_notes_file.write_text(mock_show_notes, encoding="utf-8")
    print(f"  Created: show_notes.txt")

    # Create mock audio
    audio_file = episode_dir / "podcast_nova.mp3"
    audio_file.write_text("[Mock MP3 - would contain actual audio in real RSS podcast]", encoding="utf-8")
    print(f"  Created: podcast_nova.mp3 (mock)")

    # Create metadata
    created_at = datetime.now().isoformat()

    metadata = {
        "created_at": created_at,
        "episode_id": episode_id,
        "topic": topic,
        "tone": "educational",
        "voice": "nova",
        "length": "medium",
        "source_type": "rss_feed",
        "rss_feed": {
            "feed_url": feed_url,
            "feed_title": feed.feed.get('title', 'Unknown'),
            "num_articles": num_articles,
            "articles": articles
        },
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file),
            "rss_info_file": str(rss_info_file)
        },
        "demo_mode": True,
        "note": "This is a demonstration episode created without full API calls"
    }

    metadata_file = episode_dir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Created: metadata.json")

    # Update episode index
    index_path = output_root / "episode_index.json"
    if index_path.exists():
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index_data = []

    episode_summary = {
        "created_at": created_at,
        "episode_id": episode_id,
        "topic": topic,
        "tone": "educational",
        "voice": "nova",
        "length": "medium",
        "source_type": "rss_feed",
        "episode_dir": str(episode_dir),
        "metadata_file": str(metadata_file),
        "script_file": str(script_file),
        "show_notes_file": str(show_notes_file),
        "audio_file": str(audio_file),
        "num_rss_articles": num_articles,
        "rss_feed_url": feed_url,
        "demo_mode": True
    }

    index_data.append(episode_summary)
    index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Updated: episode_index.json")

    print("\n" + "=" * 70)
    print("Demo RSS Podcast Complete!")
    print("=" * 70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Location: {episode_dir}")
    print(f"\nRSS Feed: {feed_url}")
    print(f"Articles: {num_articles}")
    print(f"\nFiles created:")
    print(f"  - sources/rss_feed_info.json")
    print(f"  - sources/article_*.txt ({num_articles} files)")
    print(f"  - script.txt")
    print(f"  - show_notes.txt")
    print(f"  - podcast_nova.mp3 (mock)")
    print(f"  - metadata.json")
    print(f"\nYou can view this episode using:")
    print(f"  python step17_episode_browser.py")


if __name__ == "__main__":
    demo_rss_podcast()
