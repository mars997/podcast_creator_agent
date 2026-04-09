"""
Step 40: Summarize Before Script Generation

Two-stage generation: first create summary/outline, then expand to full script.
Improves quality, coherence, and allows for approval before full generation.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

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


def generate_content_summary(llm_provider, topic: str, sources: Optional[list] = None) -> str:
    """Stage 1: Generate summary/outline of content"""

    if sources:
        sources_text = "\n\n---\n\n".join(sources)
        prompt = f"""Analyze these sources about "{topic}" and create a structured summary/outline.

Sources:
{sources_text}

Create a summary that includes:
1. Main themes (3-5 key themes)
2. Important facts or claims
3. Different perspectives or angles
4. Suggested structure for podcast (intro, main points, conclusion)

Generate the summary/outline:"""

    else:
        prompt = f"""Create a structured summary/outline for a podcast about: {topic}

Include:
1. Main themes to cover (3-5 themes)
2. Key points for each theme
3. Interesting angles or perspectives
4. Suggested structure (intro, main points, conclusion)
5. Hook or opening idea

Generate the summary/outline:"""

    response = llm_provider.generate_text(prompt)
    return response


def generate_script_from_summary(
    llm_provider,
    topic: str,
    summary: str,
    tone: str,
    word_range: Tuple[int, int],
    template: Optional[str] = None
) -> str:
    """Stage 2: Generate full script from approved summary"""

    template_instruction = ""
    if template:
        template_instruction = f"\nTemplate/Style: {template}"

    prompt = f"""Generate a complete podcast script based on this approved summary/outline.

Topic: {topic}
Tone: {tone}
Target length: {word_range[0]}-{word_range[1]} words{template_instruction}

APPROVED SUMMARY/OUTLINE:
{summary}

---

Generate the full podcast script following the summary/outline above.
Stay faithful to the themes, points, and structure in the summary.
Make it {tone} and engaging.

Generate the complete script:"""

    response = llm_provider.generate_text(prompt)
    return response


def refine_summary(llm_provider, summary: str, feedback: str) -> str:
    """Refine summary based on user feedback"""

    prompt = f"""Revise this podcast summary/outline based on feedback.

CURRENT SUMMARY:
{summary}

USER FEEDBACK:
{feedback}

Generate revised summary incorporating the feedback:"""

    response = llm_provider.generate_text(prompt)
    return response


def main():
    """Two-stage script generation"""
    print("\n" + "="*70)
    print("Step 40: Summarize Before Script Generation")
    print("="*70)

    # Detect providers
    available = detect_available_providers()
    if not available:
        print("\n[ERROR] No providers available")
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
        topic = "Two-Stage Generation Demo"

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

    # STAGE 1: Generate summary
    print(f"\n{'='*70}")
    print("STAGE 1: Generating Content Summary")
    print(f"{'='*70}")

    try:
        summary = generate_content_summary(llm_provider, topic)

        # Save summary
        summary_file = episode_dir / "content_summary.txt"
        save_text_file(summary, summary_file)

        print(f"\n[OK] Summary generated:")
        print(f"\n{summary}\n")

        # Allow review and refinement
        while True:
            action = input("\nActions: (a)pprove, (r)evise, (c)ancel? ").strip().lower()

            if action == 'a':
                print("[OK] Summary approved")
                break

            elif action == 'r':
                feedback = input("\nEnter feedback for revision: ").strip()
                if feedback:
                    print("\n[INFO] Refining summary...")
                    summary = refine_summary(llm_provider, summary, feedback)

                    # Save revised summary
                    save_text_file(summary, summary_file)

                    print(f"\n[OK] Revised summary:")
                    print(f"\n{summary}\n")

            elif action == 'c':
                print("[INFO] Generation cancelled")
                return

            else:
                print("[ERROR] Invalid choice")

    except Exception as e:
        print(f"[ERROR] Summary generation failed: {e}")
        return

    # STAGE 2: Generate full script
    print(f"\n{'='*70}")
    print("STAGE 2: Generating Full Script from Summary")
    print(f"{'='*70}")

    try:
        script = generate_script_from_summary(llm_provider, topic, summary, tone, word_range)

        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)

        print(f"[OK] Full script generated ({len(script)} chars)")

    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes_prompt = f"""Create show notes for this podcast.

Topic: {topic}
Production method: Two-stage generation (summary then script)

Include:
- Episode summary
- Key topics covered
- Note about production method

Script:
{script}

Generate the show notes:"""

        show_notes = llm_provider.generate_text(show_notes_prompt)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")

    except Exception as e:
        print(f"[WARN] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\nTwo-stage generation method"
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
        audio_file = None

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
        "generation_method": "two_stage",
        "stages": {
            "stage1": "content_summary",
            "stage2": "full_script"
        },
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "summary_file": str(summary_file),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file) if audio_file else None
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "two_stage_generation": True
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 40 Complete: Two-Stage Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Method: Two-stage generation")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - content_summary.txt (Stage 1)")
    print(f"  - script.txt (Stage 2)")
    print(f"  - show_notes.txt")
    if audio_file:
        print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")


if __name__ == "__main__":
    main()
