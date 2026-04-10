"""
Unified Generation Pipeline

Single entry point for all podcast generation modes with consistent processing.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import re

from core.input_models import InputContext, GenerationMode, EpisodeResult, Character
from core.validation import get_word_range
from core.file_utils import save_text_file
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
from core.content_generation import generate_audio
from core.provider_setup import get_provider_info
from providers.base import BaseLLMProvider, BaseTTSProvider
import config


class UnifiedGenerationPipeline:
    """
    Single entry point for all podcast generation modes.

    Handles:
    - Topic Mode
    - Text Mode
    - Source Material Mode
    - Multi-Character Mode
    - Persona Mode
    - Template Mode
    """

    def __init__(self, llm_provider: BaseLLMProvider, tts_provider: BaseTTSProvider):
        """
        Initialize pipeline with providers

        Args:
            llm_provider: LLM provider for text generation
            tts_provider: TTS provider for audio generation
        """
        self.llm = llm_provider
        self.tts = tts_provider

    def generate(self, context: InputContext, output_root: Path) -> EpisodeResult:
        """
        Main generation flow

        Args:
            context: Unified input context
            output_root: Root directory for episode output

        Returns:
            EpisodeResult with paths and metadata
        """
        # Create episode directory
        topic = context.get_primary_topic()
        episode_dir, episode_id = create_episode_directory(output_root, topic)

        # Route to appropriate script generator
        script = self._generate_script(context)

        # Save script
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)

        # Generate show notes
        show_notes = self._generate_show_notes(script, context)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)

        # Generate audio with voice assignment
        audio_path, voice_assignments, actual_voice_used, fallback_reason = self._generate_audio(script, context, episode_dir)

        # Build metadata
        metadata = self._build_metadata(
            context, episode_id, episode_dir, script_file,
            show_notes_file, audio_path, voice_assignments
        )
        metadata["actual_voice_used"] = actual_voice_used
        if fallback_reason:
            metadata["voice_fallback_reason"] = fallback_reason

        # Save metadata
        save_episode_metadata(episode_dir, metadata)

        # Update episode index
        episode_summary = create_episode_summary(
            metadata=metadata,
            episode_dir=episode_dir
        )
        index_file = output_root / "episode_index.json"
        update_episode_index(index_file, episode_summary)

        # Return result
        return EpisodeResult(
            episode_id=episode_id,
            episode_dir=str(episode_dir),
            script=script,
            show_notes=show_notes,
            audio_path=str(audio_path),
            metadata=metadata,
            voice_assignments=voice_assignments
        )

    def _generate_script(self, context: InputContext) -> str:
        """Route to appropriate script generator based on mode"""
        if context.mode == GenerationMode.TOPIC:
            return self._generate_topic_script(context)
        elif context.mode == GenerationMode.TEXT:
            return self._generate_text_script(context)
        elif context.mode == GenerationMode.SOURCE:
            return self._generate_source_script(context)
        elif context.mode == GenerationMode.MULTI_CHARACTER:
            return self._generate_multi_character_script(context)
        elif context.mode == GenerationMode.PERSONA:
            return self._generate_persona_script(context)
        elif context.mode == GenerationMode.TEMPLATE:
            return self._generate_template_script(context)
        else:
            raise ValueError(f"Unknown generation mode: {context.mode}")

    def _generate_topic_script(self, context: InputContext) -> str:
        """
        Enhanced topic mode using ALL fields:
        - main_topic
        - topic_details
        - focus_areas
        - desired_style
        """
        word_range = get_word_range(context.length)

        # Build comprehensive prompt
        prompt = f"""Generate a podcast script about: {context.main_topic}

"""

        if context.topic_details:
            prompt += f"""Context and Background:
{context.topic_details}

"""

        if context.focus_areas and len(context.focus_areas) > 0:
            prompt += f"""Focus Areas to Cover:
{chr(10).join(f"- {area}" for area in context.focus_areas)}

"""

        if context.desired_style:
            prompt += f"""Desired Style: {context.desired_style}

"""

        prompt += f"""Tone: {context.tone}
Target length: {word_range} words

Create an engaging podcast script that covers all the focus areas and incorporates the context provided. Make it informative and engaging for listeners."""

        return self.llm.generate_text(prompt)

    def _generate_text_script(self, context: InputContext) -> str:
        """
        Text mode with preservation of user content
        """
        word_range = get_word_range(context.length)

        structure_instruction = "Preserve the original structure and flow of the text." if context.preserve_structure else "Feel free to reorganize for better podcast flow."
        commentary_instruction = "Add host commentary and insights between sections." if context.add_commentary else "Stay close to the original text content."

        prompt = f"""Convert this text into an engaging podcast script:

