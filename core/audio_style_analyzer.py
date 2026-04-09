"""
Enhanced Audio Style Analyzer for Created Persona System

Analyzes uploaded audio to extract speaking style traits.
Does NOT clone voices - only analyzes speaking patterns and style.
"""

from pathlib import Path
from typing import Dict
import os

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def analyze_audio_style_detailed(audio_file: Path, api_key: str = None) -> Dict:
    """
    Comprehensive audio style analysis for persona creation.

    Extracts speaking style traits WITHOUT voice cloning.
    Analyzes: energy, pacing, tone, humor, intensity, conversational style.

    Args:
        audio_file: Path to audio file to analyze
        api_key: Optional OpenAI API key (uses env var if not provided)

    Returns:
        Dict with detailed style analysis:
        {
            "energy": "low" | "medium" | "high",
            "pacing": "slow" | "moderate" | "fast",
            "humor_level": "none" | "subtle" | "moderate" | "high",
            "tone": "warm" | "professional" | "energetic" | etc.,
            "intensity": "relaxed" | "moderate" | "intense",
            "conversational_style": "formal" | "casual" | "conversational",
            "confidence": "low" | "moderate" | "high",
            "warmth": "low" | "moderate" | "high",
            "dramatic_level": "low" | "moderate" | "high",
            "voice_characteristics": {
                "pitch_range": "narrow" | "moderate" | "wide",
                "rhythm": "steady" | "varied",
                "emphasis_pattern": "minimal" | "moderate" | "frequent"
            },
            "recommended_archetype": "warm_educator",  # From VOICE_STYLES
            "recommended_tts_voice": "nova",  # OpenAI TTS voice
            "style_summary": "High-energy, fast-paced..."
        }
    """
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI package required for audio analysis")

    # Step 1: Transcribe audio
    transcript = _transcribe_audio(audio_file, api_key)

    # Step 2: Analyze transcript for style traits
    style_analysis = _analyze_transcript_style(transcript, api_key)

    # Step 3: Map to voice archetype and TTS voice
    style_analysis["recommended_archetype"] = _map_to_archetype(style_analysis)
    style_analysis["recommended_tts_voice"] = _recommend_tts_voice(style_analysis)

    return style_analysis


def _transcribe_audio(audio_file: Path, api_key: str = None) -> str:
    """
    Transcribe audio file using Whisper API.

    Args:
        audio_file: Path to audio file
        api_key: Optional API key

    Returns:
        Transcript text
    """
    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    with open(audio_file, 'rb') as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text"
        )

    return transcript


