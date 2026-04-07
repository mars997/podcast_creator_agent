"""
Demo script for Step 20 - Pasted Content Podcast
Creates a demo episode from pasted text without requiring API calls.
Uses one of the existing REAL audio files to demonstrate playability.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime


def demo_pasted_content_podcast():
    """Create a demo pasted-content episode"""
    print("=" * 70)
    print("Step 20 Demo: Pasted Content Podcast")
    print("=" * 70)

    # Sample pasted content (simulating a newsletter or article)
    sample_content = """The Future of AI in Healthcare

Artificial intelligence is revolutionizing the healthcare industry in unprecedented ways. From diagnostic tools to personalized treatment plans, AI is transforming how medical professionals approach patient care.

Recent breakthroughs in machine learning have enabled AI systems to analyze medical imaging with accuracy rivaling expert radiologists. These systems can detect subtle patterns in X-rays, MRIs, and CT scans that might be missed by the human eye.

One of the most promising applications is in drug discovery. AI algorithms can analyze vast databases of molecular structures and predict which compounds are most likely to be effective against specific diseases. This dramatically reduces the time and cost of bringing new medications to market.

Personalized medicine is another frontier where AI excels. By analyzing a patient's genetic makeup, medical history, and lifestyle factors, AI systems can recommend tailored treatment plans that are more effective than one-size-fits-all approaches.

However, challenges remain. Privacy concerns, data security, and the need for transparent AI decision-making are critical issues that must be addressed. Healthcare providers must ensure that AI tools augment rather than replace human judgment and compassion.

As we move forward, the integration of AI in healthcare promises to make medical care more accurate, efficient, and accessible to people worldwide."""

    print("\nSample pasted content (newsletter/article):")
    print("-" * 70)
    print(sample_content[:300] + "...")
    print("-" * 70)
    print(f"\nContent stats:")
    print(f"  Characters: {len(sample_content)}")
    print(f"  Words: {len(sample_content.split())}")

    # Create episode
    topic = "ai_in_healthcare_newsletter"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    episode_id = f"{topic}_{timestamp}"

    output_root = Path("output")
    episode_dir = output_root / episode_id
    episode_dir.mkdir(parents=True, exist_ok=True)

    sources_dir = episode_dir / "sources"
    sources_dir.mkdir(exist_ok=True)

    print(f"\nCreating demo episode: {episode_id}")

    # Save pasted content
    source_file = sources_dir / "pasted_content.txt"
    source_file.write_text(sample_content, encoding="utf-8")
    print(f"  Created: sources/pasted_content.txt")

    # Create mock script
    mock_script = f"""AI in Healthcare: A Revolution in Medicine

[Demo episode from pasted newsletter content]

Welcome to today's episode where we dive into the exciting world of artificial intelligence in healthcare!

The content for this episode comes from a pasted newsletter article about how AI is transforming modern medicine. This demonstrates Step 20's ability to turn any pasted text - from newsletters, articles, or blog posts - into podcast episodes.

Key Topics Covered:

First, let's talk about AI in medical imaging. Machine learning systems are now analyzing X-rays, MRIs, and CT scans with incredible accuracy, often matching or exceeding expert radiologists in detecting subtle patterns.

Second, drug discovery is being revolutionized. AI algorithms analyze millions of molecular structures to predict which compounds will be most effective, dramatically reducing development time and costs.

Third, personalized medicine is becoming a reality. By analyzing genetic data, medical history, and lifestyle factors, AI creates tailored treatment plans that work better than traditional one-size-fits-all approaches.

Of course, there are challenges. Privacy, data security, and ensuring AI augments rather than replaces human judgment remain critical concerns.

The future of healthcare is here, powered by artificial intelligence making medicine more accurate, efficient, and accessible.

Thanks for listening! This demonstrates how easily you can turn pasted content into podcast episodes.

[End of demo script - {len(sample_content.split())} words from pasted content]
"""

    script_file = episode_dir / "script.txt"
    script_file.write_text(mock_script, encoding="utf-8")
    print(f"  Created: script.txt")

    # Create show notes
    mock_show_notes = f"""Show Notes - AI in Healthcare Newsletter