{context.text_content}

Instructions:
- {structure_instruction}
- {commentary_instruction}
- Preserve all key facts, examples, and details from the source
- Make it suitable for audio (conversational, clear)
- Tone: {context.tone}
- Target length: {word_range} words

Create a podcast script that brings this content to life for listeners."""

        return self.llm.generate_text(prompt)

    def _generate_source_script(self, context: InputContext) -> str:
        """
        Source material mode with audience and depth customization
        """
        word_range = get_word_range(context.length)

        depth_instruction = {
            "summary": "Provide a high-level overview hitting the key points",
            "deep_dive": "Provide comprehensive, detailed analysis covering all aspects"
        }.get(context.depth_preference.value if context.depth_preference else "summary", "Balanced coverage")

        prompt = f"""Create a podcast script based on this source material:

"""

        if context.source_title:
            prompt += f"""Source: {context.source_title}

"""

        prompt += f"""{context.source_material}

"""

        if context.emphasis_instructions:
            prompt += f"""Special Emphasis:
{context.emphasis_instructions}

"""

        prompt += f"""Target Audience: {context.target_audience or 'General'}
Coverage Depth: {depth_instruction}
Tone: {context.tone}
Target length: {word_range} words

Create a podcast script tailored for {context.target_audience or 'a general audience'} that {depth_instruction.lower()}."""

        return self.llm.generate_text(prompt)

    def _generate_multi_character_script(self, context: InputContext) -> str:
        """
        Multi-character mode with rich character profiles and interaction styles
        """
        word_range = get_word_range(context.length)

        # Build character descriptions
        character_descriptions = []
        for char in context.characters:
            char_desc = f"""- {char.name} ({char.role}):
  Personality: {char.personality}
  Speaking style: {char.speaking_style}
  Energy level: {char.energy_level}"""
            if char.humor_style:
                char_desc += f"\n  Humor: {char.humor_style}"
            character_descriptions.append(char_desc)

        interaction_guidance = {
            "interview": "Q&A format with host asking questions and guests providing insights",
            "debate": "Opposing viewpoints with structured arguments and rebuttals",
            "comedy_banter": "Playful, humorous back-and-forth with jokes and callbacks",
            "storytelling": "Collaborative narrative with characters building the story together",
            "classroom": "Teacher-student dynamic with questions and explanations",
            "roundtable": "Moderated panel discussion with diverse perspectives",
            "investigation": "Detective-style analysis with evidence and deduction"
        }.get(context.interaction_style.value if context.interaction_style else "interview", "Natural conversation")

        prompt = f"""Create a {context.interaction_style.value if context.interaction_style else 'conversational'} podcast about: {context.main_topic}

Characters:
{chr(10).join(character_descriptions)}

Interaction Style: {interaction_guidance}

Requirements:
- Each character should speak in a way that matches their personality and speaking style
- Characters' energy levels and humor should come through in their dialogue
- Interaction should feel natural and engaging
- Use clear speaker labels (CHARACTER_NAME: dialogue)
- Tone: {context.tone}
- Target length: {word_range} words

Format each line as:
{context.characters[0].name.upper().replace(' ', '_')}: dialogue text

Generate the complete multi-character script:"""

        return self.llm.generate_text(prompt)

    def _generate_persona_script(self, context: InputContext) -> str:
        """
        Persona mode with fun/serious balance control
        """
        word_range = get_word_range(context.length)

        persona = context.persona

        # Fun vs serious guidance
        if context.fun_vs_serious < 0.3:
            fun_guidance = "Maximum entertainment value - be playful, use humor liberally, keep it light"
        elif context.fun_vs_serious < 0.7:
            fun_guidance = "Balance entertainment and information - be engaging but substantive"
        else:
            fun_guidance = "Maximum informational value - be serious, thorough, minimize jokes"

        prompt = f"""You are {persona.name}: {persona.description}

Your personality traits:
- Energy: {persona.energy}
- Humor style: {persona.humor}
- Pacing: {persona.pacing}
- Tone: {persona.tone}
"""

        if persona.catchphrases and len(persona.catchphrases) > 0:
            prompt += f"""- Catchphrases: {', '.join(persona.catchphrases[:3])}

"""

        prompt += f"""Fun/Serious Balance: {fun_guidance}

Generate a podcast about: {context.main_topic}

Style requirements:
- Stay completely in character throughout
- Your energy level should be {persona.energy}
- Use {persona.pacing} pacing
- Humor style: {persona.humor}
- Target length: {word_range} words

