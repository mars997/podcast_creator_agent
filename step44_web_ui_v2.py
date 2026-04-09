"""
Step 44: Web UI v2 - 5-Tab Unified Source Material Hub

REDESIGNED: Consolidated from 6 tabs to 5 tabs
- Removed Text tab (merged into Source Material)
- Expanded Source Material into unified ingestion hub

New tab structure:
1. Topic Mode
2. Source Material (unified hub with paste/upload/link/audio)
3. Multi-Character
4. Persona Mode
5. Template Mode

To run:
    streamlit run step44_web_ui_v2.py

Then open browser to http://localhost:8501
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import Optional
import json
import os

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.unified_generation import UnifiedGenerationPipeline
from core.input_models import InputContext, GenerationMode, Character, InteractionStyle, DepthPreference
from core.source_management import (
    extract_text_from_file,
    fetch_article_text,
    fetch_youtube_transcript,
    transcribe_audio,
    analyze_audio_style,
    match_style_to_archetype
)
from step32_voice_persona_system import PERSONA_LIBRARY, create_custom_persona
from step27_podcast_templates import PODCAST_TEMPLATES
from core.voice_styles import get_voice_style
from core.voice_assignment import assign_voices_smart
import config


# Page config
st.set_page_config(
    page_title="AI Podcast Creator v2",
    page_icon="🎙️",
    layout="wide"
)


def main():
    st.title("🎙️ AI Podcast Creator v2")
    st.markdown("**5 Generation Modes** | Unified Source Material Hub | Professional AI-powered podcast production")

    # Sidebar - Global Configuration
    with st.sidebar:
        st.header("⚙️ Global Settings")

        # Provider selection
        available_providers = detect_available_providers()

        if not available_providers:
            st.error("❌ No API keys configured!")
            st.markdown("Set `OPENAI_API_KEY` or `GOOGLE_API_KEY` in `.env`")
            st.stop()

        provider_name = st.selectbox(
            "AI Provider",
            options=list(available_providers.keys()),
            help="Choose which AI provider to use for generation"
        )

        # Initialize providers
        provider_config = ProviderConfig(
            llm_provider=provider_name,
            tts_provider=provider_name
        )
        llm_provider = create_llm_provider(provider_config)
        tts_provider = create_tts_provider(provider_config)

        # Tone and Length (global defaults)
        tone = st.selectbox(
            "Default Tone",
            options=list(config.VALID_TONES),
            index=1,  # professional
            help="Overall podcast tone"
        )

        length = st.selectbox(
            "Podcast Length",
            options=list(config.VALID_LENGTHS),
            index=1,  # medium
            help="Target podcast length"
        )

        st.divider()
        st.caption(f"✅ Provider: {provider_name}")
        st.caption(f"📊 Available Voices: {len(tts_provider.available_voices)}")

    # Main content area - 5 Tabs (TEXT REMOVED, SOURCE EXPANDED)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Topic",
        "📚 Source Material",  # EXPANDED
        "👥 Multi-Character",
        "🎭 Persona Mode",
        "📋 Template Mode"
    ])

    # ===== TAB 1: TOPIC MODE =====
    with tab1:
        st.header("Topic-Based Podcast")
        st.markdown("Create a podcast from a topic with detailed guidance")

        main_topic = st.text_input(
            "Main Topic *",
            placeholder="e.g., The Future of Renewable Energy",
            help="The core subject of your podcast"
        )

        topic_details = st.text_area(
            "Topic Details / Additional Context",
            height=150,
            placeholder="Provide background, specific angles, or context you want covered...\n\nExample: Focus on recent technological breakthroughs, compare solar vs wind, discuss policy implications for developing nations.",
            help="Add depth and direction to the topic"
        )

        focus_areas_text = st.text_area(
            "Optional Focus Areas (one per line)",
            height=100,
            placeholder="e.g.,\n- Solar panel efficiency improvements\n- Grid storage challenges\n- Policy and regulation\n- Cost trends over time",
            help="Specific areas or questions you want the podcast to address"
        )

        desired_style = st.text_input(
            "Desired Tone or Style",
            placeholder="e.g., conversational and optimistic, or analytical and balanced",
            help="How should the podcast feel? This overrides the global tone setting."
        )

        if st.button("🎙️ Generate Topic Podcast", type="primary", key="generate_topic"):
            if not main_topic:
                st.error("Please enter a main topic")
            else:
                # Parse focus areas
                focus_areas = [
                    line.strip().lstrip('-').strip()
                    for line in focus_areas_text.split('\n')
                    if line.strip()
                ] if focus_areas_text else None

                # Build context
                context = InputContext(
                    mode=GenerationMode.TOPIC,
                    main_topic=main_topic,
                    topic_details=topic_details,
                    focus_areas=focus_areas,
                    desired_style=desired_style or tone,
                    tone=tone,
                    length=length,
                    voice_provider=provider_name
                )

                # Generate
                generate_podcast(context, llm_provider, tts_provider)

    # ===== TAB 2: SOURCE MATERIAL (UNIFIED HUB) =====
    with tab2:
        st.header("📚 Source Material - Unified Ingestion Hub")
        st.markdown("**Provide content in any format:** paste text, upload files, add links, or upload audio")

        # Initialize session state for source material
        if 'source_text' not in st.session_state:
            st.session_state.source_text = ""
        if 'source_urls' not in st.session_state:
            st.session_state.source_urls = []
        if 'source_files' not in st.session_state:
            st.session_state.source_files = []

        # ===== SECTION A: PASTE TEXT =====
        st.subheader("📝 Section A: Paste Text")
        st.caption("Paste your content directly (articles, notes, transcripts, etc.)")

        pasted_text = st.text_area(
            "Paste your content here",
            height=300,
            placeholder="""Paste your content here...

