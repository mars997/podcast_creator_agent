"""
Step 32: Voice Persona System

Defines voice personas with consistent characteristics across episodes.
Each persona has personality, speaking style, expertise, and preferred voice.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.provider_setup import get_provider_info
from core.content_generation import generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
from core.input_models import Persona
import config


# Enhanced Persona Library with 15+ vivid archetypes
PERSONA_LIBRARY = {
    # ===== Informative & Educational =====
    "documentary_sage": Persona(
        id="documentary_sage",
        name="The Documentary Sage",
        description="Calm, wonder-filled narrator inspired by nature documentaries. Speaks with reverence and quiet amazement about the world.",
        archetype="documentary_narrator",
        energy="calm",
        humor="subtle",
        pacing="slow",
        tone="educational",
        recommended_voice={"openai": "onyx", "gemini": "en-US-Journey-D"},
        catchphrases=["Remarkable", "In the vast tapestry of...", "Consider, if you will", "And here, we observe"]
    ),

    "professor_chaos": Persona(
        id="professor_chaos",
        name="Professor Chaos",
        description="Eccentric academic who gets wildly passionate about topics. Goes on tangents but always brings it back with brilliance.",
        archetype="eccentric_academic",
        energy="energetic",
        humor="dry",
        pacing="fast",
        tone="educational",
        recommended_voice={"openai": "echo", "gemini": "en-US-Neural2-C"},
        catchphrases=["Fascinating!", "But wait, there's more!", "This is where it gets interesting", "Let me derail for a moment"]
    ),

    "cosmic_philosopher": Persona(
        id="cosmic_philosopher",
        name="The Cosmic Philosopher",
        description="Carl Sagan-inspired cosmic perspective. Everything connects to the bigger picture of existence.",
        archetype="cosmic_thinker",
        energy="calm",
        humor="none",
        pacing="slow",
        tone="educational",
        recommended_voice={"openai": "onyx", "gemini": "en-US-Journey-D"},
        catchphrases=["We are made of star stuff", "Across the cosmic ocean", "In the grand scheme", "Pale blue dot"]
    ),

    # ===== Entertaining & Energetic =====
    "hype_machine": Persona(
        id="hype_machine",
        name="The Hype Machine",
        description="High-energy sports commentator style. Every topic is THE MOST EXCITING THING EVER!",
        archetype="hype_host",
        energy="chaotic",
        humor="playful",
        pacing="fast",
        tone="casual",
        recommended_voice={"openai": "nova", "gemini": "en-US-Neural2-A"},
        catchphrases=["LET'S GO!", "This is HUGE!", "You're not gonna believe this!", "UNBELIEVABLE!"]
    ),

    "late_night_comic": Persona(
        id="late_night_comic",
        name="The Late Night Comic",
        description="Observational humor meets conversational insight. Makes you think while you laugh.",
        archetype="comedy_host",
        energy="moderate",
        humor="witty",
        pacing="moderate",
        tone="casual",
        recommended_voice={"openai": "shimmer", "gemini": "en-US-Journey-F"},
        catchphrases=["Can we talk about...", "Am I right?", "Here's the thing", "You know what kills me?"]
    ),

    "game_show_host": Persona(
        id="game_show_host",
        name="The Game Show Host",
        description="Energetic, engaging, makes learning feel like a fun competition. Keeps energy high!",
        archetype="game_show_presenter",
        energy="energetic",
        humor="playful",
        pacing="fast",
        tone="casual",
        recommended_voice={"openai": "nova", "gemini": "en-US-Neural2-A"},
        catchphrases=["And the answer is...", "Time's up!", "Let's see what we've got", "You're doing great!"]
    ),

    # ===== Dramatic & Atmospheric =====
    "noir_detective": Persona(
        id="noir_detective",
        name="The Noir Detective",
        description="Hard-boiled investigator narration. The city was dark, the topic darker. Atmospheric and moody.",
        archetype="detective_narrator",
        energy="moderate",
        humor="dry",
        pacing="slow",
        tone="professional",
        recommended_voice={"openai": "fable", "gemini": "en-US-Journey-D"},
        catchphrases=["The facts didn't add up", "Something wasn't right", "I had a hunch", "The pieces fell into place"]
    ),

    "mystery_narrator": Persona(
        id="mystery_narrator",
        name="The Mystery Narrator",
        description="Suspenseful storytelling with dramatic pauses. Every topic becomes an investigation to uncover.",
        archetype="mystery_storyteller",
        energy="moderate",
        humor="none",
        pacing="slow",
        tone="professional",
        recommended_voice={"openai": "alloy", "gemini": "en-US-Journey-D"},
        catchphrases=["The question remains", "What they discovered next", "Beneath the surface", "The truth was hidden"]
    ),

    "historical_reenactor": Persona(
        id="historical_reenactor",
        name="The Historical Reenactor",
        description="Period-appropriate dramatic reading. Speaks as if narrating history as it happens.",
        archetype="period_narrator",
        energy="moderate",
        humor="subtle",
        pacing="moderate",
        tone="educational",
        recommended_voice={"openai": "echo", "gemini": "en-US-Journey-D"},
        catchphrases=["In those days", "As history would record", "The annals tell us", "Thus it came to pass"]
    ),

    # ===== Unique & Quirky =====
    "conspiracy_theorist": Persona(
        id="conspiracy_theorist",
        name="The Conspiracy Theorist",
        description="Playful paranoid investigator. Connects dots that may or may not exist. Self-aware and fun.",
        archetype="conspiracy_host",
        energy="energetic",
        humor="absurd",
        pacing="fast",
        tone="casual",
        recommended_voice={"openai": "echo", "gemini": "en-US-Neural2-C"},
        catchphrases=["Wake up, people!", "Connect the dots", "They don't want you to know", "Coincidence? I think not!"]
    ),

    "grumpy_critic": Persona(
        id="grumpy_critic",
        name="The Grumpy Critic",
        description="Sardonic, critical eye on everything. Lovably curmudgeonly. Nothing escapes criticism.",
        archetype="critical_reviewer",
        energy="moderate",
        humor="dry",
        pacing="moderate",
        tone="professional",
        recommended_voice={"openai": "alloy", "gemini": "en-US-Journey-D"},
        catchphrases=["Overrated", "Let me tell you what's wrong", "In my day", "Ridiculous"]
    ),

    "meditation_guide": Persona(
        id="meditation_guide",
        name="The Meditation Guide",
        description="Calm, centered, reflective. Brings mindfulness and peace to every topic.",
        archetype="mindfulness_teacher",
        energy="calm",
        humor="none",
        pacing="slow",
        tone="educational",
        recommended_voice={"openai": "onyx", "gemini": "en-US-Journey-D"},
        catchphrases=["Breathe deeply", "Let that settle", "Be present with", "Notice how"]
    ),

    "podcast_bro": Persona(
        id="podcast_bro",
        name="The Podcast Bro",
        description="Casual 'let me tell you about this' vibe. Like a friend explaining something cool over coffee.",
        archetype="casual_friend",
        energy="moderate",
        humor="playful",
        pacing="moderate",
        tone="casual",
        recommended_voice={"openai": "shimmer", "gemini": "en-US-Journey-F"},
        catchphrases=["Dude", "So check this out", "Here's the deal", "Real talk"]
    ),

    # ===== Original Personas (Updated to new format) =====
    "tech_enthusiast": Persona(
        id="tech_enthusiast",
        name="Alex the Tech Enthusiast",
        description="Energetic, curious, excited about new technology. Former software engineer turned tech educator.",
        archetype="tech_educator",
        energy="energetic",
        humor="playful",
        pacing="fast",
        tone="casual",
        recommended_voice={"openai": "nova", "gemini": "en-US-Neural2-A"},
        catchphrases=["Let me break that down", "Here's the cool part", "Think of it like this"]
    ),

    "science_explainer": Persona(
        id="science_explainer",
        name="Dr. Jordan",
        description="Patient, methodical, loves making complex things simple. PhD researcher with a passion for science communication.",
        archetype="science_educator",
        energy="moderate",
        humor="subtle",
        pacing="moderate",
        tone="educational",
        recommended_voice={"openai": "onyx", "gemini": "en-US-Journey-D"},
        catchphrases=["Let's look at the evidence", "The data shows", "Interestingly enough"]
    ),

    "hopeful_futurist": Persona(
        id="hopeful_futurist",
        name="The Hopeful Futurist",
        description="Optimistic tech visionary. Sees possibility and potential everywhere. The future is bright!",
        archetype="optimistic_visionary",
        energy="energetic",
        humor="playful",
        pacing="moderate",
        tone="casual",
        recommended_voice={"openai": "nova", "gemini": "en-US-Neural2-A"},
        catchphrases=["Imagine a world where", "The possibilities are endless", "We're on the cusp of", "Exciting times ahead"]
    ),

    "drill_sergeant": Persona(
        id="drill_sergeant",
        name="The Drill Sergeant",
        description="Intense, motivational, no-nonsense. Gets you fired up and ready to take action!",
        archetype="motivational_coach",
        energy="chaotic",
        humor="none",
        pacing="fast",
        tone="professional",
        recommended_voice={"openai": "fable", "gemini": "en-US-Neural2-C"},
        catchphrases=["Listen up!", "No excuses!", "Move it!", "You got this!"]
    )
}


def create_custom_persona(
    name: str,
    description: str,
    energy: str = "moderate",
    humor: str = "none",
    pacing: str = "moderate",
    tone: str = "casual",
    provider_voice_map: Optional[Dict[str, str]] = None
) -> Persona:
    """
    Create a custom user-defined persona

    Args:
        name: Persona name
        description: Full description of personality and style
        energy: calm|moderate|energetic|chaotic
        humor: none|dry|witty|playful|absurd
        pacing: slow|moderate|fast
        tone: casual|professional|educational
        provider_voice_map: Optional voice mapping (defaults to nova/Journey-F)
    """
    if provider_voice_map is None:
        provider_voice_map = {
            "openai": "nova",
            "gemini": "en-US-Journey-F"
        }

    persona_id = f"custom_{name.lower().replace(' ', '_')}"

    return Persona(
        id=persona_id,
        name=name,
        description=description,
        archetype="custom",
        energy=energy.lower(),
        humor=humor.lower(),
        pacing=pacing.lower(),
        tone=tone,
        recommended_voice=provider_voice_map,
        catchphrases=[],
        custom=True
    )


def create_custom_persona_interactive() -> Persona:
    """Interactive persona creation for CLI"""
    print("\n" + "="*50)
    print("Create Custom Persona")
    print("="*50)

    name = input("Persona name: ").strip() or "Custom Host"
    description = input("Description: ").strip() or "A friendly and knowledgeable host"
    energy = input("Energy (calm/moderate/energetic/chaotic): ").strip() or "moderate"
    humor = input("Humor (none/dry/witty/playful/absurd): ").strip() or "none"
    pacing = input("Pacing (slow/moderate/fast): ").strip() or "moderate"
    tone = input("Tone (casual/professional/educational): ").strip() or "casual"

    return create_custom_persona(name, description, energy, humor, pacing, tone)


def _legacy_create_custom_persona() -> Dict:
    """Legacy function for backward compatibility"""
    persona = create_custom_persona_interactive()

    # Convert to old dict format
    return {
        "name": name,
        "personality": personality,
        "speaking_style": speaking_style,
        "expertise": expertise,
        "tone_preference": tone_pref,
        "suggested_voice": voice,
        "background": "Custom persona",
        "catchphrases": []
    }


def generate_persona_script(
    llm_provider,
    persona: Dict,
    topic: str,
    word_range: tuple
) -> str:
    """Generate script in persona's voice and style"""

    persona_instruction = f"""You are playing the role of a podcast host with this persona:

NAME: {persona['name']}
PERSONALITY: {persona['personality']}
SPEAKING STYLE: {persona['speaking_style']}
EXPERTISE: {persona['expertise']}
BACKGROUND: {persona.get('background', 'Professional podcaster')}
"""

    if persona.get('catchphrases'):
        catchphrases = ', '.join(persona['catchphrases'])
        persona_instruction += f"\nSIGNATURE PHRASES (use naturally): {catchphrases}\n"

    persona_instruction += f"""
IMPORTANT: Write the entire script AS THIS CHARACTER. Use their personality, speaking style, and expertise throughout. Make it feel like {persona['name']} is speaking directly to the listener.
"""

    prompt = f"""{persona_instruction}

EPISODE TOPIC: {topic}
TARGET LENGTH: {word_range[0]}-{word_range[1]} words
TONE: {persona['tone_preference']}

Generate a podcast script where {persona['name']} discusses: {topic}

Stay in character. Use their speaking style, personality, and expertise to make the content engaging and authentic to who they are as a host.

Generate the complete podcast script:"""

    response = llm_provider.generate_text(prompt)
    return response


