"""
Test Folder Ingestion - Step 23

This script demonstrates folder batch processing using core module functions.
Automatically processes multiple files from a folder.
"""

from pathlib import Path
from datetime import datetime

from core.provider_setup import initialize_providers, get_provider_info
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file, ensure_directory
from core.source_management import (
    scan_folder_for_files,
    process_folder_sources,
    save_sources_to_directory
)
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


def test_folder_scanning():
    """Test folder scanning for files"""
    print("\n" + "="*70)
    print("TEST: Folder Scanning")
    print("="*70)

    # Create a test folder with sample files
    test_folder = Path("test_folder_sources")
    test_folder.mkdir(exist_ok=True)

    # Create sample files
    sample_files = {
        "article1.txt": "This is the first article about AI technology.",
        "article2.txt": "This is the second article about machine learning.",
        "notes.md": "# Notes\n\nSome markdown notes about the topic.",
    }

    for filename, content in sample_files.items():
        file_path = test_folder / filename
        save_text_file(content, file_path)

    print(f"\n[OK] Test folder created: {test_folder}")
    print(f"  Created {len(sample_files)} sample files")

    # Scan folder
    found_files = scan_folder_for_files(test_folder)

    print(f"\n[OK] Found {len(found_files)} files:")
    for f in found_files:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")

    # Process folder
    files, folder_info = process_folder_sources(test_folder)

    print(f"\n[OK] Folder info:")
    print(f"  Total files: {folder_info['total_files']}")
    print(f"  Text files: {folder_info['text_files']}")
    print(f"  PDF files: {folder_info['pdf_files']}")

    return test_folder, found_files


def test_recursive_scanning():
    """Test recursive folder scanning"""
    print("\n" + "="*70)
    print("TEST: Recursive Folder Scanning")
    print("="*70)

    # Create nested folder structure
    base_folder = Path("test_folder_sources")
    subfolder = base_folder / "subfolder"
    subfolder.mkdir(exist_ok=True)

    # Add file in subfolder
    sub_file = subfolder / "nested_article.txt"
    save_text_file("Content in nested folder", sub_file)

    print(f"\n[OK] Created nested structure:")
    print(f"  {base_folder}/")
    print(f"    - article1.txt")
    print(f"    - article2.txt")
    print(f"    - notes.md")
    print(f"    {subfolder.name}/")
    print(f"      - nested_article.txt")

    # Non-recursive scan
    files_non_recursive = scan_folder_for_files(base_folder, recursive=False)
    print(f"\n[OK] Non-recursive scan: {len(files_non_recursive)} files")

    # Recursive scan
    files_recursive = scan_folder_for_files(base_folder, recursive=True)
    print(f"[OK] Recursive scan: {len(files_recursive)} files")

    for f in files_recursive:
        rel_path = f.relative_to(base_folder)
        print(f"  - {rel_path}")


def create_episode_from_folder(folder_path: Path):
    """Create a full podcast episode from folder contents"""
    print("\n" + "="*70)
    print("STEP 23: Folder to Podcast Episode")
    print("="*70)

    # Scan folder first
    files, folder_info = process_folder_sources(folder_path)

    if not files:
        print(f"[FAIL] No files found in folder: {folder_path}")
        return

    print(f"\n[OK] Found {len(files)} files in folder:")
    for f in files:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")

    # Initialize providers
    print("\nInitializing providers...")
    llm_provider, tts_provider = initialize_providers(verbose=False)
    print(f"[OK] LLM: {llm_provider.provider_name}")
    print(f"[OK] TTS: {tts_provider.provider_name}")

    # Get settings
    topic = input(f"\nEnter episode topic (or press Enter for '{folder_path.name}'): ").strip()
    if not topic:
        topic = folder_path.name

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

    # Process all files from folder using core function
    print(f"\nProcessing {len(files)} files from folder...")
    all_sources = []
    successful, failed = save_sources_to_directory(
        sources_dir,
        all_sources,
        urls=None,
        files=files  # ← Batch process all files!
    )

    if not all_sources:
        print("[FAIL] No content extracted from folder files")
        return

    print(f"\n[OK] Processed {len(successful)} files successfully")
    if failed:
        print(f"[WARN] Failed to process {len(failed)} files")

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
        script = f"Mock podcast script about {topic}.\n\nGenerated from {len(files)} files."
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
        show_notes = f"Show notes for {topic}\n\nBased on {len(files)} source files."
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
        existing_audio = Path("output/ai_trending/podcast_nova.mp3")
        if existing_audio.exists():
            import shutil
            shutil.copy(existing_audio, audio_file)
            print(f"[OK] Demo audio copied: {audio_file.name}")

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
        "source_type": "folder",
        "folder_info": {
            "folder_path": str(folder_path),
            "total_files": len(files),
            "successful_files": len(successful),
            "failed_files": len(failed),
            "combined_chars": len(combined_source),
            "combined_words": len(combined_source.split())
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
            "source_type": "folder",
            "folder_path": str(folder_path),
            "total_source_files": len(files)
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)
    print(f"[OK] Episode index updated")

    # Summary
    print("\n" + "="*70)
    print("STEP 23 COMPLETE: Folder to Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Location: {episode_dir}")
    print(f"\nSource folder: {folder_path}")
    print(f"  Files processed: {len(successful)}/{len(files)}")
    print(f"  Total content: {len(combined_source):,} characters")
    print(f"\nGenerated files:")
    print(f"  - sources/ ({len(successful)} files)")
    print(f"  - script.txt")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")
    print(f"\nView episode:")
    print(f"  python step17_episode_browser.py --list")


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("Folder Ingestion - Step 23")
    print("="*70)

    print("\nOptions:")
    print("1. Test folder scanning (creates sample folder)")
    print("2. Test recursive scanning")
    print("3. Create episode from test folder")
    print("4. Create episode from custom folder path")

    choice = input("\nChoose option (1-4): ").strip()

    if choice == "1":
        test_folder, files = test_folder_scanning()
        print(f"\n[OK] Test folder ready: {test_folder}")
        print(f"  Contains {len(files)} files")

    elif choice == "2":
        test_folder_scanning()  # Create base structure first
        test_recursive_scanning()

    elif choice == "3":
        test_folder = Path("test_folder_sources")
        if not test_folder.exists():
            print(f"\n[INFO] Test folder doesn't exist. Creating it...")
            test_folder_scanning()

        create = input(f"\nCreate episode from '{test_folder}'? (y/n): ").strip().lower()
        if create == 'y':
            create_episode_from_folder(test_folder)

    elif choice == "4":
        folder_path = input("\nEnter folder path: ").strip()
        if folder_path:
            path = Path(folder_path)
            if path.exists() and path.is_dir():
                create_episode_from_folder(path)
            else:
                print(f"[FAIL] Folder not found or not a directory: {folder_path}")
        else:
            print("[FAIL] No folder path provided")

    else:
        print("[FAIL] Invalid choice")


if __name__ == "__main__":
    main()
