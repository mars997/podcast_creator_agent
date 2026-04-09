"""
Step 33: Chunk Long Scripts into Audio Segments

Splits long scripts into manageable audio chunks to handle TTS limitations.
Merges audio segments into final podcast file.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Tuple
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


# Chunking configuration
DEFAULT_CHUNK_SIZE = 4000  # characters per chunk
MIN_CHUNK_SIZE = 1000
MAX_CHUNK_SIZE = 10000


def split_script_into_chunks(script: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[str]:
    """Split script into chunks at natural breakpoints"""

    # Try to split at paragraph boundaries
    paragraphs = script.split('\n\n')

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # If adding this paragraph would exceed chunk size
        if len(current_chunk) + len(para) + 2 > chunk_size:
            # Save current chunk if it has content
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            # If single paragraph is too large, split by sentences
            if len(para) > chunk_size:
                sentences = para.split('. ')
                for sent in sentences:
                    if len(current_chunk) + len(sent) + 2 > chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                    current_chunk += sent + ". "
            else:
                current_chunk = para

        else:
            current_chunk += "\n\n" + para if current_chunk else para

    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def generate_chunked_audio(
    tts_provider,
    script: str,
    voice: str,
    output_dir: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE
) -> Tuple[List[Path], Dict]:
    """Generate audio for each chunk and return chunk files"""

    # Split script into chunks
    chunks = split_script_into_chunks(script, chunk_size)

    print(f"[OK] Split script into {len(chunks)} chunks")

    # Create chunks directory
    chunks_dir = output_dir / "audio_chunks"
    chunks_dir.mkdir(exist_ok=True)

    # Generate audio for each chunk
    chunk_files = []
    chunk_info = {
        "total_chunks": len(chunks),
        "chunk_size": chunk_size,
        "chunks": []
    }

    for i, chunk_text in enumerate(chunks, 1):
        print(f"[INFO] Generating chunk {i}/{len(chunks)}...")

        chunk_file = chunks_dir / f"chunk_{i:03d}.mp3"

        try:
            generate_audio(tts_provider, chunk_text, voice, chunk_file)
            chunk_files.append(chunk_file)

            chunk_info["chunks"].append({
                "number": i,
                "file": str(chunk_file.name),
                "char_count": len(chunk_text),
                "word_count": len(chunk_text.split())
            })

            print(f"[OK] Chunk {i} generated ({len(chunk_text)} chars)")

        except Exception as e:
            print(f"[ERROR] Chunk {i} failed: {e}")
            chunk_info["chunks"].append({
                "number": i,
                "file": None,
                "error": str(e)
            })

    return chunk_files, chunk_info


def merge_audio_chunks(chunk_files: List[Path], output_file: Path) -> bool:
    """Merge audio chunks into single file using ffmpeg or pydub"""

    print(f"\n[INFO] Merging {len(chunk_files)} chunks...")

    # Try pydub first
    try:
        from pydub import AudioSegment

        combined = AudioSegment.empty()

        for chunk_file in chunk_files:
            if chunk_file.exists():
                chunk_audio = AudioSegment.from_mp3(str(chunk_file))
                combined += chunk_audio

        combined.export(str(output_file), format="mp3")
        print(f"[OK] Audio merged successfully")
        return True

    except ImportError:
        print("[WARN] pydub not available. Trying ffmpeg...")

        # Try ffmpeg command line
        try:
            import subprocess

            # Create file list for ffmpeg
            list_file = output_file.parent / "chunk_list.txt"
            with open(list_file, 'w') as f:
                for chunk_file in chunk_files:
                    if chunk_file.exists():
                        f.write(f"file '{chunk_file.absolute()}'\n")

            # Run ffmpeg
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(list_file),
                '-c', 'copy',
                str(output_file)
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            list_file.unlink()  # Clean up list file

            print(f"[OK] Audio merged with ffmpeg")
            return True

        except Exception as e:
            print(f"[ERROR] Audio merging failed: {e}")
            print("[INFO] Individual chunks saved in audio_chunks/")
            return False


def main():
    """Chunked audio generation"""
    print("\n" + "="*70)
    print("Step 33: Chunk Long Scripts into Audio Segments")
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
        topic = "Audio Chunking Demo"

    tone = get_user_input("Choose tone (casual/professional/educational)", config.DEFAULT_TONE)
    voice = get_user_input(
        f"Choose voice ({'/'.join(tts_provider.available_voices)})",
        tts_provider.available_voices[0]
    )

    # For chunking demo, use longer length
    print("\n[INFO] For chunking demonstration, using 'long' length")
    length = "long"

    # Chunk size configuration
    chunk_size_input = input(f"\nChunk size in characters (default {DEFAULT_CHUNK_SIZE}): ").strip()
    if chunk_size_input:
        try:
            chunk_size = int(chunk_size_input)
            if chunk_size < MIN_CHUNK_SIZE:
                chunk_size = MIN_CHUNK_SIZE
            elif chunk_size > MAX_CHUNK_SIZE:
                chunk_size = MAX_CHUNK_SIZE
        except ValueError:
            chunk_size = DEFAULT_CHUNK_SIZE
    else:
        chunk_size = DEFAULT_CHUNK_SIZE

    print(f"[OK] Using chunk size: {chunk_size} characters")

    # Validate
    tone = validate_choice(tone, config.VALID_TONES, "tone")
    voice = validate_choice(voice, set(tts_provider.available_voices), "voice")
    length = validate_choice(length, config.VALID_LENGTHS, "length")
    word_range = get_word_range(length)

    # Create episode directory
    output_root = Path(config.OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"\n[OK] Episode directory: {episode_dir}")

    # Generate script
    print(f"\nGenerating script...")
    try:
        prompt = f"""Generate a podcast script about: {topic}

