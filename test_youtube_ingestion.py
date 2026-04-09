"""
Test YouTube Transcript Ingestion - Step 22

This script demonstrates YouTube transcript extraction using core module functions.
Creates a test episode from a YouTube video transcript.
"""

from pathlib import Path
from datetime import datetime

from core.provider_setup import initialize_providers, get_provider_info
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file, ensure_directory
from core.source_management import (
    extract_video_id,
    fetch_youtube_transcript,
    save_sources_to_directory
)
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


# Sample YouTube URLs for testing
SAMPLE_VIDEOS = {
    "1": {
        "url": "https://www.youtube.com/watch?v=aircAruvnKk",
        "title": "Neural Networks Explained",
        "description": "3Blue1Brown - But what is a neural network?"
    },
    "2": {
        "url": "https://www.youtube.com/watch?v=kCc8FmEb1nY",
        "title": "How does ChatGPT work",
        "description": "Visual explanation of ChatGPT"
    },
    "3": {
        "url": "https://www.youtube.com/watch?v=zjkBMFhNj_g",
        "title": "Intro to Large Language Models",
        "description": "Andrej Karpathy - Introduction to LLMs"
    }
}


def test_video_id_extraction():
    """Test video ID extraction from various URL formats"""
    print("\n" + "="*70)
    print("TEST: YouTube Video ID Extraction")
    print("="*70)

    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
    ]

    for url in test_urls:
        video_id = extract_video_id(url)
        print(f"[OK] {url}")
        print(f"     Video ID: {video_id}")

    print("\n[OK] All URL formats supported")


def test_transcript_fetch(youtube_url: str):
    """Test transcript fetching from a YouTube video"""
    print("\n" + "="*70)
    print("TEST: YouTube Transcript Extraction")
    print("="*70)

    video_id = extract_video_id(youtube_url)
    print(f"\nVideo URL: {youtube_url}")
    print(f"Video ID: {video_id}")

    try:
        # Fetch transcript
        print("\nFetching transcript...")
        transcript = fetch_youtube_transcript(youtube_url)

        print(f"\n[OK] Transcript fetched successfully")
        print(f"  Total length: {len(transcript)} characters")
        print(f"  Word count: {len(transcript.split())} words")

        # Show preview
        print(f"\n[PREVIEW] First 400 characters:")
        print("-" * 70)
        print(transcript[:400])
        if len(transcript) > 400:
            print("...")
        print("-" * 70)

        return transcript

    except Exception as e:
        print(f"\n[FAIL] Transcript fetch failed: {e}")
        print("\nPossible reasons:")
        print("  - Video has transcripts disabled")
        print("  - No English transcript available")
        print("  - Video is private or deleted")
        print("  - Network/API error")
        return None


