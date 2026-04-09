"""
Step 44: Web UI (Streamlit) - REFACTORED

6-mode interactive web interface for podcast creation with:
- Topic Mode (enhanced with 4 fields)
- Text Mode (long-form support)
- Source Material Mode (file upload + configuration)
- Multi-Character Mode (2-5 characters with rich profiles)
- Persona Mode (15+ personas + custom creation)
- Template Mode (10+ templates)

To run:
    streamlit run step44_web_ui_refactored.py

Then open browser to http://localhost:8501
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import json

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.unified_generation import UnifiedGenerationPipeline
from core.input_models import InputContext, GenerationMode, Character, InteractionStyle, DepthPreference
from step32_voice_persona_system import PERSONA_LIBRARY, create_custom_persona
from step27_podcast_templates import PODCAST_TEMPLATES
from core.voice_assignment import assign_voices_smart
import config


# Page config
st.set_page_config(
    page_title="AI Podcast Creator - Enhanced",
    page_icon="🎙️",
    layout="wide"
)


def main():
    st.title("🎙️ AI Podcast Creator - Enhanced Edition")
    st.markdown("**6 Generation Modes** | Professional AI-powered podcast production from idea to audio")

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
            help="Overall podcast tone (can be overridden per mode)"
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

    # Main content area - 6 Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Topic",
        "📄 Text",
        "📚 Source Material",
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

        if st.button("🎙️ Generate Topic Podcast", type="primary"):
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

    # ===== TAB 2: TEXT MODE =====
    with tab2:
        st.header("Text-Based Podcast")
        st.markdown("Transform your written content into an engaging audio podcast")

        text_content = st.text_area(
            "Your Text Content *",
            height=400,
            placeholder="Paste your article, blog post, notes, or any text content here.\n\nThis can be:\n- Research findings\n- Meeting notes\n- Article drafts\n- Book excerpts\n- Documentation\n- Presentation scripts\n\nWe'll preserve your key points and structure while making it engaging for audio.",
            help="Paste long-form text content"
        )

        if text_content:
            st.caption(f"📊 Character count: {len(text_content):,} | Word count: ~{len(text_content.split()):,}")

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
                help="Insert additional insights and explanations between sections"
            )

        if st.button("🎙️ Generate Text Podcast", type="primary"):
            if not text_content or len(text_content) < 100:
                st.error("Please provide at least 100 characters of text content")
            else:
                context = InputContext(
                    mode=GenerationMode.TEXT,
                    text_content=text_content,
                    preserve_structure=preserve_structure,
                    add_commentary=add_commentary,
                    tone=tone,
                    length=length,
                    voice_provider=provider_name
                )

                generate_podcast(context, llm_provider, tts_provider)

    # ===== TAB 3: SOURCE MATERIAL MODE =====
    with tab3:
        st.header("Source Material Podcast")
        st.markdown("Upload or paste source material for in-depth, audience-tailored coverage")

        # File upload
        uploaded_files = st.file_uploader(
            "Upload Source Files (optional)",
            type=["txt", "md"],
            accept_multiple_files=True,
            help="Upload text or markdown files as source material"
        )

        # Or paste directly
        source_material = st.text_area(
            "Or Paste Source Material Directly",
            height=300,
            placeholder="Paste research papers, articles, notes, documentation, or any reference material...",
            help="Direct text input alternative to file upload"
        )

        # Combine uploaded files
        combined_source = source_material
        if uploaded_files:
            for file in uploaded_files:
                content = file.read().decode('utf-8')
                combined_source += f"\n\n--- Source: {file.name} ---\n{content}"

        source_title = st.text_input(
            "Source Title (optional)",
            placeholder="e.g., Q3 2026 Financial Report",
            help="Give your source material a title for reference"
        )

        col1, col2 = st.columns(2)
        with col1:
            emphasis = st.text_area(
                "Emphasis Instructions (optional)",
                height=100,
                placeholder="What should we emphasize or focus on?\n\nE.g., 'Focus on actionable insights for small businesses' or 'Emphasize the technical breakthroughs'",
                help="Guide what aspects to highlight"
            )
        with col2:
            target_audience = st.selectbox(
                "Target Audience",
                ["General Audience", "Technical Experts", "Business Leaders", "Students", "Enthusiasts", "Policymakers"],
                help="Tailor complexity and examples to audience"
            )

        depth = st.radio(
            "Coverage Depth",
            ["Summary (high-level overview)", "Deep Dive (comprehensive analysis)"],
            horizontal=True,
            help="Summary = key highlights, Deep Dive = thorough exploration"
        )
        depth_pref = DepthPreference.DEEP_DIVE if "Deep Dive" in depth else DepthPreference.SUMMARY

        if st.button("🎙️ Generate Source-Based Podcast", type="primary"):
            if not combined_source or len(combined_source) < 100:
                st.error("Please provide source material (upload files or paste text)")
            else:
                context = InputContext(
                    mode=GenerationMode.SOURCE,
                    source_material=combined_source,
                    source_title=source_title,
                    emphasis_instructions=emphasis,
                    target_audience=target_audience,
                    depth_preference=depth_pref,
                    tone=tone,
                    length=length,
                    voice_provider=provider_name
                )

                generate_podcast(context, llm_provider, tts_provider)

    # ===== TAB 4: MULTI-CHARACTER MODE =====
    with tab4:
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

        st.info(f"ℹ️ Available voices: {len(tts_provider.available_voices)}. If you have more characters than voices, some will share voices.")

        if st.button("🎙️ Generate Multi-Character Podcast", type="primary"):
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

    # ===== TAB 5: PERSONA MODE =====
    with tab5:
        st.header("Persona-Driven Podcast")
        st.markdown("Choose a vivid host personality or create your own!")

        # Categorize personas
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
            ],
            "✨ Custom": ["create_your_own"]
        }

        category = st.selectbox("Persona Category", list(persona_categories.keys()))
        persona_keys = persona_categories[category]

        # Build display names
        persona_display_names = {}
        for key in persona_keys:
            if key == "create_your_own":
                persona_display_names[key] = "➕ Create Your Own"
            else:
                persona = PERSONA_LIBRARY[key]
                persona_display_names[key] = f"{persona.name} ({persona.archetype})"

        selected_display = st.selectbox(
            "Select Persona",
            options=list(persona_display_names.values())
        )

        # Reverse lookup
        persona_key = [k for k, v in persona_display_names.items() if v == selected_display][0]

        # Show persona details or custom creation
        if persona_key != "create_your_own":
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

        if st.button("🎙️ Generate Persona Podcast", type="primary"):
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

    # ===== TAB 6: TEMPLATE MODE =====
    with tab6:
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

        if st.button("🎙️ Generate Template Podcast", type="primary"):
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
