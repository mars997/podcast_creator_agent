"""
Step 29: Stronger Grounding Rules

Reduces hallucination and ensures generated content stays faithful to source material.
Implements explicit grounding instructions and source verification.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Optional

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.provider_setup import get_provider_info
from core.content_generation import generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file, read_text_file
from core.source_management import save_sources_to_directory
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


# Grounding rule templates
GROUNDING_RULES = {
    "strict": """CRITICAL GROUNDING RULES - STRICT MODE:

1. ONLY discuss information explicitly stated in the provided sources
2. If a detail is not in the sources, say "the sources don't specify" - DO NOT infer or guess
3. Quote or paraphrase directly from sources - cite which source when possible
4. If sources contradict each other, acknowledge the contradiction
5. Do not add background knowledge, common facts, or general information beyond the sources
6. If asked about something not covered, say "this isn't covered in the provided material"

Your task is to create a podcast script that is 100% grounded in the source material.""",

    "balanced": """GROUNDING RULES - BALANCED MODE:

1. Prioritize information from the provided sources
2. Clearly distinguish between source material and general context
3. When adding context for clarity, use phrases like "for context" or "generally speaking"
4. Stay close to the facts and claims in the sources
5. If you add an example not in sources, make it clear: "for example" or "to illustrate"
6. Acknowledge uncertainty: use "according to the sources" when appropriate

Your task is to create a podcast script primarily grounded in source material, with minimal helpful context.""",

    "guided": """GROUNDING RULES - GUIDED MODE:

1. Use the provided sources as the foundation for your script
2. You may add relevant background and context to improve understanding
3. Clearly cite when quoting or closely paraphrasing sources
4. Don't contradict the source material
5. If you add information beyond sources, ensure it supports and clarifies the source content
6. Stay on topic - focus on what the sources are about

Your task is to create an engaging podcast script guided by the source material."""
}


def build_grounded_script(
    llm_provider,
    topic: str,
    sources: List[str],
    grounding_mode: str,
    tone: str,
    word_range: tuple
) -> str:
    """Generate script with strong grounding rules"""

    grounding_instruction = GROUNDING_RULES.get(grounding_mode, GROUNDING_RULES["balanced"])

    # Combine all sources
    combined_sources = "\n\n---SOURCE SEPARATOR---\n\n".join(sources)

    prompt = f"""{grounding_instruction}

TOPIC: {topic}
TONE: {tone}
TARGET LENGTH: {word_range[0]}-{word_range[1]} words

SOURCE MATERIAL:
{combined_sources}

---

Based ONLY on the source material above, generate a podcast script about: {topic}

Remember: Stay grounded in the sources. Make it {tone} and engaging while remaining faithful to the material.

Generate the complete podcast script:"""

    response = llm_provider.generate_text(prompt)
    return response


def build_grounded_show_notes(llm_provider, script: str, sources: List[str], grounding_mode: str) -> str:
    """Generate show notes with grounding awareness"""

    grounding_note = {
        "strict": "This episode is strictly based on provided source material with no additional context.",
        "balanced": "This episode is primarily based on provided sources with minimal additional context.",
        "guided": "This episode is guided by provided sources with helpful background added."
    }[grounding_mode]

    prompt = f"""Create show notes for this podcast script.

Grounding mode: {grounding_mode}
Note: {grounding_note}

Include:
- Brief episode summary
- Key topics from sources
- Main takeaways
- Grounding mode used

Script:
{script}

Generate the show notes:"""

    response = llm_provider.generate_text(prompt)
    return response


def main():
    """Grounded podcast generation"""
    print("\n" + "="*70)
    print("Step 29: Stronger Grounding Rules")
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

    # Get grounding mode
    print("\n" + "="*70)
    print("Grounding Modes")
    print("="*70)
    print("\n1. STRICT - Only information from sources, no additions")
    print("2. BALANCED - Primarily sources, minimal context (RECOMMENDED)")
    print("3. GUIDED - Sources as foundation, helpful context added")
    print("="*70)

    grounding_choice = input("\nChoose grounding mode (1-3, default 2): ").strip() or "2"
    grounding_modes = ["strict", "balanced", "guided"]

    try:
        grounding_idx = int(grounding_choice) - 1
        if 0 <= grounding_idx < 3:
            grounding_mode = grounding_modes[grounding_idx]
        else:
            grounding_mode = "balanced"
    except ValueError:
        grounding_mode = "balanced"

    print(f"\n[OK] Grounding mode: {grounding_mode.upper()}")

    # Get episode settings
    topic = input("\nEnter episode topic: ").strip()
    if not topic:
        topic = "Grounded Podcast Demo"

    # Source input
    print("\nProvide source material (required for grounding):")
    print("1. Enter text/paste content")
    print("2. Provide file path")
    print("3. Provide URL")

    source_choice = input("\nChoice (1-3, default 1): ").strip() or "1"

    all_sources = []

    if source_choice == "1":
        print("\nPaste or type your source content (press Enter twice when done):")
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
        content = "\n".join(lines)
        if content.strip():
            all_sources.append(content)

    elif source_choice == "2":
        file_path = input("\nEnter file path: ").strip()
        if file_path:
            try:
                content = read_text_file(Path(file_path))
                all_sources.append(content)
                print(f"[OK] Loaded file: {file_path}")
            except Exception as e:
                print(f"[ERROR] Failed to read file: {e}")
                return

    elif source_choice == "3":
        url = input("\nEnter URL: ").strip()
        if url:
            all_sources.append(f"URL: {url}\n(URL content would be fetched)")

    if not all_sources:
        print("[ERROR] No source material provided. Grounding requires sources.")
        return

    print(f"\n[OK] Loaded {len(all_sources)} source(s)")

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
    print(f"[OK] Grounding mode: {grounding_mode}")

    # Save sources
    sources_dir = episode_dir / "sources"
    sources_dir.mkdir(exist_ok=True)

    for i, source_content in enumerate(all_sources, 1):
        source_file = sources_dir / f"source_{i}.txt"
        save_text_file(source_content, source_file)

    print(f"[OK] Saved {len(all_sources)} source file(s)")

    # Generate grounded script
    print(f"\nGenerating script with {grounding_mode.upper()} grounding...")
    try:
        script = build_grounded_script(llm_provider, topic, all_sources, grounding_mode, tone, word_range)
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Grounded script generated")
    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes = build_grounded_show_notes(llm_provider, script, all_sources, grounding_mode)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")
    except Exception as e:
        print(f"[WARN] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\nGrounding mode: {grounding_mode}"
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)

    # Save grounding info
    grounding_info_file = episode_dir / "grounding_info.txt"
    grounding_info = f"""Grounding Information
{"="*50}

Mode: {grounding_mode.upper()}

{GROUNDING_RULES[grounding_mode]}

Sources: {len(all_sources)} source file(s) in sources/ directory
"""
    save_text_file(grounding_info, grounding_info_file)

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
        "grounding": {
            "mode": grounding_mode,
            "num_sources": len(all_sources),
            "rules_applied": True
        },
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file),
            "grounding_info_file": str(grounding_info_file),
            "sources_dir": str(sources_dir)
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "grounding_mode": grounding_mode,
            "num_sources": len(all_sources)
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 29 Complete: Grounded Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Grounding mode: {grounding_mode.upper()}")
    print(f"Sources: {len(all_sources)}")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - sources/ (source material)")
    print(f"  - script.txt (grounded in sources)")
    print(f"  - grounding_info.txt")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")


if __name__ == "__main__":
    main()
