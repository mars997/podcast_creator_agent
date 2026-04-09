"""
Voice Style System

Rich voice archetypes with TTS optimization metadata.
Maps personality archetypes to provider voices with delivery hints.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class EnergyLevel(str, Enum):
    """Voice energy levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class HumorLevel(str, Enum):
    """Humor intensity"""
    NONE = "none"
    SUBTLE = "subtle"
    MODERATE = "moderate"
    HIGH = "high"
    DRY = "dry"  # Deadpan


class Pacing(str, Enum):
    """Speaking pace"""
    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"
    RAPID = "rapid"


class SentenceLength(str, Enum):
    """Preferred sentence length for TTS"""
    SHORT = "short"  # 5-10 words
    MEDIUM = "medium"  # 10-15 words
    LONG = "long"  # 15-20 words


class PunctuationStyle(str, Enum):
    """Punctuation strategy"""
    MINIMAL = "minimal"  # Few marks
    STANDARD = "standard"  # Normal
    DRAMATIC = "dramatic"  # Lots of pauses, em dashes


@dataclass
class VoiceStyle:
    """
    Rich voice archetype definition with TTS optimization metadata.

    Maps personality archetypes to provider-specific voices and
    includes hints for script generation optimization.
    """
    # Identity
    id: str
    display_name: str
    archetype: str
    description: str

    # Provider voice mappings
    openai_voice: str  # Standard TTS voice
    openai_hd_voice: str  # HD TTS voice (same as standard for now)
    gemini_voice: Optional[str] = None
    elevenlabs_voice: Optional[str] = None  # Future

    # Voice characteristics
    gender_presentation: str = "neutral"  # male, female, neutral
    age_vibe: str = "middle"  # young, middle, mature, elderly
    energy_level: EnergyLevel = EnergyLevel.MEDIUM
    humor_level: HumorLevel = HumorLevel.SUBTLE
    pacing: Pacing = Pacing.MODERATE
    tone: str = "warm"  # warm, cool, sharp, smooth, rough
    clarity: str = "clear"  # crystal, clear, conversational, rough
    intensity: str = "moderate"  # calm, moderate, intense, chaotic

    # Script generation hints
    sentence_length: SentenceLength = SentenceLength.MEDIUM
    use_contractions: bool = True
    use_interjections: bool = True
    use_filler_words: bool = False
    punctuation_style: PunctuationStyle = PunctuationStyle.STANDARD

    # TTS-specific
    openai_speed: float = 1.0  # 0.25 - 4.0
    prefer_hd: bool = True  # Use HD model when available

    # Use cases
    recommended_for: List[str] = field(default_factory=list)

    # Fallback
    fallback_voice: str = "alloy"

    def get_voice_for_provider(self, provider: str, use_hd: bool = True) -> str:
        """Get voice ID for specific provider"""
        if provider == "openai":
            return self.openai_hd_voice if (use_hd and self.prefer_hd) else self.openai_voice
        elif provider == "gemini":
            return self.gemini_voice or "en-US-Journey-F"
        elif provider == "elevenlabs":
            return self.elevenlabs_voice or self.fallback_voice
        else:
            return self.fallback_voice

    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "display_name": self.display_name,
            "archetype": self.archetype,
            "description": self.description,
            "openai_voice": self.openai_voice,
            "gender_presentation": self.gender_presentation,
            "age_vibe": self.age_vibe,
            "energy_level": self.energy_level.value,
            "humor_level": self.humor_level.value,
            "pacing": self.pacing.value,
            "tone": self.tone,
            "recommended_for": self.recommended_for,
            "openai_speed": self.openai_speed
        }


# ===== VOICE STYLE LIBRARY =====

