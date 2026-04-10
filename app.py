"""
AI Podcast Creator - Main Web Application

A streamlined, production-ready web UI for creating AI-powered podcasts.

Features:
- Simple podcast creation from topics, text, URLs, or files
- Voice persona selection with ElevenLabs integration
- Multi-character podcast generation
- Episode history and management
- Real-time progress tracking

To run:
    streamlit run app.py
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import json
import os

# Core imports
from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.unified_generation import UnifiedGenerationPipeline
from core.input_models import InputContext, GenerationMode, Character, InteractionStyle
from core.source_management import (
    extract_text_from_file,
    fetch_article_text,
    fetch_youtube_transcript,
)
from core.episode_management import load_episode_index
import config

# Configure page
st.set_page_config(
    page_title="AI Podcast Creator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .episode-card {
        padding: 1.5rem;
        border-radius: 12px;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'create'
    if 'source_urls' not in st.session_state:
        st.session_state.source_urls = []
    if 'generation_complete' not in st.session_state:
        st.session_state.generation_complete = False
    if 'last_episode' not in st.session_state:
        st.session_state.last_episode = None


def render_sidebar():
    """Render sidebar with navigation and settings"""
    with st.sidebar:
        st.markdown("## 🎙️ AI Podcast Creator")
        st.markdown("---")

        # Navigation
        st.markdown("### Navigation")
        page = st.radio(
            "Go to:",
            ["🎬 Create Podcast", "📚 Episode History", "⚙️ Settings"],
            label_visibility="collapsed"
        )

        # Map selection to page
        if "Create" in page:
            st.session_state.current_page = 'create'
        elif "History" in page:
            st.session_state.current_page = 'history'
        elif "Settings" in page:
            st.session_state.current_page = 'settings'

        st.markdown("---")

        # Provider selection
        st.markdown("### AI Provider")
        available_providers = detect_available_providers()

        if not available_providers:
            st.error("❌ No API keys configured!")
            st.markdown("Add API keys to `.env`:")
            st.code("OPENAI_API_KEY=sk-...\nELEVENLABS_API_KEY=...", language="bash")
            st.stop()

        provider_name = st.selectbox(
            "Provider",
            options=list(available_providers.keys()),
            help="Choose AI provider for generation",
            label_visibility="collapsed"
        )

        # Store in session state
        st.session_state.provider_name = provider_name

        # Voice settings
        st.markdown("### Voice Settings")

        # Check for ElevenLabs
        has_elevenlabs = os.getenv("ELEVENLABS_API_KEY") is not None

        if has_elevenlabs:
            voice_provider = st.selectbox(
                "Voice Provider",
                ["OpenAI TTS", "ElevenLabs"],
                help="ElevenLabs provides higher quality and custom voices"
            )
            st.session_state.voice_provider = "elevenlabs" if "ElevenLabs" in voice_provider else provider_name
        else:
            st.session_state.voice_provider = provider_name
            st.caption("💡 Add ELEVENLABS_API_KEY for premium voices")

        st.markdown("---")

        # Quick stats
        st.markdown("### Quick Stats")
        try:
            index_file = Path(config.OUTPUT_ROOT) / "episode_index.json"
            if index_file.exists():
                with open(index_file, 'r') as f:
                    episodes = json.load(f)
                st.metric("Total Episodes", len(episodes))
            else:
                st.metric("Total Episodes", 0)
        except:
            st.metric("Total Episodes", "?")

        st.markdown("---")
        st.caption("Made with ❤️ using Claude AI")


def render_create_page():
    """Render the main podcast creation page"""
    st.markdown('<h1 class="main-header">🎙️ Create Your Podcast</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform any content into an engaging AI-powered podcast</p>', unsafe_allow_html=True)

    # Mode selection
    st.markdown("### Choose Your Creation Mode")

    mode_col1, mode_col2, mode_col3 = st.columns(3)

    with mode_col1:
        if st.button("📝 From Topic", use_container_width=True, type="secondary"):
            st.session_state.creation_mode = 'topic'

    with mode_col2:
        if st.button("📚 From Sources", use_container_width=True, type="secondary"):
            st.session_state.creation_mode = 'sources'

    with mode_col3:
        if st.button("👥 Multi-Character", use_container_width=True, type="secondary"):
            st.session_state.creation_mode = 'multichar'

    if 'creation_mode' not in st.session_state:
        st.session_state.creation_mode = 'topic'

    st.markdown("---")

    # Render appropriate creation form
    if st.session_state.creation_mode == 'topic':
        render_topic_mode()
    elif st.session_state.creation_mode == 'sources':
        render_sources_mode()
    elif st.session_state.creation_mode == 'multichar':
        render_multichar_mode()


def render_topic_mode():
    """Render topic-based podcast creation"""
    st.markdown("### 📝 Topic-Based Podcast")
    st.markdown("Create a podcast from a topic or idea")

    col1, col2 = st.columns([2, 1])

    with col1:
        topic = st.text_input(
            "Podcast Topic",
            placeholder="e.g., The Future of Quantum Computing",
            help="Main topic for your podcast"
        )

        details = st.text_area(
            "Additional Context (optional)",
            height=150,
            placeholder="Provide background, angles, or specific aspects you want covered...",
            help="Add more detail and direction"
        )

    with col2:
        tone = st.selectbox(
            "Tone",
            options=list(config.VALID_TONES),
            index=1,
            help="Overall podcast tone"
        )

        length = st.selectbox(
            "Length",
            options=list(config.VALID_LENGTHS),
            index=1,
            help="Target podcast length"
        )

        fun_slider = st.slider(
            "Style Balance",
            0.0, 1.0, 0.5,
            help="0 = Fun & entertaining, 1 = Serious & informative"
        )

    # Generate button
    st.markdown("---")

    if st.button("🎬 Generate Podcast", type="primary", use_container_width=True):
        if not topic:
            st.error("Please enter a topic")
        else:
            context = InputContext(
                mode=GenerationMode.TOPIC,
                main_topic=topic,
                topic_details=details,
                tone=tone,
                length=length,
                fun_vs_serious=fun_slider,
                voice_provider=st.session_state.voice_provider
            )

            generate_podcast_workflow(context)


def render_sources_mode():
    """Render source-based podcast creation"""
    st.markdown("### 📚 Source-Based Podcast")
    st.markdown("Create a podcast from existing content")

    # Tab-based source input
    source_tab1, source_tab2, source_tab3 = st.tabs(["📝 Paste Text", "📎 Upload Files", "🔗 Add URLs"])

    combined_source = ""

    with source_tab1:
        st.markdown("#### Paste your content directly")
        pasted_text = st.text_area(
            "Content",
            height=400,
            placeholder="Paste articles, notes, transcripts, or any text content here...",
            label_visibility="collapsed"
        )

        if pasted_text:
            st.success(f"✅ {len(pasted_text):,} characters | ~{len(pasted_text.split()):,} words")
            combined_source += f"{pasted_text}\n\n"

    with source_tab2:
        st.markdown("#### Upload documents")
        uploaded_files = st.file_uploader(
            "Files",
            type=["pdf", "txt", "md", "docx", "html"],
            accept_multiple_files=True,
            help="Upload PDF, TXT, MD, DOCX, or HTML files",
            label_visibility="collapsed"
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            for file in uploaded_files:
                st.caption(f"📎 {file.name} ({file.size:,} bytes)")

    with source_tab3:
        st.markdown("#### Add web content or YouTube videos")

        col1, col2 = st.columns([4, 1])
        with col1:
            url_input = st.text_input(
                "URL",
                placeholder="https://example.com/article or youtube.com/watch?v=...",
                label_visibility="collapsed"
            )
        with col2:
            if st.button("➕ Add", use_container_width=True):
                if url_input and url_input not in st.session_state.source_urls:
                    st.session_state.source_urls.append(url_input)
                    st.rerun()

        # Display added URLs
        if st.session_state.source_urls:
            st.markdown("**Added URLs:**")
            for i, url in enumerate(st.session_state.source_urls):
                col1, col2 = st.columns([5, 1])
                with col1:
                    icon = "🎥" if "youtube" in url.lower() else "🔗"
                    st.caption(f"{icon} {url}")
                with col2:
                    if st.button("❌", key=f"remove_{i}", use_container_width=True):
                        st.session_state.source_urls.pop(i)
                        st.rerun()

    # Settings
    st.markdown("---")
    st.markdown("### Podcast Settings")

    col1, col2, col3 = st.columns(3)

    with col1:
        tone = st.selectbox("Tone", list(config.VALID_TONES), index=1)

    with col2:
        length = st.selectbox("Length", list(config.VALID_LENGTHS), index=1)

    with col3:
        preserve = st.checkbox("Preserve structure", value=True, help="Keep original flow")

    # Generate button
    st.markdown("---")

    if st.button("🎬 Generate Podcast", type="primary", use_container_width=True):
        # Collect sources
        source_content = combined_source

        # Process uploaded files
        if uploaded_files:
            for file in uploaded_files:
                try:
                    temp_path = Path(f"temp_{file.name}")
                    with open(temp_path, 'wb') as f:
                        f.write(file.getvalue())

                    extracted = extract_text_from_file(temp_path)
                    source_content += f"{extracted}\n\n"
                    temp_path.unlink()
                except Exception as e:
                    st.error(f"Error processing {file.name}: {e}")

        # Process URLs
        if st.session_state.source_urls:
            for url in st.session_state.source_urls:
                try:
                    with st.spinner(f"Fetching {url}..."):
                        if 'youtube.com' in url or 'youtu.be' in url:
                            text = fetch_youtube_transcript(url)
                        else:
                            text = fetch_article_text(url)
                        source_content += f"{text}\n\n"
                except Exception as e:
                    st.error(f"Error fetching {url}: {e}")

        # Validate
        if not source_content or len(source_content) < 100:
            st.error("Please provide source material (minimum 100 characters)")
        else:
            context = InputContext(
                mode=GenerationMode.SOURCE,
                source_material=source_content,
                tone=tone,
                length=length,
                preserve_structure=preserve,
                voice_provider=st.session_state.voice_provider
            )

            generate_podcast_workflow(context)


def render_multichar_mode():
    """Render multi-character podcast creation"""
    st.markdown("### 👥 Multi-Character Podcast")
    st.markdown("Create dynamic conversations with multiple speakers")

    topic = st.text_input(
        "Discussion Topic",
        placeholder="e.g., The Ethics of AI in Healthcare"
    )

    col1, col2 = st.columns(2)

    with col1:
        num_chars = st.slider("Number of Characters", 2, 4, 2)

    with col2:
        interaction = st.selectbox(
            "Interaction Style",
            ["Interview", "Debate", "Comedy Banter", "Roundtable"]
        )

    # Character configuration
    st.markdown("#### Configure Characters")

    characters = []
    for i in range(num_chars):
        with st.expander(f"Character {i+1}", expanded=(i < 2)):
            char_col1, char_col2 = st.columns(2)

            with char_col1:
                name = st.text_input("Name", value=f"Speaker {i+1}", key=f"char_{i}_name")
                role = st.selectbox("Role", ["Host", "Guest", "Expert", "Moderator"], key=f"char_{i}_role")

            with char_col2:
                personality = st.text_input("Personality", placeholder="e.g., energetic and curious", key=f"char_{i}_personality")
                energy = st.select_slider("Energy", ["Low", "Medium", "High"], value="Medium", key=f"char_{i}_energy")

            characters.append(Character(
                name=name,
                role=role,
                personality=personality or f"{energy} energy {role.lower()}",
                speaking_style="clear and engaging",
                preferred_voice="nova",
                energy_level=energy.lower()
            ))

    # Generate button
    st.markdown("---")

    if st.button("🎬 Generate Multi-Character Podcast", type="primary", use_container_width=True):
        if not topic:
            st.error("Please enter a topic")
        else:
            # Map interaction style
            interaction_map = {
                "Interview": InteractionStyle.INTERVIEW,
                "Debate": InteractionStyle.DEBATE,
                "Comedy Banter": InteractionStyle.COMEDY_BANTER,
                "Roundtable": InteractionStyle.ROUNDTABLE
            }

            context = InputContext(
                mode=GenerationMode.MULTI_CHARACTER,
                main_topic=topic,
                characters=characters,
                interaction_style=interaction_map.get(interaction, InteractionStyle.INTERVIEW),
                tone="professional",
                length="medium",
                voice_provider=st.session_state.voice_provider
            )

            generate_podcast_workflow(context)


def generate_podcast_workflow(context: InputContext):
    """Execute podcast generation with progress tracking"""

    # Initialize providers
    provider_config = ProviderConfig(
        llm_provider=st.session_state.provider_name,
        tts_provider=st.session_state.voice_provider
    )
    llm_provider = create_llm_provider(provider_config)

    # Determine TTS provider
    if st.session_state.voice_provider == "elevenlabs":
        from providers.elevenlabs_provider import ElevenLabsTTSProvider
        tts_provider = ElevenLabsTTSProvider()
    else:
        tts_provider = create_tts_provider(provider_config)

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Step 1: Initialize
        status_text.text("🚀 Initializing generation pipeline...")
        progress_bar.progress(10)

        pipeline = UnifiedGenerationPipeline(llm_provider, tts_provider)
        output_root = Path(config.OUTPUT_ROOT)

        # Step 2: Generate script
        status_text.text("✍️ Generating podcast script...")
        progress_bar.progress(30)

        # Step 3: Generate (internal progress)
        status_text.text("🎙️ Creating audio and finalizing...")
        progress_bar.progress(50)

        result = pipeline.generate(context, output_root)

        progress_bar.progress(100)
        status_text.text("✅ Podcast generated successfully!")

        # Display results
        st.balloons()
        st.markdown("---")

        # Success message
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("### 🎉 Podcast Created Successfully!")
        st.markdown(f"**Episode ID:** `{result.episode_id}`")
        st.markdown(f"**Location:** `{result.episode_dir}`")
        st.markdown('</div>', unsafe_allow_html=True)

        # Audio player
        st.markdown("### 🎧 Listen Now")
        st.audio(str(result.audio_path))

        # Script and show notes
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📝 Script")
            with st.expander("View Script", expanded=False):
                st.text_area("", result.script, height=400, key="result_script", label_visibility="collapsed")
                if st.download_button("📥 Download Script", result.script, f"script_{result.episode_id}.txt"):
                    st.success("Downloaded!")

        with col2:
            st.markdown("### 📋 Show Notes")
            with st.expander("View Show Notes", expanded=False):
                st.text_area("", result.show_notes, height=400, key="result_notes", label_visibility="collapsed")
                if st.download_button("📥 Download Show Notes", result.show_notes, f"notes_{result.episode_id}.txt"):
                    st.success("Downloaded!")

        # Metadata
        with st.expander("📊 Episode Metadata"):
            st.json(result.to_dict())

        # Store in session
        st.session_state.last_episode = result
        st.session_state.generation_complete = True

    except Exception as e:
        progress_bar.progress(0)
        status_text.text("")
        st.error(f"❌ Generation failed: {str(e)}")
        with st.expander("🐛 Error Details"):
            import traceback
            st.code(traceback.format_exc())


def render_history_page():
    """Render episode history and management"""
    st.markdown('<h1 class="main-header">📚 Episode History</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Browse and manage your podcast episodes</p>', unsafe_allow_html=True)

    # Load episode index
    index_file = Path(config.OUTPUT_ROOT) / "episode_index.json"

    if not index_file.exists():
        st.info("No episodes yet. Create your first podcast to get started!")
        return

    try:
        episodes = load_episode_index(index_file)

        if not episodes:
            st.info("No episodes yet. Create your first podcast to get started!")
            return

        # Sort by date (newest first)
        episodes_sorted = sorted(
            episodes,
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )

        st.markdown(f"### Found {len(episodes_sorted)} episode(s)")

        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Search episodes", placeholder="Search by topic, mode, or ID...")
        with col2:
            sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "A-Z"])

        # Filter episodes
        filtered = episodes_sorted
        if search:
            filtered = [
                ep for ep in episodes_sorted
                if search.lower() in ep.get('topic', '').lower()
                or search.lower() in ep.get('mode', '').lower()
                or search.lower() in ep.get('episode_id', '').lower()
            ]

        # Apply sorting
        if sort_by == "Oldest First":
            filtered = reversed(filtered)
        elif sort_by == "A-Z":
            filtered = sorted(filtered, key=lambda x: x.get('topic', ''))

        # Display episodes
        for ep in filtered:
            with st.container():
                st.markdown('<div class="episode-card">', unsafe_allow_html=True)

                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"### {ep.get('topic', 'Untitled')}")
                    st.caption(f"🎙️ {ep.get('mode', 'unknown').title()} Mode | 🕐 {ep.get('created_at', 'Unknown')[:10]}")
                    st.caption(f"📁 ID: `{ep.get('episode_id', 'N/A')}`")

                with col2:
                    # Play audio button
                    audio_path = Path(ep.get('audio_path', ''))
                    if audio_path.exists():
                        with st.expander("▶️ Play"):
                            st.audio(str(audio_path))

                with col3:
                    # View details button
                    if st.button("📊 Details", key=f"details_{ep.get('episode_id')}", use_container_width=True):
                        st.session_state.selected_episode = ep

                st.markdown('</div>', unsafe_allow_html=True)

        # Show selected episode details
        if 'selected_episode' in st.session_state:
            st.markdown("---")
            st.markdown("### Episode Details")

            ep = st.session_state.selected_episode

            # Audio
            st.markdown("#### 🎧 Audio")
            audio_path = Path(ep.get('audio_path', ''))
            if audio_path.exists():
                st.audio(str(audio_path))

            # Script and notes
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📝 Script")
                script_path = Path(ep.get('script_path', ''))
                if script_path.exists():
                    with open(script_path, 'r', encoding='utf-8') as f:
                        script = f.read()
                    st.text_area("", script, height=300, key="history_script", label_visibility="collapsed")

            with col2:
                st.markdown("#### 📋 Show Notes")
                notes_path = Path(ep.get('show_notes_path', ''))
                if notes_path.exists():
                    with open(notes_path, 'r', encoding='utf-8') as f:
                        notes = f.read()
                    st.text_area("", notes, height=300, key="history_notes", label_visibility="collapsed")

            # Metadata
            with st.expander("📊 Full Metadata"):
                st.json(ep)

            if st.button("❌ Close Details"):
                del st.session_state.selected_episode
                st.rerun()

    except Exception as e:
        st.error(f"Error loading episode history: {e}")
        import traceback
        st.code(traceback.format_exc())


def render_settings_page():
    """Render settings and configuration"""
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Configure your podcast creator</p>', unsafe_allow_html=True)

    # API Keys
    st.markdown("### 🔑 API Keys")
    st.info("API keys are loaded from your `.env` file. Edit the `.env` file to update keys.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### OpenAI")
        if os.getenv("OPENAI_API_KEY"):
            st.success("✅ Configured")
        else:
            st.warning("❌ Not configured")
            st.code("OPENAI_API_KEY=sk-...", language="bash")

    with col2:
        st.markdown("#### ElevenLabs")
        if os.getenv("ELEVENLABS_API_KEY"):
            st.success("✅ Configured")
        else:
            st.warning("❌ Not configured")
            st.code("ELEVENLABS_API_KEY=...", language="bash")

    st.markdown("---")

    # Default Settings
    st.markdown("### 🎛️ Default Podcast Settings")

    col1, col2 = st.columns(2)

    with col1:
        default_tone = st.selectbox(
            "Default Tone",
            list(config.VALID_TONES),
            index=1
        )

    with col2:
        default_length = st.selectbox(
            "Default Length",
            list(config.VALID_LENGTHS),
            index=1
        )

    st.markdown("---")

    # Output Settings
    st.markdown("### 📁 Output Settings")

    output_dir = st.text_input(
        "Output Directory",
        value=config.OUTPUT_ROOT,
        help="Where episodes are saved"
    )

    st.caption(f"Current output directory: `{Path(output_dir).absolute()}`")

    st.markdown("---")

    # System Info
    st.markdown("### 💻 System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Python Version", f"3.x")
        st.metric("Streamlit Version", st.__version__)

    with col2:
        # Count episodes
        try:
            index_file = Path(config.OUTPUT_ROOT) / "episode_index.json"
            if index_file.exists():
                with open(index_file, 'r') as f:
                    episodes = json.load(f)
                st.metric("Total Episodes", len(episodes))
            else:
                st.metric("Total Episodes", 0)
        except:
            st.metric("Total Episodes", "?")

        # Disk usage
        try:
            output_path = Path(config.OUTPUT_ROOT)
            if output_path.exists():
                size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file())
                size_mb = size / (1024 * 1024)
                st.metric("Storage Used", f"{size_mb:.1f} MB")
            else:
                st.metric("Storage Used", "0 MB")
        except:
            st.metric("Storage Used", "?")


def main():
    """Main application entry point"""
    initialize_session_state()
    render_sidebar()

    # Route to appropriate page
    if st.session_state.current_page == 'create':
        render_create_page()
    elif st.session_state.current_page == 'history':
        render_history_page()
    elif st.session_state.current_page == 'settings':
        render_settings_page()


if __name__ == "__main__":
    main()
