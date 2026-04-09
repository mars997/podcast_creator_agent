"""
Central configuration for podcast creator with multi-provider support.
"""

# Default provider (for backward compatibility)
DEFAULT_PROVIDER = "openai"

# Provider-specific model configurations
PROVIDER_MODELS = {
    "openai": {
        "llm_model": "gpt-4.1-mini",
        "tts_model": "tts-1-hd",  # HD model for better quality
        "api_key_env": "OPENAI_API_KEY",
        "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "default_voice": "nova",
    },
    "gemini": {
        "llm_model": "gemini-1.5-flash",
        "tts_model": "gemini-2.5-flash",
        "api_key_env": "GOOGLE_API_KEY",
        "voices": [
            "en-US-Journey-D",
            "en-US-Journey-F",
            "en-US-Neural2-A",
            "en-US-Neural2-C",
        ],
        "default_voice": "en-US-Journey-F",
    },
}

# Podcast generation settings
DEFAULT_TONE = "educational"
DEFAULT_LENGTH = "medium"
OUTPUT_ROOT = "output"

VALID_TONES = {"casual", "professional", "educational"}
VALID_LENGTHS = {"short", "medium", "long"}

# Word count ranges by length
WORD_RANGES = {
    "short": "300 to 450 words",
    "medium": "500 to 700 words",
    "long": "800 to 1100 words",
}


def get_word_range(length: str) -> str:
    """Get word range for a given length"""
    return WORD_RANGES.get(length.lower(), WORD_RANGES["medium"])
