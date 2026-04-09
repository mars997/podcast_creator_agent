"""
Step 30: Segment-Aware Generation

Generates podcasts with explicit segment structure (intro, body sections, conclusion).
Each segment has specific purpose and word targets for better pacing.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

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


# Segment structure templates
SEGMENT_STRUCTURES = {
    "basic": {
        "name": "Basic (Intro + Body + Conclusion)",
        "segments": [
            {"name": "intro", "purpose": "Hook and overview", "word_pct": 0.15},
            {"name": "body", "purpose": "Main content", "word_pct": 0.70},
            {"name": "conclusion", "purpose": "Summary and takeaways", "word_pct": 0.15}
        ]
    },

    "three_act": {
        "name": "Three-Act Structure",
        "segments": [
            {"name": "intro", "purpose": "Hook and setup", "word_pct": 0.10},
            {"name": "act1_context", "purpose": "Background and context", "word_pct": 0.25},
            {"name": "act2_exploration", "purpose": "Deep dive and analysis", "word_pct": 0.35},
            {"name": "act3_implications", "purpose": "Implications and future", "word_pct": 0.20},
            {"name": "conclusion", "purpose": "Wrap-up and key takeaways", "word_pct": 0.10}
        ]
    },

    "news_format": {
        "name": "News Format",
        "segments": [
            {"name": "headlines", "purpose": "Quick overview of topics", "word_pct": 0.10},
            {"name": "story1", "purpose": "First main story", "word_pct": 0.30},
            {"name": "story2", "purpose": "Second main story", "word_pct": 0.30},
            {"name": "story3", "purpose": "Third main story", "word_pct": 0.20},
            {"name": "closing", "purpose": "Recap and sign-off", "word_pct": 0.10}
        ]
    },

    "educational": {
        "name": "Educational Deep Dive",
        "segments": [
            {"name": "intro", "purpose": "What we'll learn today", "word_pct": 0.10},
            {"name": "fundamentals", "purpose": "Core concepts", "word_pct": 0.25},
            {"name": "examples", "purpose": "Real-world examples", "word_pct": 0.25},
            {"name": "advanced", "purpose": "Advanced topics or implications", "word_pct": 0.25},
            {"name": "summary", "purpose": "Review and next steps", "word_pct": 0.15}
        ]
    }
}


def calculate_segment_word_targets(total_words: int, segments: List[Dict]) -> List[Tuple[str, int]]:
    """Calculate word count target for each segment"""
    targets = []
    for segment in segments:
        target_words = int(total_words * segment["word_pct"])
        targets.append((segment["name"], segment["purpose"], target_words))
    return targets


def generate_segmented_script(
    llm_provider,
    topic: str,
    structure_key: str,
    tone: str,
    total_words: int
) -> Tuple[str, Dict]:
    """Generate script with explicit segment structure"""

    structure = SEGMENT_STRUCTURES[structure_key]
    segments = structure["segments"]
    segment_targets = calculate_segment_word_targets(total_words, segments)

    # Build segment instructions
    segment_instructions = "\n".join([
        f"{i+1}. [{seg_name.upper()}] ({purpose}) - Target: ~{words} words"
        for i, (seg_name, purpose, words) in enumerate(segment_targets)
    ])

    prompt = f"""Generate a podcast script with EXPLICIT SEGMENT STRUCTURE.

Topic: {topic}
Tone: {tone}
Total target: {total_words} words
Structure: {structure['name']}

SEGMENT BREAKDOWN:
{segment_instructions}

REQUIREMENTS:
- Clearly mark each segment with headers: [SEGMENT_NAME]
- Stay close to word targets for each segment
- Each segment should fulfill its specific purpose
- Smooth transitions between segments
- Overall coherence across all segments

Example format:
[INTRO]
Content for intro segment...

[BODY]
Content for body segment...

[CONCLUSION]
Content for conclusion segment...

