"""
Step 44: Web UI (Streamlit)

Interactive web interface for podcast creation with:
- File upload and URL input
- Persona selection
- Multi-character mode
- Template selection
- Real-time episode generation
- Audio playback

To run:
    streamlit run step44_web_ui.py

Then open browser to http://localhost:8501
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import json

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import get_word_range
from core.file_utils import save_text_file
from core.episode_management import create_episode_directory, save_episode_metadata
from step32_voice_persona_system import PERSONA_LIBRARY
from step27_podcast_templates import PODCAST_TEMPLATES
import config


# Page config
st.set_page_config(
    page_title="AI Podcast Creator",
    page_icon="🎙️",
    layout="wide"
)


def main():
    st.title("🎙️ AI Podcast Creator")
    st.markdown("Generate professional podcasts with AI - From ideas to audio in minutes")

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Provider selection
        available_providers = detect_available_providers()

        if not available_providers:
            st.error("❌ No API keys configured!")
            st.markdown("Set `OPENAI_API_KEY` or `GOOGLE_API_KEY` in `.env`")
            st.stop()

        provider_name = st.selectbox(
            "AI Provider",
            options=list(available_providers.keys()),
            help="Choose which AI provider to use"
        )

        # Voice selection
        provider_config = ProviderConfig(
            llm_provider=provider_name,
            tts_provider=provider_name
        )
        tts_provider = create_tts_provider(provider_config)

        voice = st.selectbox(
            "Voice",
            options=tts_provider.available_voices,
            help="Select podcast voice"
        )

        # Tone and Length
        tone = st.selectbox(
            "Tone",
            options=list(config.VALID_TONES),
            index=1,  # professional
            help="Overall podcast tone"
        )

        length = st.selectbox(
            "Length",
            options=list(config.VALID_LENGTHS),
            index=1,  # medium
            help="Podcast length"
        )

        st.divider()
        st.caption(f"✅ Provider: {provider_name}")

    # Main content area - Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Topic/Text",
        "👥 Multi-Character",
        "🎭 Persona Mode",
        "📄 Template Mode"
    ])

    # Tab 1: Simple topic/text input
    with tab1:
        st.header("Simple Podcast Generation")

        topic = st.text_input(
            "Podcast Topic",
            placeholder="e.g., The Future of Renewable Energy",
            help="Enter the topic for your podcast"
        )

        sources_text = st.text_area(
            "Source Material (Optional)",
            placeholder="Paste text, URLs, or article content here...",
            height=200,
            help="Optional: Provide source material for the podcast"
        )

        if st.button("🎙️ Generate Simple Podcast", type="primary"):
            if not topic:
                st.error("Please enter a topic")
            else:
                generate_simple_podcast(
                    topic, sources_text, provider_name, voice, tone, length
                )

    # Tab 2: Multi-Character Mode
    with tab2:
        st.header("Multi-Character Podcast")
        st.markdown("Generate conversations with multiple speakers")

        mc_topic = st.text_input(
            "Discussion Topic",
            placeholder="e.g., AI Ethics Debate",
            key="mc_topic"
        )

        num_characters = st.slider(
            "Number of Speakers",
            min_value=2,
            max_value=4,
            value=2,
            help="How many characters/speakers?"
        )

        # Show character preview
        st.markdown("**Character Roles:**")
        if num_characters == 2:
            st.markdown("- **HOST**: Asks questions, guides conversation")
            st.markdown("- **GUEST**: Provides expertise and insights")
        elif num_characters == 3:
            st.markdown("- **HOST**: Moderator")
            st.markdown("- **EXPERT1**: Primary expert")
            st.markdown("- **EXPERT2**: Secondary expert, different perspective")
        else:
            st.markdown(f"- {num_characters} speakers with distinct roles")

        if st.button("🎙️ Generate Multi-Character Podcast", type="primary", key="mc_gen"):
            if not mc_topic:
                st.error("Please enter a topic")
            else:
                generate_multi_character_podcast(
                    mc_topic, num_characters, provider_name, voice, tone, length
                )

    # Tab 3: Persona Mode
    with tab3:
        st.header("Persona-Driven Podcast")
        st.markdown("Choose a host persona with unique personality and style")

        # Persona selection
        persona_options = {
            f"{p.name} - {p.description[:50]}...": key
            for key, p in PERSONA_LIBRARY.items()
        }

        selected_persona_display = st.selectbox(
            "Select Host Persona",
            options=list(persona_options.keys())
        )
        selected_persona_key = persona_options[selected_persona_display]
        selected_persona = PERSONA_LIBRARY[selected_persona_key]

        # Show persona details
        with st.expander("📋 Persona Details"):
            st.markdown(f"**Name**: {selected_persona.name}")
            st.markdown(f"**Description**: {selected_persona.description}")
            st.markdown(f"**Energy**: {selected_persona.energy}")
            st.markdown(f"**Humor**: {selected_persona.humor}")
            st.markdown(f"**Pacing**: {selected_persona.pacing}")

        persona_topic = st.text_input(
            "Podcast Topic",
            placeholder="e.g., Blockchain Technology Explained",
            key="persona_topic"
        )

        if st.button("🎙️ Generate Persona Podcast", type="primary", key="persona_gen"):
            if not persona_topic:
                st.error("Please enter a topic")
            else:
                generate_persona_podcast(
                    persona_topic, selected_persona_key, selected_persona,
                    provider_name, voice, tone, length
                )

    # Tab 4: Template Mode
    with tab4:
        st.header("Template-Based Podcast")
        st.markdown("Use predefined formats for consistent structure")

        # Template selection
        template_options = {
            f"{t['name']} - {t['description']}": key
            for key, t in PODCAST_TEMPLATES.items()
        }

        selected_template_display = st.selectbox(
            "Select Template",
            options=list(template_options.keys())
        )
        selected_template_key = template_options[selected_template_display]
        selected_template = PODCAST_TEMPLATES[selected_template_key]

        # Show template details
        with st.expander("📋 Template Structure"):
            st.code(selected_template['system_prompt'][:500] + "...")

        template_topic = st.text_input(
            "Podcast Topic",
            placeholder="e.g., Climate Change Solutions",
            key="template_topic"
        )

        if st.button("🎙️ Generate Template Podcast", type="primary", key="template_gen"):
            if not template_topic:
                st.error("Please enter a topic")
            else:
                generate_template_podcast(
                    template_topic, selected_template_key, selected_template,
                    provider_name, voice, tone, length
                )


def generate_simple_podcast(topic, sources_text, provider_name, voice, tone, length):
    """Generate simple podcast"""
    with st.spinner("🎬 Generating podcast..."):
        try:
            # Initialize providers
            provider_config = ProviderConfig(
                llm_provider=provider_name,
                tts_provider=provider_name
            )
            llm_provider = create_llm_provider(provider_config)
            tts_provider = create_tts_provider(provider_config)

            # Create episode directory
            output_root = Path(config.OUTPUT_ROOT)
            episode_dir, episode_id = create_episode_directory(output_root, topic)

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Generate script
            status_text.text("📝 Generating script...")
            progress_bar.progress(25)

            word_range = get_word_range(length)
            script = build_script(llm_provider, topic, tone, word_range)

            script_file = episode_dir / "script.txt"
            save_text_file(script, script_file)

            # Save sources if provided
            if sources_text:
                sources_dir = episode_dir / "sources"
                sources_dir.mkdir(exist_ok=True)
                save_text_file(sources_text, sources_dir / "source_1.txt")

            # Generate show notes
            status_text.text("📋 Generating show notes...")
            progress_bar.progress(50)

            show_notes = build_show_notes(llm_provider, script)
            show_notes_file = episode_dir / "show_notes.txt"
            save_text_file(show_notes, show_notes_file)

            # Generate audio
            status_text.text("🎵 Generating audio (this may take a minute)...")
            progress_bar.progress(75)

            audio_file = episode_dir / f"podcast_{voice}.mp3"
            generate_audio(tts_provider, script, voice, audio_file)

            # Save metadata
            progress_bar.progress(90)
            metadata = {
                "created_at": datetime.now().isoformat(),
                "episode_id": episode_id,
                "topic": topic,
                "tone": tone,
                "voice": voice,
                "length": length,
                "mode": "simple",
                "has_sources": bool(sources_text)
            }
            save_episode_metadata(episode_dir, metadata)

            progress_bar.progress(100)
            status_text.text("✅ Complete!")

            # Display results
            st.success(f"✅ Podcast generated: {episode_id}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📝 Script")
                st.text_area("", script, height=300, key=f"script_{episode_id}")

            with col2:
                st.markdown("### 📋 Show Notes")
                st.text_area("", show_notes, height=300, key=f"notes_{episode_id}")

            # Audio player
            st.markdown("### 🎧 Listen to Podcast")
            st.audio(str(audio_file))

            st.info(f"📁 Episode saved to: `{episode_dir}`")

        except Exception as e:
            st.error(f"❌ Error: {e}")
            import traceback
            st.code(traceback.format_exc())


def generate_multi_character_podcast(topic, num_characters, provider_name, voice, tone, length):
    """Generate multi-character podcast"""
    with st.spinner("🎬 Generating multi-character podcast..."):
        try:
            from step28_multi_character_podcast import generate_multi_character_script, detect_characters_in_script

            # Initialize providers
            provider_config = ProviderConfig(
                llm_provider=provider_name,
                tts_provider=provider_name
            )
            llm_provider = create_llm_provider(provider_config)
            tts_provider = create_tts_provider(provider_config)

            # Create episode directory
            output_root = Path(config.OUTPUT_ROOT)
            episode_dir, episode_id = create_episode_directory(output_root, topic)

            progress_bar = st.progress(0)
            status_text = st.empty()

            # Generate script
            status_text.text(f"📝 Generating {num_characters}-character dialogue...")
            progress_bar.progress(30)

            word_range = get_word_range(length)
            script = generate_multi_character_script(llm_provider, topic, num_characters, tone, word_range)

            script_file = episode_dir / "script.txt"
            save_text_file(script, script_file)

            # Detect characters
            characters = detect_characters_in_script(script)
            st.info(f"👥 Detected {len(characters)} characters: {', '.join(characters)}")

            # Generate audio
            status_text.text("🎵 Generating audio...")
            progress_bar.progress(70)

            audio_file = episode_dir / f"podcast_{voice}.mp3"
            generate_audio(tts_provider, script, voice, audio_file)

            # Save metadata
            progress_bar.progress(90)
            metadata = {
                "created_at": datetime.now().isoformat(),
                "episode_id": episode_id,
                "topic": topic,
                "tone": tone,
                "voice": voice,
                "length": length,
                "mode": "multi_character",
                "num_characters": num_characters,
                "characters": characters
            }
            save_episode_metadata(episode_dir, metadata)

            progress_bar.progress(100)
            status_text.text("✅ Complete!")

            # Display results
            st.success(f"✅ Multi-character podcast generated!")

            st.markdown("### 📝 Dialogue Script")
            st.text_area("", script, height=400, key=f"mc_script_{episode_id}")

            st.markdown("### 🎧 Listen to Podcast")
            st.audio(str(audio_file))

            st.info(f"📁 Episode saved to: `{episode_dir}`")

        except Exception as e:
            st.error(f"❌ Error: {e}")
            import traceback
            st.code(traceback.format_exc())


def generate_persona_podcast(topic, persona_key, persona, provider_name, voice, tone, length):
    """Generate persona-driven podcast"""
    with st.spinner(f"🎬 Generating as {persona.name}..."):
        try:
            from step32_voice_persona_system import generate_persona_script

            # Initialize providers
            provider_config = ProviderConfig(
                llm_provider=provider_name,
                tts_provider=provider_name
            )
            llm_provider = create_llm_provider(provider_config)
            tts_provider = create_tts_provider(provider_config)

            # Create episode directory
            output_root = Path(config.OUTPUT_ROOT)
            episode_dir, episode_id = create_episode_directory(output_root, topic)

            progress_bar = st.progress(0)
            status_text = st.empty()

            # Generate script
            status_text.text(f"📝 Generating as {persona.name}...")
            progress_bar.progress(30)

            word_range = get_word_range(length)
            script = generate_persona_script(llm_provider, persona, topic, word_range)

            script_file = episode_dir / "script.txt"
            save_text_file(script, script_file)

            # Save persona profile
            persona_file = episode_dir / "persona_profile.json"
            with open(persona_file, 'w') as f:
                json.dump(persona.to_dict(), f, indent=2)

            # Generate audio
            status_text.text("🎵 Generating audio...")
            progress_bar.progress(70)

            audio_file = episode_dir / f"podcast_{voice}.mp3"
            generate_audio(tts_provider, script, voice, audio_file)

            # Save metadata
            progress_bar.progress(90)
            metadata = {
                "created_at": datetime.now().isoformat(),
                "episode_id": episode_id,
                "topic": topic,
                "tone": tone,
                "voice": voice,
                "length": length,
                "mode": "persona",
                "persona": persona.name
            }
            save_episode_metadata(episode_dir, metadata)

            progress_bar.progress(100)
            status_text.text("✅ Complete!")

            # Display results
            st.success(f"✅ Persona podcast generated by {persona.name}!")

            st.markdown("### 📝 Script")
            st.text_area("", script, height=400, key=f"persona_script_{episode_id}")

            st.markdown("### 🎧 Listen to Podcast")
            st.audio(str(audio_file))

            st.info(f"📁 Episode saved to: `{episode_dir}`")

        except Exception as e:
            st.error(f"❌ Error: {e}")
            import traceback
            st.code(traceback.format_exc())


def generate_template_podcast(topic, template_key, template, provider_name, voice, tone, length):
    """Generate template-based podcast"""
    with st.spinner(f"🎬 Generating {template['name']} podcast..."):
        try:
            from step27_podcast_templates import build_script_with_template

            # Initialize providers
            provider_config = ProviderConfig(
                llm_provider=provider_name,
                tts_provider=provider_name
            )
            llm_provider = create_llm_provider(provider_config)
            tts_provider = create_tts_provider(provider_config)

            # Create episode directory
            output_root = Path(config.OUTPUT_ROOT)
            episode_dir, episode_id = create_episode_directory(output_root, topic)

            progress_bar = st.progress(0)
            status_text = st.empty()

            # Generate script
            status_text.text(f"📝 Generating {template['name']} script...")
            progress_bar.progress(30)

            word_range = get_word_range(length)
            script = build_script_with_template(llm_provider, topic, template_key, tone, word_range)

            script_file = episode_dir / "script.txt"
            save_text_file(script, script_file)

            # Generate audio
            status_text.text("🎵 Generating audio...")
            progress_bar.progress(70)

            audio_file = episode_dir / f"podcast_{voice}.mp3"
            generate_audio(tts_provider, script, voice, audio_file)

            # Save metadata
            progress_bar.progress(90)
            metadata = {
                "created_at": datetime.now().isoformat(),
                "episode_id": episode_id,
                "topic": topic,
                "tone": tone,
                "voice": voice,
                "length": length,
                "mode": "template",
                "template": template['name']
            }
            save_episode_metadata(episode_dir, metadata)

            progress_bar.progress(100)
            status_text.text("✅ Complete!")

            # Display results
            st.success(f"✅ {template['name']} podcast generated!")

            st.markdown("### 📝 Script")
            st.text_area("", script, height=400, key=f"template_script_{episode_id}")

            st.markdown("### 🎧 Listen to Podcast")
            st.audio(str(audio_file))

            st.info(f"📁 Episode saved to: `{episode_dir}`")

        except Exception as e:
            st.error(f"❌ Error: {e}")
            import traceback
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
