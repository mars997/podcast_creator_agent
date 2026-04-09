"""
Step 37: Automated Episode Generation

Enables fully automated podcast creation with minimal user input.
Runs on schedule or triggered events, generates episodes end-to-end.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.provider_setup import get_provider_info
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.file_utils import save_text_file
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


# Automation configuration templates
AUTOMATION_PROFILES = {
    "daily_briefing": {
        "name": "Daily Briefing",
        "description": "Automated daily news/updates podcast",
        "frequency": "daily",
        "tone": "professional",
        "voice": "nova",
        "length": "short",
        "template": "news_recap",
        "auto_publish": False
    },

    "weekly_deep_dive": {
        "name": "Weekly Deep Dive",
        "description": "Automated weekly in-depth analysis",
        "frequency": "weekly",
        "tone": "educational",
        "voice": "onyx",
        "length": "long",
        "template": "deep_dive",
        "auto_publish": False
    },

    "trending_topics": {
        "name": "Trending Topics",
        "description": "Automated podcast on trending subjects",
        "frequency": "as_needed",
        "tone": "casual",
        "voice": "echo",
        "length": "medium",
        "template": "solo_explainer",
        "auto_publish": False
    }
}


def generate_automated_episode(
    topic: str,
    profile: Dict,
    provider_config: Optional[ProviderConfig] = None,
    sources: Optional[List[str]] = None
) -> Dict:
    """Generate complete episode automatically"""

    print(f"\n{'='*70}")
    print(f"Automated Episode Generation: {profile['name']}")
    print(f"{'='*70}")

    # Provider setup
    if not provider_config:
        available = detect_available_providers()
        if not available:
            raise Exception("No providers available")

        provider_name = list(available.keys())[0]
        provider_config = ProviderConfig(
            llm_provider=provider_name,
            tts_provider=provider_name
        )

    llm_provider = create_llm_provider(provider_config)
    tts_provider = create_tts_provider(provider_config)

    print(f"[OK] Provider: {llm_provider.provider_name}")

    # Extract settings from profile
    tone = profile.get("tone", config.DEFAULT_TONE)
    voice = profile.get("voice", "nova")
    length = profile.get("length", config.DEFAULT_LENGTH)

    # Validate
    voice = validate_choice(voice, set(tts_provider.available_voices), "voice", default=voice)
    word_range = get_word_range(length)

    # Create episode directory
    output_root = Path(config.OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"[OK] Episode: {episode_id}")
    print(f"[OK] Settings: {tone}, {voice}, {length}")

    # Generate script
    print("\n[1/4] Generating script...")
    try:
        if sources:
            # Use sources if provided
            combined_sources = "\n\n".join(sources)
            script_prompt = f"""Generate a podcast script about: {topic}

Tone: {tone}
Target length: {word_range[0]}-{word_range[1]} words

Source material:
{combined_sources}

