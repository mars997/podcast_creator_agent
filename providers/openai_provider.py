"""
OpenAI provider implementation.

Maintains existing API patterns for backward compatibility.
"""

import os
from pathlib import Path
from typing import List

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .base import BaseLLMProvider, BaseTTSProvider


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI LLM provider maintaining existing API patterns"""

    def __init__(self, api_key: str = None, model: str = "gpt-4.1-mini"):
        if OpenAI is None:
            raise ImportError(
                "openai package not installed.\n"
                "Install it with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables.\n"
                "Please set OPENAI_API_KEY in your .env file."
            )
        self.client = OpenAI(api_key=self.api_key)
        self._model = model

    def generate_text(self, prompt: str) -> str:
        """
        Generate text using OpenAI API.
        Preserves existing client.responses.create() pattern.
        """
        response = self.client.responses.create(model=self._model, input=prompt)
        return response.output_text.strip()

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def provider_name(self) -> str:
        return "openai"


class OpenAITTSProvider(BaseTTSProvider):
    """
    OpenAI TTS provider with HD model support and speed control.

    Supports:
    - HD model (tts-1-hd) for better quality
    - Speed control (0.25 - 4.0)
    - All 6 OpenAI voices
    """

    VALID_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(self, api_key: str = None, model: str = "tts-1-hd", use_hd: bool = True):
        """
        Initialize OpenAI TTS provider

        Args:
            api_key: OpenAI API key (defaults to env var)
            model: TTS model (tts-1 or tts-1-hd)
            use_hd: Use HD model for better quality (default: True)
        """
        if OpenAI is None:
            raise ImportError(
                "openai package not installed.\n"
                "Install it with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables.\n"
                "Please set OPENAI_API_KEY in your .env file."
            )
        self.client = OpenAI(api_key=self.api_key)

        # Use HD model by default for better quality
        if use_hd and model == "gpt-4o-mini-tts":
            # Legacy model name - upgrade to tts-1-hd
            model = "tts-1-hd"
        elif use_hd and model == "tts-1":
            model = "tts-1-hd"

        self._model = model
        self._use_hd = use_hd

    def generate_audio(
        self, text: str, voice: str, output_path: Path, speed: float = 1.0, **kwargs
    ) -> None:
        """
        Generate audio using OpenAI TTS with speed control.

        Args:
            text: Text to convert to speech
            voice: Voice ID (alloy, echo, fable, onyx, nova, shimmer)
            output_path: Where to save MP3 file
            speed: Speaking rate (0.25 - 4.0, default: 1.0)
            **kwargs: Additional parameters (ignored for compatibility)
        """
        if voice not in self.VALID_VOICES:
            print(f"[WARNING] Voice '{voice}' is not a valid OpenAI voice. Falling back to 'nova'.")
            voice = "nova"

        # Clamp speed to valid range
        speed = max(0.25, min(4.0, speed))

        # Generate with speed parameter
        with self.client.audio.speech.with_streaming_response.create(
            model=self._model,
            voice=voice,
            input=text,
            speed=speed,  # NEW: Speed control
        ) as response:
            response.stream_to_file(output_path)

    @property
    def available_voices(self) -> List[str]:
        return self.VALID_VOICES

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def provider_name(self) -> str:
        return "openai"
