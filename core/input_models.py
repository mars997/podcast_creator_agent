"""
Unified Input Models for Podcast Generation

Defines data structures for all 6 generation modes:
- Topic Mode
- Text Mode
- Source Material Mode
- Multi-Character Mode
- Persona Mode
- Template Mode
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum


class GenerationMode(str, Enum):
    """Podcast generation modes"""
    TOPIC = "topic"
    TEXT = "text"
    SOURCE = "source"
    MULTI_CHARACTER = "multi_character"
    PERSONA = "persona"
    TEMPLATE = "template"


class InteractionStyle(str, Enum):
    """Multi-character interaction styles"""
    INTERVIEW = "interview"
    DEBATE = "debate"
    COMEDY_BANTER = "comedy_banter"
    STORYTELLING = "storytelling"
    CLASSROOM = "classroom"
    ROUNDTABLE = "roundtable"
    INVESTIGATION = "investigation"


class DepthPreference(str, Enum):
    """Source material coverage depth"""
    SUMMARY = "summary"
    DEEP_DIVE = "deep_dive"


@dataclass
class Character:
    """Rich character definition for multi-character mode"""
    name: str
    role: str  # host, guest, expert, moderator, analyst, etc.
    personality: str  # energetic and curious, analytical and calm, etc.
    speaking_style: str  # uses metaphors, asks probing questions, etc.
    preferred_voice: str  # Voice ID from TTS provider
    energy_level: str = "medium"  # low, medium, high
    humor_style: Optional[str] = None  # dry, witty, playful, none

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "role": self.role,
            "personality": self.personality,
            "speaking_style": self.speaking_style,
            "preferred_voice": self.preferred_voice,
            "energy_level": self.energy_level,
            "humor_style": self.humor_style
        }


@dataclass
class Persona:
    """Enhanced persona definition with vivid archetypes"""
    id: str
    name: str
    description: str
    archetype: str  # documentary_narrator, hype_host, calm_educator, etc.
    energy: str  # calm, moderate, energetic, chaotic
    humor: str  # dry, witty, playful, none, absurd
    pacing: str  # slow, moderate, fast
    tone: str  # casual, professional, educational
    recommended_voice: Dict[str, str]  # provider -> voice mapping
    catchphrases: Optional[List[str]] = None
    custom: bool = False  # True if user-created

    def get_voice_for_provider(self, provider: str) -> str:
        """Get recommended voice for a specific provider"""
        return self.recommended_voice.get(provider, list(self.recommended_voice.values())[0])

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "archetype": self.archetype,
            "energy": self.energy,
            "humor": self.humor,
            "pacing": self.pacing,
            "tone": self.tone,
            "recommended_voice": self.recommended_voice,
            "catchphrases": self.catchphrases,
            "custom": self.custom
        }


@dataclass
class InputContext:
    """
    Unified input representation for all generation modes.

    Each mode uses a subset of these fields. The mode field determines
    which fields are relevant for a given generation request.
    """
    mode: GenerationMode

    # ===== Topic Mode Fields =====
    main_topic: Optional[str] = None
    topic_details: Optional[str] = None  # Additional context
    focus_areas: Optional[List[str]] = None  # Specific areas to cover
    desired_style: Optional[str] = None  # Tone/style override

    # ===== Text Mode Fields =====
    text_content: Optional[str] = None  # Long-form text input
    preserve_structure: bool = True
    add_commentary: bool = False

    # ===== Source Material Mode Fields =====
    source_material: Optional[str] = None  # Pasted or extracted source text
    source_files: Optional[List[str]] = None  # Uploaded file paths
    source_title: Optional[str] = None
    emphasis_instructions: Optional[str] = None  # What to emphasize
    target_audience: Optional[str] = None  # General, Technical, Business, etc.
    depth_preference: Optional[DepthPreference] = None  # summary vs deep_dive

    # ===== Multi-Character Mode Fields =====
    characters: Optional[List[Character]] = None
    interaction_style: Optional[InteractionStyle] = None

    # ===== Persona Mode Fields =====
    persona: Optional[Persona] = None
    fun_vs_serious: float = 0.5  # 0.0 = max fun, 1.0 = max serious

    # ===== Template Mode Fields =====
    template_key: Optional[str] = None

    # ===== Shared Configuration =====
    tone: str = "professional"  # casual, professional, educational
    length: str = "medium"  # short, medium, long
    voice_provider: str = "openai"  # openai, gemini
    preferred_voice: Optional[str] = None  # Override TTS voice (e.g. matched from uploaded audio)

    # Additional metadata
    metadata: Dict = field(default_factory=dict)

    def get_primary_topic(self) -> str:
        """Extract the primary topic regardless of mode"""
        if self.mode == GenerationMode.TOPIC:
            return self.main_topic or "Untitled Topic"
        elif self.mode == GenerationMode.TEXT:
            # Extract first line or truncate
            if self.text_content:
                first_line = self.text_content.split('\n')[0]
                return first_line[:100] if len(first_line) > 100 else first_line
            return "Text Content"
        elif self.mode == GenerationMode.SOURCE:
            return self.source_title or "Source Material"
        elif self.mode == GenerationMode.MULTI_CHARACTER:
            return self.main_topic or "Multi-Character Discussion"
        elif self.mode == GenerationMode.PERSONA:
            return self.main_topic or f"{self.persona.name} Episode"
        elif self.mode == GenerationMode.TEMPLATE:
            return self.main_topic or "Template Episode"
        return "Untitled Episode"

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "mode": self.mode.value,
            "main_topic": self.main_topic,
            "topic_details": self.topic_details,
            "focus_areas": self.focus_areas,
            "desired_style": self.desired_style,
            "text_content": self.text_content[:500] if self.text_content else None,  # Truncate for metadata
            "preserve_structure": self.preserve_structure,
            "add_commentary": self.add_commentary,
            "source_title": self.source_title,
            "emphasis_instructions": self.emphasis_instructions,
            "target_audience": self.target_audience,
            "depth_preference": self.depth_preference.value if self.depth_preference else None,
            "characters": [c.to_dict() for c in self.characters] if self.characters else None,
            "interaction_style": self.interaction_style.value if self.interaction_style else None,
            "persona": self.persona.to_dict() if self.persona else None,
            "fun_vs_serious": self.fun_vs_serious,
            "template_key": self.template_key,
            "tone": self.tone,
            "length": self.length,
            "voice_provider": self.voice_provider,
            "metadata": self.metadata
        }


@dataclass
class EpisodeResult:
    """Result of a generation pipeline"""
    episode_id: str
    episode_dir: str
    script: str
    show_notes: str
    audio_path: str
    metadata: Dict
    voice_assignments: Optional[Dict[str, str]] = None  # character -> voice mapping

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "episode_id": self.episode_id,
            "episode_dir": self.episode_dir,
            "script_length": len(self.script),
            "audio_path": self.audio_path,
            "voice_assignments": self.voice_assignments,
            "metadata": self.metadata
        }
