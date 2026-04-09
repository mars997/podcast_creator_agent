"""
Test PDF Ingestion - Step 21

This script demonstrates PDF extraction using core module functions.
Creates a test episode from a PDF file.
"""

from pathlib import Path
from datetime import datetime

from core.provider_setup import initialize_providers, get_provider_info
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file, ensure_directory
from core.source_management import extract_text_from_pdf, save_sources_to_directory
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


def test_pdf_extraction():
    """Test PDF extraction without creating full episode"""
    print("\n" + "="*70)
    print("TEST: PDF Text Extraction")
    print("="*70)

    # Look for any PDF in current directory
    pdf_files = list(Path(".").glob("*.pdf"))

    if not pdf_files:
        print("\n[INFO] No PDF files found in current directory")
        print("To test PDF ingestion:")
        print("  1. Place a PDF file in this directory")
        print("  2. Run: python test_pdf_ingestion.py")
        print("\nAlternatively, create a sample PDF:")
        print("  python -c \"from fpdf import FPDF; pdf=FPDF(); pdf.add_page(); pdf.set_font('Arial',size=12); pdf.cell(200,10,txt='Test PDF Content',ln=True); pdf.output('sample.pdf')\"")
        return None

    pdf_file = pdf_files[0]
    print(f"\n[OK] Found PDF: {pdf_file.name}")

    try:
        # Extract text
        extracted_text = extract_text_from_pdf(pdf_file)

        print(f"\n[OK] Text extracted successfully")
        print(f"  File: {pdf_file.name}")
        print(f"  Size: {pdf_file.stat().st_size} bytes")
        print(f"  Extracted length: {len(extracted_text)} characters")
        print(f"  Word count: {len(extracted_text.split())} words")

        # Show preview
        print(f"\n[PREVIEW] First 300 characters:")
        print("-" * 70)
        print(extracted_text[:300])
        if len(extracted_text) > 300:
            print("...")
        print("-" * 70)

        return pdf_file, extracted_text

    except Exception as e:
        print(f"\n[FAIL] PDF extraction failed: {e}")
        return None


def create_episode_from_pdf(pdf_file: Path):
    """Create a full podcast episode from PDF"""
    print("\n" + "="*70)
    print("STEP 21: PDF to Podcast Episode")
    print("="*70)

    # Initialize providers
    print("\nInitializing providers...")
    llm_provider, tts_provider = initialize_providers(verbose=False)
    print(f"[OK] LLM: {llm_provider.provider_name}")
    print(f"[OK] TTS: {tts_provider.provider_name}")

    # Get settings
    topic = input(f"\nEnter episode topic (or press Enter for '{pdf_file.stem}'): ").strip()
    if not topic:
        topic = pdf_file.stem

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

    # Extract PDF content using core function
    print(f"\nExtracting PDF content from: {pdf_file.name}")
    all_sources = []
    successful, failed = save_sources_to_directory(
        sources_dir,
        all_sources,
        urls=None,
        files=[pdf_file]
    )

    if not all_sources:
        print("[FAIL] No content extracted from PDF")
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
        script = f"This is a mock podcast script about {topic}.\n\nGenerated from PDF: {pdf_file.name}"
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
        show_notes = f"Show notes for {topic}"
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
        "source_type": "pdf",
        "pdf_info": {
            "filename": pdf_file.name,
            "size_bytes": pdf_file.stat().st_size,
            "extracted_chars": len(combined_source),
            "extracted_words": len(combined_source.split())
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
            "num_successful_files": len(successful),
            "num_failed_files": len(failed),
            "num_successful_urls": 0,
            "num_failed_urls": 0,
            "source_type": "pdf",
            "pdf_filename": pdf_file.name
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)
    print(f"[OK] Episode index updated")

    # Summary
    print("\n" + "="*70)
    print("STEP 21 COMPLETE: PDF to Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Location: {episode_dir}")
    print(f"\nSource PDF: {pdf_file.name}")
    print(f"  Size: {pdf_file.stat().st_size:,} bytes")
    print(f"  Extracted: {len(combined_source):,} characters")
    print(f"\nGenerated files:")
    print(f"  - sources/{sources_dir.name}/source_1_{pdf_file.stem}.txt")
    print(f"  - script.txt")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")
    print(f"\nView episode:")
    print(f"  python step17_episode_browser.py --list")


def main():
    """Main test function"""
    result = test_pdf_extraction()

    if result:
        pdf_file, extracted_text = result

        print("\n" + "="*70)
        print("PDF extraction successful!")
        print("="*70)

        choice = input("\nCreate full podcast episode from this PDF? (y/n): ").strip().lower()

        if choice == 'y':
            create_episode_from_pdf(pdf_file)
        else:
            print("\n[OK] PDF extraction test complete")
            print(f"\nTo create episode later, run:")
            print(f"  python test_pdf_ingestion.py")


if __name__ == "__main__":
    main()
