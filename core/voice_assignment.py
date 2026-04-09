"""
Voice Assignment Strategy

Smart voice-to-character mapping with fallback handling.
"""

from typing import List, Dict, Set
from core.input_models import Character


class VoiceAssignmentStrategy:
    """
    Handles smart voice assignment to characters with graceful fallback.

    Strategy:
    1. Use preferred voice if available
    2. Assign unused voices to remaining characters
    3. Round-robin fallback if more characters than voices
    """

    def __init__(self, available_voices: List[str]):
        """
        Initialize with available TTS voices

        Args:
            available_voices: List of voice IDs from TTS provider
        """
        self.available_voices = available_voices

    def assign(self, characters: List[Character]) -> Dict[str, str]:
        """
        Assign voices to characters

        Args:
            characters: List of Character objects

        Returns:
            Dict mapping character name to voice ID
        """
        assignments = {}
        used_voices: Set[str] = set()

        # Priority 1: Use preferred voice if available
        for char in characters:
            if char.preferred_voice in self.available_voices:
                assignments[char.name] = char.preferred_voice
                used_voices.add(char.preferred_voice)

        # Priority 2: Assign remaining characters to unused voices
        remaining_chars = [c for c in characters if c.name not in assignments]
        remaining_voices = [v for v in self.available_voices if v not in used_voices]

        for char, voice in zip(remaining_chars, remaining_voices):
            assignments[char.name] = voice
            used_voices.add(voice)

        # Fallback: If more characters than voices, round-robin
        if len(remaining_chars) > len(remaining_voices):
            overflow_chars = remaining_chars[len(remaining_voices):]
            for i, char in enumerate(overflow_chars):
                # Use round-robin from all available voices
                voice = self.available_voices[i % len(self.available_voices)]
                assignments[char.name] = voice

        return assignments

    def validate_assignments(self, assignments: Dict[str, str]) -> bool:
        """
        Validate that all assigned voices are available

        Args:
            assignments: Character name to voice mapping

        Returns:
            True if all voices are valid
        """
        return all(voice in self.available_voices for voice in assignments.values())

    def get_voice_distribution(self, assignments: Dict[str, str]) -> Dict[str, int]:
        """
        Get distribution of how many characters use each voice

        Args:
            assignments: Character name to voice mapping

        Returns:
            Dict mapping voice ID to count of characters using it
        """
        distribution = {}
        for voice in assignments.values():
            distribution[voice] = distribution.get(voice, 0) + 1
        return distribution

    def suggest_voice_for_role(self, role: str, exclude: Set[str] = None) -> str:
        """
        Suggest a voice based on character role

        Simple heuristic-based suggestions. Can be enhanced with ML.

        Args:
            role: Character role (host, guest, expert, etc.)
            exclude: Set of voices to exclude from suggestion

        Returns:
            Suggested voice ID
        """
        exclude = exclude or set()
        available = [v for v in self.available_voices if v not in exclude]

        if not available:
            return self.available_voices[0]

        # Simple role-based heuristics for common OpenAI voices
        role_suggestions = {
            "host": ["nova", "shimmer", "alloy"],
            "guest": ["echo", "fable", "onyx"],
            "expert": ["onyx", "alloy", "fable"],
            "moderator": ["alloy", "shimmer"],
            "narrator": ["onyx", "fable"],
            "analyst": ["alloy", "onyx"],
            "comedian": ["nova", "echo"],
            "teacher": ["onyx", "shimmer"]
        }

        # Get suggestions for this role
        suggestions = role_suggestions.get(role.lower(), self.available_voices)

        # Return first available suggestion
        for voice in suggestions:
            if voice in available:
                return voice

        # Fallback to first available
        return available[0]


def assign_voices_smart(
    characters: List[Character],
    available_voices: List[str],
    provider: str = "openai"
) -> Dict[str, str]:
    """
    Convenience function for smart voice assignment

    Args:
        characters: List of characters needing voice assignment
        available_voices: Available voices from TTS provider
        provider: Provider name for voice mapping (default: openai)

    Returns:
        Character name to voice mapping
    """
    strategy = VoiceAssignmentStrategy(available_voices)

    # First pass: try preferred voices
    assignments = strategy.assign(characters)

    # Validate
    if not strategy.validate_assignments(assignments):
        # Fallback: reassign with role-based suggestions
        assignments = {}
        used = set()

        for char in characters:
            voice = strategy.suggest_voice_for_role(char.role, exclude=used)
            assignments[char.name] = voice
            used.add(voice)

    return assignments
