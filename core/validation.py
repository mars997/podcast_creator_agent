"""
Input validation and sanitization utilities for podcast creation.

This module provides functions to validate and sanitize user inputs including:
- Filename sanitization
- Tone, voice, and length validation
- Generic choice validation
"""

from typing import Set
import config


def sanitize_filename(text: str) -> str:
    """
    Sanitize text to create a valid filename.

    Removes special characters, keeping only alphanumeric characters,
    spaces, hyphens, and underscores. Replaces spaces with underscores.

    Args:
        text: The text to sanitize

    Returns:
        Sanitized filename-safe string

    Examples:
        >>> sanitize_filename("My Cool Podcast!")
        'My_Cool_Podcast'
        >>> sanitize_filename("AI & ML: The Future")
        'AI__ML_The_Future'
    """
    cleaned = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in text).strip()
    return cleaned.replace(" ", "_")


def validate_choice(value: str, valid_set: Set[str], field_name: str) -> str:
    """
    Validate that a value is in a set of valid choices.

    Args:
        value: The value to validate
        valid_set: Set of valid choices
        field_name: Name of the field being validated (for error messages)

    Returns:
        The validated value

    Raises:
        ValueError: If the value is not in the valid set

    Examples:
        >>> validate_choice("casual", {"casual", "formal"}, "tone")
        'casual'
        >>> validate_choice("invalid", {"casual", "formal"}, "tone")
        Traceback (most recent call last):
        ...
        ValueError: Invalid tone: invalid. Valid options: casual, formal
    """
    if value not in valid_set:
        valid_options = ", ".join(sorted(valid_set))
        raise ValueError(f"Invalid {field_name}: {value}. Valid options: {valid_options}")
    return value


def validate_tone(tone: str) -> str:
    """
    Validate podcast tone selection.

    Args:
        tone: The tone to validate

    Returns:
        The validated tone

    Raises:
        ValueError: If tone is not valid
    """
    return validate_choice(tone, config.VALID_TONES, "tone")


def validate_voice(voice: str, valid_voices: Set[str] = None) -> str:
    """
    Validate TTS voice selection.

    Args:
        voice: The voice to validate
        valid_voices: Optional set of valid voices. If not provided,
                     uses the default OpenAI voices from config.

    Returns:
        The validated voice

    Raises:
        ValueError: If voice is not valid
    """
    if valid_voices is None:
        # Use OpenAI voices as default for backward compatibility
        valid_voices = set(config.PROVIDER_MODELS["openai"]["voices"])

    return validate_choice(voice, valid_voices, "voice")


def validate_length(length: str) -> str:
    """
    Validate podcast length selection.

    Args:
        length: The length to validate

    Returns:
        The validated length

    Raises:
        ValueError: If length is not valid
    """
    return validate_choice(length, config.VALID_LENGTHS, "length")


def get_word_range(length: str) -> str:
    """
    Get the word range for a given length.

    This is a convenience wrapper around config.get_word_range()
    that can be used without importing config separately.

    Args:
        length: The length (short/medium/long)

    Returns:
        Word range string (e.g., "500 to 700 words")
    """
    return config.get_word_range(length)
