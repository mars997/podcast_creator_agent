"""
Step 43: CLI Improvements

Enhanced command-line interface with:
- Better menus and prompts
- Retry flow
- Cleaner error messages
- Interactive mode selection
"""

from pathlib import Path
from datetime import datetime
import sys

from providers.factory import detect_available_providers, ProviderConfig, create_llm_provider, create_tts_provider
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import get_word_range
from core.file_utils import save_text_file
from core.episode_management import create_episode_directory, save_episode_metadata
import config


def print_header():
    """Print CLI header"""
    print("\n" + "="*70)
    print("  AI PODCAST CREATOR - Enhanced CLI")
    print("="*70)


def print_menu():
    """Print main menu"""
    print("\n" + "="*70)
    print("  MAIN MENU")
    print("="*70)
    print("  1. Quick Podcast (topic only)")
    print("  2. Source-Based Podcast (with text/files)")
    print("  3. Multi-Character Podcast")
    print("  4. Persona-Driven Podcast")
    print("  5. Template-Based Podcast")
    print("  6. View Recent Episodes")
    print("  7. Settings")
    print("  8. Exit")
    print("="*70)


def get_choice(prompt, valid_options, allow_retry=True):
    """Get validated user choice with retry"""
    while True:
        choice = input(f"\n{prompt}: ").strip()

        if choice in valid_options:
            return choice

        print(f"[ERROR] Invalid choice. Valid options: {', '.join(valid_options)}")

        if not allow_retry:
            return None

        retry = input("Try again? (y/n): ").strip().lower()
        if retry != 'y':
            return None


def get_text_input(prompt, required=True, multiline=False):
    """Get text input with validation"""
    while True:
        if multiline:
            print(f"\n{prompt} (press Enter twice when done):")
            lines = []
            empty_count = 0
            while True:
                line = input()
                if not line:
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                    lines.append(line)
            text = "\n".join(lines).strip()
        else:
            text = input(f"\n{prompt}: ").strip()

        if text or not required:
            return text

        print("[ERROR] This field is required.")
        retry = input("Try again? (y/n): ").strip().lower()
        if retry != 'y':
            return None


def check_prerequisites():
    """Check if system is ready"""
    print("\n[INFO] Checking prerequisites...")

    # Check API keys
    available = detect_available_providers()

    if not available:
        print("\n" + "="*70)
        print("  [ERROR] No API Keys Configured")
        print("="*70)
        print("\n  Please configure at least one API key in .env:")
        print("  - OPENAI_API_KEY for OpenAI")
        print("  - GOOGLE_API_KEY for Google Gemini")
        print("\n  Get keys from:")
        print("  - OpenAI: https://platform.openai.com/api-keys")
        print("  - Gemini: https://aistudio.google.com/app/apikey")
        print("="*70)
        return False

    print(f"[OK] Available providers: {', '.join(available.keys())}")
    return True


def configure_settings():
    """Interactive settings configuration"""
    print("\n" + "="*70)
    print("  SETTINGS")
    print("="*70)

    available = detect_available_providers()
    provider = list(available.keys())[0]

    # Voice
    provider_config = ProviderConfig(llm_provider=provider, tts_provider=provider)
    tts_provider = create_tts_provider(provider_config)

    print(f"\nAvailable voices: {', '.join(tts_provider.available_voices)}")
    voice = get_choice("Select voice", set(tts_provider.available_voices))

    # Tone
    print(f"\nAvailable tones: {', '.join(config.VALID_TONES)}")
    tone = get_choice("Select tone", config.VALID_TONES)

    # Length
    print(f"\nAvailable lengths: {', '.join(config.VALID_LENGTHS)}")
    length = get_choice("Select length", config.VALID_LENGTHS)

    return {
        "provider": provider,
        "voice": voice or "nova",
        "tone": tone or "professional",
        "length": length or "medium"
    }


