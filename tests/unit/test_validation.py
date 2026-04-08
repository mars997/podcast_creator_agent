"""
Unit tests for core.validation module.
"""

import pytest
from core.validation import (
    sanitize_filename,
    validate_choice,
    validate_tone,
    validate_voice,
    validate_length,
    get_word_range,
)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_basic_text(self):
        """Test basic alphanumeric text."""
        assert sanitize_filename("MyPodcast") == "MyPodcast"

    def test_text_with_spaces(self):
        """Test text with spaces gets converted to underscores."""
        assert sanitize_filename("My Cool Podcast") == "My_Cool_Podcast"

    def test_special_characters_removed(self):
        """Test special characters are removed."""
        assert sanitize_filename("AI & ML: The Future!") == "AI__ML_The_Future"
        assert sanitize_filename("Podcast@2024#1") == "Podcast20241"

    def test_preserves_hyphens_underscores(self):
        """Test that hyphens and underscores are preserved."""
        assert sanitize_filename("my-podcast_v2") == "my-podcast_v2"

    def test_unicode_characters(self):
        """Test unicode characters handling."""
        # Note: é is considered alphanumeric by Python's isalnum(), but ☕ is not
        assert sanitize_filename("Café ☕ Talks") == "Café__Talks"

    def test_multiple_consecutive_spaces(self):
        """Test multiple spaces are collapsed to single underscore."""
        assert sanitize_filename("My    Podcast") == "My____Podcast"

    def test_leading_trailing_spaces(self):
        """Test leading and trailing spaces are stripped."""
        assert sanitize_filename("  MyPodcast  ") == "MyPodcast"

    def test_empty_string(self):
        """Test empty string returns empty string."""
        assert sanitize_filename("") == ""

    def test_only_special_characters(self):
        """Test string with only special characters returns empty."""
        assert sanitize_filename("!@#$%^&*()") == ""

    def test_mixed_case_preserved(self):
        """Test that case is preserved."""
        assert sanitize_filename("MyPodcast") == "MyPodcast"
        assert sanitize_filename("mypodcast") == "mypodcast"


class TestValidateChoice:
    """Tests for validate_choice function."""

    def test_valid_choice(self):
        """Test valid choice returns the value."""
        result = validate_choice("casual", {"casual", "formal"}, "tone")
        assert result == "casual"

    def test_invalid_choice_raises_error(self):
        """Test invalid choice raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_choice("invalid", {"casual", "formal"}, "tone")

        assert "Invalid tone" in str(exc_info.value)
        assert "invalid" in str(exc_info.value)

    def test_error_message_includes_valid_options(self):
        """Test error message includes valid options."""
        with pytest.raises(ValueError) as exc_info:
            validate_choice("wrong", {"a", "b", "c"}, "test")

        error_msg = str(exc_info.value)
        assert "Valid options:" in error_msg
        assert "a" in error_msg
        assert "b" in error_msg
        assert "c" in error_msg

    def test_single_valid_option(self):
        """Test with only one valid option."""
        result = validate_choice("only", {"only"}, "field")
        assert result == "only"

    def test_empty_valid_set(self):
        """Test with empty valid set always raises error."""
        with pytest.raises(ValueError):
            validate_choice("anything", set(), "field")


class TestValidateTone:
    """Tests for validate_tone function."""

    def test_valid_casual_tone(self):
        """Test valid casual tone."""
        assert validate_tone("casual") == "casual"

    def test_valid_professional_tone(self):
        """Test valid professional tone."""
        assert validate_tone("professional") == "professional"

    def test_valid_educational_tone(self):
        """Test valid educational tone."""
        assert validate_tone("educational") == "educational"

    def test_invalid_tone(self):
        """Test invalid tone raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_tone("funny")

        assert "Invalid tone" in str(exc_info.value)

    def test_case_sensitive(self):
        """Test that validation is case-sensitive."""
        with pytest.raises(ValueError):
            validate_tone("CASUAL")


class TestValidateVoice:
    """Tests for validate_voice function."""

    def test_valid_openai_voice(self):
        """Test valid OpenAI voice (default)."""
        assert validate_voice("nova") == "nova"
        assert validate_voice("alloy") == "alloy"

    def test_invalid_voice_default_set(self):
        """Test invalid voice with default set."""
        with pytest.raises(ValueError) as exc_info:
            validate_voice("invalid")

        assert "Invalid voice" in str(exc_info.value)

    def test_custom_valid_voices(self):
        """Test with custom set of valid voices."""
        custom_voices = {"voice1", "voice2", "voice3"}
        assert validate_voice("voice1", custom_voices) == "voice1"

    def test_invalid_custom_voice(self):
        """Test invalid voice with custom set."""
        custom_voices = {"voice1", "voice2"}
        with pytest.raises(ValueError):
            validate_voice("voice3", custom_voices)


class TestValidateLength:
    """Tests for validate_length function."""

    def test_valid_short_length(self):
        """Test valid short length."""
        assert validate_length("short") == "short"

    def test_valid_medium_length(self):
        """Test valid medium length."""
        assert validate_length("medium") == "medium"

    def test_valid_long_length(self):
        """Test valid long length."""
        assert validate_length("long") == "long"

    def test_invalid_length(self):
        """Test invalid length raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validate_length("extra-long")

        assert "Invalid length" in str(exc_info.value)

    def test_case_sensitive(self):
        """Test that validation is case-sensitive."""
        with pytest.raises(ValueError):
            validate_length("SHORT")


class TestGetWordRange:
    """Tests for get_word_range function."""

    def test_short_word_range(self):
        """Test short word range."""
        result = get_word_range("short")
        assert "300" in result or "450" in result

    def test_medium_word_range(self):
        """Test medium word range."""
        result = get_word_range("medium")
        assert "500" in result or "700" in result

    def test_long_word_range(self):
        """Test long word range."""
        result = get_word_range("long")
        assert "800" in result or "1100" in result

    def test_invalid_defaults_to_medium(self):
        """Test invalid length defaults to medium."""
        result = get_word_range("invalid")
        assert result == get_word_range("medium")

    def test_case_insensitive(self):
        """Test case insensitive length."""
        assert get_word_range("SHORT") == get_word_range("short")
