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
    """OpenAI TTS provider maintaining existing API patterns"""

    VALID_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini-tts"):
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

    def generate_audio(
        self, text: str, voice: str, output_path: Path, **kwargs
    ) -> None:
        """
        Generate audio using OpenAI TTS.
        Preserves existing streaming pattern.
        """
        if voice not in self.VALID_VOICES:
            raise ValueError(
                f"Invalid voice '{voice}'. Must be one of: {', '.join(self.VALID_VOICES)}"
            )

        # Preserves existing streaming pattern
        with self.client.audio.speech.with_streaming_response.create(
            model=self._model,
            voice=voice,
            input=text,
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