def generate_podcast_with_retry(settings):
    """Generate podcast with retry on failure"""
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            print(f"\n[INFO] Generation attempt {attempt}/{max_attempts}...")

            # Get topic
            topic = get_text_input("Enter podcast topic", required=True)
            if not topic:
                return

            # Initialize providers
            provider_config = ProviderConfig(
                llm_provider=settings["provider"],
                tts_provider=settings["provider"]
            )
            llm_provider = create_llm_provider(provider_config)
            tts_provider = create_tts_provider(provider_config)

            # Create episode
            output_root = Path(config.OUTPUT_ROOT)
            episode_dir, episode_id = create_episode_directory(output_root, topic)

            print(f"\n[1/4] Generating script...")
            word_range = get_word_range(settings["length"])
            script = build_script(llm_provider, topic, settings["tone"], word_range)

            script_file = episode_dir / "script.txt"
            save_text_file(script, script_file)
            print(f"[OK] Script saved ({len(script)} chars)")

            print(f"\n[2/4] Generating show notes...")
            show_notes = build_show_notes(llm_provider, script)

            show_notes_file = episode_dir / "show_notes.txt"
            save_text_file(show_notes, show_notes_file)
            print(f"[OK] Show notes saved")

            print(f"\n[3/4] Generating audio (this may take a minute)...")
            audio_file = episode_dir / f"podcast_{settings['voice']}.mp3"
            generate_audio(tts_provider, script, settings["voice"], audio_file)
            print(f"[OK] Audio saved")

            print(f"\n[4/4] Saving metadata...")
            metadata = {
                "created_at": datetime.now().isoformat(),
                "episode_id": episode_id,
                "topic": topic,
                "tone": settings["tone"],
                "voice": settings["voice"],
                "length": settings["length"]
            }
            save_episode_metadata(episode_dir, metadata)
            print(f"[OK] Metadata saved")

            print("\n" + "="*70)
            print("  SUCCESS!")
            print("="*70)
            print(f"\n  Episode: {episode_id}")
            print(f"  Location: {episode_dir}")
            print(f"\n  Files:")
            print(f"    - script.txt")
            print(f"    - show_notes.txt")
            print(f"    - podcast_{settings['voice']}.mp3")
            print(f"    - metadata.json")
            print("="*70)

            return True

        except Exception as e:
            print(f"\n[ERROR] Generation failed: {e}")

            if attempt < max_attempts:
                print(f"\n{max_attempts - attempt} attempts remaining.")
                retry = input("Retry? (y/n): ").strip().lower()
                if retry != 'y':
                    break
            else:
                print("\n[ERROR] Max attempts reached.")

    print("\n[FAILED] Podcast generation unsuccessful.")
    return False


def main():
    """Enhanced CLI main loop"""
    print_header()

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Get initial settings
    settings = configure_settings()

    # Main loop
    while True:
        print_menu()

        choice = get_choice("Select option (1-8)", {"1", "2", "3", "4", "5", "6", "7", "8"})

        if choice == "1":
            # Quick podcast
            generate_podcast_with_retry(settings)

        elif choice == "2":
            print("\n[INFO] Source-based podcast - use step9_podcast_from_sources.py")

        elif choice == "3":
            print("\n[INFO] Multi-character - use step28_multi_character_podcast.py")

        elif choice == "4":
            print("\n[INFO] Persona mode - use step32_voice_persona_system.py")

        elif choice == "5":
            print("\n[INFO] Template mode - use step27_podcast_templates.py")

        elif choice == "6":
            # View recent episodes
            output_dir = Path(config.OUTPUT_ROOT)
            episodes = sorted(output_dir.glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]

            print("\n" + "="*70)
            print("  RECENT EPISODES")
            print("="*70)
            for i, ep in enumerate(episodes, 1):
                print(f"  {i}. {ep.name}")
            print("="*70)

        elif choice == "7":
            # Settings
            settings = configure_settings()
            print("\n[OK] Settings updated")

        elif choice == "8":
            # Exit
            print("\n[INFO] Goodbye!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