VOICE_STYLES = {
    "rapid_fire_comedian": VoiceStyle(
        id="rapid_fire_comedian",
        display_name="Rapid-Fire Comedian",
        archetype="high_energy_comedian",
        description="High-energy, punchy delivery with perfect joke timing. Fast-paced and charismatic.",
        openai_voice="echo",
        openai_hd_voice="echo",
        gemini_voice="en-US-Neural2-A",
        gender_presentation="neutral",
        age_vibe="young",
        energy_level=EnergyLevel.EXTREME,
        humor_level=HumorLevel.HIGH,
        pacing=Pacing.RAPID,
        tone="sharp",
        clarity="conversational",
        intensity="chaotic",
        sentence_length=SentenceLength.SHORT,
        use_contractions=True,
        use_interjections=True,
        use_filler_words=True,
        punctuation_style=PunctuationStyle.DRAMATIC,
        openai_speed=1.15,
        recommended_for=["comedy", "entertainment", "high_energy_content"],
        fallback_voice="echo"
    ),

    "animated_troublemaker": VoiceStyle(
        id="animated_troublemaker",
        display_name="Animated Troublemaker",
        archetype="chaotic_mischievous",
        description="Chaotic, mischievous energy with exaggerated reactions. Playful and unpredictable.",
        openai_voice="nova",
        openai_hd_voice="nova",
        gemini_voice="en-US-Journey-F",
        gender_presentation="neutral",
        age_vibe="young",
        energy_level=EnergyLevel.EXTREME,
        humor_level=HumorLevel.HIGH,
        pacing=Pacing.FAST,
        tone="sharp",
        clarity="conversational",
        intensity="chaotic",
        sentence_length=SentenceLength.SHORT,
        use_contractions=True,
        use_interjections=True,
        use_filler_words=True,
        punctuation_style=PunctuationStyle.DRAMATIC,
        openai_speed=1.1,
        recommended_for=["comedy", "character_roleplay", "playful_content"],
        fallback_voice="nova"
    ),

    "big_sports_host": VoiceStyle(
        id="big_sports_host",
        display_name="Big Personality Sports Host",
        archetype="hype_sports_commentator",
        description="Bold, loud, hype personality with oversized energy. Charismatic and commanding.",
        openai_voice="fable",
        openai_hd_voice="fable",
        gemini_voice="en-US-Journey-D",
        gender_presentation="neutral",
        age_vibe="middle",
        energy_level=EnergyLevel.EXTREME,
        humor_level=HumorLevel.MODERATE,
        pacing=Pacing.FAST,
        tone="warm",
        clarity="clear",
        intensity="intense",
        sentence_length=SentenceLength.SHORT,
        use_contractions=True,
        use_interjections=True,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.DRAMATIC,
        openai_speed=1.1,
        recommended_for=["sports", "hype_content", "motivational"],
        fallback_voice="fable"
    ),

    "smooth_night_show_host": VoiceStyle(
        id="smooth_night_show_host",
        display_name="Smooth Late-Night Host",
        archetype="cool_conversational_host",
        description="Cool, confident, conversational with smooth delivery. Witty and engaging.",
        openai_voice="alloy",
        openai_hd_voice="alloy",
        gemini_voice="en-US-Journey-D",
        gender_presentation="neutral",
        age_vibe="middle",
        energy_level=EnergyLevel.MEDIUM,
        humor_level=HumorLevel.MODERATE,
        pacing=Pacing.MODERATE,
        tone="smooth",
        clarity="clear",
        intensity="moderate",
        sentence_length=SentenceLength.MEDIUM,
        use_contractions=True,
        use_interjections=True,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.STANDARD,
        openai_speed=1.0,
        recommended_for=["talk_shows", "interviews", "conversational"],
        fallback_voice="alloy"
    ),

    "nerdy_tech_builder": VoiceStyle(
        id="nerdy_tech_builder",
        display_name="Nerdy Tech Builder",
        archetype="enthusiastic_tech_explainer",
        description="Sharp, precise, enthusiastic about tech. Fast-talking but clear.",
        openai_voice="shimmer",
        openai_hd_voice="shimmer",
        gemini_voice="en-US-Neural2-C",
        gender_presentation="neutral",
        age_vibe="young",
        energy_level=EnergyLevel.HIGH,
        humor_level=HumorLevel.SUBTLE,
        pacing=Pacing.FAST,
        tone="sharp",
        clarity="crystal",
        intensity="moderate",
        sentence_length=SentenceLength.MEDIUM,
        use_contractions=True,
        use_interjections=True,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.STANDARD,
        openai_speed=1.05,
        recommended_for=["tech", "tutorials", "educational"],
        fallback_voice="shimmer"
    ),

    "confident_startup_founder": VoiceStyle(
        id="confident_startup_founder",
        display_name="Confident Startup Founder",
        archetype="bold_visionary",
        description="Bold, visionary, intense with big ideas. Confident and authoritative.",
        openai_voice="onyx",
        openai_hd_voice="onyx",
        gemini_voice="en-US-Journey-D",
        gender_presentation="neutral",
        age_vibe="middle",
        energy_level=EnergyLevel.HIGH,
        humor_level=HumorLevel.SUBTLE,
        pacing=Pacing.MODERATE,
        tone="sharp",
        clarity="clear",
        intensity="intense",
        sentence_length=SentenceLength.MEDIUM,
        use_contractions=True,
        use_interjections=False,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.STANDARD,
        openai_speed=1.0,
        recommended_for=["business", "pitches", "visionary_content"],
        fallback_voice="onyx"
    ),

    "epic_documentary_narrator": VoiceStyle(
        id="epic_documentary_narrator",
        display_name="Epic Documentary Narrator",
        archetype="rich_authoritative_narrator",
        description="Rich, authoritative, wonder-filled documentary narration. Slow and majestic.",
        openai_voice="onyx",
        openai_hd_voice="onyx",
        gemini_voice="en-US-Journey-D",
        gender_presentation="neutral",
        age_vibe="mature",
        energy_level=EnergyLevel.LOW,
        humor_level=HumorLevel.NONE,
        pacing=Pacing.SLOW,
        tone="warm",
        clarity="crystal",
        intensity="calm",
        sentence_length=SentenceLength.LONG,
        use_contractions=False,
        use_interjections=False,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.MINIMAL,
        openai_speed=0.9,
        recommended_for=["documentaries", "nature", "storytelling"],
        fallback_voice="onyx"
    ),

    "deadpan_professor": VoiceStyle(
        id="deadpan_professor",
        display_name="Deadpan Professor",
        archetype="dry_intellectual",
        description="Dry, intellectual, measured delivery with subtle humor. Deadpan and precise.",
        openai_voice="alloy",
        openai_hd_voice="alloy",
        gemini_voice="en-US-Neural2-C",
        gender_presentation="neutral",
        age_vibe="mature",
        energy_level=EnergyLevel.LOW,
        humor_level=HumorLevel.DRY,
        pacing=Pacing.SLOW,
        tone="cool",
        clarity="crystal",
        intensity="calm",
        sentence_length=SentenceLength.LONG,
        use_contractions=False,
        use_interjections=False,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.MINIMAL,
        openai_speed=0.95,
        recommended_for=["academic", "intellectual", "dry_humor"],
        fallback_voice="alloy"
    ),

    "conspiracy_radio_guy": VoiceStyle(
        id="conspiracy_radio_guy",
        display_name="Conspiracy Radio Host",
        archetype="intense_urgent_investigator",
        description="Intense, urgent, dramatic with conspiratorial energy. Fast and captivating.",
        openai_voice="echo",
        openai_hd_voice="echo",
        gemini_voice="en-US-Neural2-A",
        gender_presentation="neutral",
        age_vibe="middle",
        energy_level=EnergyLevel.HIGH,
        humor_level=HumorLevel.MODERATE,
        pacing=Pacing.FAST,
        tone="rough",
        clarity="conversational",
        intensity="intense",
        sentence_length=SentenceLength.SHORT,
        use_contractions=True,
        use_interjections=True,
        use_filler_words=True,
        punctuation_style=PunctuationStyle.DRAMATIC,
        openai_speed=1.05,
        recommended_for=["mystery", "investigation", "dramatic_content"],
        fallback_voice="echo"
    ),

    "martial_arts_philosopher": VoiceStyle(
        id="martial_arts_philosopher",
        display_name="Martial-Arts Philosopher",
        archetype="calm_wise_teacher",
        description="Calm, wise, measured with philosophical depth. Peaceful and authoritative.",
        openai_voice="fable",
        openai_hd_voice="fable",
        gemini_voice="en-US-Journey-D",
        gender_presentation="neutral",
        age_vibe="mature",
        energy_level=EnergyLevel.LOW,
        humor_level=HumorLevel.SUBTLE,
        pacing=Pacing.SLOW,
        tone="warm",
        clarity="clear",
        intensity="calm",
        sentence_length=SentenceLength.MEDIUM,
        use_contractions=False,
        use_interjections=False,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.MINIMAL,
        openai_speed=0.9,
        recommended_for=["philosophy", "wisdom", "meditation"],
        fallback_voice="fable"
    ),

    "energetic_game_show_host": VoiceStyle(
        id="energetic_game_show_host",
        display_name="Energetic Game Show Host",
        archetype="upbeat_engaging_entertainer",
        description="Upbeat, engaging, fun with game show energy. Enthusiastic and clear.",
        openai_voice="nova",
        openai_hd_voice="nova",
        gemini_voice="en-US-Journey-F",
        gender_presentation="neutral",
        age_vibe="middle",
        energy_level=EnergyLevel.EXTREME,
        humor_level=HumorLevel.HIGH,
        pacing=Pacing.FAST,
        tone="warm",
        clarity="crystal",
        intensity="moderate",
        sentence_length=SentenceLength.SHORT,
        use_contractions=True,
        use_interjections=True,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.DRAMATIC,
        openai_speed=1.1,
        recommended_for=["games", "entertainment", "interactive"],
        fallback_voice="nova"
    ),

    "warm_educator": VoiceStyle(
        id="warm_educator",
        display_name="Warm Educator",
        archetype="patient_kind_teacher",
        description="Patient, kind, clear with warm teaching style. Encouraging and accessible.",
        openai_voice="shimmer",
        openai_hd_voice="shimmer",
        gemini_voice="en-US-Journey-F",
        gender_presentation="neutral",
        age_vibe="middle",
        energy_level=EnergyLevel.MEDIUM,
        humor_level=HumorLevel.SUBTLE,
        pacing=Pacing.MODERATE,
        tone="warm",
        clarity="crystal",
        intensity="calm",
        sentence_length=SentenceLength.MEDIUM,
        use_contractions=True,
        use_interjections=True,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.STANDARD,
        openai_speed=0.95,
        recommended_for=["education", "tutorials", "how_to"],
        fallback_voice="shimmer"
    ),

    "sarcastic_critic": VoiceStyle(
        id="sarcastic_critic",
        display_name="Sarcastic Critic",
        archetype="sharp_witty_reviewer",
        description="Sharp, witty, cutting with sarcastic edge. Critical but entertaining.",
        openai_voice="echo",
        openai_hd_voice="echo",
        gemini_voice="en-US-Neural2-C",
        gender_presentation="neutral",
        age_vibe="middle",
        energy_level=EnergyLevel.MEDIUM,
        humor_level=HumorLevel.HIGH,
        pacing=Pacing.MODERATE,
        tone="sharp",
        clarity="clear",
        intensity="moderate",
        sentence_length=SentenceLength.MEDIUM,
        use_contractions=True,
        use_interjections=True,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.STANDARD,
        openai_speed=1.0,
        recommended_for=["reviews", "comedy", "critique"],
        fallback_voice="echo"
    ),

    "storyteller": VoiceStyle(
        id="storyteller",
        display_name="Engaging Storyteller",
        archetype="narrative_expressive_narrator",
        description="Narrative, expressive, rhythmic storytelling. Captivating and dynamic.",
        openai_voice="fable",
        openai_hd_voice="fable",
        gemini_voice="en-US-Journey-D",
        gender_presentation="neutral",
        age_vibe="middle",
        energy_level=EnergyLevel.MEDIUM,
        humor_level=HumorLevel.SUBTLE,
        pacing=Pacing.MODERATE,
        tone="warm",
        clarity="clear",
        intensity="moderate",
        sentence_length=SentenceLength.MEDIUM,
        use_contractions=True,
        use_interjections=False,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.STANDARD,
        openai_speed=0.95,
        recommended_for=["stories", "narrative", "audiobooks"],
        fallback_voice="fable"
    ),

    "debate_moderator": VoiceStyle(
        id="debate_moderator",
        display_name="Debate Moderator",
        archetype="neutral_authoritative_host",
        description="Neutral, clear, authoritative moderation. Professional and balanced.",
        openai_voice="alloy",
        openai_hd_voice="alloy",
        gemini_voice="en-US-Journey-D",
        gender_presentation="neutral",
        age_vibe="middle",
        energy_level=EnergyLevel.MEDIUM,
        humor_level=HumorLevel.NONE,
        pacing=Pacing.MODERATE,
        tone="cool",
        clarity="crystal",
        intensity="moderate",
        sentence_length=SentenceLength.MEDIUM,
        use_contractions=False,
        use_interjections=False,
        use_filler_words=False,
        punctuation_style=PunctuationStyle.STANDARD,
        openai_speed=1.0,
        recommended_for=["debates", "moderation", "professional"],
        fallback_voice="alloy"
    )
}


