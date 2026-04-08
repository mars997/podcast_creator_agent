"""
Abstract base classes for LLM and TTS providers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate text from prompt"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name (openai/gemini)"""
        pass


class BaseTTSProvider(ABC):
    """Abstract base class for TTS providers"""

    @abstractmethod
    def generate_audio(
        self, text: str, voice: str, output_path: Path, **kwargs
    ) -> None:
        """Generate audio file from text"""
        pass

    @property
    @abstractmethod
    def available_voices(self) -> List[str]:
        """Return list of available voice IDs"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the TTS model identifier"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name (openai/gemini)"""
        pass