Tone: {tone}
Target length: {word_range[0]}-{word_range[1]} words

This will be split into audio chunks, so use clear paragraph breaks and maintain good flow between sections.

Generate the complete podcast script:"""

        script = llm_provider.generate_text(prompt)
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)

        script_chars = len(script)
        script_words = len(script.split())

        print(f"[OK] Script generated ({script_chars} chars, {script_words} words)")

    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Generate chunked audio
    print(f"\nGenerating audio in chunks...")
    try:
        chunk_files, chunk_info = generate_chunked_audio(
            tts_provider, script, voice, episode_dir, chunk_size
        )

        # Save chunk info
        chunk_info_file = episode_dir / "chunk_info.json"
        with open(chunk_info_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_info, f, indent=2)

        print(f"\n[OK] All chunks generated")

    except Exception as e:
        print(f"[ERROR] Chunked audio generation failed: {e}")
        return

    # Merge chunks
    audio_file = episode_dir / f"podcast_{voice}.mp3"

    merge_success = merge_audio_chunks(chunk_files, audio_file)

    if not merge_success:
        print(f"\n[WARN] Merged audio not available")
        print(f"[INFO] Individual chunks available in: {episode_dir}/audio_chunks/")
        audio_file = None

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes_prompt = f"""Create show notes for this podcast.

Topic: {topic}
Audio: Generated in {chunk_info['total_chunks']} chunks

Include:
- Episode summary
- Key topics
- Technical note about chunked audio generation

Script:
{script}

Generate the show notes:"""

        show_notes = llm_provider.generate_text(show_notes_prompt)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")

    except Exception as e:
        print(f"[WARN] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\nGenerated in {chunk_info['total_chunks']} chunks"
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
        "script_stats": {
            "chars": len(script),
            "words": len(script.split())
        },
        "audio_chunking": chunk_info,
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "chunk_info_file": str(chunk_info_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file) if audio_file else None,
            "chunks_dir": str(episode_dir / "audio_chunks")
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "chunked_audio": True,
            "num_chunks": chunk_info['total_chunks']
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 33 Complete: Chunked Audio Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Script: {len(script)} chars")
    print(f"Chunks: {chunk_info['total_chunks']}")
    print(f"Chunk size: {chunk_size} chars")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - script.txt")
    print(f"  - audio_chunks/ ({chunk_info['total_chunks']} files)")
    print(f"  - chunk_info.json")
    if audio_file:
        print(f"  - podcast_{voice}.mp3 (merged)")
    print(f"  - show_notes.txt")
    print(f"  - metadata.json")

    if not merge_success:
        print(f"\n[INFO] Note: Install pydub for automatic audio merging:")
        print(f"       pip install pydub")


if __name__ == "__main__":
    main()
