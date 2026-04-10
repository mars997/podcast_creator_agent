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

    # Show Python environment info in sidebar expander for debugging
    import sys as _sys
    _python_exe = _sys.executable

    # Fetch ElevenLabs voices once per session and cache in session_state
    if "el_voices_loaded" not in st.session_state:
        _vlist, _verr = _fetch_elevenlabs_voices()
        st.session_state["_el_voices"] = _vlist
        st.session_state["_el_voices_error"] = _verr
        st.session_state["el_voices_loaded"] = True

    _SESSION_EL_VOICES = st.session_state.get("_el_voices", [])

    # Sidebar - Global Configuration
    with st.sidebar:
        st.header("⚙️ Global Settings")
        with st.expander("🐍 Python Environment", expanded=False):
            st.code(_python_exe, language=None)
            try:
                import elevenlabs as _el_mod
                st.success(f"elevenlabs {_el_mod.__version__} ✓")
            except ImportError:
                st.error("elevenlabs NOT installed in this Python")

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

        # ===== SECTION D: SELECT PERSONA =====
        st.subheader("🎙️ Section D: Select Persona (Optional)")
        st.caption("Apply a voice persona to narrate the generated podcast")

        # Build persona options from ElevenLabs voices + created personas
        from core.created_personas import load_created_personas as _load_created_personas
        _src_el_voices = _SESSION_EL_VOICES
        _src_created_personas = _load_created_personas()

        _src_persona_options = {"— None (default voice) —": None}

        for _v in _src_el_voices:
            _badge = "🎙️" if _v["category"] == "cloned" else "🔊"
            _label = f"{_badge} {_v['name']} ({_v['category']})"
            _src_persona_options[_label] = ("el", _v["id"], _v)

        for _cp in _src_created_personas:
            _OPENAI_VOICES = {"alloy", "echo", "fable", "onyx", "nova", "shimmer", "coqui_cloned"}
            _is_el = _cp.preferred_tts_voice and _cp.preferred_tts_voice not in _OPENAI_VOICES
            _badge = "🎤" if _is_el else "💾"
            _label = f"{_badge} {_cp.persona_name} (created)"
            _src_persona_options[_label] = ("created", _cp.persona_id, _cp)

        _src_selected_label = st.selectbox(
            "Persona / Voice",
            options=list(_src_persona_options.keys()),
            key="source_persona_select"
        )
        _src_selected = _src_persona_options[_src_selected_label]

        # Show brief details for the selected persona
        if _src_selected:
            _src_kind, _src_id, _src_data = _src_selected
            if _src_kind == "el":
                with st.expander("Voice details", expanded=False):
                    st.markdown(f"**{_src_data['name']}** — {_src_data['category']}")
                    if _src_data.get("description"):
                        st.caption(_src_data["description"])
            elif _src_kind == "created":
                with st.expander("Persona details", expanded=False):
                    st.markdown(f"**{_src_data.persona_name}** — {_src_data.voice_archetype}")
                    st.caption(_src_data.persona_description)

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

            # Resolve persona voice from Section D selection
            matched_voice = None
            if _src_selected:
                _gen_kind, _gen_id, _gen_data = _src_selected
                if _gen_kind == "el":
                    matched_voice = _gen_id
                elif _gen_kind == "created":
                    _OPENAI_SET = {"alloy", "echo", "fable", "onyx", "nova", "shimmer", "coqui_cloned"}
                    _v = _gen_data.preferred_tts_voice
                    if _v and _v not in _OPENAI_SET:
                        matched_voice = _v  # ElevenLabs voice_id from created persona

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
                    voice_provider=provider_name,
                    preferred_voice=matched_voice,
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

        # Use ElevenLabs voices fetched once at startup
        el_voices = _SESSION_EL_VOICES
        _el_fetch_error = st.session_state.get("_el_voices_error", "")
        if _el_fetch_error:
            st.warning(f"ElevenLabs voices unavailable: {_el_fetch_error}")

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

        # Add ElevenLabs voices category
        if el_voices:
            persona_categories["🎤 ElevenLabs Voices"] = [f"el__{v['id']}" for v in el_voices]

        # Add created personas category if any exist
        if created_personas:
            persona_categories["💾 Your Created Personas"] = [p.persona_id for p in created_personas]

        # Always add custom creation option
        persona_categories["✨ Create New"] = ["create_your_own"]

        category = st.selectbox("Persona Category", list(persona_categories.keys()))
        persona_keys = persona_categories[category]

        # Build display names
        persona_display_names = {}
        # Build a quick lookup for ElevenLabs voices by id
        el_voice_lookup = {v["id"]: v for v in el_voices}
        for key in persona_keys:
            if key == "create_your_own":
                persona_display_names[key] = "➕ Create Your Own"
            elif key.startswith("el__"):
                # ElevenLabs account voice
                voice_id = key[4:]
                v = el_voice_lookup.get(voice_id, {})
                name = v.get("name", voice_id)
                category = v.get("category", "premade")
                badge = "🎙️" if category == "cloned" else "🔊"
                persona_display_names[key] = f"{badge} {name} ({category})"
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

        # Check what type of persona is selected
        is_el_voice = persona_key.startswith("el__")
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
        if is_el_voice:
            # ElevenLabs account voice selected
            voice_id = persona_key[4:]
            v_info = el_voice_lookup.get(voice_id, {})
            with st.expander("🎙️ ElevenLabs Voice Details", expanded=True):
                st.success(f"**{v_info.get('name', voice_id)}** — will use this voice for audio generation")
                st.markdown(f"- **Category:** {v_info.get('category', 'premade')}")
                if v_info.get("description"):
                    st.markdown(f"- **Description:** {v_info['description']}")

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

        elif is_created_persona and selected_created_persona:
            # Display created persona — detect ElevenLabs clones too
            _STANDARD_VOICES = {"alloy", "echo", "fable", "onyx", "nova", "shimmer", "coqui_cloned", ""}
            is_voice_cloned = (selected_created_persona.preferred_tts_voice not in _STANDARD_VOICES
                               and selected_created_persona.preferred_tts_voice is not None)

            with st.expander("📖 Created Persona Details", expanded=True):
                if is_voice_cloned:
                    voice_id = selected_created_persona.preferred_tts_voice
                    voice_status = _check_elevenlabs_voice_status(voice_id)

                    if voice_status == "ready":
                        st.success("🎤 **Voice Cloned Persona** — voice is active and will be used for generation!")
                    elif voice_status == "blocked":
                        st.error("🚫 **ElevenLabs rejected this voice sample** (`detected_captcha_voice`)")
                        st.markdown(
                            "ElevenLabs' AI detected the uploaded audio as a synthetic or heavily-processed voice "
                            "and will not clone it. This is a platform-level content policy.\n\n"
                            "**To fix:** delete this persona and re-upload a **plain voice recording** — "
                            "just you talking naturally, no music, no effects, no auto-tune, quiet room.\n\n"
                            "**Until then:** podcasts will still generate using OpenAI **nova** voice as fallback."
                        )
                    else:
                        st.warning("🎤 Voice Cloned Persona — could not check voice status.")

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
                    st.markdown(f"- **TTS Voice:** {'Voice Cloned (ElevenLabs)' if is_voice_cloned else selected_created_persona.preferred_tts_voice}")
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
                import os as _persona_os
                if _persona_os.getenv("ELEVENLABS_API_KEY"):
                    st.info("🎤 **Creating a Persona with Voice Cloning:** Your voice will be cloned via ElevenLabs and saved as a reusable persona.")
                else:
                    st.info("ℹ️ **Creating a Persona:** We'll analyze speaking STYLE (energy, pacing, tone) and map to our voice system. Add `ELEVENLABS_API_KEY` to enable real voice cloning.")

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

                                # Attempt voice cloning via ElevenLabs (if key available)
                                voice_cloning_succeeded = False
                                cloned_voice_path = None
                                import os as _os2

                                if _os2.getenv("ELEVENLABS_API_KEY"):
                                    try:
                                        with st.spinner("🎤 Preprocessing and cloning voice..."):
                                            from providers.elevenlabs_provider import ElevenLabsTTSProvider
                                            el = ElevenLabsTTSProvider()
                                            try:
                                                cleaned = _preprocess_audio_for_cloning(temp_audio)
                                            except Exception:
                                                cleaned = temp_audio
                                            voice_id = el.clone_voice(
                                                audio_path=cleaned,
                                                name=f"Persona — {audio_file.name}",
                                            )
                                            if cleaned != temp_audio and cleaned.exists():
                                                cleaned.unlink(missing_ok=True)
                                            # Store the ElevenLabs voice_id as the "path" for downstream use
                                            cloned_voice_path = voice_id
                                            voice_cloning_succeeded = True
                                            st.success("✅ Voice cloned via ElevenLabs!")
                                    except Exception as clone_error:
                                        st.warning(f"⚠️ Voice cloning failed: {str(clone_error)}")
                                        st.info("📊 Falling back to style analysis...")
                                else:
                                    st.info("📊 No ElevenLabs key — analyzing speaking style instead.")

                                # Style analysis (always run as backup/supplement)
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
                    # Determine voice_id and persona for generation
                    OPENAI_VOICES = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}
                    cloned_voice_id = None

                    if is_el_voice:
                        # ElevenLabs account voice — extract voice_id and build a neutral persona
                        cloned_voice_id = persona_key[4:]
                        v_info = el_voice_lookup.get(cloned_voice_id, {})
                        voice_name = v_info.get("name", cloned_voice_id)
                        persona = create_custom_persona(
                            name=voice_name,
                            description=f"Podcast narrated by {voice_name}",
                            energy="medium",
                            humor="none",
                            pacing="moderate",
                            tone="neutral",
                            provider_voice_map={provider_name: "nova"}
                        )
                    elif is_created_persona and selected_created_persona:
                        v = selected_created_persona.preferred_tts_voice
                        if v and v not in OPENAI_VOICES and v != "coqui_cloned":
                            cloned_voice_id = v  # ElevenLabs voice_id

                    context = InputContext(
                        mode=GenerationMode.PERSONA,
                        main_topic=persona_topic,
                        persona=persona,
                        fun_vs_serious=fun_vs_serious,
                        tone=tone,
                        length=length,
                        voice_provider=provider_name,
                        preferred_voice=cloned_voice_id,
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


def _preprocess_audio_for_cloning(input_path: Path) -> Path:
    """
    Clean up audio before sending to ElevenLabs to avoid detection rejections.
    - Convert to mono WAV at 22050 Hz
    - Normalize volume to -3 dBFS
    - Strip metadata / unusual encodings
    Returns path to cleaned WAV (temp file).
    """
    from pydub import AudioSegment
    from pydub.effects import normalize
    import tempfile

    audio = AudioSegment.from_file(str(input_path))

    # Convert to mono, resample to 22050 Hz (ElevenLabs prefers this)
    audio = audio.set_channels(1).set_frame_rate(22050).set_sample_width(2)

    # Normalize to -3 dBFS
    audio = normalize(audio, headroom=3.0)

    out_path = Path(tempfile.mktemp(suffix="_clean.wav"))
    audio.export(str(out_path), format="wav")
    return out_path


@st.cache_data(ttl=60)
def _check_elevenlabs_voice_status(voice_id: str) -> str:
    """
    Returns 'ready', 'blocked', or 'error'.
    Cached for 60 seconds so selecting the persona doesn't hammer the API.
    """
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return "error"
    try:
        import tempfile
        from pathlib import Path as _Path
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=api_key)
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text="test",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        out = _Path(tempfile.mktemp(suffix=".mp3"))
        with open(out, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
        out.unlink(missing_ok=True)
        return "ready"
    except Exception as e:
        if "voice_access_denied" in str(e) or "authorization_error" in str(e):
            return "blocked"
        return "error"


def _fetch_elevenlabs_voices():
    """Fetch all voices from ElevenLabs account via REST API. Returns (list, error_str_or_None)."""
    import os as _os
    import requests as _requests
    from dotenv import load_dotenv
    load_dotenv()
    api_key = _os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return [], "ELEVENLABS_API_KEY not set"
    try:
        resp = _requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        voices = data.get("voices", [])
        return [
            {
                "id": v["voice_id"],
                "name": v["name"],
                "category": v.get("category", "premade") or "premade",
                "description": v.get("description", "") or "",
            }
            for v in voices
        ], None
    except Exception as _e:
        return [], str(_e)


def _clone_voice_elevenlabs(audio_path: Path, original_filename: str, current_tts_provider):
    """
    Clone voice via ElevenLabs, save as a CreatedPersona, and return
    (voice_id, tts_provider_to_use).

    If the ElevenLabs key has TTS permission → returns (voice_id, ElevenLabsTTSProvider).
    If only clone permission (no TTS) → saves persona but returns (None, current_tts_provider)
    so caller can fall back to style-matched OpenAI voice.
    """
    from providers.elevenlabs_provider import ElevenLabsTTSProvider
    from core.created_personas import CreatedPersona, save_created_persona
    import uuid
    from datetime import datetime
    import tempfile

    try:
        el_provider = ElevenLabsTTSProvider()

        # Preprocess audio to maximise ElevenLabs acceptance rate
        try:
            cleaned_path = _preprocess_audio_for_cloning(audio_path)
            clone_source = cleaned_path
            print(f"[INFO] Audio preprocessed for cloning: {cleaned_path}")
        except Exception as prep_err:
            print(f"[WARNING] Audio preprocessing failed ({prep_err}), using original.")
            clone_source = audio_path
            cleaned_path = None

        persona_name = f"Cloned — {original_filename}"
        voice_id = el_provider.clone_voice(
            audio_path=clone_source,
            name=persona_name,
            description=f"Voice cloned from uploaded file: {original_filename}",
        )

        if cleaned_path and cleaned_path.exists():
            cleaned_path.unlink(missing_ok=True)

        # Test that TTS actually works with this key before committing to ElevenLabs TTS
        tts_works = False
        try:
            test_out = Path(tempfile.mktemp(suffix=".mp3"))
            el_provider.generate_audio("test", voice_id, test_out)
            if test_out.exists():
                test_out.unlink()
            tts_works = True
        except Exception as tts_err:
            print(f"[WARNING] ElevenLabs TTS permission check failed: {tts_err}")

        # Save as a CreatedPersona so it appears in Persona Mode
        now = datetime.now().isoformat()
        persona = CreatedPersona(
            persona_id=f"cloned_{uuid.uuid4().hex[:8]}",
            persona_name=persona_name,
            persona_description=f"ElevenLabs voice clone from {original_filename}",
            reference_audio_filename=original_filename,
            voice_archetype="cloned_voice",
            preferred_tts_voice=voice_id,
            energy="medium",
            pacing="moderate",
            humor_level="subtle",
            tone="warm",
            intensity="moderate",
            conversational_style="conversational",
            style_notes=f"Voice cloned via ElevenLabs from {original_filename}",
            system_prompt_guidance="Speak in a natural, engaging conversational tone.",
            created_by_user="default",
            created_at=now,
            last_modified=now,
        )
        save_created_persona(persona)

        if tts_works:
            return voice_id, el_provider
        else:
            # Clone saved but TTS blocked — signal caller with a special sentinel
            return f"__no_tts__{voice_id}", current_tts_provider

    except Exception as e:
        print(f"[ERROR] ElevenLabs voice cloning failed: {e}")
        return None, current_tts_provider


def _match_style_to_tts_voice(style: dict, available_voices: list) -> str:
    """
    Map analyzed audio style traits to the closest available TTS voice.

    OpenAI voice personality guide:
      alloy   - balanced, neutral, versatile
      echo    - clear, deliberate, moderate energy
      fable   - expressive, warm, storytelling
      onyx    - deep, authoritative, calm/professional
      nova    - warm, friendly, moderate energy (good default)
      shimmer - soft, gentle, low energy
    """
    energy = style.get("energy", "medium")
    pacing = style.get("pacing", "moderate")
    humor = style.get("humor", "subtle")
    tone_trait = style.get("tone", "warm")

    # Priority rules (most specific first)
    if energy in ("high", "extreme") and humor in ("moderate", "high"):
        candidate = "fable"
    elif energy in ("high", "extreme") and pacing in ("fast", "rapid"):
        candidate = "alloy"
    elif energy in ("low",) or pacing in ("slow",):
        candidate = "shimmer"
    elif tone_trait in ("cool", "sharp") or energy == "low":
        candidate = "onyx"
    elif tone_trait == "warm" and humor in ("none", "subtle"):
        candidate = "nova"
    else:
        candidate = "echo"

    # Fall back to first available if candidate not in provider's list
    return candidate if candidate in available_voices else (available_voices[0] if available_voices else "nova")


def generate_podcast(context: InputContext, llm_provider, tts_provider):
    """Generate podcast using unified pipeline"""
    output_root = Path(config.OUTPUT_ROOT)

    with st.spinner(f"🎬 Generating {context.mode.value} podcast..."):
        try:
            st.caption(f"Debug — mode: {context.mode.value} | persona: {getattr(context.persona, 'name', None)} | preferred_voice: {str(context.preferred_voice)[:20] if context.preferred_voice else None}")

            # Create pipeline
            pipeline = UnifiedGenerationPipeline(llm_provider, tts_provider)

            # Generate
            result = pipeline.generate(context, output_root)

            # Display success
            st.success("✅ Podcast generated successfully!")

            # Voice status — shown prominently before anything else
            _actual_voice = result.metadata.get("actual_voice_used", "")
            _fallback_reason = result.metadata.get("voice_fallback_reason", "")
            if _fallback_reason:
                st.warning(
                    f"**Voice fallback triggered** — ElevenLabs rejected the voice. Audio used OpenAI **nova** instead.\n\n"
                    f"**Reason:** `{_fallback_reason}`"
                )
            elif _actual_voice:
                if "fallback" in _actual_voice:
                    st.warning(f"Voice fallback: {_actual_voice}")
                else:
                    st.success(f"**Voice applied:** `{_actual_voice}`")

            # Audio player — right after voice status
            st.subheader("🎧 Audio")
            st.audio(result.audio_path)

            # Display outputs
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📝 Script")
                st.text_area("", result.script, height=300, key=f"script_{result.episode_id}")

            with col2:
                st.subheader("📋 Show Notes")
                st.text_area("", result.show_notes, height=300, key=f"notes_{result.episode_id}")

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
