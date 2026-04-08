"""
User input handling utilities for podcast creation.

This module provides functions to get user input with defaults,
read multiline input, and collect podcast settings.
"""

from typing import Dict


def get_user_input(prompt_text: str, default_value: str) -> str:
    """
    Get user input with a default value.

    Displays a prompt with the default value in brackets.
    If user presses Enter without input, returns the default.

    Args:
        prompt_text: The prompt to display to the user
        default_value: The default value if user provides no input

    Returns:
        User input (lowercased) or default value

    Examples:
        >>> tone = get_user_input("Choose tone", "casual")
        Choose tone [casual]: professional
        >>> # Returns "professional"
        >>>
        >>> tone = get_user_input("Choose tone", "casual")
        Choose tone [casual]:
        >>> # Returns "casual" (user pressed Enter)
    """
    user_value = input(f"{prompt_text} [{default_value}]: ").strip().lower()
    return user_value if user_value else default_value


def get_podcast_settings(
    default_tone: str = "educational",
    default_voice: str = "nova",
    default_length: str = "medium"
) -> Dict[str, str]:
    """
    Collect podcast settings from user with defaults.

    Prompts the user for tone, voice, and length preferences,
    providing defaults for each.

    Args:
        default_tone: Default tone (casual/professional/educational)
        default_voice: Default voice name
        default_length: Default length (short/medium/long)

    Returns:
        Dictionary with keys: 'tone', 'voice', 'length'

    Examples:
        >>> settings = get_podcast_settings()
        >>> # Returns: {'tone': 'educational', 'voice': 'nova', 'length': 'medium'}
    """
    tone = get_user_input(
        "Choose tone (casual/professional/educational)",
        default_tone
    )
    voice = get_user_input(
        "Choose voice (alloy/echo/fable/onyx/nova/shimmer)",
        default_voice
    )
    length = get_user_input(
        "Choose length (short/medium/long)",
        default_length
    )

    return {
        "tone": tone,
        "voice": voice,
        "length": length
    }


def read_multiline_input() -> str:
    """
    Read multi-line text input from user.

    Prompts the user to paste content and continue entering lines
    until they type '###END###' on a new line.

    Returns:
        The multi-line content as a single string

    Examples:
        >>> content = read_multiline_input()
        Paste your content below.
        When finished, enter '###END###' on a new line and press Enter:
        ----------------------------------------------------------------------
        This is line 1
        This is line 2
        ###END###
        >>> # Returns: "This is line 1\\nThis is line 2"
    """
    print("\nPaste your content below.")
    print("When finished, enter '###END###' on a new line and press Enter:")
    print("-" * 70)

    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "###END###":
                break
            lines.append(line)
        except EOFError:
            # Handle Ctrl+D (Unix) or Ctrl+Z (Windows)
            break

    content = "\n".join(lines).strip()
    return content
