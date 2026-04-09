"""
Step 31: Citation / Source Trace Support

Enables citation tracking in scripts - which claims come from which sources.
Generates citation map and optionally includes inline citations in script.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import json
import re

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.provider_setup import get_provider_info
from core.content_generation import generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file, read_text_file
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


def generate_cited_script(
    llm_provider,
    topic: str,
    sources: List[Tuple[str, str]],  # [(source_id, content), ...]
    citation_style: str,
    tone: str,
    word_range: tuple
) -> str:
    """Generate script with inline citations"""

    # Build source list for prompt
    source_list = "\n\n".join([
        f"[Source {source_id}]\n{content}"
        for source_id, content in sources
    ])

    if citation_style == "inline":
        citation_instruction = """CITATION REQUIREMENT - INLINE STYLE:
- When mentioning a fact, claim, or idea from a source, cite it inline
- Use format: "According to [Source 1], ..." or "...[Source 2 notes]..." or "...fact here [Source 3]."
- Multiple sources for one claim: [Sources 1, 3]
- Aim for natural phrasing with citations"""

    elif citation_style == "footnote":
        citation_instruction = """CITATION REQUIREMENT - FOOTNOTE STYLE:
- When mentioning a fact, claim, or idea from a source, add a superscript number
- Use format: "...the key finding^1 demonstrates..." or "recent research^2,3 shows..."
- List footnotes at the end of the script
- Format: ^1 = Source 1, ^2 = Source 2, etc."""

    elif citation_style == "section":
        citation_instruction = """CITATION REQUIREMENT - SECTION STYLE:
- Group related information by source
- Start each section with "According to [Source X]:" or "From [Source Y]:"
- Include multiple points from that source
- Transition smoothly between sources"""

    else:  # attributed
        citation_instruction = """CITATION REQUIREMENT - ATTRIBUTED STYLE:
- Mention source naturally in narrative
- Use phrases like "The article mentions...", "According to the research...", "The study found..."
- Make attribution feel conversational, not academic
- Source numbers tracked internally but not explicitly shown"""

    prompt = f"""{citation_instruction}

TOPIC: {topic}
TONE: {tone}
TARGET LENGTH: {word_range[0]}-{word_range[1]} words

SOURCES:
{source_list}

---

Generate a podcast script about "{topic}" that:
1. Uses information from the provided sources
2. Cites sources using the {citation_style} style described above
3. Maintains a {tone} and engaging tone
4. Stays grounded in the source material

