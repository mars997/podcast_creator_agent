"""
Step 35: Multi-Voice Rendering

Renders podcasts with different voices for different characters/speakers.
Automatically detects speaker segments and assigns appropriate voices.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import re
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


# Speaker detection patterns (from Step 28)
SPEAKER_PATTERNS = [
    r'^([A-Z][A-Z\s]+):\s*(.+)$',  # ALL CAPS: text
    r'^(\[.+?\]):\s*(.+)$',  # [Role]: text
    r'^(.+?):\s*(.+)$',  # Name: text
]


def detect_speakers_in_script(script: str) -> List[str]:
    """Detect speaker names from script"""
    speakers = set()

    for line in script.split('\n'):
        line = line.strip()
        if not line:
            continue

        for pattern in SPEAKER_PATTERNS:
            match = re.match(pattern, line)
            if match:
                speaker = match.group(1).strip().strip('[]').strip()
                if speaker and len(speaker) < 30:
                    speakers.add(speaker)
                break

    return sorted(list(speakers))


def split_script_by_speaker(script: str) -> List[Tuple[str, str]]:
    """Split script into (speaker, dialogue) segments"""
    segments = []

    for line in script.split('\n'):
        line = line.strip()
        if not line:
            continue

        matched = False
        for pattern in SPEAKER_PATTERNS:
            match = re.match(pattern, line)
            if match:
                speaker = match.group(1).strip().strip('[]').strip()
                dialogue = match.group(2).strip()
                if speaker and dialogue:
                    segments.append((speaker, dialogue))
                    matched = True
                    break

        if not matched and line:
            # Narration or non-speaker text
            segments.append(("NARRATOR", line))

    return segments


def assign_voices_to_speakers(speakers: List[str], available_voices: List[str], manual: bool = False) -> Dict[str, str]:
    """Assign voices to speakers"""
    assignments = {}

    if manual:
        print("\n" + "="*50)
        print("Manual Voice Assignment")
        print("="*50)
        print(f"Available voices: {', '.join(available_voices)}")

        for speaker in speakers:
            print(f"\nAssign voice for {speaker}:")
            for i, voice in enumerate(available_voices, 1):
                print(f"  {i}. {voice}")

            choice = input(f"Choice (1-{len(available_voices)}, default 1): ").strip() or "1"
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_voices):
                    assignments[speaker] = available_voices[idx]
                else:
                    assignments[speaker] = available_voices[0]
            except ValueError:
                assignments[speaker] = available_voices[0]

            print(f"[OK] {speaker} → {assignments[speaker]}")

    else:
        # Automatic round-robin assignment
        for i, speaker in enumerate(speakers):
            assignments[speaker] = available_voices[i % len(available_voices)]

    return assignments


def generate_multi_voice_audio(
    tts_provider,
    segments: List[Tuple[str, str]],
    voice_assignments: Dict[str, str],
    output_dir: Path
) -> Tuple[List[Path], Dict]:
    """Generate audio for each segment with appropriate voice"""

    # Create segments directory
    segments_dir = output_dir / "voice_segments"
    segments_dir.mkdir(exist_ok=True)

    segment_files = []
    segment_info = {
        "total_segments": len(segments),
        "speakers": list(voice_assignments.keys()),
        "segments": []
    }

    print(f"\n[INFO] Generating {len(segments)} voice segments...")

    for i, (speaker, dialogue) in enumerate(segments, 1):
        voice = voice_assignments.get(speaker, list(voice_assignments.values())[0])

        segment_file = segments_dir / f"segment_{i:04d}_{speaker.lower().replace(' ', '_')}.mp3"

        try:
            generate_audio(tts_provider, dialogue, voice, segment_file)
            segment_files.append(segment_file)

            segment_info["segments"].append({
                "number": i,
                "speaker": speaker,
                "voice": voice,
                "file": str(segment_file.name),
                "text_length": len(dialogue)
            })

            if i % 10 == 0:
                print(f"[OK] {i}/{len(segments)} segments generated")

        except Exception as e:
            print(f"[ERROR] Segment {i} failed: {e}")
            segment_info["segments"].append({
                "number": i,
                "speaker": speaker,
                "error": str(e)
            })

    print(f"[OK] All {len(segment_files)} segments generated")

    return segment_files, segment_info


def combine_multi_voice_segments(segment_files: List[Path], output_file: Path) -> bool:
    """Combine multi-voice segments into final podcast"""

    print(f"\n[INFO] Combining {len(segment_files)} voice segments...")

    try:
        from pydub import AudioSegment

        combined = AudioSegment.empty()

        # Add small silence between speaker changes
        silence = AudioSegment.silent(duration=200)

        for segment_file in segment_files:
            if segment_file.exists():
                segment_audio = AudioSegment.from_mp3(str(segment_file))
                combined += segment_audio + silence

        # Remove final silence
        combined = combined[:-200]

        combined.export(str(output_file), format="mp3")
        print(f"[OK] Multi-voice audio combined")
        return True

    except ImportError:
        print("[WARN] pydub not available for combining")
        print("[INFO] Individual voice segments saved in voice_segments/")
        return False

    except Exception as e:
        print(f"[ERROR] Audio combining failed: {e}")
        return False


def generate_multi_speaker_script(llm_provider, topic: str, num_speakers: int, tone: str, word_range: tuple) -> str:
    """Generate multi-speaker dialogue script"""

    if num_speakers == 2:
        setup = "Create a two-person dialogue (HOST and GUEST)"
    elif num_speakers == 3:
        setup = "Create a three-person dialogue (HOST, EXPERT1, EXPERT2)"
    else:
        setup = f"Create a {num_speakers}-person dialogue with distinct speakers"

    prompt = f"""{setup} about: {topic}

