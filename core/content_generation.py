"""
Content generation utilities for podcast creation.

This module provides functions to generate podcast content including:
- Script generation from topics and sources
- Show notes generation from scripts
- Audio generation using TTS
"""

from pathlib import Path
from typing import List


def build_script(
    llm_provider,
    topic: str,
    tone: str,
    word_range: str,
    source_material: str = None
) -> str:
    """
    Generate a podcast script using the LLM provider.

    Args:
        llm_provider: The LLM provider instance
        topic: The podcast episode topic
        tone: The desired tone (casual/professional/educational)
        word_range: Target word count range (e.g., "500 to 700 words")
        source_material: Optional source material to base the script on

    Returns:
        Generated podcast script text

    Examples:
        >>> script = build_script(
        ...     llm_provider,
        ...     "AI Trends in 2024",
        ...     "educational",
        ...     "500 to 700 words",
        ...     "Source 1: Article about AI..."
        ... )
    """
    if source_material:
        prompt = f"""
You are a podcast writer creating a solo-host podcast episode.

Episode topic: {topic}
Tone: {tone}
Target length: {word_range}

Use the source materials below to write the episode.
Combine the ideas clearly and naturally.
Stay grounded in the sources and do not invent specific facts not supported by them.

Requirements:
- A catchy episode title on the first line
- A short welcome intro
- 3 clear main talking points
- A short conclusion
- Sound natural when spoken aloud
- No bullet points
- Beginner-friendly
- Smooth transitions between sections

Source materials:
{source_material}
"""
    else:
        prompt = f"""
You are a podcast writer creating a solo-host podcast episode.

Topic: {topic}
Tone: {tone}
Length: {word_range}

Write a podcast episode script with the following:
- A catchy episode title on the first line
- A short welcome intro
- 3 clear main talking points
- A short conclusion
- Sound natural when spoken aloud
- No bullet points
- Beginner-friendly
- Smooth transitions between sections
"""

    return llm_provider.generate_text(prompt)


def build_show_notes(llm_provider, script: str) -> str:
    """
    Generate show notes from a podcast script.

    Args:
        llm_provider: The LLM provider instance
        script: The podcast script

    Returns:
        Generated show notes text

    Examples:
        >>> notes = build_show_notes(llm_provider, "Episode Title\\n\\nWelcome...")
    """
    prompt = f"""
Based on the following podcast script, create show notes.

Requirements:
- Include the episode title
- Include a short summary
- Include 3 key takeaways
- Clean and readable format

Podcast script:
{script}
"""

    return llm_provider.generate_text(prompt)


def split_script_into_chunks(script: str, chunk_size: int = 4000) -> List[str]:
    """
    Split script into chunks at natural breakpoints.

    Args:
        script: The full script text
        chunk_size: Max characters per chunk (default: 4000)

    Returns:
        List of script chunks
    """
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


def generate_audio(tts_provider, script: str, voice: str, audio_path: Path, speed: float = 1.0) -> None:
    """
    Generate audio from script using TTS provider with automatic chunking.

    Args:
        tts_provider: The TTS provider instance
        script: The script text to convert to speech
        voice: The voice name to use
        audio_path: Path where the audio file should be saved
        speed: Speaking rate (0.25-4.0, default: 1.0)

    Examples:
        >>> generate_audio(
        ...     tts_provider,
        ...     "Welcome to my podcast...",
        ...     "nova",
        ...     Path("output/episode/podcast.mp3"),
        ...     speed=1.1
        ... )
    """
    # Check if script exceeds TTS character limit
    MAX_TTS_LENGTH = 4096  # OpenAI TTS limit

    if len(script) <= MAX_TTS_LENGTH:
        # Short script - direct generation
        tts_provider.generate_audio(script, voice, audio_path, speed=speed)
    else:
        # Long script - chunk and merge
        print(f"[INFO] Script length ({len(script)} chars) exceeds TTS limit. Chunking...")

        # Split into chunks
        chunks = split_script_into_chunks(script, chunk_size=4000)
        print(f"[OK] Split into {len(chunks)} chunks")

        # Create temp directory for chunks - use system temp to avoid permission issues
        import tempfile
        import shutil

        temp_dir = Path(tempfile.mkdtemp(prefix="podcast_chunks_"))

        try:
            # Generate audio for each chunk
            chunk_files = []
            for i, chunk_text in enumerate(chunks, 1):
                print(f"[INFO] Generating chunk {i}/{len(chunks)}...")
                chunk_file = temp_dir / f"chunk_{i:03d}.mp3"
                tts_provider.generate_audio(chunk_text, voice, chunk_file, speed=speed)
                chunk_files.append(chunk_file)

            # Merge audio files
            print("[INFO] Merging audio chunks...")
            _merge_audio_files(chunk_files, audio_path)

            print(f"[OK] Generated merged audio: {audio_path}")

        finally:
            # Cleanup temp directory and all files
            shutil.rmtree(temp_dir, ignore_errors=True)


def _merge_audio_files(audio_files: List[Path], output_path: Path) -> None:
    """
    Merge multiple audio files into one.

    Args:
        audio_files: List of audio file paths to merge
        output_path: Where to save merged audio
    """
    import shutil

    try:
        from pydub import AudioSegment

        print(f"[INFO] Merging {len(audio_files)} audio chunks...")

        # Load all audio files
        segments = [AudioSegment.from_mp3(str(f)) for f in audio_files]

        # Concatenate
        merged = segments[0]
        for segment in segments[1:]:
            merged += segment

        # Export
        merged.export(str(output_path), format="mp3")
        print(f"[OK] Merged audio exported to {output_path}")

    except ImportError:
        print("[WARNING] pydub not installed. Installing now...")
        import subprocess
        try:
            subprocess.run(["pip", "install", "pydub"], check=True, capture_output=True)
            print("[OK] pydub installed successfully")

            # Try again with pydub
            from pydub import AudioSegment
            segments = [AudioSegment.from_mp3(str(f)) for f in audio_files]
            merged = segments[0]
            for segment in segments[1:]:
                merged += segment
            merged.export(str(output_path), format="mp3")
            print(f"[OK] Merged audio exported to {output_path}")

        except Exception as e:
            # Installation or merge failed
            print(f"[ERROR] Could not install/use pydub: {e}")
            print("[WARNING] Using first chunk only as fallback")
            shutil.copy(audio_files[0], output_path)

    except Exception as e:
        # pydub installed but merge failed
        print(f"[ERROR] Could not merge audio chunks: {e}")
        print("[WARNING] Using first chunk only as fallback")
        shutil.copy(audio_files[0], output_path)