Generate the complete cited podcast script:"""

    response = llm_provider.generate_text(prompt)
    return response


def extract_citations_from_script(script: str) -> Dict:
    """Extract citation references from script"""
    citations = {
        "inline_references": [],
        "source_mentions": {},
        "citation_count": 0
    }

    # Find inline citations like [Source 1] or [Sources 1, 3]
    inline_pattern = r'\[Sources?\s+([\d,\s]+)\]'
    matches = re.findall(inline_pattern, script)

    for match in matches:
        source_nums = [int(n.strip()) for n in match.split(',')]
        citations["inline_references"].extend(source_nums)
        citations["citation_count"] += 1

    # Find footnote-style citations like ^1 or ^2,3
    footnote_pattern = r'\^([\d,]+)'
    footnote_matches = re.findall(footnote_pattern, script)

    for match in footnote_matches:
        source_nums = [int(n.strip()) for n in match.split(',')]
        citations["inline_references"].extend(source_nums)
        citations["citation_count"] += 1

    # Count mentions per source
    for ref in citations["inline_references"]:
        citations["source_mentions"][f"Source {ref}"] = citations["source_mentions"].get(f"Source {ref}", 0) + 1

    return citations


def main():
    """Citation-enabled podcast generation"""
    print("\n" + "="*70)
    print("Step 31: Citation / Source Trace Support")
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

    # Choose citation style
    print("\n" + "="*70)
    print("Citation Styles")
    print("="*70)
    print("\n1. INLINE - [Source 1] style citations in text")
    print("2. FOOTNOTE - Superscript numbers^1 with footnote list")
    print("3. SECTION - Group content by source")
    print("4. ATTRIBUTED - Natural attribution without explicit numbers")
    print("="*70)

    citation_choice = input("\nChoose citation style (1-4, default 1): ").strip() or "1"
    citation_styles = ["inline", "footnote", "section", "attributed"]

    try:
        cit_idx = int(citation_choice) - 1
        if 0 <= cit_idx < 4:
            citation_style = citation_styles[cit_idx]
        else:
            citation_style = "inline"
    except ValueError:
        citation_style = "inline"

    print(f"\n[OK] Citation style: {citation_style.upper()}")

    # Get episode settings
    topic = input("\nEnter episode topic: ").strip()
    if not topic:
        topic = "Citation Demo"

    # Source input (required for citations)
    print("\nProvide sources (minimum 2 recommended for citations):")
    print("Enter source content. Type 'DONE' when finished.")

    sources = []
    source_num = 1

    while True:
        print(f"\n--- Source {source_num} ---")
        print("Paste content (or type DONE to finish):")

        lines = []
        while True:
            line = input()
            if line.strip().upper() == "DONE":
                break
            lines.append(line)

        content = "\n".join(lines).strip()

        if content.upper() == "DONE" or not content:
            break

        sources.append((str(source_num), content))
        source_num += 1
        print(f"[OK] Source {source_num-1} added")

        if len(sources) >= 3:
            more = input("\nAdd another source? (y/n, default n): ").strip().lower()
            if more != 'y':
                break

    if not sources:
        print("[ERROR] No sources provided. Citations require source material.")
        return

    print(f"\n[OK] Loaded {len(sources)} source(s)")

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
    print(f"[OK] Citation style: {citation_style}")

    # Save sources
    sources_dir = episode_dir / "sources"
    sources_dir.mkdir(exist_ok=True)

    for source_id, content in sources:
        source_file = sources_dir / f"source_{source_id}.txt"
        save_text_file(content, source_file)

    print(f"[OK] Saved {len(sources)} source file(s)")

    # Generate cited script
    print(f"\nGenerating script with {citation_style.upper()} citations...")
    try:
        script = generate_cited_script(llm_provider, topic, sources, citation_style, tone, word_range)
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Cited script generated")
    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Extract citation information
    print("\nAnalyzing citations...")
    citation_data = extract_citations_from_script(script)
    print(f"[OK] Found {citation_data['citation_count']} citation references")

    if citation_data['source_mentions']:
        print("[OK] Source usage:")
        for source, count in citation_data['source_mentions'].items():
            print(f"    {source}: {count} times")

    # Save citation map
    citation_map_file = episode_dir / "citation_map.json"
    with open(citation_map_file, 'w', encoding='utf-8') as f:
        json.dump({
            "citation_style": citation_style,
            "total_sources": len(sources),
            "total_citations": citation_data['citation_count'],
            "source_mentions": citation_data['source_mentions'],
            "sources": [
                {
                    "id": source_id,
                    "file": f"sources/source_{source_id}.txt",
                    "char_count": len(content)
                }
                for source_id, content in sources
            ]
        }, f, indent=2)

    print(f"[OK] Citation map saved")

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes_prompt = f"""Create show notes for this cited podcast script.

Citation style: {citation_style}
Sources: {len(sources)}

Include:
- Episode summary
- List of sources referenced
- Key topics from each source
- Citation style used

Script:
{script}

Generate the show notes:"""

        show_notes = llm_provider.generate_text(show_notes_prompt)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")
    except Exception as e:
        print(f"[WARN] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\nCitation style: {citation_style}\nSources: {len(sources)}"
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
        "citations": {
            "enabled": True,
            "style": citation_style,
            "num_sources": len(sources),
            "num_citations": citation_data['citation_count'],
            "source_mentions": citation_data['source_mentions']
        },
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "citation_map_file": str(citation_map_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file),
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
            "citations_enabled": True,
            "citation_style": citation_style,
            "num_sources": len(sources)
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 31 Complete: Cited Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Citation style: {citation_style.upper()}")
    print(f"Sources: {len(sources)}")
    print(f"Citations: {citation_data['citation_count']}")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - sources/ ({len(sources)} source files)")
    print(f"  - script.txt (with citations)")
    print(f"  - citation_map.json")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")


if __name__ == "__main__":
    main()
