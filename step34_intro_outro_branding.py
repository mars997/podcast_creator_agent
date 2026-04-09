"""
Step 34: Intro / Outro Audio Branding

Adds custom intro and outro segments to podcasts for branding.
Supports pre-recorded audio files or TTS-generated branding segments.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import json

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.provider_setup import get_provider_info
from core.content_generation import generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


# Default branding templates
DEFAULT_INTRO_TEMPLATES = {
    "tech": "Welcome to Tech Insights, where we break down the latest in technology and innovation. I'm your host, and today we're diving into {topic}.",
    "business": "You're listening to Business Briefing. Today's episode: {topic}. Let's get started.",
    "educational": "Welcome to the Learning Hour. Today we're exploring {topic}. Let's dive in.",
    "news": "This is your Daily News Recap. Here's what's happening with {topic}.",
    "casual": "Hey everyone! Welcome back to the podcast. Today we're talking about {topic}. Let's jump right in."
}

DEFAULT_OUTRO_TEMPLATES = {
    "tech": "Thanks for listening to Tech Insights. Don't forget to subscribe for more episodes. See you next time!",
    "business": "That's all for today's Business Briefing. For more episodes, subscribe wherever you get your podcasts.",
    "educational": "Thanks for learning with us today. If you enjoyed this episode, please share it with others. Until next time!",
    "news": "That's your news recap for today. Stay informed, and we'll see you in the next episode.",
    "casual": "Alright, that's it for today! Thanks for hanging out. Catch you in the next one!"
}


def generate_intro_text(topic: str, template_key: str = "casual", custom_text: Optional[str] = None) -> str:
    """Generate intro text"""
    if custom_text:
        return custom_text

    template = DEFAULT_INTRO_TEMPLATES.get(template_key, DEFAULT_INTRO_TEMPLATES["casual"])
    return template.format(topic=topic)


def generate_outro_text(template_key: str = "casual", custom_text: Optional[str] = None) -> str:
    """Generate outro text"""
    if custom_text:
        return custom_text

    return DEFAULT_OUTRO_TEMPLATES.get(template_key, DEFAULT_OUTRO_TEMPLATES["casual"])


def create_branded_audio(
    tts_provider,
    intro_text: str,
    main_script: str,
    outro_text: str,
    voice: str,
    output_dir: Path
) -> Tuple[Optional[Path], Optional[Path], Optional[Path], Optional[Path]]:
    """Generate intro, main, outro, and combined audio"""

    # Create branding directory
    branding_dir = output_dir / "branding"
    branding_dir.mkdir(exist_ok=True)

    # Generate intro
    intro_file = branding_dir / "intro.mp3"
    print("[INFO] Generating intro audio...")
    try:
        generate_audio(tts_provider, intro_text, voice, intro_file)
        print("[OK] Intro generated")
    except Exception as e:
        print(f"[ERROR] Intro generation failed: {e}")
        intro_file = None

    # Generate main content
    main_file = branding_dir / "main_content.mp3"
    print("[INFO] Generating main content audio...")
    try:
        generate_audio(tts_provider, main_script, voice, main_file)
        print("[OK] Main content generated")
    except Exception as e:
        print(f"[ERROR] Main content generation failed: {e}")
        main_file = None

    # Generate outro
    outro_file = branding_dir / "outro.mp3"
    print("[INFO] Generating outro audio...")
    try:
        generate_audio(tts_provider, outro_text, voice, outro_file)
        print("[OK] Outro generated")
    except Exception as e:
        print(f"[ERROR] Outro generation failed: {e}")
        outro_file = None

    # Combine all segments
    combined_file = output_dir / f"podcast_{voice}.mp3"

    if intro_file and main_file and outro_file:
        print("\n[INFO] Combining intro + content + outro...")
        try:
            from pydub import AudioSegment

            intro_audio = AudioSegment.from_mp3(str(intro_file))
            main_audio = AudioSegment.from_mp3(str(main_file))
            outro_audio = AudioSegment.from_mp3(str(outro_file))

            # Add 500ms silence between segments
            silence = AudioSegment.silent(duration=500)

            combined = intro_audio + silence + main_audio + silence + outro_audio
            combined.export(str(combined_file), format="mp3")

            print("[OK] Combined audio created")

        except ImportError:
            print("[WARN] pydub not available. Individual segments saved.")
            print("[INFO] Install pydub for automatic combining: pip install pydub")
            combined_file = None

        except Exception as e:
            print(f"[ERROR] Audio combining failed: {e}")
            combined_file = None
    else:
        print("[WARN] Some segments missing. Combined audio not created.")
        combined_file = None

    return intro_file, main_file, outro_file, combined_file


def main():
    """Branded podcast generation with intro/outro"""
    print("\n" + "="*70)
    print("Step 34: Intro / Outro Audio Branding")
    print("="*70)

    # Detect providers
    available = detect_available_providers()
    if not available:
        print("\n[ERROR] No providers available. Set OPENAI_API_KEY or GOOGLE_API_KEY")
        return

    # Provider setup
    provider_name = list(available.keys())[0]
    provider_config = ProviderConfig(
        llm_provider=provider_name,
        tts_provider=provider_name
    )

    llm_provider = create_llm_provider(provider_config)
    tts_provider = create_tts_provider(provider_config)

    print(f"\n[OK] Using provider: {provider_name}")

    # Get episode settings
    topic = input("\nEnter episode topic: ").strip()
    if not topic:
        topic = "Branded Podcast Demo"

    # Choose branding style
    print("\n" + "="*70)
    print("Branding Styles")
    print("="*70)
    styles = list(DEFAULT_INTRO_TEMPLATES.keys())
    for i, style in enumerate(styles, 1):
        print(f"{i}. {style.capitalize()}")

    print(f"{len(styles)+1}. Custom (enter your own)")
    print("="*70)

    style_choice = input(f"\nChoose branding style (1-{len(styles)+1}, default 1): ").strip() or "1"

    try:
        style_idx = int(style_choice) - 1
        if 0 <= style_idx < len(styles):
            style_key = styles[style_idx]
            custom_intro = None
            custom_outro = None
        else:
            style_key = "custom"
            print("\nEnter custom intro (include {topic} where topic should appear):")
            custom_intro = input().strip()
            print("\nEnter custom outro:")
            custom_outro = input().strip()
    except ValueError:
        style_key = styles[0]
        custom_intro = None
        custom_outro = None

    print(f"\n[OK] Branding style: {style_key}")

    # Other settings
    tone = get_user_input("Choose tone (casual/professional/educational)", config.DEFAULT_TONE)
    voice = get_user_input(
        f"Choose voice ({'/'.join(tts_provider.available_voices)})",
        tts_provider.available_voices[0]
    )
    length = get_user_input("Choose length (short/medium/long)", config.DEFAULT_LENGTH)

    # Validate
    tone = validate_choice(tone, config.VALID_TONES, "tone")
    voice = validate_choice(voice, set(tts_provider.available_voices), "voice")
    length = validate_choice(length, config.VALID_LENGTHS, "length")
    word_range = get_word_range(length)

    # Create episode directory
    output_root = Path(config.OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"\n[OK] Episode directory: {episode_dir}")

    # Generate intro and outro text
    intro_text = generate_intro_text(topic, style_key, custom_intro)
    outro_text = generate_outro_text(style_key, custom_outro)

    # Save branding scripts
    branding_file = episode_dir / "branding_scripts.txt"
    branding_content = f"""Branding Scripts
{"="*50}