Examples:
• Article or blog post text
• Meeting notes or transcripts
• Research findings
• Book excerpts
• Documentation

We'll transform this into an engaging podcast.""",
            help="Paste long-form text content"
        )

        if pasted_text:
            st.caption(f"📊 Character count: {len(pasted_text):,} | Word count: ~{len(pasted_text.split()):,}")

        col1, col2 = st.columns(2)
        with col1:
            preserve_structure = st.checkbox(
                "Preserve original structure",
                value=True,
                help="Keep the flow and organization of your original text"
            )
        with col2:
            add_commentary = st.checkbox(
                "Add host commentary",
                value=False,
                help="Insert additional insights and explanations"
            )

        st.divider()

        # ===== SECTION B: UPLOAD FILES =====
        st.subheader("📄 Section B: Upload Files")
        st.caption("Upload documents: PDF, DOCX, EPUB, TXT, MD, HTML")

        uploaded_files = st.file_uploader(
            "Upload source documents",
            type=["pdf", "txt", "md", "docx", "epub", "html", "htm"],
            accept_multiple_files=True,
            help="Upload documents to extract text from"
        )

        if uploaded_files:
            st.info(f"✅ {len(uploaded_files)} file(s) uploaded")
            for file in uploaded_files:
                st.caption(f"📎 {file.name} ({file.size:,} bytes)")

        st.divider()

        # ===== SECTION C: ADD LINKS =====
        st.subheader("🔗 Section C: Add Links")
        st.caption("Add YouTube videos or web articles")

        col1, col2 = st.columns([4, 1])
        with col1:
            url_input = st.text_input(
                "Paste URL",
                placeholder="https://youtube.com/watch?v=... or https://article-website.com/post",
                help="Enter YouTube video or article URL"
            )
        with col2:
            if st.button("➕ Add URL"):
                if url_input and url_input not in st.session_state.source_urls:
                    st.session_state.source_urls.append(url_input)
                    st.success("Added!")
                elif not url_input:
                    st.error("Enter a URL first")
                else:
                    st.warning("Already added")

        # Display added URLs
        if st.session_state.source_urls:
            st.write("**Added URLs:**")
            for i, url in enumerate(st.session_state.source_urls):
                col1, col2 = st.columns([5, 1])
                with col1:
                    # Auto-detect type
                    if 'youtube.com' in url or 'youtu.be' in url:
                        st.caption(f"🎥 YouTube: {url}")
                    else:
                        st.caption(f"🔗 Article: {url}")
                with col2:
                    if st.button("❌", key=f"remove_url_{i}"):
                        st.session_state.source_urls.pop(i)
                        st.rerun()

        st.divider()

        # ===== SECTION D: UPLOAD AUDIO =====
        st.subheader("🎙️ Section D: Upload Audio")
        st.caption("Upload audio to transcribe or create a voice-cloned persona")

        audio_file = st.file_uploader(
            "Upload audio file",
            type=["mp3", "wav", "m4a", "ogg", "webm"],
            help="Supported: MP3, WAV, M4A, OGG, WEBM",
            key="source_audio_upload"
        )

        audio_purpose = None
        if audio_file:
            st.audio(audio_file, format=f'audio/{audio_file.name.split(".")[-1]}')

            audio_purpose = st.radio(
                "What would you like to do with this audio?",
                [
                    "📝 Transcribe as source material",
                    "🎤 Clone voice & create persona (then use in podcast)"
                ],
                help="Choose whether to transcribe the audio content or clone the voice for persona creation",
                key="audio_purpose_radio"
            )

            if "Clone voice" in audio_purpose:
                st.info("🎤 **Voice Cloning:** We'll attempt to clone the voice from this audio. If network blocks it, we'll fall back to style analysis.")
                st.info("💡 **Better option:** Go to **Persona Mode** tab → **✨ Create New** → **📤 Upload Audio** for the full persona creation interface.")

        st.divider()

        # ===== SOURCE MATERIAL CONFIGURATION =====
        st.subheader("⚙️ Generation Configuration")

        col1, col2 = st.columns(2)
        with col1:
            source_title = st.text_input(
                "Source Title (optional)",
                placeholder="e.g., Q3 2026 Financial Report",
                help="Give your source material a descriptive title"
            )

            target_audience = st.selectbox(
                "Target Audience",
                ["General Audience", "Technical Experts", "Business Leaders", "Students", "Enthusiasts", "Policymakers"],
                help="Tailor complexity and examples to audience"
            )

        with col2:
            emphasis = st.text_area(
                "Emphasis Instructions (optional)",
                height=100,
                placeholder="What should we emphasize?\n\ne.g., 'Focus on actionable insights' or 'Emphasize technical breakthroughs'",
                help="Guide what aspects to highlight"
            )

            depth = st.radio(
                "Coverage Depth",
                ["Summary (high-level overview)", "Deep Dive (comprehensive analysis)"],
                horizontal=True,
                help="Summary = key highlights, Deep Dive = thorough exploration"
            )

        depth_pref = DepthPreference.DEEP_DIVE if "Deep Dive" in depth else DepthPreference.SUMMARY

        # ===== GENERATE BUTTON =====
        if st.button("⚡ Generate Podcast", type="primary", use_container_width=True, key="generate_source"):
            # Collect all source material
            combined_source = ""

            # Add pasted text
            if pasted_text:
                combined_source += f"=== Pasted Text ===\n\n{pasted_text}\n\n"

            # Process uploaded files
            if uploaded_files:
                for file in uploaded_files:
                    try:
                        # Save temp file
                        temp_path = Path(f"temp_{file.name}")
                        with open(temp_path, 'wb') as f:
                            f.write(file.getvalue())

                        # Extract text
                        extracted = extract_text_from_file(temp_path)
                        combined_source += f"{extracted}\n\n"

                        # Cleanup
                        temp_path.unlink()
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {e}")

            # Process URLs
            if st.session_state.source_urls:
                for url in st.session_state.source_urls:
                    try:
                        if 'youtube.com' in url or 'youtu.be' in url:
                            text = fetch_youtube_transcript(url)
                        else:
                            text = fetch_article_text(url)
                        combined_source += f"{text}\n\n"
                    except Exception as e:
                        st.error(f"Error fetching {url}: {e}")

            # Process audio (only if transcription mode selected)
            if audio_file and audio_purpose and "Transcribe" in audio_purpose:
                try:
                    # Save temp audio file
                    temp_audio = Path(f"temp_audio.{audio_file.name.split('.')[-1]}")
                    with open(temp_audio, 'wb') as f:
                        f.write(audio_file.getvalue())

                    # Transcribe audio for source material
                    with st.spinner("🎤 Transcribing audio..."):
                        transcript = transcribe_audio(temp_audio)
                        combined_source += f"{transcript}\n\n"
                        st.success("✅ Audio transcribed")

                    temp_audio.unlink()

                except Exception as e:
                    st.error(f"Error processing audio: {e}")
                    import traceback
                    st.code(traceback.format_exc())

            # Validate
            if not combined_source or len(combined_source) < 100:
                st.error("Please provide source material (paste text, upload files, or add links)")
            else:
                # Build context
                context = InputContext(
                    mode=GenerationMode.SOURCE,
                    source_material=combined_source,
                    source_title=source_title,
                    emphasis_instructions=emphasis,
                    target_audience=target_audience,
                    depth_preference=depth_pref,
                    preserve_structure=preserve_structure,
                    add_commentary=add_commentary,
                    tone=tone,
                    length=length,
                    voice_provider=provider_name
                )

                # Generate
                generate_podcast(context, llm_provider, tts_provider)

    # ===== TAB 3: MULTI-CHARACTER MODE =====
    with tab3:
        st.header("Multi-Character Podcast")
        st.markdown("Create dynamic conversations with multiple distinct characters (2-5 speakers)")

        mc_topic = st.text_input(
            "Discussion Topic *",
            placeholder="e.g., The Ethics of AI in Healthcare",
            key="mc_topic",
            help="What will the characters discuss?"
        )

        num_characters = st.slider(
            "Number of Characters",
            min_value=2,
            max_value=5,
            value=2,
            help="How many distinct speakers in the conversation"
        )

        interaction_style = st.selectbox(
            "Interaction Style",
            [
                "Interview (host + guest Q&A)",
                "Debate (opposing viewpoints)",
                "Comedy Banter (playful back-and-forth)",
                "Storytelling (collaborative narrative)",
                "Classroom Discussion (teacher + students)",
                "Roundtable (moderated panel)",
                "Investigation (detective-style analysis)"
            ],
            help="How should the characters interact?"
        )

        # Parse interaction style
        interaction_map = {
            "Interview": InteractionStyle.INTERVIEW,
            "Debate": InteractionStyle.DEBATE,
            "Comedy Banter": InteractionStyle.COMEDY_BANTER,
            "Storytelling": InteractionStyle.STORYTELLING,
            "Classroom": InteractionStyle.CLASSROOM,
            "Roundtable": InteractionStyle.ROUNDTABLE,
            "Investigation": InteractionStyle.INVESTIGATION
        }
        interaction_enum = interaction_map.get(interaction_style.split('(')[0].strip(), InteractionStyle.INTERVIEW)

        st.subheader("Character Configuration")
        st.markdown(f"Configure each of your {num_characters} characters below:")

        characters = []
        for i in range(num_characters):
            with st.expander(f"⭐ Character {i+1}", expanded=(i < 2)):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input(
                        "Name",
                        key=f"char_{i}_name",
                        value=f"Speaker {i+1}",
                        help="Character's name"
                    )
                    role = st.selectbox(
                        "Role",
                        ["Host", "Guest", "Expert", "Moderator", "Commentator", "Analyst", "Comedian", "Narrator"],
                        key=f"char_{i}_role",
                        help="Character's role in the conversation"
                    )
                    personality = st.text_input(
                        "Personality",
                        key=f"char_{i}_personality",
                        placeholder="e.g., energetic and curious",
                        help="Key personality traits"
                    )
                with col2:
                    speaking_style = st.text_input(
                        "Speaking Style",
                        key=f"char_{i}_style",
                        placeholder="e.g., uses metaphors, asks probing questions",
                        help="How this character speaks"
                    )
                    energy = st.select_slider(
                        "Energy Level",
                        options=["Low", "Medium", "High"],
                        value="Medium",
                        key=f"char_{i}_energy",
                        help="Character's energy/enthusiasm level"
                    )
                    voice = st.selectbox(
                        "Voice",
                        options=tts_provider.available_voices,
                        key=f"char_{i}_voice",
                        help="TTS voice for this character"
                    )
                    humor = st.selectbox(
                        "Humor Style",
                        ["None", "Dry", "Witty", "Playful"],
                        key=f"char_{i}_humor"
                    )

                characters.append(Character(
                    name=name,
                    role=role,
                    personality=personality or f"{energy} energy {role.lower()}",
                    speaking_style=speaking_style or "clear and engaging",
                    preferred_voice=voice,
                    energy_level=energy.lower(),
                    humor_style=humor.lower() if humor != "None" else None
                ))

        st.info(f"ℹ️ Available voices: {len(tts_provider.available_voices)}. Characters will use assigned voices where possible.")

        if st.button("🎙️ Generate Multi-Character Podcast", type="primary", key="generate_mc"):
            if not mc_topic:
                st.error("Please enter a discussion topic")
            else:
                context = InputContext(
                    mode=GenerationMode.MULTI_CHARACTER,
                    main_topic=mc_topic,
                    characters=characters,
                    interaction_style=interaction_enum,
                    tone=tone,
                    length=length,
                    voice_provider=provider_name
                )

                generate_podcast(context, llm_provider, tts_provider)

    # ===== TAB 4: PERSONA MODE =====
    with tab4:
        st.header("Persona-Driven Podcast")
        st.markdown("Choose a vivid host personality or create your own!")

        # Load created personas
        from core.created_personas import load_created_personas
        created_personas = load_created_personas()

        # Categorize personas (built-in)
        persona_categories = {
            "🎓 Informative & Educational": [
                "documentary_sage", "professor_chaos", "cosmic_philosopher", "science_explainer"
            ],
            "🎉 Entertaining & Energetic": [
                "hype_machine", "late_night_comic", "game_show_host", "tech_enthusiast"
            ],
            "🎬 Dramatic & Atmospheric": [
                "noir_detective", "mystery_narrator", "historical_reenactor"
            ],
            "🎨 Unique & Quirky": [
                "conspiracy_theorist", "grumpy_critic", "meditation_guide", "podcast_bro",
                "hopeful_futurist", "drill_sergeant"
            ]
        }

        # Add created personas category if any exist
        if created_personas:
            persona_categories["💾 Your Created Personas"] = [p.persona_id for p in created_personas]

        # Always add custom creation option
        persona_categories["✨ Create New"] = ["create_your_own"]

        category = st.selectbox("Persona Category", list(persona_categories.keys()))
        persona_keys = persona_categories[category]

        # Build display names
        persona_display_names = {}
        for key in persona_keys:
            if key == "create_your_own":
                persona_display_names[key] = "➕ Create Your Own"
            elif key.startswith("created_") or key.startswith("cloned_"):
                # Created or cloned persona
                cp = next((p for p in created_personas if p.persona_id == key), None)
                if cp:
                    if cp.preferred_tts_voice == "coqui_cloned":
                        persona_display_names[key] = f"🎤 {cp.persona_name} (Voice Cloned)"
                    else:
                        persona_display_names[key] = f"💾 {cp.persona_name} ({cp.voice_archetype})"
            else:
                # Built-in persona
                persona = PERSONA_LIBRARY[key]
                persona_display_names[key] = f"{persona.name} ({persona.archetype})"

        selected_display = st.selectbox(
            "Select Persona",
            options=list(persona_display_names.values())
        )

        # Reverse lookup
        persona_key = [k for k, v in persona_display_names.items() if v == selected_display][0]

        # Check if it's a created persona
        is_created_persona = persona_key.startswith("created_") or persona_key.startswith("cloned_")
        selected_created_persona = None

        if is_created_persona:
            selected_created_persona = next((p for p in created_personas if p.persona_id == persona_key), None)

        # Initialize variables that may be used later
        persona = None
        persona_topic = None
        fun_vs_serious = 0.5
        creation_method = "📤 Upload Audio (Analyze Speaking Style)"  # Default

        # Show persona details or custom creation
        if is_created_persona and selected_created_persona:
            # Display created persona
            is_voice_cloned = selected_created_persona.preferred_tts_voice == "coqui_cloned"

            with st.expander("📖 Created Persona Details", expanded=True):
                if is_voice_cloned:
                    st.info("🎤 **Voice Cloned Persona** - This persona uses voice cloning technology")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{selected_created_persona.persona_name}**")
                    st.markdown(f"*{selected_created_persona.persona_description}*")
                    if not is_voice_cloned:
                        st.markdown(f"- **Energy:** {selected_created_persona.energy.capitalize()}")
                        st.markdown(f"- **Humor:** {selected_created_persona.humor_level.capitalize()}")
                        st.markdown(f"- **Pacing:** {selected_created_persona.pacing.capitalize()}")
                with col2:
                    if not is_voice_cloned:
                        st.markdown(f"- **Tone:** {selected_created_persona.tone.capitalize()}")
                        st.markdown(f"- **Archetype:** {selected_created_persona.voice_archetype}")
                    st.markdown(f"- **TTS Voice:** {'Voice Cloned' if is_voice_cloned else selected_created_persona.preferred_tts_voice}")
                    st.caption(f"📅 Created: {selected_created_persona.created_at[:10]}")

                # Delete option
                if st.button("🗑️ Delete This Persona", use_container_width=True):
                    from core.created_personas import delete_created_persona
                    if delete_created_persona(persona_key):
                        st.success("Persona deleted! Refresh page to update list.")
                        st.rerun()

            persona_topic = st.text_input(
                "Podcast Topic *",
                placeholder="e.g., The History of Space Exploration",
                key="persona_topic"
            )

            fun_vs_serious = 0.5  # Default for created personas

            # Convert created persona to Persona object for compatibility
            persona = create_custom_persona(
                name=selected_created_persona.persona_name,
                description=selected_created_persona.persona_description,
                energy=selected_created_persona.energy,
                humor=selected_created_persona.humor_level,
                pacing=selected_created_persona.pacing,
                tone=selected_created_persona.tone,
                provider_voice_map={provider_name: selected_created_persona.preferred_tts_voice}
            )
            # Attach persona_id for voice cloning detection
            persona.persona_id = selected_created_persona.persona_id

        elif persona_key != "create_your_own":
            # Display built-in persona
            persona = PERSONA_LIBRARY[persona_key]

            with st.expander("📖 Persona Details", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{persona.name}**")
                    st.markdown(f"*{persona.description}*")
                    st.markdown(f"- **Energy:** {persona.energy.capitalize()}")
                    st.markdown(f"- **Humor:** {persona.humor.capitalize()}")
                with col2:
                    st.markdown(f"- **Pacing:** {persona.pacing.capitalize()}")
                    st.markdown(f"- **Tone:** {persona.tone.capitalize()}")
                    if persona.catchphrases:
                        st.markdown(f"- **Catchphrases:** {', '.join(persona.catchphrases[:3])}")

            persona_topic = st.text_input(
                "Podcast Topic *",
                placeholder="e.g., The History of Space Exploration",
                key="persona_topic"
            )

            fun_vs_serious = st.slider(
                "Fun ↔ Serious Balance",
                0.0, 1.0, 0.5,
                help="0 = Maximum fun/entertainment | 1 = Maximum serious/informative"
            )
            if fun_vs_serious < 0.3:
                st.caption("🎉 Optimized for entertainment and engagement")
            elif fun_vs_serious > 0.7:
                st.caption("📚 Optimized for depth and information")
            else:
                st.caption("⚖️ Balanced entertainment and information")

        else:
            # Custom persona creation
            st.subheader("✨ Create Your Custom Persona")

            # Choose creation method
            creation_method = st.radio(
                "How would you like to create the persona?",
                ["📤 Upload Audio (Analyze Speaking Style)", "✍️ Manual Entry"],
                help="Upload audio to analyze speaking style automatically, or manually define traits",
                index=0  # Default to Upload Audio
            )

            if "Upload Audio" in creation_method:
                # Audio-based persona creation with session state
                st.markdown("### 🎙️ Upload Audio Reference")
                st.info("ℹ️ **Creating a Persona:** We'll analyze speaking STYLE (energy, pacing, tone) and map to our voice system. This is NOT voice cloning.")

                # Initialize session state for persona creation
                if 'persona_creation_step' not in st.session_state:
                    st.session_state.persona_creation_step = 'upload'
                if 'persona_analysis_result' not in st.session_state:
                    st.session_state.persona_analysis_result = None
                if 'persona_audio_filename' not in st.session_state:
                    st.session_state.persona_audio_filename = None
                if 'persona_cloned_voice_path' not in st.session_state:
                    st.session_state.persona_cloned_voice_path = None
                if 'persona_voice_cloning_succeeded' not in st.session_state:
                    st.session_state.persona_voice_cloning_succeeded = False

                # Step 1: Upload Audio
                if st.session_state.persona_creation_step == 'upload':
                    audio_file = st.file_uploader(
                        "Upload audio file (10-30 seconds recommended)",
                        type=["mp3", "wav", "m4a", "ogg", "webm"],
                        help="Clear speech, minimal background noise",
                        key="persona_audio_upload"
                    )

                    if audio_file:
                        st.audio(audio_file, format=f'audio/{audio_file.name.split(".")[-1]}')

                        if st.button("🎯 Analyze Audio", type="primary", use_container_width=True):
                            try:
                                # Save temp audio file
                                temp_audio = Path(f"temp_persona_audio.{audio_file.name.split('.')[-1]}")
                                with open(temp_audio, 'wb') as f:
                                    f.write(audio_file.getvalue())

                                # Attempt voice cloning
                                voice_cloning_succeeded = False
                                cloned_voice_path = None

                                try:
                                    with st.spinner("🎤 Attempting voice cloning..."):
                                        from providers.coqui_provider import CoquiTTSProvider
                                        coqui = CoquiTTSProvider()

                                        personas_dir = Path("personas")
                                        personas_dir.mkdir(exist_ok=True)

                                        cloned_voice_filename = f"cloned_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{audio_file.name}"
                                        cloned_voice_path = personas_dir / cloned_voice_filename

                                        import shutil
                                        shutil.copy(temp_audio, cloned_voice_path)

                                        test_audio = personas_dir / f"test_{cloned_voice_filename}"
                                        coqui.set_speaker_voice(cloned_voice_path)
                                        coqui.generate_audio(
                                            text="This is a test of the voice cloning system.",
                                            voice="cloned",
                                            output_path=test_audio,
                                            language="en"
                                        )

                                        voice_cloning_succeeded = True
                                        st.success("✅ Voice cloning successful!")

                                        if test_audio.exists():
                                            test_audio.unlink()

                                except Exception as clone_error:
                                    st.warning(f"⚠️ Voice cloning failed: {str(clone_error)}")
                                    st.info("📊 Falling back to style analysis...")
                                    voice_cloning_succeeded = False

                                # Analyze audio style (if cloning failed or as backup)
                                if not voice_cloning_succeeded:
                                    with st.spinner("🎯 Analyzing speaking style..."):
                                        from core.audio_style_analyzer import analyze_audio_for_persona
                                        style_analysis = analyze_audio_for_persona(temp_audio)
                                    st.session_state.persona_analysis_result = style_analysis
                                else:
                                    st.session_state.persona_analysis_result = None

                                st.session_state.persona_audio_filename = audio_file.name
                                st.session_state.persona_cloned_voice_path = str(cloned_voice_path) if cloned_voice_path else None
                                st.session_state.persona_voice_cloning_succeeded = voice_cloning_succeeded
                                st.session_state.persona_creation_step = 'save'

                                temp_audio.unlink(missing_ok=True)
                                st.rerun()

                            except Exception as e:
                                st.error(f"Error: {e}")
                                import traceback
                                st.code(traceback.format_exc())

                # Step 2: Save Persona
                elif st.session_state.persona_creation_step == 'save':
                    # Show analysis results
                    if st.session_state.persona_voice_cloning_succeeded:
                        st.success("✅ Voice cloning successful!")
                        st.info("🎤 This persona will use your cloned voice for audio generation")
                    else:
                        st.success("✅ Style analysis complete!")
                        style_analysis = st.session_state.persona_analysis_result

                        st.subheader("🎨 Detected Style Traits")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Energy", style_analysis.get('energy', 'medium').title())
                            st.metric("Pacing", style_analysis.get('pacing', 'moderate').title())
                        with col2:
                            st.metric("Humor", style_analysis.get('humor_level', 'subtle').title())
                            st.metric("Tone", style_analysis.get('tone', 'professional').title())
                        with col3:
                            st.metric("Intensity", style_analysis.get('intensity', 'moderate').title())
                            st.metric("Style", style_analysis.get('conversational_style', 'conversational').title())

                        st.info(f"📋 **Style Summary:** {style_analysis.get('style_summary', 'N/A')}")
                        st.info(f"🎭 **Recommended Archetype:** {style_analysis.get('recommended_archetype', 'warm_educator')}")
                        st.info(f"🎙️ **Recommended TTS Voice:** {style_analysis.get('recommended_tts_voice', 'nova')}")

                    # Save form
                    st.subheader("💾 Save as Reusable Persona")

                    if st.session_state.persona_voice_cloning_succeeded:
                        default_description = f"Voice-cloned persona from {st.session_state.persona_audio_filename}"
                    else:
                        default_description = st.session_state.persona_analysis_result.get('style_summary', '')

                    persona_name = st.text_input(
                        "Persona Name *",
                        value=f"Custom Persona {datetime.now().strftime('%m/%d')}",
                        help="Give this persona a memorable name",
                        key="persona_name_input"
                    )

                    persona_description = st.text_area(
                        "Description (optional)",
                        value=default_description,
                        help="Describe this persona's speaking style",
                        key="persona_desc_input"
                    )

                    col_save, col_cancel = st.columns([1, 1])

                    with col_save:
                        if st.button("💾 Save Persona", type="primary", use_container_width=True, key="save_persona_btn"):
                            if not persona_name or len(persona_name.strip()) < 2:
                                st.error("Please enter a persona name (at least 2 characters)")
                            else:
                                try:
                                    from core.created_personas import create_persona_from_analysis, save_created_persona, create_persona_from_voice_clone

                                    # Create persona
                                    if st.session_state.persona_voice_cloning_succeeded:
                                        persona = create_persona_from_voice_clone(
                                            persona_name=persona_name.strip(),
                                            cloned_voice_path=st.session_state.persona_cloned_voice_path,
                                            description=persona_description.strip() if persona_description else "",
                                            user="default"
                                        )
                                    else:
                                        persona = create_persona_from_analysis(
                                            persona_name=persona_name.strip(),
                                            audio_filename=st.session_state.persona_audio_filename,
                                            style_analysis=st.session_state.persona_analysis_result,
                                            description=persona_description.strip() if persona_description else "",
                                            user="default"
                                        )

                                    # Save
                                    if save_created_persona(persona):
                                        st.success(f"✅ Persona '{persona_name}' saved successfully!")
                                        if st.session_state.persona_voice_cloning_succeeded:
                                            st.info("🎤 Voice cloned persona ready to use!")
                                        st.info("🔄 Refresh the page to see your persona in the dropdown list.")
                                        st.balloons()

                                        # Reset session state
                                        st.session_state.persona_creation_step = 'upload'
                                        st.session_state.persona_analysis_result = None
                                        st.session_state.persona_audio_filename = None
                                        st.session_state.persona_cloned_voice_path = None
                                        st.session_state.persona_voice_cloning_succeeded = False
                                    else:
                                        st.error("Failed to save persona. Please try again.")

                                except Exception as e:
                                    st.error(f"Error saving persona: {e}")
                                    import traceback
                                    st.code(traceback.format_exc())

                    with col_cancel:
                        if st.button("❌ Cancel", use_container_width=True, key="cancel_persona_btn"):
                            # Reset session state
                            st.session_state.persona_creation_step = 'upload'
                            st.session_state.persona_analysis_result = None
                            st.session_state.persona_audio_filename = None
                            st.session_state.persona_cloned_voice_path = None
                            st.session_state.persona_voice_cloning_succeeded = False
                            st.rerun()

            else:
                # Manual persona creation
                st.markdown("### ✍️ Manual Persona Definition")

                custom_name = st.text_input("Persona Name", placeholder="e.g., The Data Detective")
                custom_desc = st.text_area(
                    "Description",
                    placeholder="Describe the personality, background, and approach...",
                    height=100
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    custom_energy = st.select_slider(
                        "Energy",
                        options=["Calm", "Moderate", "Energetic", "Chaotic"],
                        value="Moderate"
                    )
                with col2:
                    custom_humor = st.selectbox(
                        "Humor Style",
                        ["None", "Dry", "Witty", "Playful", "Absurd"]
                    )
                with col3:
                    custom_pacing = st.selectbox(
                        "Pacing",
                        ["Slow", "Moderate", "Fast"]
                    )

                custom_tone = st.selectbox("Tone", list(config.VALID_TONES))

                # Build custom persona
                if custom_name and custom_desc:
                    voice_map = {provider_name: tts_provider.available_voices[0]}
                    persona = create_custom_persona(
                        custom_name, custom_desc,
                        custom_energy.lower(), custom_humor.lower(),
                        custom_pacing.lower(), custom_tone, voice_map
                    )

                    st.success(f"✅ Custom persona '{custom_name}' created!")
                else:
                    persona = None

                persona_topic = st.text_input(
                    "Podcast Topic *",
                    placeholder="e.g., Decoding Cryptocurrency Trends",
                    key="custom_persona_topic"
                )

                fun_vs_serious = 0.5

        # Only show generate button if not in audio creation mode
        if persona_key != "create_your_own" or (persona_key == "create_your_own" and "Manual Entry" in creation_method):
            if st.button("🎙️ Generate Persona Podcast", type="primary", key="generate_persona"):
                if not persona_topic:
                    st.error("Please enter a podcast topic")
                elif persona is None and persona_key == "create_your_own":
                    st.error("Please complete the custom persona fields")
                else:
                    context = InputContext(
                        mode=GenerationMode.PERSONA,
                        main_topic=persona_topic,
                        persona=persona,
                        fun_vs_serious=fun_vs_serious,
                        tone=tone,
                        length=length,
                        voice_provider=provider_name
                    )

                    generate_podcast(context, llm_provider, tts_provider)

    # ===== TAB 5: TEMPLATE MODE =====
    with tab5:
        st.header("Template-Based Podcast")
        st.markdown("Use professional podcast formats and structures")

        # Categorize templates
        template_categories = {
            "📚 Informational": ["solo_explainer", "documentary_exploration", "educational_breakdown"],
            "💬 Conversational": ["interview_style", "roundtable_discussion", "debate_match"],
            "🎭 Entertainment": ["comedy_panel", "character_roleplay", "storytime_adventure"],
            "🔧 Practical": ["how_to_guide", "review_analysis", "investigation_report"],
            "📰 News & Updates": ["news_recap", "daily_briefing", "deep_dive"]
        }

        template_category = st.selectbox("Template Category", list(template_categories.keys()))
        template_keys = template_categories[template_category]

        # Build display names
        template_display_names = {}
        for key in template_keys:
            template = PODCAST_TEMPLATES[key]
            template_display_names[key] = f"{template['name']} - {template['description']}"

        selected_template_display = st.selectbox(
            "Select Template",
            options=list(template_display_names.values())
        )

        # Reverse lookup
        template_key = [k for k, v in template_display_names.items() if v == selected_template_display][0]
        template = PODCAST_TEMPLATES[template_key]

        # Show template details
        with st.expander("📋 Template Structure", expanded=True):
            st.markdown(f"**{template['name']}**")
            st.markdown(f"*{template['description']}*")
            if 'speaker_count' in template:
                st.markdown(f"- **Speakers:** {template['speaker_count']}")
            if 'roles' in template:
                st.markdown(f"- **Roles:** {', '.join(template['roles'])}")
            if 'recommended_tone' in template:
                st.markdown(f"- **Recommended Tone:** {template['recommended_tone']}")
            if 'structure' in template:
                st.markdown(f"- **Structure:** {template['structure']}")

        template_topic = st.text_input(
            "Topic *",
            placeholder="e.g., Modern Urban Planning Challenges",
            key="template_topic"
        )

        if st.button("🎙️ Generate Template Podcast", type="primary", key="generate_template"):
            if not template_topic:
                st.error("Please enter a topic")
            else:
                context = InputContext(
                    mode=GenerationMode.TEMPLATE,
                    main_topic=template_topic,
                    template_key=template_key,
                    tone=template.get('recommended_tone', tone),
                    length=length,
                    voice_provider=provider_name
                )

                generate_podcast(context, llm_provider, tts_provider)


def _handle_persona_creation(audio_path: Path, original_filename: str, clone_voice: bool = True) -> Optional[str]:
    """
    Handle persona creation from uploaded audio.

    Args:
        audio_path: Path to uploaded audio file
        original_filename: Original filename
        clone_voice: If True, attempt voice cloning. If False or if cloning fails, use style analysis.

    Returns persona_id if successful, None otherwise
    """
    from core.audio_style_analyzer import analyze_audio_for_persona
    from core.created_personas import create_persona_from_analysis, save_created_persona, create_persona_from_voice_clone

    try:
        voice_cloning_succeeded = False
        cloned_voice_path = None
        style_analysis = None

        # Step 1: Attempt voice cloning if requested
        if clone_voice:
            try:
                with st.spinner("🎤 Attempting voice cloning..."):
                    from providers.coqui_provider import CoquiTTSProvider

                    # Initialize Coqui provider
                    coqui = CoquiTTSProvider()

                    # Create personas directory if needed
                    personas_dir = Path("personas")
                    personas_dir.mkdir(exist_ok=True)

                    # Save cloned voice reference
                    cloned_voice_filename = f"cloned_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{original_filename}"
                    cloned_voice_path = personas_dir / cloned_voice_filename

                    # Copy audio to personas directory
                    import shutil
                    shutil.copy(audio_path, cloned_voice_path)

                    # Test voice cloning to verify it works
                    test_audio = personas_dir / f"test_{cloned_voice_filename}"

                    # Set the speaker voice for cloning
                    coqui.set_speaker_voice(cloned_voice_path)

                    # Generate test audio
                    coqui.generate_audio(
                        text="This is a test of the voice cloning system.",
                        voice="cloned",  # Ignored by Coqui, uses speaker_wav
                        output_path=test_audio,
                        language="en"
                    )

                    # If we got here, cloning succeeded
                    voice_cloning_succeeded = True
                    st.success("✅ Voice cloning successful!")
                    st.info("🎙️ This persona will use your cloned voice for audio generation")

                    # Clean up test audio
                    if test_audio.exists():
                        test_audio.unlink()

            except Exception as clone_error:
                st.warning(f"⚠️ Voice cloning failed: {str(clone_error)}")
                st.info("📊 Falling back to style analysis method...")
                voice_cloning_succeeded = False

        # Step 2: If voice cloning failed or not requested, use style analysis
        if not voice_cloning_succeeded:
            with st.spinner("🎯 Analyzing speaking style..."):
                style_analysis = analyze_audio_for_persona(audio_path)

            st.success("✅ Style analysis complete!")

            # Show preview of detected traits
            st.subheader("🎨 Detected Style Traits")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Energy", style_analysis.get('energy', 'medium').title())
                st.metric("Pacing", style_analysis.get('pacing', 'moderate').title())
            with col2:
                st.metric("Humor", style_analysis.get('humor_level', 'subtle').title())
                st.metric("Tone", style_analysis.get('tone', 'professional').title())
            with col3:
                st.metric("Intensity", style_analysis.get('intensity', 'moderate').title())
                st.metric("Style", style_analysis.get('conversational_style', 'conversational').title())

            st.info(f"📋 **Style Summary:** {style_analysis.get('style_summary', 'N/A')}")
            st.info(f"🎭 **Recommended Archetype:** {style_analysis.get('recommended_archetype', 'warm_educator')}")
            st.info(f"🎙️ **Recommended TTS Voice:** {style_analysis.get('recommended_tts_voice', 'nova')}")

        # Step 3: Let user name and save the persona
        st.subheader("💾 Save as Reusable Persona")

        persona_name = st.text_input(
            "Persona Name *",
            value=f"Custom Persona {datetime.now().strftime('%m/%d')}",
            help="Give this persona a memorable name"
        )

        if voice_cloning_succeeded:
            default_description = f"Voice-cloned persona from {original_filename}"
        else:
            default_description = style_analysis.get('style_summary', '') if style_analysis else ''

        persona_description = st.text_area(
            "Description (optional)",
            value=default_description,
            help="Describe this persona's speaking style"
        )

        col_save, col_cancel = st.columns([1, 1])

        with col_save:
            if st.button("💾 Save Persona", type="primary", use_container_width=True):
                if not persona_name or len(persona_name.strip()) < 2:
                    st.error("Please enter a persona name (at least 2 characters)")
                    return None

                # Create persona object based on method used
                if voice_cloning_succeeded:
                    persona = create_persona_from_voice_clone(
                        persona_name=persona_name.strip(),
                        cloned_voice_path=str(cloned_voice_path),
                        description=persona_description.strip() if persona_description else "",
                        user="default"
                    )
                else:
                    persona = create_persona_from_analysis(
                        persona_name=persona_name.strip(),
                        audio_filename=original_filename,
                        style_analysis=style_analysis,
                        description=persona_description.strip() if persona_description else "",
                        user="default"
                    )

                # Save to storage
                if save_created_persona(persona):
                    st.success(f"✅ Persona '{persona_name}' saved successfully!")
                    if voice_cloning_succeeded:
                        st.info(f"🎤 Voice cloned persona ready to use!")
                    st.info(f"🎯 You can now use this persona in **Persona Mode** or **Multi-Character Mode**")
                    st.balloons()
                    return persona.persona_id
                else:
                    st.error("Failed to save persona. Please try again.")
                    return None

        with col_cancel:
            if st.button("❌ Cancel", use_container_width=True):
                st.warning("Persona creation cancelled")
                return None

        return None

    except Exception as e:
        st.error(f"❌ Persona creation failed: {str(e)}")
        import traceback
        with st.expander("🐛 Error Details"):
            st.code(traceback.format_exc())
        return None


def generate_podcast(context: InputContext, llm_provider, tts_provider):
    """Generate podcast using unified pipeline"""
    output_root = Path(config.OUTPUT_ROOT)

    with st.spinner(f"🎬 Generating {context.mode.value} podcast..."):
        try:
            # Create pipeline
            pipeline = UnifiedGenerationPipeline(llm_provider, tts_provider)

            # Generate
            result = pipeline.generate(context, output_root)

            # Display success
            st.success("✅ Podcast generated successfully!")

            # Display outputs
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📝 Script")
                st.text_area("", result.script, height=300, key=f"script_{result.episode_id}")

            with col2:
                st.subheader("📋 Show Notes")
                st.text_area("", result.show_notes, height=300, key=f"notes_{result.episode_id}")

            # Audio player
            st.subheader("🎧 Audio")
            st.audio(result.audio_path)

            # Episode info
            with st.expander("ℹ️ Episode Details"):
                st.json(result.to_dict())

            st.info(f"💾 Episode saved to: `{result.episode_dir}`")

        except Exception as e:
            st.error(f"❌ Generation failed: {str(e)}")
            import traceback
            with st.expander("🐛 Error Details"):
                st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
