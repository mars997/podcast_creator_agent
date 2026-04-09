"""
Created Persona System

Manages user-created personas based on audio style analysis.
Does NOT clone voices - only extracts and maps speaking style traits.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
import json
import uuid


@dataclass
class CreatedPersona:
    """
    A custom persona created from audio style analysis.

    Represents speaking STYLE, NOT exact voice cloning.
    Maps extracted traits to existing voice archetypes and TTS voices.
    """
    persona_id: str
    persona_name: str
    persona_description: str
    reference_audio_filename: str
    voice_archetype: str  # Maps to VOICE_STYLES (e.g., "rapid_fire_comedian")
    preferred_tts_voice: str  # e.g., "nova", "onyx"
    energy: str  # "low", "medium", "high"
    pacing: str  # "slow", "moderate", "fast"
    humor_level: str  # "none", "subtle", "moderate", "high"
    tone: str  # "warm", "professional", "energetic", etc.
    intensity: str  # "relaxed", "moderate", "intense"
    conversational_style: str  # "formal", "casual", "conversational"
    style_notes: str  # Free-form style notes
    system_prompt_guidance: str  # Instructions for script generation
    created_by_user: str  # Username or "default"
    created_at: str  # ISO datetime
    last_modified: str  # ISO datetime

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CreatedPersona':
        """Create from dictionary loaded from JSON"""
        return cls(**data)

    def __str__(self) -> str:
        return f"CreatedPersona({self.persona_name}, archetype={self.voice_archetype})"


# Storage configuration
PERSONAS_DIR = Path("personas")
CREATED_PERSONAS_FILE = PERSONAS_DIR / "created_personas.json"


def _ensure_personas_dir():
    """Ensure personas directory exists"""
    PERSONAS_DIR.mkdir(exist_ok=True)


def _load_personas_json() -> List[Dict]:
    """Load raw JSON data from storage file"""
    _ensure_personas_dir()

    if not CREATED_PERSONAS_FILE.exists():
        return []

    try:
        with open(CREATED_PERSONAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[WARNING] Could not load created personas: {e}")
        return []


def _save_personas_json(personas_data: List[Dict]):
    """Save raw JSON data to storage file"""
    _ensure_personas_dir()

    with open(CREATED_PERSONAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(personas_data, f, indent=2, ensure_ascii=False)


def load_created_personas() -> List[CreatedPersona]:
    """
    Load all created personas from storage.

    Returns:
        List of CreatedPersona objects
    """
    personas_data = _load_personas_json()
    return [CreatedPersona.from_dict(p) for p in personas_data]


def get_created_persona(persona_id: str) -> Optional[CreatedPersona]:
    """
    Get a specific created persona by ID.

    Args:
        persona_id: Unique persona identifier

    Returns:
        CreatedPersona if found, None otherwise
    """
    personas = load_created_personas()
    for persona in personas:
        if persona.persona_id == persona_id:
            return persona
    return None


def save_created_persona(persona: CreatedPersona) -> bool:
    """
    Save a new created persona or update existing one.

    Args:
        persona: CreatedPersona to save

    Returns:
        True if saved successfully
    """
    try:
        personas_data = _load_personas_json()

        # Check if persona already exists
        existing_index = None
        for i, p in enumerate(personas_data):
            if p.get('persona_id') == persona.persona_id:
                existing_index = i
                break

        # Update last_modified timestamp
        persona.last_modified = datetime.now().isoformat()

        # Add or update
        if existing_index is not None:
            personas_data[existing_index] = persona.to_dict()
            print(f"[OK] Updated persona: {persona.persona_name}")
        else:
            personas_data.append(persona.to_dict())
            print(f"[OK] Saved new persona: {persona.persona_name}")

        _save_personas_json(personas_data)
        return True

    except Exception as e:
        print(f"[ERROR] Failed to save persona: {e}")
        return False


def delete_created_persona(persona_id: str) -> bool:
    """
    Delete a created persona.

    Args:
        persona_id: ID of persona to delete

    Returns:
        True if deleted successfully
    """
    try:
        personas_data = _load_personas_json()

        # Filter out the persona to delete
        original_count = len(personas_data)
        personas_data = [p for p in personas_data if p.get('persona_id') != persona_id]

        if len(personas_data) < original_count:
            _save_personas_json(personas_data)
            print(f"[OK] Deleted persona: {persona_id}")
            return True
        else:
            print(f"[WARNING] Persona not found: {persona_id}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to delete persona: {e}")
        return False


def update_created_persona(persona: CreatedPersona) -> bool:
    """
    Update an existing created persona.

    Args:
        persona: Updated CreatedPersona object

    Returns:
        True if updated successfully
    """
    # Same as save_created_persona - it handles both create and update
    return save_created_persona(persona)


def create_persona_from_analysis(
    persona_name: str,
    audio_filename: str,
    style_analysis: Dict,
    description: str = "",
    user: str = "default"
) -> CreatedPersona:
    """
    Create a new CreatedPersona from audio style analysis results.

    Args:
        persona_name: User-provided name for the persona
        audio_filename: Original audio filename (for reference)
        style_analysis: Dict from analyze_audio_style_detailed()
        description: Optional description
        user: Username who created it

    Returns:
        CreatedPersona object ready to save
    """
    now = datetime.now().isoformat()

    # Generate unique ID
    persona_id = f"created_{uuid.uuid4().hex[:12]}"

    # Auto-generate description if not provided
    if not description:
        description = f"Created from {audio_filename}. {style_analysis.get('style_summary', 'Custom speaking style.')}"

    # Build system prompt guidance
    system_prompt_guidance = _build_system_prompt(style_analysis)

    persona = CreatedPersona(
        persona_id=persona_id,
        persona_name=persona_name,
        persona_description=description,
        reference_audio_filename=audio_filename,
        voice_archetype=style_analysis.get('recommended_archetype', 'warm_educator'),
        preferred_tts_voice=style_analysis.get('recommended_tts_voice', 'nova'),
        energy=style_analysis.get('energy', 'medium'),
        pacing=style_analysis.get('pacing', 'moderate'),
        humor_level=style_analysis.get('humor_level', 'subtle'),
        tone=style_analysis.get('tone', 'professional'),
        intensity=style_analysis.get('intensity', 'moderate'),
        conversational_style=style_analysis.get('conversational_style', 'conversational'),
        style_notes=style_analysis.get('style_summary', ''),
        system_prompt_guidance=system_prompt_guidance,
        created_by_user=user,
        created_at=now,
        last_modified=now
    )

    return persona


def create_persona_from_voice_clone(
    persona_name: str,
    cloned_voice_path: str,
    description: str = "",
    user: str = "default"
) -> CreatedPersona:
    """
    Create a new CreatedPersona with voice cloning enabled.

    Args:
        persona_name: User-provided name for the persona
        cloned_voice_path: Path to cloned voice audio file
        description: Optional description
        user: Username who created it

    Returns:
        CreatedPersona object ready to save
    """
    now = datetime.now().isoformat()

    # Generate unique ID
    persona_id = f"cloned_{uuid.uuid4().hex[:12]}"

    # Auto-generate description if not provided
    if not description:
        description = f"Voice-cloned persona from {Path(cloned_voice_path).name}"

    # For voice cloned personas, we use special markers
    persona = CreatedPersona(
        persona_id=persona_id,
        persona_name=persona_name,
        persona_description=description,
        reference_audio_filename=cloned_voice_path,  # Store full path for cloning
        voice_archetype="voice_cloned",  # Special marker
        preferred_tts_voice="coqui_cloned",  # Marker to use Coqui
        energy="medium",  # Defaults since we're using actual voice
        pacing="moderate",
        humor_level="none",
        tone="natural",
        intensity="moderate",
        conversational_style="conversational",
        style_notes=f"Voice cloned from {Path(cloned_voice_path).name}",
        system_prompt_guidance="Use natural, conversational language appropriate for the content.",
        created_by_user=user,
        created_at=now,
        last_modified=now
    )

    return persona


def _build_system_prompt(style_analysis: Dict) -> str:
    """Build system prompt guidance from style analysis"""

    energy = style_analysis.get('energy', 'medium')
    pacing = style_analysis.get('pacing', 'moderate')
    tone = style_analysis.get('tone', 'professional')
    humor = style_analysis.get('humor_level', 'subtle')
    style = style_analysis.get('conversational_style', 'conversational')

    prompt_parts = []

    # Energy
    if energy == "high":
        prompt_parts.append("Use energetic, dynamic language.")
    elif energy == "low":
        prompt_parts.append("Use calm, measured language.")

    # Pacing
    if pacing == "fast":
        prompt_parts.append("Keep sentences short and punchy.")
    elif pacing == "slow":
        prompt_parts.append("Use longer, more deliberate sentences.")

    # Tone
    prompt_parts.append(f"Maintain a {tone} tone throughout.")

    # Humor
    if humor in ["moderate", "high"]:
        prompt_parts.append("Include light humor and wit where appropriate.")

    # Style
    if style == "casual":
        prompt_parts.append("Write in a casual, friendly style.")
    elif style == "formal":
        prompt_parts.append("Write in a formal, professional style.")

    return " ".join(prompt_parts)


def get_all_personas_for_ui() -> Dict[str, Dict]:
    """
    Get all personas (built-in + created) formatted for UI dropdown.

    Returns:
        Dict mapping persona keys to persona info
    """
    from step32_voice_persona_system import PERSONA_LIBRARY

    # Start with built-in personas
    all_personas = {**PERSONA_LIBRARY}

    # Add created personas
    created = load_created_personas()
    for persona in created:
        all_personas[persona.persona_id] = {
            "name": persona.persona_name,
            "description": persona.persona_description,
            "voice": persona.preferred_tts_voice,
            "energy_level": persona.energy,
            "pacing": persona.pacing,
            "tone": persona.tone,
            "archetype": persona.voice_archetype,
            "is_created": True,  # Flag to distinguish from built-in
            "created_at": persona.created_at
        }

    return all_personas


# Example usage
if __name__ == "__main__":
    # Test creating a persona
    test_analysis = {
        "energy": "high",
        "pacing": "fast",
        "humor_level": "moderate",
        "tone": "energetic",
        "intensity": "moderate",
        "conversational_style": "casual",
        "recommended_archetype": "rapid_fire_comedian",
        "recommended_tts_voice": "nova",
        "style_summary": "High-energy, fast-paced, moderately humorous delivery"
    }

    persona = create_persona_from_analysis(
        persona_name="Test Energetic Host",
        audio_filename="test_audio.mp3",
        style_analysis=test_analysis,
        description="Test persona for development"
    )

    print(f"Created: {persona}")
    print(f"System prompt: {persona.system_prompt_guidance}")

    # Test save/load
    if save_created_persona(persona):
        loaded = get_created_persona(persona.persona_id)
        print(f"Loaded: {loaded}")

        # Test delete
        delete_created_persona(persona.persona_id)
