"""
Step 28: Multi-Character Podcast Mode

Generates podcasts with multiple distinct speakers/characters.
Automatically detects character roles and assigns appropriate voices.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re

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


# Character/role detection patterns
CHARACTER_PATTERNS = [
    r'^([A-Z][A-Z\s]+):\s*(.+)$',  # ALL CAPS: text
    r'^(\[.+?\]):\s*(.+)$',  # [Role]: text
    r'^(.+?):\s*(.+)$',  # Name: text
]


def detect_characters_in_script(script: str) -> List[str]:
    """Detect character names/roles from script dialogue"""
    characters = set()

    for line in script.split('\n'):
        line = line.strip()
        if not line:
            continue

        for pattern in CHARACTER_PATTERNS:
            match = re.match(pattern, line)
            if match:
                character = match.group(1).strip()
                # Clean up character name
                character = character.strip('[]').strip()
                if character and len(character) < 30:  # Sanity check
                    characters.add(character)
                break

    return sorted(list(characters))


def assign_voices_to_characters(characters: List[str], available_voices: List[str]) -> Dict[str, str]:
    """Assign different voices to each character"""
    voice_assignments = {}

    # Simple round-robin assignment
    for i, character in enumerate(characters):
        voice = available_voices[i % len(available_voices)]
        voice_assignments[character] = voice

    return voice_assignments


def split_script_by_character(script: str) -> List[Tuple[str, str]]:
    """Split script into (character, dialogue) pairs"""
    segments = []

    for line in script.split('\n'):
        line = line.strip()
        if not line:
            continue

        matched = False
        for pattern in CHARACTER_PATTERNS:
            match = re.match(pattern, line)
            if match:
                character = match.group(1).strip().strip('[]').strip()
                dialogue = match.group(2).strip()
                if character and dialogue:
                    segments.append((character, dialogue))
                    matched = True
                    break

        # If no character pattern matched, treat as narration
        if not matched and line:
            segments.append(("NARRATOR", line))

    return segments


def generate_multi_character_script(llm_provider, topic: str, num_characters: int, tone: str, word_range: tuple) -> str:
    """Generate script with multiple characters"""

    if num_characters == 2:
        character_setup = """Create a two-person dialogue:
- HOST: Asks questions, guides conversation
- GUEST: Provides expertise and insights"""
    elif num_characters == 3:
        character_setup = """Create a three-person dialogue:
- HOST: Moderator, asks questions
- EXPERT1: Primary expert on the topic
- EXPERT2: Secondary expert, different perspective"""
    else:
        character_setup = f"""Create a {num_characters}-person dialogue with distinct roles.
Each speaker should have a clear purpose in the conversation."""

    prompt = f"""Generate a multi-character podcast script about: {topic}

{character_setup}

Requirements:
- Use clear speaker labels (e.g., "HOST:", "GUEST:", "EXPERT1:")
- Each character has distinct personality and speaking style
- Natural back-and-forth dialogue
- Characters build on each other's points
- Conversational and engaging tone: {tone}
- Target length: {word_range[0]}-{word_range[1]} words

Format each line as:
CHARACTER_NAME: dialogue text

