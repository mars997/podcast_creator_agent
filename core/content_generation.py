"""
Content generation utilities for podcast creation.

This module provides functions to generate podcast content including:
- Script generation from topics and sources
- Show notes generation from scripts
- Audio generation using TTS
"""

from pathlib import Path


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


def generate_audio(tts_provider, script: str, voice: str, audio_path: Path) -> None:
    """
    Generate audio from script using TTS provider.

    Args:
        tts_provider: The TTS provider instance
        script: The script text to convert to speech
        voice: The voice name to use
        audio_path: Path where the audio file should be saved

    Examples:
        >>> generate_audio(
        ...     tts_provider,
        ...     "Welcome to my podcast...",
        ...     "nova",
        ...     Path("output/episode/podcast.mp3")
        ... )
    """
    tts_provider.generate_audio(script, voice, audio_path)