def get_voice_style(style_id: str) -> Optional[VoiceStyle]:
    """Get voice style by ID"""
    return VOICE_STYLES.get(style_id)


def get_voice_styles_by_category() -> Dict[str, List[VoiceStyle]]:
    """Group voice styles by category"""
    return {
        "Comic & Energetic": [
            VOICE_STYLES["rapid_fire_comedian"],
            VOICE_STYLES["animated_troublemaker"],
            VOICE_STYLES["energetic_game_show_host"],
            VOICE_STYLES["sarcastic_critic"]
        ],
        "Professional & Tech": [
            VOICE_STYLES["nerdy_tech_builder"],
            VOICE_STYLES["confident_startup_founder"],
            VOICE_STYLES["debate_moderator"]
        ],
        "Storytelling & Documentary": [
            VOICE_STYLES["epic_documentary_narrator"],
            VOICE_STYLES["storyteller"],
            VOICE_STYLES["martial_arts_philosopher"]
        ],
        "Hosts & Entertainers": [
            VOICE_STYLES["big_sports_host"],
            VOICE_STYLES["smooth_night_show_host"],
            VOICE_STYLES["conspiracy_radio_guy"]
        ],
        "Educational": [
            VOICE_STYLES["warm_educator"],
            VOICE_STYLES["deadpan_professor"]
        ]
    }


def get_recommended_style_for_use_case(use_case: str) -> Optional[VoiceStyle]:
    """Get recommended voice style for a use case"""
    for style in VOICE_STYLES.values():
        if use_case in style.recommended_for:
            return style
    return None