INTRO:
{intro_text}

{"="*50}

OUTRO:
{outro_text}
"""
    save_text_file(branding_content, branding_file)
    print(f"[OK] Branding scripts saved")

    # Generate main script
    print(f"\nGenerating main podcast script...")
    try:
        prompt = f"""Generate a podcast script about: {topic}

Tone: {tone}
Target length: {word_range[0]}-{word_range[1]} words

NOTE: Do NOT include intro or outro - they will be added separately.
Focus only on the main content.

Generate the complete podcast script:"""

        main_script = llm_provider.generate_text(prompt)
        script_file = episode_dir / "script.txt"

        # Save full script (intro + main + outro)
        full_script = f"{intro_text}\n\n{main_script}\n\n{outro_text}"
        save_text_file(full_script, script_file)

        print(f"[OK] Script generated")

    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Generate branded audio
    print(f"\nGenerating branded audio (intro + content + outro)...")
    try:
        intro_file, main_file, outro_file, combined_file = create_branded_audio(
            tts_provider, intro_text, main_script, outro_text, voice, episode_dir
        )

    except Exception as e:
        print(f"[ERROR] Audio generation failed: {e}")
        intro_file = main_file = outro_file = combined_file = None

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes_prompt = f"""Create show notes for this branded podcast.

Topic: {topic}
Branding: Includes custom intro and outro

Include:
- Episode summary
- Note about branded format
- Key topics

Main script:
{main_script}

Generate the show notes:"""

        show_notes = llm_provider.generate_text(show_notes_prompt)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")

    except Exception as e:
        print(f"[WARN] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\nBranded format with intro/outro"
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)

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
        "branding": {
            "enabled": True,
            "style": style_key,
            "intro_text": intro_text,
            "outro_text": outro_text,
            "has_intro_audio": intro_file is not None,
            "has_outro_audio": outro_file is not None,
            "has_combined_audio": combined_file is not None
        },
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "branding_scripts_file": str(branding_file),
            "show_notes_file": str(show_notes_file),
            "intro_file": str(intro_file) if intro_file else None,
            "main_file": str(main_file) if main_file else None,
            "outro_file": str(outro_file) if outro_file else None,
            "combined_file": str(combined_file) if combined_file else None
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "branded": True,
            "branding_style": style_key
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 34 Complete: Branded Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Branding: {style_key}")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - branding_scripts.txt (intro & outro text)")
    print(f"  - script.txt (full script with branding)")
    print(f"  - branding/intro.mp3")
    print(f"  - branding/main_content.mp3")
    print(f"  - branding/outro.mp3")
    if combined_file:
        print(f"  - podcast_{voice}.mp3 (combined)")
    print(f"  - show_notes.txt")
    print(f"  - metadata.json")

    if not combined_file:
        print(f"\n[INFO] Install pydub for automatic audio combining:")
        print(f"       pip install pydub")


if __name__ == "__main__":
    main()