Requirements:
- Clear speaker labels (e.g., "HOST:", "GUEST:", "EXPERT1:")
- Natural conversation flow
- Each speaker has distinct personality
- {tone} tone throughout
- Target: {word_range[0]}-{word_range[1]} words

Format each line as:
SPEAKER_NAME: dialogue

Generate the complete multi-speaker script:"""

    response = llm_provider.generate_text(prompt)
    return response


def main():
    """Multi-voice podcast rendering"""
    print("\n" + "="*70)
    print("Step 35: Multi-Voice Rendering")
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
        topic = "Multi-Voice Demo"

    num_speakers_input = input("Number of speakers (2-4, default 2): ").strip() or "2"
    try:
        num_speakers = int(num_speakers_input)
        if num_speakers < 2:
            num_speakers = 2
        elif num_speakers > 4:
            num_speakers = 4
    except ValueError:
        num_speakers = 2

    tone = get_user_input("Choose tone (casual/professional/educational)", config.DEFAULT_TONE)
    length = get_user_input("Choose length (short/medium/long)", config.DEFAULT_LENGTH)

    # Voice assignment mode
    manual_voices = input("\nManually assign voices? (y/n, default n): ").strip().lower() == 'y'

    # Validate
    tone = validate_choice(tone, config.VALID_TONES, "tone")
    length = validate_choice(length, config.VALID_LENGTHS, "length")
    word_range = get_word_range(length)

    # Create episode directory
    output_root = Path(config.OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"\n[OK] Episode directory: {episode_dir}")
    print(f"[OK] Speakers: {num_speakers}")

    # Generate multi-speaker script
    print(f"\nGenerating {num_speakers}-speaker script...")
    try:
        script = generate_multi_speaker_script(llm_provider, topic, num_speakers, tone, word_range)
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Multi-speaker script generated")
    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Detect speakers
    print("\nDetecting speakers...")
    speakers = detect_speakers_in_script(script)
    print(f"[OK] Found {len(speakers)} speakers: {', '.join(speakers)}")

    # Assign voices
    print("\nAssigning voices to speakers...")
    voice_assignments = assign_voices_to_speakers(speakers, tts_provider.available_voices, manual_voices)

    print("\n[OK] Voice assignments:")
    for speaker, voice in voice_assignments.items():
        print(f"    {speaker} → {voice}")

    # Save voice assignments
    voice_file = episode_dir / "voice_assignments.json"
    with open(voice_file, 'w', encoding='utf-8') as f:
        json.dump(voice_assignments, f, indent=2)

    # Split script by speaker
    segments = split_script_by_speaker(script)
    print(f"\n[OK] Split into {len(segments)} dialogue segments")

    # Generate multi-voice audio
    print(f"\nGenerating multi-voice audio...")
    try:
        segment_files, segment_info = generate_multi_voice_audio(
            tts_provider, segments, voice_assignments, episode_dir
        )

        # Save segment info
        segment_info_file = episode_dir / "segment_info.json"
        with open(segment_info_file, 'w', encoding='utf-8') as f:
            json.dump(segment_info, f, indent=2)

    except Exception as e:
        print(f"[ERROR] Multi-voice generation failed: {e}")
        return

    # Combine segments
    audio_file = episode_dir / f"podcast_multi_voice.mp3"
    combine_success = combine_multi_voice_segments(segment_files, audio_file)

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes_prompt = f"""Create show notes for this multi-voice podcast.

Speakers: {', '.join(speakers)}
Voice assignments: {json.dumps(voice_assignments, indent=2)}

Include:
- Episode summary
- Speaker/voice list
- Key topics
- Note about multi-voice production

Script:
{script}

Generate the show notes:"""

        show_notes = llm_provider.generate_text(show_notes_prompt)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")

    except Exception as e:
        print(f"[WARN] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\nSpeakers: {', '.join(speakers)}"
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
        "length": length,
        "word_range_target": word_range,
        "multi_voice": True,
        "num_speakers": len(speakers),
        "speakers": speakers,
        "voice_assignments": voice_assignments,
        "segment_info": segment_info,
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "voice_assignments_file": str(voice_file),
            "segment_info_file": str(segment_info_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file) if combine_success else None,
            "segments_dir": str(episode_dir / "voice_segments")
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "multi_voice": True,
            "num_speakers": len(speakers),
            "speakers": speakers
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 35 Complete: Multi-Voice Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Speakers: {len(speakers)}")
    print(f"Voice assignments:")
    for speaker, voice in voice_assignments.items():
        print(f"  {speaker} → {voice}")
    print(f"Segments: {segment_info['total_segments']}")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - script.txt (multi-speaker dialogue)")
    print(f"  - voice_assignments.json")
    print(f"  - voice_segments/ ({segment_info['total_segments']} files)")
    print(f"  - segment_info.json")
    if combine_success:
        print(f"  - podcast_multi_voice.mp3 (combined)")
    print(f"  - show_notes.txt")
    print(f"  - metadata.json")

    if not combine_success:
        print(f"\n[INFO] Install pydub for automatic combining:")
        print(f"       pip install pydub")


if __name__ == "__main__":
    main()
