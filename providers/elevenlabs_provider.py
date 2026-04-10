"""
ElevenLabs TTS Provider with Voice Cloning Support

Supports:
- Instant voice cloning from uploaded audio (6+ seconds recommended)
- High-quality TTS generation with cloned or preset voices
- Requires ELEVENLABS_API_KEY in environment
"""

import os
from pathlib import Path
from typing import List, Optional

ElevenLabs = None
ELEVENLABS_AVAILABLE = False
try:
    from elevenlabs.client import ElevenLabs as _ElevenLabs
    ElevenLabs = _ElevenLabs
    ELEVENLABS_AVAILABLE = True
except Exception:
    pass

from .base import BaseTTSProvider


# ElevenLabs preset voices (free-tier available)
ELEVENLABS_PRESET_VOICES = [
    "Rachel",
    "Drew",
    "Clyde",
    "Paul",
    "Domi",
    "Dave",
    "Fin",
    "Sarah",
    "Antoni",
    "Thomas",
    "Charlie",
    "George",
    "Emily",
    "Elli",
    "Callum",
    "Patrick",
    "Harry",
    "Liam",
    "Dorothy",
    "Josh",
    "Arnold",
    "Charlotte",
    "Matilda",
    "Matthew",
    "James",
    "Joseph",
    "Jeremy",
    "Michael",
    "Ethan",
    "Gigi",
    "Freya",
    "Grace",
    "Daniel",
    "Lily",
    "Serena",
    "Adam",
    "Nicole",
    "Jessie",
    "Ryan",
    "Sam",
    "Glinda",
    "Giovanni",
    "Mimi",
]


class ElevenLabsTTSProvider(BaseTTSProvider):
    """
    ElevenLabs TTS provider with instant voice cloning.

    Voice cloning flow:
        provider = ElevenLabsTTSProvider()
        voice_id = provider.clone_voice(audio_path, name="My Voice")
        provider.generate_audio(text, voice_id, output_path)
    """

    def __init__(self, api_key: str = None, model: str = "eleven_multilingual_v2"):
        # Always attempt a live import so stale module-level flags don't block us
        try:
            from elevenlabs.client import ElevenLabs as _EL
        except Exception as _ie:
            raise ImportError(
                f"elevenlabs package not available: {_ie}\n"
                "Install it with: pip install elevenlabs"
            )

        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ELEVENLABS_API_KEY not found in environment variables.\n"
                "Please set ELEVENLABS_API_KEY in your .env file.\n"
                "Get a free key at: https://elevenlabs.io"
            )

        self._client = _EL(api_key=self.api_key)
        self._model = model
        self._cloned_voices: dict = {}  # name -> voice_id cache

    def clone_voice(self, audio_path: Path, name: str, description: str = "") -> str:
        """
        Clone a voice from an audio file using ElevenLabs Instant Voice Cloning.

        Args:
            audio_path: Path to audio file (MP3, WAV, M4A etc.)
                        6-30 seconds recommended for best quality
            name: Name to give the cloned voice
            description: Optional description

        Returns:
            voice_id: ElevenLabs voice ID for this cloned voice
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"[INFO] Cloning voice from: {audio_path.name}")

        with open(audio_path, "rb") as f:
            voice = self._client.voices.ivc.create(
                name=name,
                description=description or f"Voice cloned from {audio_path.name}",
                files=[f],
            )

        voice_id = voice.voice_id
        self._cloned_voices[name] = voice_id
        print(f"[OK] Voice cloned successfully. voice_id={voice_id}")
        return voice_id

    def generate_audio(
        self,
        text: str,
        voice: str,
        output_path: Path,
        speed: float = 1.0,
        **kwargs,
    ) -> None:
        """
        Generate audio using ElevenLabs TTS.

        Args:
            text: Text to convert to speech
            voice: Voice name (preset) or voice_id (cloned)
            output_path: Where to save the MP3 file
            speed: Not directly supported by ElevenLabs (ignored)
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        audio = self._client.text_to_speech.convert(
            voice_id=voice,
            text=text,
            model_id=self._model,
            output_format="mp3_44100_128",
        )

        with open(output_path, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

        print(f"[OK] ElevenLabs audio saved: {output_path}")

    def delete_cloned_voice(self, voice_id: str) -> bool:
        """
        Delete a cloned voice from ElevenLabs (to keep account clean).

        Args:
            voice_id: Voice ID to delete

        Returns:
            True if deleted successfully
        """
        try:
            self._client.voices.delete(voice_id)
            print(f"[OK] Deleted ElevenLabs voice: {voice_id}")
            return True
        except Exception as e:
            print(f"[WARNING] Could not delete voice {voice_id}: {e}")
            return False

    @property
    def available_voices(self) -> List[str]:
        return ELEVENLABS_PRESET_VOICES

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def provider_name(self) -> str:
        return "elevenlabs"
