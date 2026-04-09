"""
Coqui TTS Provider with Voice Cloning Support

Uses XTTS v2 model for high-quality voice cloning from audio samples.
Completely free and runs locally.
"""

import os
from pathlib import Path
from typing import List, Optional

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False
    TTS = None

from .base import BaseTTSProvider


class CoquiTTSProvider(BaseTTSProvider):
    """
    Coqui TTS provider with XTTS v2 voice cloning.

    Features:
    - Voice cloning from 6+ second audio samples
    - 17 language support
    - Free, local processing
    - No API keys required
    """

    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        """
        Initialize Coqui TTS provider

        Args:
            model_name: TTS model to use (default: XTTS v2)
        """
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch not installed.\n"
                "Install it with: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu\n"
                "Note: Required for Coqui TTS voice cloning"
            )

        if not COQUI_AVAILABLE:
            raise ImportError(
                "Coqui TTS not installed.\n"
                "Install it with: pip install coqui-tts\n"
                "Note: Requires Python 3.10-3.14"
            )

        self._model_name = model_name
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._tts = None  # Lazy load
        self._speaker_wav = None  # Voice clone reference

        print(f"[INFO] Coqui TTS initialized (device: {self._device})")

    def _load_model(self):
        """Lazy load TTS model"""
        if self._tts is None:
            print(f"[INFO] Loading {self._model_name}...")

            # Accept license agreement programmatically
            import os
            os.environ["COQUI_TOS_AGREED"] = "1"

            # Disable SSL verification for model download (workaround for SSL issues)
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context

            try:
                self._tts = TTS(self._model_name, progress_bar=False).to(self._device)
                print("[OK] Model loaded")
            except Exception as e:
                print(f"[ERROR] Failed to load model: {e}")
                print("[INFO] Trying with GPU disabled...")
                # Fallback: force CPU
                self._device = "cpu"
                self._tts = TTS(self._model_name, progress_bar=False, gpu=False)
                print("[OK] Model loaded on CPU")

    def set_speaker_voice(self, speaker_wav_path: Path):
        """
        Set the voice to clone from an audio file

        Args:
            speaker_wav_path: Path to audio file (6+ seconds recommended)
        """
        if not speaker_wav_path.exists():
            raise FileNotFoundError(f"Speaker audio not found: {speaker_wav_path}")

        self._speaker_wav = str(speaker_wav_path)
        print(f"[OK] Voice clone reference set: {speaker_wav_path.name}")

    def generate_audio(
        self,
        text: str,
        voice: str,
        output_path: Path,
        speed: float = 1.0,
        language: str = "en",
        **kwargs
    ) -> None:
        """
        Generate audio using voice cloning

        Args:
            text: Text to convert to speech
            voice: Ignored (uses speaker_wav instead)
            output_path: Where to save audio file
            speed: Speaking rate (default: 1.0)
            language: Language code (default: "en")
            **kwargs: Additional parameters

        Notes:
            - If speaker_wav is set, it will clone that voice
            - If not set, falls back to default XTTS voice
        """
        self._load_model()

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"[INFO] Generating audio ({len(text)} chars)...")

        if self._speaker_wav:
            # Voice cloning mode
            print(f"[INFO] Using voice clone from: {Path(self._speaker_wav).name}")
            self._tts.tts_to_file(
                text=text,
                speaker_wav=self._speaker_wav,
                language=language,
                file_path=str(output_path),
                speed=speed
            )
        else:
            # Default voice mode (no cloning)
            print("[WARNING] No speaker voice set, using default voice")
            self._tts.tts_to_file(
                text=text,
                language=language,
                file_path=str(output_path),
                speed=speed
            )

        print(f"[OK] Audio generated: {output_path}")

    @property
    def available_voices(self) -> List[str]:
        """
        Return available voices

        Note: For voice cloning, this is dynamically set via set_speaker_voice()
        """
        if self._speaker_wav:
            return [f"cloned_voice ({Path(self._speaker_wav).name})"]
        else:
            return ["default_xtts_voice"]

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def provider_name(self) -> str:
        return "coqui_xtts"

    def clone_voice_from_audio(self, audio_path: Path, output_name: str = "cloned_voice") -> str:
        """
        Clone a voice from an audio file

        Args:
            audio_path: Path to audio file to clone from
            output_name: Name for the cloned voice

        Returns:
            Voice ID (path to speaker wav)
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # For XTTS, we just need to reference the audio file
        # No separate training step required
        self.set_speaker_voice(audio_path)

        print(f"[OK] Voice cloned: {output_name}")
        print(f"    Source: {audio_path.name}")
        print(f"    Duration: 6+ seconds recommended for best quality")

        return str(audio_path)