Generate the complete segmented podcast script:"""

    response = llm_provider.generate_text(prompt)

    # Metadata about segments
    segment_info = {
        "structure": structure['name'],
        "total_segments": len(segments),
        "segments": [
            {
                "name": seg_name,
                "purpose": purpose,
                "target_words": words
            }
            for seg_name, purpose, words in segment_targets
        ]
    }

    return response, segment_info


def main():
    """Segment-aware podcast generation"""
    print("\n" + "="*70)
    print("Step 30: Segment-Aware Generation")
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

    # Choose segment structure
    print("\n" + "="*70)
    print("Segment Structures")
    print("="*70)

    structure_keys = list(SEGMENT_STRUCTURES.keys())
    for i, (key, struct) in enumerate(SEGMENT_STRUCTURES.items(), 1):
        print(f"\n{i}. {struct['name']}")
        print(f"   Segments: {len(struct['segments'])}")
        for seg in struct['segments']:
            print(f"     - {seg['name']}: {seg['purpose']} ({int(seg['word_pct']*100)}%)")

    print("="*70)
    structure_choice = input(f"\nChoose structure (1-{len(structure_keys)}, default 1): ").strip() or "1"

    try:
        struct_idx = int(structure_choice) - 1
        if 0 <= struct_idx < len(structure_keys):
            structure_key = structure_keys[struct_idx]
        else:
            structure_key = structure_keys[0]
    except ValueError:
        structure_key = structure_keys[0]

    selected_structure = SEGMENT_STRUCTURES[structure_key]
    print(f"\n[OK] Selected: {selected_structure['name']}")

    # Get episode settings
    topic = input("\nEnter episode topic: ").strip()
    if not topic:
        topic = "Segment-Aware Demo"

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

    # Use midpoint of word range for segment calculations
    target_words = (word_range[0] + word_range[1]) // 2

    # Create episode directory
    output_root = Path(config.OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"\n[OK] Episode directory: {episode_dir}")
    print(f"[OK] Structure: {selected_structure['name']}")
    print(f"[OK] Target words: {target_words}")

    # Generate segmented script
    print(f"\nGenerating {len(selected_structure['segments'])}-segment script...")
    try:
        script, segment_info = generate_segmented_script(
            llm_provider, topic, structure_key, tone, target_words
        )
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Segmented script generated")
    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Save segment breakdown
    segment_file = episode_dir / "segment_breakdown.txt"
    segment_content = f"""Segment Breakdown
{"="*50}

Structure: {segment_info['structure']}
Total Segments: {segment_info['total_segments']}

Segment Details:
"""
    for seg in segment_info['segments']:
        segment_content += f"\n{seg['name'].upper()}\n"
        segment_content += f"  Purpose: {seg['purpose']}\n"
        segment_content += f"  Target: {seg['target_words']} words\n"

    save_text_file(segment_content, segment_file)
    print(f"[OK] Segment breakdown saved")

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes_prompt = f"""Create show notes for this segmented podcast script.

Structure: {segment_info['structure']}
Segments: {segment_info['total_segments']}

Include:
- Episode summary
- Segment breakdown with timestamps (estimate based on reading pace)
- Key topics per segment
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
        show_notes = f"Show notes for {topic}\nStructure: {segment_info['structure']}"
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)

    # Generate audio
    audio_file = episode_dir / f"podcast_{voice}.mp3"
    print(f"\nGenerating audio...")
    try:
        generate_audio(tts_provider, script, voice, audio_file)
        print(f"[OK] Audio generated")
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
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "target_words": target_words,
        "segment_structure": segment_info,
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "segment_breakdown_file": str(segment_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file)
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "segment_structure": segment_info['structure'],
            "num_segments": segment_info['total_segments']
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 30 Complete: Segment-Aware Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Structure: {segment_info['structure']}")
    print(f"Segments: {segment_info['total_segments']}")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - script.txt (with segment markers)")
    print(f"  - segment_breakdown.txt")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")


if __name__ == "__main__":
    main()