Create a podcast script that embodies {persona.name}'s personality completely:"""

        return self.llm.generate_text(prompt)

    def _generate_template_script(self, context: InputContext) -> str:
        """
        Template mode using predefined formats
        """
        from step27_podcast_templates import PODCAST_TEMPLATES

        word_range = get_word_range(context.length)

        template = PODCAST_TEMPLATES.get(context.template_key)
        if not template:
            raise ValueError(f"Unknown template: {context.template_key}")

        # Use template's system prompt as base
        prompt = template["system_prompt"]

        # Add topic and requirements
        prompt += f"""

Topic: {context.main_topic}
Tone: {context.tone}
Target length: {word_range} words

Generate the podcast script following the template structure exactly:"""

        return self.llm.generate_text(prompt)

    def _generate_show_notes(self, script: str, context: InputContext) -> str:
        """Generate show notes from script"""
        prompt = f"""Based on this podcast script, create comprehensive show notes.

Script:
{script[:3000]}...

Include:
- Episode summary (2-3 sentences)
- Key topics discussed
- Main takeaways (3-5 bullet points)
- Additional context or resources mentioned

Generate the show notes:"""

        return self.llm.generate_text(prompt)

    def _generate_audio(self, script: str, context: InputContext, episode_dir: Path) -> "Tuple[Path, Optional[Dict[str, str]]]":
        """
        Generate audio with appropriate voice assignment

        Returns:
            (audio_path, voice_assignments)
        """
        from core.created_personas import get_created_persona

        # Check if using a voice-cloned persona
        is_voice_cloned = False
        cloned_voice_path = None

        if context.mode == GenerationMode.PERSONA and context.persona:
            # Check if this is a created persona with voice cloning
            persona_id = getattr(context.persona, 'persona_id', None)
            if persona_id and persona_id.startswith('cloned_'):
                # This is a voice-cloned persona
                created_persona = get_created_persona(persona_id)
                if created_persona and created_persona.preferred_tts_voice == "coqui_cloned":
                    is_voice_cloned = True
                    cloned_voice_path = created_persona.reference_audio_filename
                    print(f"[INFO] Using voice cloning from: {cloned_voice_path}")

        # For multi-character mode, we'd implement multi-voice rendering here
        # For now, use simple single-voice generation

        if context.mode == GenerationMode.MULTI_CHARACTER and context.characters:
            # Get voice from first character
            voice = context.characters[0].preferred_voice
            voice_assignments = {char.name: char.preferred_voice for char in context.characters}

            # Save voice assignments
            voice_info_file = episode_dir / "voice_assignments.txt"
            voice_info_content = "Voice Assignments\n" + "="*50 + "\n\n"
            for char in context.characters:
                voice_info_content += f"{char.name}: {char.preferred_voice}\n"
            save_text_file(voice_info_content, voice_info_file)
        elif context.mode == GenerationMode.PERSONA and context.persona:
            # preferred_voice takes priority (e.g. ElevenLabs voice_id from cloned persona)
            if context.preferred_voice:
                voice = context.preferred_voice
            else:
                voice = context.persona.get_voice_for_provider(context.voice_provider)
            voice_assignments = {context.persona.name: voice}

            # Save persona profile
            persona_file = episode_dir / "persona_profile.json"
            import json
            with open(persona_file, 'w') as f:
                json.dump(context.persona.to_dict(), f, indent=2)
        else:
            # Use preferred_voice if set (cloned voice_id or style-matched voice)
            available_voices = self.tts.available_voices
            if context.preferred_voice:
                voice = context.preferred_voice
                print(f"[INFO] Using preferred voice: {voice}")
            else:
                voice = available_voices[0] if available_voices else "nova"
            voice_assignments = None

        # Resolve the active TTS provider.
        # If the voice is not in this provider's list it's an ElevenLabs voice_id — switch providers.
        import os as _os
        from dotenv import load_dotenv as _load_dotenv
        _load_dotenv()
        active_tts = self.tts
        actual_voice_used = voice
        fallback_reason = None

        print(f"[DEBUG] voice='{voice}' | ELEVENLABS_API_KEY set={bool(_os.getenv('ELEVENLABS_API_KEY'))} | available_voices={active_tts.available_voices[:3]}")

        if voice not in active_tts.available_voices:
            el_key = _os.getenv("ELEVENLABS_API_KEY")
            if el_key:
                try:
                    from providers.elevenlabs_provider import ElevenLabsTTSProvider
                    active_tts = ElevenLabsTTSProvider(api_key=el_key)
                    print(f"[INFO] Switched to ElevenLabs provider for voice '{voice[:16]}...'")
                except Exception as el_init_err:
                    import traceback
                    err_detail = f"ElevenLabs init failed: {el_init_err}\n{traceback.format_exc()}"
                    print(f"[ERROR] {err_detail}")
                    fallback_reason = err_detail
                    voice = "nova"
                    actual_voice_used = "nova (fallback)"
                    active_tts = self.tts
            else:
                fallback_reason = f"No ELEVENLABS_API_KEY found — voice '{voice[:16]}' cannot be used"
                print(f"[WARNING] {fallback_reason}")
                voice = active_tts.available_voices[0] if active_tts.available_voices else "nova"
                actual_voice_used = f"{voice} (fallback)"

        # Safe filename: strip characters that aren't alphanumeric/underscore
        import re as _re
        safe_voice = _re.sub(r"[^a-zA-Z0-9_]", "", voice)[:24] or "podcast"
        audio_file = episode_dir / f"podcast_{safe_voice}.mp3"

        # Generate with fallback: if provider rejects the voice, fall back to OpenAI nova
        _FALLBACK_ERRORS = [
            "voice_access_denied", "missing_permissions", "authorization_error",
            "Invalid voice", "detected_captcha_voice", "voice_not_found",
            "quota_exceeded", "max_character_count_exceeded",
        ]

        def _openai_fallback(path, reason=""):
            nonlocal actual_voice_used, fallback_reason
            from providers.openai_provider import OpenAITTSProvider
            if path.exists():
                path.unlink()
            generate_audio(OpenAITTSProvider(), script, "nova", path)
            actual_voice_used = "nova (fallback)"
            fallback_reason = reason
            print(f"[OK] Fallback audio generated with OpenAI nova. Reason: {reason}")

        try:
            generate_audio(active_tts, script, voice, audio_file)
        except Exception as tts_err:
            err_str = str(tts_err)
            if any(x in err_str for x in _FALLBACK_ERRORS):
                print(f"[WARNING] TTS failed: {err_str[:120]}. Falling back.")
                _openai_fallback(audio_file, reason=err_str[:120])
            else:
                raise

        # If file is missing or empty (ElevenLabs wrote 0 bytes before erroring)
        if not audio_file.exists() or audio_file.stat().st_size < 1000:
            print("[WARNING] Audio file empty/missing. Falling back to OpenAI nova.")
            _openai_fallback(audio_file, reason="empty/missing audio file from ElevenLabs")

        return audio_file, voice_assignments, actual_voice_used, fallback_reason

    def _build_metadata(
        self,
        context: InputContext,
        episode_id: str,
        episode_dir: Path,
        script_file: Path,
        show_notes_file: Path,
        audio_file: Path,
        voice_assignments: Optional[Dict[str, str]]
    ) -> Dict:
        """Build complete metadata dictionary"""
        provider_info = get_provider_info(self.llm, self.tts)

        metadata = {
            "created_at": datetime.now().isoformat(),
            "episode_id": episode_id,
            "mode": context.mode.value,
            "topic": context.get_primary_topic(),
            "tone": context.tone,
            "length": context.length,
            "word_range_target": get_word_range(context.length),
            "providers": provider_info,
            "outputs": {
                "episode_dir": str(episode_dir),
                "script_file": str(script_file),
                "show_notes_file": str(show_notes_file),
                "audio_file": str(audio_file)
            }
        }

        # Add mode-specific metadata
        if context.mode == GenerationMode.TOPIC:
            metadata["topic_details"] = context.topic_details
            metadata["focus_areas"] = context.focus_areas
            metadata["desired_style"] = context.desired_style

        elif context.mode == GenerationMode.SOURCE:
            metadata["source_title"] = context.source_title
            metadata["target_audience"] = context.target_audience
            metadata["depth_preference"] = context.depth_preference.value if context.depth_preference else None

        elif context.mode == GenerationMode.MULTI_CHARACTER:
            metadata["num_characters"] = len(context.characters) if context.characters else 0
            metadata["characters"] = [char.to_dict() for char in context.characters] if context.characters else []
            metadata["interaction_style"] = context.interaction_style.value if context.interaction_style else None
            metadata["voice_assignments"] = voice_assignments

        elif context.mode == GenerationMode.PERSONA:
            metadata["persona"] = context.persona.to_dict() if context.persona else None
            metadata["fun_vs_serious"] = context.fun_vs_serious
            metadata["voice_assignments"] = voice_assignments

        elif context.mode == GenerationMode.TEMPLATE:
            metadata["template_key"] = context.template_key

        # Add input context for reference
        metadata["input_context"] = context.to_dict()

        return metadata