Stay grounded in the source material. Generate the complete podcast script:"""
            script = llm_provider.generate_text(script_prompt)
        else:
            # Generate from topic
            script = build_script(llm_provider, topic, tone, word_range)

        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Script generated ({len(script)} chars)")

    except Exception as e:
        raise Exception(f"Script generation failed: {e}")

    # Generate show notes
    print("\n[2/4] Generating show notes...")
    try:
        show_notes = build_show_notes(llm_provider, script)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")

    except Exception as e:
        print(f"[WARN] Show notes failed: {e}")
        show_notes = f"Automated episode: {topic}"
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)

    # Generate audio
    print("\n[3/4] Generating audio...")
    audio_file = episode_dir / f"podcast_{voice}.mp3"
    try:
        generate_audio(tts_provider, script, voice, audio_file)
        print(f"[OK] Audio generated")

    except Exception as e:
        print(f"[ERROR] Audio generation failed: {e}")
        audio_file = None

    # Save metadata
    print("\n[4/4] Saving metadata...")
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
        "automated": True,
        "automation_profile": profile['name'],
        "automation_settings": profile,
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file) if audio_file else None
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "automated": True,
            "profile": profile['name']
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    print(f"[OK] Metadata saved")

    print(f"\n{'='*70}")
    print(f"Automated Episode Complete")
    print(f"{'='*70}")
    print(f"Episode ID: {episode_id}")
    print(f"Profile: {profile['name']}")
    print(f"Location: {episode_dir}")

    return {
        "success": True,
        "episode_id": episode_id,
        "episode_dir": str(episode_dir),
        "metadata": metadata
    }


def save_automation_profile(profile_name: str, profile_config: Dict, config_dir: Path):
    """Save automation profile configuration"""
    config_dir.mkdir(exist_ok=True)

    profile_file = config_dir / f"{profile_name}.json"
    with open(profile_file, 'w', encoding='utf-8') as f:
        json.dump(profile_config, f, indent=2)

    print(f"[OK] Profile saved: {profile_file}")


def load_automation_profile(profile_name: str, config_dir: Path) -> Optional[Dict]:
    """Load automation profile configuration"""
    profile_file = config_dir / f"{profile_name}.json"

    if not profile_file.exists():
        return None

    with open(profile_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Automated episode generation demo"""
    print("\n" + "="*70)
    print("Step 37: Automated Episode Generation")
    print("="*70)

    # Check providers
    available = detect_available_providers()
    if not available:
        print("\n[ERROR] No providers available")
        return

    print("\n[OK] Automation ready")

    # Choose profile
    print("\n" + "="*70)
    print("Automation Profiles")
    print("="*70)

    profile_keys = list(AUTOMATION_PROFILES.keys())
    for i, (key, profile) in enumerate(AUTOMATION_PROFILES.items(), 1):
        print(f"\n{i}. {profile['name']}")
        print(f"   {profile['description']}")
        print(f"   Frequency: {profile['frequency']}")
        print(f"   Settings: {profile['tone']}, {profile['voice']}, {profile['length']}")

    print("="*70)

    profile_choice = input(f"\nChoose profile (1-{len(profile_keys)}, default 1): ").strip() or "1"

    try:
        profile_idx = int(profile_choice) - 1
        if 0 <= profile_idx < len(profile_keys):
            profile_key = profile_keys[profile_idx]
        else:
            profile_key = profile_keys[0]
    except ValueError:
        profile_key = profile_keys[0]

    profile = AUTOMATION_PROFILES[profile_key]

    print(f"\n[OK] Selected: {profile['name']}")

    # Get topic
    topic = input("\nEnter episode topic (or press Enter for auto-suggested topic): ").strip()

    if not topic:
        # Auto-suggest topic based on profile
        if profile_key == "daily_briefing":
            topic = f"Daily Update - {datetime.now().strftime('%Y-%m-%d')}"
        elif profile_key == "weekly_deep_dive":
            topic = f"Weekly Analysis - Week of {datetime.now().strftime('%Y-%m-%d')}"
        else:
            topic = "Automated Episode"

        print(f"[OK] Auto-generated topic: {topic}")

    # Generate episode automatically
    print(f"\nStarting automated generation...")

    try:
        result = generate_automated_episode(
            topic=topic,
            profile=profile,
            sources=None
        )

        if result["success"]:
            print(f"\n{'='*70}")
            print(f"SUCCESS: Automated episode generated")
            print(f"{'='*70}")
            print(f"\nEpisode ID: {result['episode_id']}")
            print(f"Location: {result['episode_dir']}")
            print(f"\nThis episode was generated fully automatically using the")
            print(f"'{profile['name']}' profile.")

            # Save automation log
            log_dir = Path(config.OUTPUT_ROOT) / "automation_logs"
            log_dir.mkdir(exist_ok=True)

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "profile": profile['name'],
                "topic": topic,
                "episode_id": result['episode_id'],
                "success": True
            }

            log_file = log_dir / f"automation_log_{datetime.now().strftime('%Y%m%d')}.json"

            # Append to daily log
            logs = []
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)

            logs.append(log_entry)

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)

            print(f"\n[OK] Automation log updated: {log_file}")

    except Exception as e:
        print(f"\n[ERROR] Automated generation failed: {e}")


if __name__ == "__main__":
    main()