def main():
    """Voice persona-based podcast generation"""
    print("\n" + "="*70)
    print("Step 32: Voice Persona System")
    print("="*70)

    # Detect providers
    available = detect_available_providers()
    if not available:
        print("\n[ERROR] No providers available. Set OPENAI_API_KEY or GOOGLE_API_KEY")
        return

    # Provider setup
    provider_name = list(available.keys())[0]
    provider_config = ProviderConfig(
        llm_provider=provider_name,
        tts_provider=provider_name
    )

    llm_provider = create_llm_provider(provider_config)
    tts_provider = create_tts_provider(provider_config)

    print(f"\n[OK] Using provider: {provider_name}")

    # Choose persona
    print("\n" + "="*70)
    print("Voice Personas")
    print("="*70)

    persona_keys = list(PERSONA_LIBRARY.keys())
    for i, (key, persona) in enumerate(PERSONA_LIBRARY.items(), 1):
        print(f"\n{i}. {persona['name']}")
        print(f"   Personality: {persona['personality']}")
        print(f"   Expertise: {persona['expertise']}")
        print(f"   Voice: {persona['suggested_voice']}")

    print(f"\n{len(persona_keys)+1}. Create custom persona")
    print("="*70)

    persona_choice = input(f"\nChoose persona (1-{len(persona_keys)+1}, default 1): ").strip() or "1"

    try:
        pers_idx = int(persona_choice) - 1
        if 0 <= pers_idx < len(persona_keys):
            persona_key = persona_keys[pers_idx]
            persona = PERSONA_LIBRARY[persona_key]
            print(f"\n[OK] Selected: {persona['name']}")
        elif pers_idx == len(persona_keys):
            persona = create_custom_persona()
            persona_key = "custom"
            print(f"\n[OK] Created custom persona: {persona['name']}")
        else:
            persona_key = persona_keys[0]
            persona = PERSONA_LIBRARY[persona_key]
            print(f"\n[OK] Selected: {persona['name']}")
    except ValueError:
        persona_key = persona_keys[0]
        persona = PERSONA_LIBRARY[persona_key]
        print(f"\n[OK] Selected: {persona['name']}")

    # Get episode settings
    topic = input("\nEnter episode topic: ").strip()
    if not topic:
        topic = "Persona Demo"

    # Use persona's preferred settings
    tone = persona['tone_preference']
    voice = persona['suggested_voice']

    # Allow override
    override_voice = input(f"Voice ({voice} recommended, or choose another): ").strip()
    if override_voice:
        voice = override_voice

    length = get_user_input("Choose length (short/medium/long)", config.DEFAULT_LENGTH)

    # Validate
    if voice not in tts_provider.available_voices:
        voice = persona['suggested_voice']  # Use persona default if invalid
    length = validate_choice(length, config.VALID_LENGTHS, "length")
    word_range = get_word_range(length)

    # Create episode directory
    output_root = Path(config.OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"\n[OK] Episode directory: {episode_dir}")
    print(f"[OK] Persona: {persona['name']}")
    print(f"[OK] Voice: {voice}")

    # Save persona info
    persona_file = episode_dir / "persona_profile.json"
    with open(persona_file, 'w', encoding='utf-8') as f:
        json.dump(persona, f, indent=2)
    print(f"[OK] Persona profile saved")

    # Generate persona-driven script
    print(f"\nGenerating script as {persona['name']}...")
    try:
        script = generate_persona_script(llm_provider, persona, topic, word_range)
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Script generated in {persona['name']}'s voice")
    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes_prompt = f"""Create show notes for this podcast episode.

Host: {persona['name']}
Host bio: {persona.get('background', 'Professional podcaster')}
Topic: {topic}

Include:
- Episode summary
- About the host (using persona info)
- Key topics covered
- Host's perspective/approach

Script:
{script}

Generate the show notes:"""

        show_notes = llm_provider.generate_text(show_notes_prompt)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")
    except Exception as e:
        print(f"[WARN] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\nHost: {persona['name']}"
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)

    # Generate audio
    audio_file = episode_dir / f"podcast_{voice}.mp3"
    print(f"\nGenerating audio as {persona['name']}...")
    try:
        generate_audio(tts_provider, script, voice, audio_file)
        print(f"[OK] Audio generated")
    except Exception as e:
        print(f"[ERROR] Audio generation failed: {e}")

    # Save metadata
    created_at = datetime.now().isoformat()
    provider_info = get_provider_info(llm_provider, tts_provider)

    metadata = {
        "created_at": created_at,
        "episode_id": episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "persona": {
            "key": persona_key,
            "name": persona['name'],
            "personality": persona['personality'],
            "speaking_style": persona['speaking_style'],
            "expertise": persona['expertise']
        },
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "persona_file": str(persona_file),
            "script_file": str(script_file),
            "show_notes_file": str(show_notes_file),
            "audio_file": str(audio_file)
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "persona_name": persona['name'],
            "persona_key": persona_key
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 32 Complete: Persona-Based Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Host: {persona['name']}")
    print(f"Personality: {persona['personality']}")
    print(f"Voice: {voice}")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - persona_profile.json")
    print(f"  - script.txt (in {persona['name']}'s voice)")
    print(f"  - show_notes.txt")
    print(f"  - podcast_{voice}.mp3")
    print(f"  - metadata.json")


if __name__ == "__main__":
    main()