def _analyze_transcript_style(transcript: str, api_key: str = None) -> Dict:
    """
    Analyze transcript to extract speaking style traits.

    Uses LLM to identify patterns in speaking style from transcript.

    Args:
        transcript: Transcribed audio text
        api_key: Optional API key

    Returns:
        Dict with style traits
    """
    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    # Comprehensive style analysis prompt
    prompt = f"""Analyze the following transcript excerpt to identify the speaker's STYLE characteristics.
Focus on HOW they speak, not WHAT they say.

Transcript:
\"\"\"
{transcript[:2000]}  # Limit to first 2000 chars
\"\"\"

Provide a JSON analysis with these exact keys:

{{
  "energy": "low" | "medium" | "high",
  "pacing": "slow" | "moderate" | "fast",
  "humor_level": "none" | "subtle" | "moderate" | "high",
  "tone": "warm" | "professional" | "energetic" | "serious" | "casual" | "enthusiastic",
  "intensity": "relaxed" | "moderate" | "intense",
  "conversational_style": "formal" | "casual" | "conversational",
  "confidence": "low" | "moderate" | "high",
  "warmth": "low" | "moderate" | "high",
  "dramatic_level": "low" | "moderate" | "high",
  "voice_characteristics": {{
    "pitch_range": "narrow" | "moderate" | "wide",
    "rhythm": "steady" | "varied",
    "emphasis_pattern": "minimal" | "moderate" | "frequent"
  }},
  "style_summary": "2-3 sentence description of overall speaking style"
}}

Base your analysis on:
- Sentence length and structure
- Word choice (simple vs complex, formal vs casual)
- Use of contractions, interjections, filler words
- Punctuation patterns (exclamations, questions, pauses)
- Repetition and emphasis indicators
- Overall tone and mood

Return ONLY the JSON, no other text."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert speech analyst. Analyze speaking styles objectively based on transcript patterns."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    import json
    analysis = json.loads(response.choices[0].message.content)

    return analysis


def _map_to_archetype(style_analysis: Dict) -> str:
    """
    Map style traits to a voice archetype from VOICE_STYLES.

    Args:
        style_analysis: Style analysis dict

    Returns:
        Voice archetype ID (e.g., "rapid_fire_comedian")
    """
    from core.voice_styles import VOICE_STYLES

    energy = style_analysis.get("energy", "medium")
    pacing = style_analysis.get("pacing", "moderate")
    humor = style_analysis.get("humor_level", "subtle")
    tone = style_analysis.get("tone", "professional")

    # Mapping logic based on dominant traits
    if energy == "high" and pacing == "fast":
        if humor in ["moderate", "high"]:
            return "rapid_fire_comedian"
        else:
            return "energetic_game_show_host"

    if energy == "high" and tone in ["energetic", "enthusiastic"]:
        return "big_sports_host"

    if energy == "low" and tone == "warm":
        return "warm_educator"

    if pacing == "slow" and tone in ["serious", "professional"]:
        return "epic_documentary_narrator"

    if humor in ["moderate", "high"] and pacing == "moderate":
        return "animated_troublemaker"

    if tone == "professional" and energy == "medium":
        return "deadpan_professor"

    if tone == "warm" and energy == "medium":
        return "warm_educator"

    # Default fallback
    return "warm_educator"


def _recommend_tts_voice(style_analysis: Dict) -> str:
    """
    Recommend an OpenAI TTS voice based on style traits.

    Available voices: alloy, echo, fable, onyx, nova, shimmer

    Args:
        style_analysis: Style analysis dict

    Returns:
        TTS voice ID
    """
    energy = style_analysis.get("energy", "medium")
    tone = style_analysis.get("tone", "professional")
    warmth = style_analysis.get("warmth", "moderate")

    # Mapping based on OpenAI voice characteristics:
    # - alloy: neutral, balanced
    # - echo: moderate, clear
    # - fable: expressive, warm
    # - onyx: deep, authoritative
    # - nova: energetic, friendly
    # - shimmer: bright, clear

    if energy == "high":
        if warmth == "high":
            return "nova"  # Energetic and friendly
        else:
            return "shimmer"  # Energetic and clear

    if energy == "low":
        if tone in ["serious", "professional"]:
            return "onyx"  # Deep and authoritative
        else:
            return "echo"  # Calm and clear

    if warmth == "high":
        return "fable"  # Warm and expressive

    # Default
    return "alloy"  # Balanced and neutral


# Quick analysis function (wrapper for backward compatibility)
def analyze_audio_for_persona(audio_file: Path, api_key: str = None) -> Dict:
    """
    Wrapper function specifically for persona creation.

    Returns comprehensive analysis formatted for CreatedPersona.

    Args:
        audio_file: Path to audio file
        api_key: Optional API key

    Returns:
        Style analysis dict ready for create_persona_from_analysis()
    """
    return analyze_audio_style_detailed(audio_file, api_key)


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python audio_style_analyzer.py <audio_file>")
        sys.exit(1)

    audio_path = Path(sys.argv[1])

    if not audio_path.exists():
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)

    print(f"Analyzing audio: {audio_path}")
    print("-" * 60)

    analysis = analyze_audio_style_detailed(audio_path)

    print("\nStyle Analysis:")
    print(f"  Energy: {analysis['energy']}")
    print(f"  Pacing: {analysis['pacing']}")
    print(f"  Humor: {analysis['humor_level']}")
    print(f"  Tone: {analysis['tone']}")
    print(f"  Intensity: {analysis['intensity']}")
    print(f"  Style: {analysis['conversational_style']}")
    print(f"\n  Recommended Archetype: {analysis['recommended_archetype']}")
    print(f"  Recommended Voice: {analysis['recommended_tts_voice']}")
    print(f"\n  Summary: {analysis['style_summary']}")