Summary:
This episode explores how artificial intelligence is revolutionizing healthcare,
from medical imaging to drug discovery and personalized medicine.

Content Source: Pasted newsletter/article
Word Count: {len(sample_content.split())} words
Input Method: Pasted text (Step 20 feature)

Key Takeaways:
1. AI systems can analyze medical imaging with expert-level accuracy
2. Machine learning is accelerating drug discovery and reducing costs
3. Personalized medicine powered by AI enables tailored treatment plans

Challenges Addressed:
- Privacy and data security concerns
- Need for transparent AI decision-making
- Ensuring AI augments human judgment

This episode demonstrates Step 20's pasted-content ingestion feature, which allows
you to create podcast episodes from any text you can copy and paste - no file
creation required!

[Demo show notes - Step 20]
"""

    show_notes_file = episode_dir / "show_notes.txt"
    show_notes_file.write_text(mock_show_notes, encoding="utf-8")
    print(f"  Created: show_notes.txt")

    # IMPORTANT: Copy a REAL audio file from existing episodes
    # This ensures the audio is actually playable
    source_audio = None
    for audio_path in [
        "output/ai_trending/podcast_nova.mp3",
        "output/healthcare/podcast_nova.mp3",
        "output/test/podcast_nova.mp3"
    ]:
        if Path(audio_path).exists():
            source_audio = Path(audio_path)
            break

    audio_file = episode_dir / "podcast_nova.mp3"

    if source_audio and source_audio.exists():
        # Copy real audio file
        shutil.copy2(source_audio, audio_file)
        audio_size_kb = audio_file.stat().st_size // 1024
        print(f"  Created: podcast_nova.mp3 (REAL audio, {audio_size_kb} KB)")
        print(f"    Copied from: {source_audio}")
        print(f"    This audio file WILL PLAY in Windows Media Player!")
    else:
        # Fallback to mock
        audio_file.write_text("[Mock MP3 - no real audio files found to copy]", encoding="utf-8")
        print(f"  Created: podcast_nova.mp3 (mock - no source audio found)")

    # Create metadata
    created_at = datetime.now().isoformat()

    metadata = {
        "created_at": created_at,
        "episode_id": episode_id,
        "topic": topic,
        "tone": "educational",
        "voice": "nova",
        "length": "medium",
        "source_type": "pasted_content",
        "content_info": {
            "source": "pasted_text",
            "character_count": len(sample_content),
            "word_count": len(sample_content.split()),
            "input_method": "paste"
        },
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file),
            "source_file": str(source_file)
        },
        "demo_mode": True,
        "note": "Demo episode - audio copied from existing real file" if source_audio else "Demo episode"
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
        "source_type": "pasted_content",
        "episode_dir": str(episode_dir),
        "metadata_file": str(metadata_file),
        "script_file": str(script_file),
        "show_notes_file": str(show_notes_file),
        "audio_file": str(audio_file),
        "content_word_count": len(sample_content.split()),
        "demo_mode": True
    }

    index_data.append(episode_summary)
    index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Updated: episode_index.json")

    print("\n" + "=" * 70)
    print("Demo Pasted Content Podcast Complete!")
    print("=" * 70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Location: {episode_dir}")
    print(f"\nContent source: Pasted newsletter/article")
    print(f"Word count: {len(sample_content.split())}")
    print(f"\nFiles created:")
    print(f"  - sources/pasted_content.txt")
    print(f"  - script.txt")
    print(f"  - show_notes.txt")
    if source_audio:
        print(f"  - podcast_nova.mp3 (REAL PLAYABLE AUDIO)")
    else:
        print(f"  - podcast_nova.mp3 (mock)")
    print(f"  - metadata.json")
    print(f"\nYou can view this episode using:")
    print(f"  python step17_episode_browser.py")
    if source_audio:
        print(f"\nAudio file location:")
        print(f"  {audio_file}")
        print(f"\n  >>> This audio file WILL PLAY in Windows Media Player! <<<")


if __name__ == "__main__":
    demo_pasted_content_podcast()