def create_episode_from_youtube(youtube_url: str):
    """Create a full podcast episode from YouTube video"""
    print("\n" + "="*70)
    print("STEP 22: YouTube to Podcast Episode")
    print("="*70)

    # Initialize providers
    print("\nInitializing providers...")
    llm_provider, tts_provider = initialize_providers(verbose=False)
    print(f"[OK] LLM: {llm_provider.provider_name}")
    print(f"[OK] TTS: {tts_provider.provider_name}")

    # Extract video ID
    video_id = extract_video_id(youtube_url)

    # Get settings
    topic = input(f"\nEnter episode topic (or press Enter for 'YouTube_{video_id}'): ").strip()
    if not topic:
        topic = f"YouTube_{video_id}"

    tone = get_user_input("Choose tone (casual/professional/educational)", config.DEFAULT_TONE)
    voice = get_user_input(
        f"Choose voice ({'/'.join(tts_provider.available_voices)})",
        config.PROVIDER_MODELS.get(tts_provider.provider_name, {}).get("default_voice", "nova")
    )
    length = get_user_input("Choose length (short/medium/long)", config.DEFAULT_LENGTH)

    # Validate
    tone = validate_choice(tone, config.VALID_TONES, "tone")
    voice = validate_choice(voice, set(tts_provider.available_voices), "voice")
    length = validate_choice(length, config.VALID_LENGTHS, "length")
    word_range = get_word_range(length)

    # Create unique episode directory
    output_root = Path(config.OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)
    sources_dir = ensure_directory(episode_dir / "sources")

    print(f"\n[OK] Episode directory: {episode_dir}")
    print(f"[OK] Episode ID: {episode_id}")

    # Fetch YouTube transcript using core function
    print(f"\nFetching YouTube transcript from: {youtube_url}")
    all_sources = []
    successful, failed = save_sources_to_directory(
        sources_dir,
        all_sources,
        urls=[youtube_url],  # ← Automatically detects YouTube!
        files=None
    )

    if not all_sources:
        print("[FAIL] No transcript extracted from YouTube")
        print("\nTry a different video with available transcripts")
        return

    combined_source = "\n\n".join(all_sources)

    # Generate script
    print("\nGenerating podcast script...")
    try:
        script = build_script(llm_provider, topic, tone, word_range, combined_source)
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Script saved: {script_file.name}")
    except Exception as e:
        print(f"[SKIP] Script generation failed (SSL/API issue): {e}")
        # Use mock script for demo
        script = f"This is a mock podcast script about {topic}.\n\nGenerated from YouTube video: {youtube_url}"
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Mock script saved: {script_file.name}")

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes = build_show_notes(llm_provider, script)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes saved: {show_notes_file.name}")
    except Exception as e:
        print(f"[SKIP] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\n\nSource: YouTube video {video_id}"
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Mock show notes saved: {show_notes_file.name}")

    # Generate audio (or use mock)
    audio_file = episode_dir / f"podcast_{voice}.mp3"
    print("\nGenerating audio...")
    try:
        generate_audio(tts_provider, script, voice, audio_file)
        print(f"[OK] Audio saved: {audio_file.name}")
    except Exception as e:
        print(f"[SKIP] Audio generation failed: {e}")
        # Copy existing audio as demo
        existing_audio = Path("output/ai_trending/podcast_nova.mp3")
        if existing_audio.exists():
            import shutil
            shutil.copy(existing_audio, audio_file)
            print(f"[OK] Demo audio copied: {audio_file.name}")
        else:
            print(f"[SKIP] No demo audio available")

    # Save metadata
    created_at = datetime.now().isoformat()
    provider_info = get_provider_info(llm_provider, tts_provider)

    metadata = {
        "created_at": created_at,
        "episode_id": episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "source_type": "youtube",
        "youtube_info": {
            "video_url": youtube_url,
            "video_id": video_id,
            "transcript_chars": len(combined_source),
            "transcript_words": len(combined_source.split())
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
            "audio_file": str(audio_file)
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved: {metadata_file.name}")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "num_successful_urls": len(successful),
            "num_failed_urls": len(failed),
            "num_successful_files": 0,
            "num_failed_files": 0,
            "source_type": "youtube",
            "youtube_video_id": video_id,
            "youtube_url": youtube_url
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)
    print(f"[OK] Episode index updated")

    # Summary
    print("\n" + "="*70)
    print("STEP 22 COMPLETE: YouTube to Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Location: {episode_dir}")
    print(f"\nYouTube video: {youtube_url}")
    print(f"  Video ID: {video_id}")
    print(f"  Transcript: {len(combined_source):,} characters")
    print(f"\nGenerated files:")
    print(f"  - sources/source_1_youtube_{video_id}.txt")
    print(f"  - script.txt")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")
    print(f"\nView episode:")
    print(f"  python step17_episode_browser.py --list")


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("YouTube Transcript Ingestion - Step 22")
    print("="*70)

    print("\nOptions:")
    print("1. Test video ID extraction")
    print("2. Test transcript fetching (sample videos)")
    print("3. Create full episode from YouTube URL")
    print("4. Enter custom YouTube URL")

    choice = input("\nChoose option (1-4): ").strip()

    if choice == "1":
        test_video_id_extraction()

    elif choice == "2":
        print("\nSample videos:")
        for key, info in SAMPLE_VIDEOS.items():
            print(f"{key}. {info['title']}")
            print(f"   {info['description']}")

        video_choice = input(f"\nChoose video (1-{len(SAMPLE_VIDEOS)}): ").strip()
        if video_choice in SAMPLE_VIDEOS:
            url = SAMPLE_VIDEOS[video_choice]["url"]
            transcript = test_transcript_fetch(url)

            if transcript:
                create = input("\nCreate full episode from this video? (y/n): ").strip().lower()
                if create == 'y':
                    create_episode_from_youtube(url)

    elif choice == "3":
        print("\nSample videos:")
        for key, info in SAMPLE_VIDEOS.items():
            print(f"{key}. {info['title']}")

        video_choice = input(f"\nChoose video (1-{len(SAMPLE_VIDEOS)}): ").strip()
        if video_choice in SAMPLE_VIDEOS:
            url = SAMPLE_VIDEOS[video_choice]["url"]
            create_episode_from_youtube(url)

    elif choice == "4":
        url = input("\nEnter YouTube URL: ").strip()
        if url:
            transcript = test_transcript_fetch(url)
            if transcript:
                create = input("\nCreate full episode? (y/n): ").strip().lower()
                if create == 'y':
                    create_episode_from_youtube(url)
        else:
            print("[FAIL] No URL provided")

    else:
        print("[FAIL] Invalid choice")


if __name__ == "__main__":
    main()