Generate the complete multi-character script:"""

    response = llm_provider.generate_text(prompt)
    return response


def generate_multi_voice_audio(tts_provider, script: str, voice_assignments: Dict[str, str], output_file: Path):
    """Generate audio with different voices for each character"""

    # For now, use first assigned voice for entire script
    # Future: will implement actual multi-voice rendering in Step 35
    segments = split_script_by_character(script)

    if segments:
        first_character = segments[0][0]
        primary_voice = voice_assignments.get(first_character, list(voice_assignments.values())[0])
    else:
        primary_voice = list(voice_assignments.values())[0]

    # Generate single-voice audio (multi-voice rendering is Step 35)
    generate_audio(tts_provider, script, primary_voice, output_file)

    return primary_voice


def main():
    """Multi-character podcast generation"""
    print("\n" + "="*70)
    print("Step 28: Multi-Character Podcast Mode")
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
    print(f"[OK] Available voices: {', '.join(tts_provider.available_voices)}")

    # Get episode settings
    topic = input("\nEnter episode topic: ").strip()
    if not topic:
        topic = "Multi-Character Demo"

    num_characters_input = input("Number of characters (2-4, default 2): ").strip() or "2"
    try:
        num_characters = int(num_characters_input)
        if num_characters < 2:
            num_characters = 2
        elif num_characters > 4:
            num_characters = 4
    except ValueError:
        num_characters = 2

    tone = get_user_input("Choose tone (casual/professional/educational)", config.DEFAULT_TONE)
    length = get_user_input("Choose length (short/medium/long)", config.DEFAULT_LENGTH)

    # Validate
    tone = validate_choice(tone, config.VALID_TONES, "tone")
    length = validate_choice(length, config.VALID_LENGTHS, "length")
    word_range = get_word_range(length)

    # Create episode directory
    output_root = Path(config.OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"\n[OK] Episode directory: {episode_dir}")
    print(f"[OK] Characters: {num_characters}")

    # Generate multi-character script
    print(f"\nGenerating {num_characters}-character script...")
    try:
        script = generate_multi_character_script(llm_provider, topic, num_characters, tone, word_range)
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Multi-character script generated")
    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Detect characters
    print("\nDetecting characters in script...")
    characters = detect_characters_in_script(script)
    print(f"[OK] Found {len(characters)} characters: {', '.join(characters)}")

    # Assign voices
    voice_assignments = assign_voices_to_characters(characters, tts_provider.available_voices)
    print("\n[OK] Voice assignments:")
    for character, voice in voice_assignments.items():
        print(f"    {character}: {voice}")

    # Save voice assignment info
    voice_info_file = episode_dir / "voice_assignments.txt"
    voice_info_content = "Voice Assignments\n" + "="*50 + "\n\n"
    for character, voice in voice_assignments.items():
        voice_info_content += f"{character}: {voice}\n"
    save_text_file(voice_info_content, voice_info_file)

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes_prompt = f"""Based on this multi-character podcast script, create show notes.

Characters: {', '.join(characters)}

Include:
- Episode summary
- Character/speaker list
- Key topics discussed
- Main takeaways

Script:
{script}

Generate the show notes:"""

        show_notes = llm_provider.generate_text(show_notes_prompt)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")
    except Exception as e:
        print(f"[WARN] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\nCharacters: {', '.join(characters)}"
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)

    # Generate audio
    audio_file = episode_dir / f"podcast_multi_character.mp3"
    print(f"\nGenerating audio...")
    print("[INFO] Note: Multi-voice rendering will be implemented in Step 35")
    print("[INFO] Using single voice for now")

    try:
        primary_voice = generate_multi_voice_audio(tts_provider, script, voice_assignments, audio_file)
        print(f"[OK] Audio generated (voice: {primary_voice})")
    except Exception as e:
        print(f"[ERROR] Audio generation failed: {e}")

    # Save metadata
    created_at = datetime.now().isoformat()
    provider_info = get_provider_info(llm_provider, tts_provider)

    metadata = {
        "created_at": created_at,
        "episode_id": episode_id,
        "topic": topic,
        "tone": tone,
        "length": length,
        "word_range_target": word_range,
        "multi_character": True,
        "num_characters": num_characters,
        "characters": characters,
        "voice_assignments": voice_assignments,
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file),
            "voice_assignments_file": str(voice_info_file)
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "multi_character": True,
            "num_characters": num_characters,
            "characters": characters
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 28 Complete: Multi-Character Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Characters: {len(characters)} ({', '.join(characters)})")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - script.txt (multi-character dialogue)")
    print(f"  - voice_assignments.txt")
    print(f"  - show_notes.txt")
    print(f"  - podcast_multi_character.mp3")
    print(f"  - metadata.json")
    print(f"\nNote: Full multi-voice rendering will be available in Step 35")


if __name__ == "__main__":
    main()
