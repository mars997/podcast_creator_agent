"""
Google Gemini provider implementation.

Supports both LLM and TTS via the Gemini API.
"""

import os
from pathlib import Path
from typing import List

try:
    from google import genai
except ImportError:
    genai = None

from .base import BaseLLMProvider, BaseTTSProvider


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini LLM provider"""

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        if genai is None:
            raise ImportError(
                "google-genai package not installed.\n"
                "Install it with: pip install google-genai"
            )

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables.\n"
                "Please set GOOGLE_API_KEY in your .env file.\n"
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )

        genai.configure(api_key=self.api_key)
        self._model_name = model
        self.model = genai.GenerativeModel(model)

    def generate_text(self, prompt: str) -> str:
        """Generate text using Gemini API"""
        response = self.model.generate_content(prompt)
        return response.text.strip()

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def provider_name(self) -> str:
        return "gemini"


class GeminiTTSProvider(BaseTTSProvider):
    """
    Google Gemini TTS provider using native Gemini API.

    Note: This is a placeholder implementation. The actual Gemini TTS API
    may require different configuration. Users should verify the API
    at: https://ai.google.dev/gemini-api/docs/speech-generation
    """

    # Sample voices - Gemini supports 380+ voices
    # See: https://docs.cloud.google.com/text-to-speech/docs/gemini-tts
    SAMPLE_VOICES = [
        "en-US-Journey-D",  # Male voice
        "en-US-Journey-F",  # Female voice
        "en-US-Neural2-A",
        "en-US-Neural2-C",
    ]

    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        if genai is None:
            raise ImportError(
                "google-genai package not installed.\n"
                "Install it with: pip install google-genai"
            )

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables.\n"
                "Please set GOOGLE_API_KEY in your .env file.\n"
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )

        genai.configure(api_key=self.api_key)
        self._model_name = model
        self.model = genai.GenerativeModel(model)

    def generate_audio(
        self, text: str, voice: str, output_path: Path, **kwargs
    ) -> None:
        """
        Generate audio using Gemini's native TTS.

        Note: Gemini TTS uses natural language style prompts for voice control.
        The actual API implementation may vary - check official documentation.
        """
        # Gemini uses style prompts for voice control
        # Example: "Speak in a professional news anchor voice"
        style_prompt = kwargs.get("style_prompt", f"Speak clearly in a {voice} style")

        # NOTE: This is a placeholder implementation
        # The actual Gemini TTS API may use different methods
        # Users should consult: https://ai.google.dev/gemini-api/docs/speech-generation
        try:
            # Attempt to generate audio using Gemini TTS
            # This API structure may need adjustment based on actual Gemini TTS implementation
            response = self.model.generate_content(
                text,
                generation_config={
                    "speech_config": {"voice_config": {"style_prompt": style_prompt}}
                },
            )

            # Write audio data to file
            if hasattr(response, "audio_data"):
                output_path.write_bytes(response.audio_data)
            else:
                raise NotImplementedError(
                    "Gemini TTS API structure may have changed. "
                    "Please check the latest documentation at: "
                    "https://ai.google.dev/gemini-api/docs/speech-generation"
                )
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate audio with Gemini TTS: {e}\n"
                f"Note: Gemini TTS API is evolving. Consider using OpenAI TTS instead.\n"
                f"Set PODCAST_TTS_PROVIDER=openai in your .env file."
            ) from e

    @property
    def available_voices(self) -> List[str]:
        return self.SAMPLE_VOICES

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def provider_name(self) -> str:
        return "gemini"
