# Podcast Creator Agent - Refactor Implementation Plan

## Executive Summary

Transform the 4-tab podcast creator into a **6-mode unified system** with rich character/persona capabilities, enhanced input handling, and end-to-end voice assignment.

---

## Phase 1: Foundation - Unified Data Models

### 1.1 Create Unified Input Context (NEW: `core/input_models.py`)

```python
@dataclass
class InputContext:
    """Unified input representation for all generation modes"""
    mode: str  # topic|text|source|multi_character|persona|template
    
    # Topic Mode fields
    main_topic: Optional[str]
    topic_details: Optional[str]
    focus_areas: Optional[List[str]]
    desired_style: Optional[str]
    
    # Text Mode fields
    text_content: Optional[str]
    
    # Source Mode fields
    source_material: Optional[str]
    source_title: Optional[str]
    emphasis_instructions: Optional[str]
    target_audience: Optional[str]
    depth_preference: Optional[str]  # summary|deep_dive
    
    # Multi-Character Mode fields
    characters: Optional[List['Character']]
    interaction_style: Optional[str]  # debate|interview|banter|etc
    
    # Persona Mode fields
    persona: Optional['Persona']
    fun_vs_serious: Optional[float]  # 0.0-1.0
    
    # Template Mode fields
    template_key: Optional[str]
    
    # Shared configuration
    tone: str
    length: str
    voice_provider: str

@dataclass
class Character:
    """Rich character definition"""
    name: str
    role: str  # host|guest|expert|moderator|etc
    personality: str
    speaking_style: str
    preferred_voice: str
    energy_level: str  # low|medium|high
    humor_style: Optional[str]

@dataclass
class Persona:
    """Enhanced persona definition"""
    id: str
    name: str
    description: str
    archetype: str  # documentary_narrator|hype_host|calm_educator|etc
    energy: str  # calm|moderate|energetic|chaotic
    humor: str  # dry|witty|playful|none
    pacing: str  # slow|moderate|fast
    tone: str
    recommended_voice: Dict[str, str]  # provider → voice
    catchphrases: Optional[List[str]]
    custom: bool  # True if user-created
```

**Deliverable:** `core/input_models.py` with complete type definitions

---

### 1.2 Enhanced Persona Library (UPDATE: `step32_voice_persona_system.py`)

**Current Personas (5):** tech_enthusiast, science_explainer, business_analyst, storyteller, skeptical_thinker

**New Personas (15+):**
- `documentary_sage`: David Attenborough-inspired, calm, wonder-filled
- `hype_machine`: High-energy sports commentator style
- `conspiracy_theorist`: Playful paranoid investigator
- `professor_chaos`: Eccentric academic, tangential, passionate
- `noir_detective`: Hard-boiled investigator narration
- `cosmic_philosopher`: Carl Sagan-inspired cosmic perspective
- `drill_sergeant`: Intense, motivational, no-nonsense
- `late_night_comic`: Observational humor, conversational
- `mystery_narrator`: Suspenseful storytelling
- `game_show_host`: Energetic, audience-engaging
- `meditation_guide`: Calm, centered, reflective
- `grumpy_critic`: Sardonic, critical eye
- `hopeful_futurist`: Optimistic tech visionary
- `historical_reenactor`: Period-appropriate dramatic reading
- `podcast_bro`: Casual, "let me tell you about this" vibe

**Plus:** Support for custom persona creation via UI

**Deliverable:** Updated `PERSONA_LIBRARY` with 15+ personas + custom persona creation function

---

### 1.3 Expanded Template Library (UPDATE: `step27_podcast_templates.py`)

**Current Templates (5):** solo_explainer, news_recap, interview_style, daily_briefing, deep_dive

**New Templates (10+):**
- `debate_match`: Two opposing viewpoints, moderator
- `documentary_exploration`: Narrated journey with expert insights
- `storytime_adventure`: Narrative storytelling format
- `educational_breakdown`: Structured learning with examples
- `comedy_panel`: Multiple hosts, banter, jokes
- `character_roleplay`: In-character discussion (historical figures, etc.)
- `roundtable_discussion`: 3-5 experts, moderated conversation
- `investigation_report`: Mystery/case study format
- `how_to_guide`: Step-by-step instructional
- `review_analysis`: Critical review format

**Each template defines:**
- Structure (intro/body/conclusion segments)
- Pacing guidance
- Suggested speaker count/roles
- Tone/style constraints
- Narration vs dialogue balance

**Deliverable:** Updated `PODCAST_TEMPLATES` with 10+ templates

---

## Phase 2: UI Transformation - 6 Input Modes

### 2.1 Refactor Web UI Structure (UPDATE: `step44_web_ui.py`)

**Current:** 4 tabs (Topic/Text, Multi-Character, Persona, Template)

**New:** 6 tabs with enhanced inputs

```python
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Topic",
    "📄 Text", 
    "📚 Source Material",
    "👥 Multi-Character",
    "🎭 Persona Mode",
    "📋 Template Mode"
])
```

**Deliverable:** Restructured tab layout with placeholder sections

---

### 2.2 Topic Mode (Tab 1) - Enhanced Input

**Current:** Single `st.text_input("Topic")`

**New:**
```python
with tab1:
    st.header("Topic-Based Podcast")
    
    main_topic = st.text_input(
        "Main Topic *", 
        placeholder="e.g., The Future of Renewable Energy"
    )
    
    topic_details = st.text_area(
        "Topic Details / Additional Context",
        height=150,
        placeholder="Provide background, specific angles, or context you want covered..."
    )
    
    focus_areas = st.text_area(
        "Optional Focus Areas (one per line)",
        height=100,
        placeholder="e.g.,\n- Solar panel efficiency\n- Grid storage challenges\n- Policy implications"
    )
    
    desired_style = st.text_input(
        "Desired Tone or Style",
        placeholder="e.g., conversational and optimistic"
    )
    
    if st.button("Generate Topic Podcast"):
        # Build InputContext from all fields
        # Pass to unified generation pipeline
```

**Generation Logic:**
- Parse `focus_areas` into list (split by newlines)
- Build comprehensive LLM prompt incorporating ALL fields:
  ```
  Topic: {main_topic}
  Context: {topic_details}
  Focus Areas: {focus_areas}
  Style: {desired_style}
  Tone: {tone}
  ```

**Deliverable:** Enhanced topic mode with 4-field input system

---

### 2.3 Text Mode (Tab 2) - Long-Form Support

**Current:** Combined with Topic in single tab, small text area

**New:**
```python
with tab2:
    st.header("Text-Based Podcast")
    st.markdown("Paste your text content and we'll turn it into a podcast")
    
    text_content = st.text_area(
        "Your Text Content *",
        height=400,  # Much larger
        placeholder="Paste your article, blog post, notes, or any text content here.\n\nThis can be:\n- Research findings\n- Meeting notes\n- Article drafts\n- Book excerpts\n- Documentation\n\nWe'll preserve your key points and structure while making it engaging for audio."
    )
    
    st.caption(f"Character count: {len(text_content)}")
    
    # Optional refinement controls
    with st.expander("Advanced Options"):
        preserve_structure = st.checkbox("Preserve original structure", value=True)
        add_commentary = st.checkbox("Add host commentary", value=False)
    
    if st.button("Generate Text Podcast"):
        # Pass full text to generation with preservation instructions
```

**Generation Logic:**
- Handle text up to 10,000+ characters
- Instruct LLM to preserve user details: "Convert this text into a podcast script. Preserve all key facts, examples, and structure from the source."
- Add optional commentary layer if requested

**Deliverable:** Dedicated text mode with large input area

---

### 2.4 Source Material Mode (Tab 3) - NEW

**New Feature:**
```python
with tab3:
    st.header("Source Material Podcast")
    st.markdown("Upload or paste source material for in-depth coverage")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload Source Files (optional)",
        type=["txt", "pdf", "docx", "md"],
        accept_multiple_files=True
    )
    
    # Or paste directly
    source_material = st.text_area(
        "Or Paste Source Material",
        height=300,
        placeholder="Paste research, articles, notes, or any reference material..."
    )
    
    source_title = st.text_input(
        "Source Title (optional)",
        placeholder="e.g., Q3 Financial Report"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        emphasis = st.text_area(
            "Emphasis Instructions (optional)",
            height=100,
            placeholder="What should we emphasize or focus on?"
        )
    with col2:
        target_audience = st.selectbox(
            "Target Audience",
            ["General", "Technical Experts", "Business Leaders", "Students", "Enthusiasts"]
        )
    
    depth = st.radio(
        "Coverage Depth",
        ["Summary (high-level overview)", "Deep Dive (comprehensive analysis)"],
        horizontal=True
    )
    
    if st.button("Generate Source-Based Podcast"):
        # Process files if uploaded
        # Build context with source material + instructions
```

**Generation Logic:**
- Extract text from uploaded files using existing `core/source_management.py` utilities
- Combine with pasted material
- Build LLM prompt:
  ```
  Source Title: {title}
  Audience: {audience}
  Depth: {depth}
  Emphasis: {emphasis}
  
  Source Material:
  {combined_sources}
  
  Create a {depth} podcast covering this material for {audience}.
  ```

**Deliverable:** New source material mode with file upload + rich configuration

---

### 2.5 Multi-Character Mode (Tab 4) - Major Enhancement

**Current:** Topic + slider (2-4 characters) → auto character detection

**New:**
```python
with tab4:
    st.header("Multi-Character Podcast")
    st.markdown("Create dynamic conversations with multiple distinct characters")
    
    # Topic
    topic = st.text_input("Discussion Topic *")
    
    # Character count
    num_characters = st.slider("Number of Characters", 2, 5, 2)
    
    # Interaction style
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
        ]
    )
    
    # Character builder
    st.subheader("Character Configuration")
    
    characters = []
    for i in range(num_characters):
        with st.expander(f"Character {i+1}"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(f"Name", key=f"char_{i}_name", value=f"Speaker {i+1}")
                role = st.selectbox(
                    f"Role", 
                    ["Host", "Guest", "Expert", "Moderator", "Commentator", "Analyst"],
                    key=f"char_{i}_role"
                )
                personality = st.text_input(
                    f"Personality",
                    key=f"char_{i}_personality",
                    placeholder="e.g., energetic and curious"
                )
            with col2:
                speaking_style = st.text_input(
                    f"Speaking Style",
                    key=f"char_{i}_style",
                    placeholder="e.g., uses metaphors, asks probing questions"
                )
                energy = st.select_slider(
                    f"Energy Level",
                    options=["Low", "Medium", "High"],
                    value="Medium",
                    key=f"char_{i}_energy"
                )
                # Voice selection per character
                voice = st.selectbox(
                    f"Voice",
                    tts_provider.available_voices,
                    key=f"char_{i}_voice"
                )
            
            characters.append({
                "name": name,
                "role": role,
                "personality": personality,
                "speaking_style": speaking_style,
                "energy": energy,
                "voice": voice
            })
    
    # Fallback strategy if not enough voices
    st.info(f"Available voices: {len(tts_provider.available_voices)}. If you have more characters than voices, some will share voices.")
    
    if st.button("Generate Multi-Character Podcast"):
        # Build Character objects
        # Pass to multi-character generation with voice assignments
```

**Generation Logic:**
- Build rich character profiles with all fields
- Generate script with LLM using character personalities:
  ```
  Create a {interaction_style} podcast about {topic}.
  
  Characters:
  - {char1.name} ({char1.role}): {char1.personality}. Speaking style: {char1.speaking_style}. Energy: {char1.energy}.
  - {char2.name} ({char2.role}): ...
  
  Format:
  {CHAR_NAME}: dialogue
  ```
- Parse script to extract character lines
- Assign voices per character (use user selections)
- Generate separate audio for each character's lines
- Merge audio files in dialogue order

**Deliverable:** Rich multi-character mode with per-character configuration

---

### 2.6 Persona Mode (Tab 5) - Enhanced & Fun

**Current:** Dropdown with 5 personas

**New:**
```python
with tab5:
    st.header("Persona-Driven Podcast")
    st.markdown("Choose a host personality that brings your topic to life")
    
    # Persona selection
    persona_categories = {
        "Informative & Educational": [
            "documentary_sage", "professor_chaos", "cosmic_philosopher"
        ],
        "Entertaining & Energetic": [
            "hype_machine", "late_night_comic", "game_show_host"
        ],
        "Dramatic & Atmospheric": [
            "noir_detective", "mystery_narrator", "historical_reenactor"
        ],
        "Unique & Quirky": [
            "conspiracy_theorist", "grumpy_critic", "meditation_guide"
        ],
        "Custom": ["create_your_own"]
    }
    
    category = st.selectbox("Persona Category", persona_categories.keys())
    persona_key = st.selectbox("Persona", persona_categories[category])
    
    # Show persona details
    if persona_key != "create_your_own":
        persona = PERSONA_LIBRARY[persona_key]
        with st.expander("Persona Details"):
            st.write(f"**{persona.name}**")
            st.write(f"*{persona.description}*")
            st.write(f"- Energy: {persona.energy}")
            st.write(f"- Humor: {persona.humor}")
            st.write(f"- Pacing: {persona.pacing}")
            if persona.catchphrases:
                st.write(f"- Catchphrases: {', '.join(persona.catchphrases[:3])}")
    else:
        # Custom persona creation
        st.subheader("Create Custom Persona")
        custom_name = st.text_input("Persona Name")
        custom_desc = st.text_area("Description")
        custom_energy = st.select_slider("Energy", ["Calm", "Moderate", "Energetic", "Chaotic"])
        custom_humor = st.selectbox("Humor Style", ["None", "Dry", "Witty", "Playful", "Absurd"])
        custom_pacing = st.selectbox("Pacing", ["Slow", "Moderate", "Fast"])
        custom_tone = st.selectbox("Tone", config.VALID_TONES)
        
        # Build custom persona
        persona = create_custom_persona(
            custom_name, custom_desc, custom_energy, custom_humor, custom_pacing, custom_tone
        )
    
    # Fun vs Serious slider
    fun_vs_serious = st.slider(
        "Fun vs. Serious Balance",
        0.0, 1.0, 0.5,
        help="0 = Maximum fun/entertainment, 1 = Maximum serious/informative"
    )
    
    # Topic
    topic = st.text_input("Topic *")
    
    if st.button("Generate Persona Podcast"):
        # Pass persona + fun_vs_serious to generation
```

**Generation Logic:**
- Inject persona traits into LLM prompt:
  ```
  You are {persona.name}: {persona.description}
  
  Speaking style:
  - Energy: {persona.energy}
  - Humor: {persona.humor}
  - Pacing: {persona.pacing}
  - Tone: {persona.tone}
  - Fun/Serious balance: {fun_vs_serious}
  
  Generate a podcast about {topic} in this persona.
  ```
- Use persona's recommended voice for TTS
- Save custom personas to user library

**Deliverable:** Enhanced persona mode with categories, custom creation, and fun/serious slider

---

### 2.7 Template Mode (Tab 6) - Enhanced

**Current:** Dropdown with 5 templates

**New:**
```python
with tab6:
    st.header("Template-Based Podcast")
    st.markdown("Use structured formats for professional podcast production")
    
    template_categories = {
        "Informational": ["solo_explainer", "documentary_exploration", "educational_breakdown"],
        "Conversational": ["interview_style", "roundtable_discussion", "debate_match"],
        "Entertainment": ["comedy_panel", "character_roleplay", "storytime_adventure"],
        "Practical": ["how_to_guide", "review_analysis", "investigation_report"],
        "News & Updates": ["news_recap", "daily_briefing"]
    }
    
    category = st.selectbox("Template Category", template_categories.keys())
    template_key = st.selectbox("Template", template_categories[category])
    
    template = PODCAST_TEMPLATES[template_key]
    
    with st.expander("Template Structure"):
        st.write(f"**{template['name']}**")
        st.write(f"{template['description']}")
        st.write(f"- Suggested Speakers: {template.get('speaker_count', '1')}")
        st.write(f"- Tone: {template.get('recommended_tone', 'any')}")
        st.write(f"- Structure: {template.get('structure', 'Standard')}")
    
    topic = st.text_input("Topic *")
    
    if st.button("Generate Template Podcast"):
        # Pass template + topic to generation
```

**Deliverable:** Categorized template selection with rich metadata display

---

## Phase 3: Core Generation Refactor

### 3.1 Unified Generation Pipeline (NEW: `core/unified_generation.py`)

```python
class UnifiedGenerationPipeline:
    """Single entry point for all podcast generation modes"""
    
    def __init__(self, llm_provider, tts_provider):
        self.llm = llm_provider
        self.tts = tts_provider
    
    def generate(self, context: InputContext) -> EpisodeResult:
        """
        Unified generation flow:
        1. Build script based on mode
        2. Generate show notes
        3. Generate audio (single or multi-voice)
        4. Save episode
        """
        # Route to appropriate script generator
        if context.mode == "topic":
            script = self._generate_topic_script(context)
        elif context.mode == "text":
            script = self._generate_text_script(context)
        elif context.mode == "source":
            script = self._generate_source_script(context)
        elif context.mode == "multi_character":
            script = self._generate_multi_character_script(context)
        elif context.mode == "persona":
            script = self._generate_persona_script(context)
        elif context.mode == "template":
            script = self._generate_template_script(context)
        
        # Generate show notes
        show_notes = self._generate_show_notes(script, context)
        
        # Generate audio with voice assignment
        audio_path = self._generate_audio(script, context)
        
        # Save episode
        episode = self._save_episode(script, show_notes, audio_path, context)
        
        return episode
    
    def _generate_topic_script(self, context):
        """Enhanced topic mode using ALL fields"""
        prompt = f"""Generate a podcast script about: {context.main_topic}

Context: {context.topic_details}

Focus on these areas:
{chr(10).join(f"- {area}" for area in context.focus_areas)}

Desired style: {context.desired_style}
Tone: {context.tone}
Target length: {get_word_range(context.length)} words

Create an engaging podcast script."""
        
        return self.llm.generate_text(prompt)
    
    # ... other mode-specific generators
```

**Deliverable:** `core/unified_generation.py` with complete pipeline

---

### 3.2 Multi-Voice Audio Rendering (NEW: `core/multi_voice_audio.py`)

```python
class MultiVoiceRenderer:
    """Handles multi-character audio generation and merging"""
    
    def __init__(self, tts_provider):
        self.tts = tts_provider
    
    def render(self, script: str, voice_assignment: Dict[str, str], output_path: Path):
        """
        1. Parse script for character lines
        2. Generate audio per character
        3. Merge in dialogue order
        """
        # Parse script
        segments = self._parse_script(script)  # [(character, text), ...]
        
        # Generate per character
        character_audio_files = {}
        for character in set(seg[0] for seg in segments):
            voice = voice_assignment.get(character, self.tts.available_voices[0])
            # Collect all lines for this character
            character_lines = [seg[1] for seg in segments if seg[0] == character]
            character_text = " ".join(character_lines)
            
            temp_file = Path(f"temp_{character}.mp3")
            self.tts.generate_audio(character_text, voice, temp_file)
            character_audio_files[character] = temp_file
        
        # Merge segments in order
        self._merge_audio_segments(segments, character_audio_files, output_path)
        
        # Cleanup temp files
        for temp_file in character_audio_files.values():
            temp_file.unlink()
    
    def _parse_script(self, script):
        """Parse 'CHARACTER: text' format"""
        segments = []
        for line in script.split('\n'):
            match = re.match(r'^([A-Z_]+):\s*(.+)$', line)
            if match:
                character, text = match.groups()
                segments.append((character, text))
        return segments
    
    def _merge_audio_segments(self, segments, audio_files, output):
        """Merge audio in dialogue order using pydub"""
        from pydub import AudioSegment
        
        # Create segment-by-segment audio
        # This is complex - for now, concatenate full character audio
        # Future: split and interleave properly
        combined = AudioSegment.empty()
        for character, text in segments:
            if character in audio_files:
                segment = AudioSegment.from_mp3(audio_files[character])
                combined += segment
        
        combined.export(output, format="mp3")
```

**Note:** This is a simplified version. Full implementation requires:
- Segment-level audio splitting
- Timing/pacing between speakers
- Optional background music/effects

**Deliverable:** `core/multi_voice_audio.py` with basic multi-voice rendering

---

### 3.3 Voice Assignment Strategy (NEW: `core/voice_assignment.py`)

```python
class VoiceAssignmentStrategy:
    """Smart voice-to-character mapping"""
    
    def __init__(self, available_voices: List[str]):
        self.available_voices = available_voices
    
    def assign(self, characters: List[Character]) -> Dict[str, str]:
        """Assign voices to characters with fallback"""
        assignments = {}
        
        # Priority 1: Use preferred voice if available
        used_voices = set()
        for char in characters:
            if char.preferred_voice in self.available_voices:
                assignments[char.name] = char.preferred_voice
                used_voices.add(char.preferred_voice)
        
        # Priority 2: Assign remaining characters to unused voices
        remaining_chars = [c for c in characters if c.name not in assignments]
        remaining_voices = [v for v in self.available_voices if v not in used_voices]
        
        for char, voice in zip(remaining_chars, remaining_voices):
            assignments[char.name] = voice
        
        # Fallback: If more characters than voices, round-robin
        if len(remaining_chars) > len(remaining_voices):
            for i, char in enumerate(remaining_chars[len(remaining_voices):]):
                assignments[char.name] = self.available_voices[i % len(self.available_voices)]
        
        return assignments
```

**Deliverable:** `core/voice_assignment.py` with smart assignment logic

---

## Phase 4: Integration & Testing

### 4.1 Update Web UI to Use Unified Pipeline

**In `step44_web_ui.py`:**

```python
from core.unified_generation import UnifiedGenerationPipeline
from core.input_models import InputContext, Character, Persona

# Inside each tab's generate button handler:
if st.button("Generate ..."):
    # Build InputContext
    context = InputContext(
        mode="topic",  # or text, source, multi_character, persona, template
        main_topic=main_topic,
        topic_details=topic_details,
        # ... all other fields
        tone=tone,
        length=length,
        voice_provider=provider
    )
    
    # Generate via unified pipeline
    pipeline = UnifiedGenerationPipeline(llm_provider, tts_provider)
    
    with st.spinner("Generating podcast..."):
        episode = pipeline.generate(context)
    
    # Display results
    st.success("Podcast generated!")
    st.subheader("Script")
    st.text_area("", episode.script, height=300)
    # ... show notes, audio player
```

**Deliverable:** Updated `step44_web_ui.py` using unified pipeline for all 6 modes

---

### 4.2 Enhanced Persona Library Implementation

**In `step32_voice_persona_system.py`:**

```python
PERSONA_LIBRARY = {
    "documentary_sage": Persona(
        id="documentary_sage",
        name="The Documentary Sage",
        description="Calm, wonder-filled narrator inspired by nature documentaries. Speaks with reverence and curiosity.",
        archetype="documentary_narrator",
        energy="calm",
        humor="subtle",
        pacing="slow",
        tone="educational",
        recommended_voice={"openai": "onyx", "gemini": "en-US-Journey-D"},
        catchphrases=["Remarkable", "In the vast tapestry of...", "Consider, if you will"]
    ),
    "hype_machine": Persona(
        id="hype_machine",
        name="The Hype Machine",
        description="High-energy sports commentator style. Everything is exciting and intense!",
        archetype="hype_host",
        energy="chaotic",
        humor="playful",
        pacing="fast",
        tone="casual",
        recommended_voice={"openai": "nova", "gemini": "en-US-Neural2-A"},
        catchphrases=["LET'S GO!", "This is HUGE!", "You're not gonna believe this!"]
    ),
    # ... 13 more personas
}

def create_custom_persona(name, description, energy, humor, pacing, tone):
    """Create user-defined persona"""
    return Persona(
        id=f"custom_{name.lower().replace(' ', '_')}",
        name=name,
        description=description,
        archetype="custom",
        energy=energy.lower(),
        humor=humor.lower(),
        pacing=pacing.lower(),
        tone=tone,
        recommended_voice={"openai": "nova", "gemini": "en-US-Journey-F"},
        catchphrases=[],
        custom=True
    )
```

**Deliverable:** `step32_voice_persona_system.py` with 15+ personas + custom creation

---

### 4.3 Enhanced Template Library Implementation

**In `step27_podcast_templates.py`:**

```python
PODCAST_TEMPLATES = {
    "debate_match": {
        "name": "Debate Match",
        "description": "Two opposing viewpoints with a neutral moderator",
        "speaker_count": 3,
        "roles": ["Moderator", "Pro Side", "Con Side"],
        "recommended_tone": "professional",
        "structure": "Opening statements → Arguments → Rebuttals → Closing",
        "system_prompt": """Create a debate-style podcast with three speakers:
        
MODERATOR: Introduces topic, asks questions, maintains balance
PRO_SPEAKER: Argues in favor of the topic
CON_SPEAKER: Argues against the topic

Format:
MODERATOR: text
PRO_SPEAKER: text
CON_SPEAKER: text

Include opening statements, main arguments, rebuttals, and closing remarks."""
    },
    
    "comedy_panel": {
        "name": "Comedy Panel",
        "description": "Multiple hosts with playful banter and jokes",
        "speaker_count": "3-4",
        "roles": ["Lead Host", "Co-hosts"],
        "recommended_tone": "casual",
        "structure": "Intro banter → Topic discussion → Jokes/callbacks → Outro",
        "system_prompt": """Create a comedy panel podcast with 3-4 hosts who have great chemistry.

Include:
- Playful banter and callbacks
- Jokes and humorous observations
- Each host has distinct comedic style
- Natural conversational flow

Format:
HOST1: text
HOST2: text
HOST3: text"""
    },
    
    # ... 8 more templates
}
```

**Deliverable:** `step27_podcast_templates.py` with 10+ templates

---

### 4.4 Testing Plan

**Test Scenarios:**

1. **Topic Mode:**
   - Enter main topic + details + focus areas + style
   - Verify script incorporates ALL fields
   - Check audio generation

2. **Text Mode:**
   - Paste 5000+ character text
   - Verify script preserves key details
   - Check audio quality

3. **Source Mode:**
   - Upload PDF file
   - Add emphasis instructions
   - Select "Deep Dive" depth
   - Verify comprehensive coverage

4. **Multi-Character Mode:**
   - Create 3 characters with distinct personalities
   - Select "Debate" interaction style
   - Verify script has character-specific dialogue
   - Check multi-voice audio (if implemented)

5. **Persona Mode:**
   - Select "Hype Machine" persona
   - Adjust fun/serious slider
   - Verify script matches persona energy
   - Create custom persona and test

6. **Template Mode:**
   - Select "Comedy Panel" template
   - Verify script follows template structure
   - Check speaker count matches template

**Deliverable:** Test report with pass/fail for each mode

---

## Phase 5: Documentation & Polish

### 5.1 Update Documentation

- **README.md:** Update with 6-mode overview
- **UI_TESTING_GUIDE.md:** Update with new testing scenarios
- **ARCHITECTURE.md:** Document unified pipeline architecture

### 5.2 UI Polish

- Add mode-specific help text
- Improve error messages
- Add progress indicators
- Add example inputs/placeholders

### 5.3 Performance Optimization

- Cache persona/template libraries
- Optimize multi-voice rendering
- Add generation timeout handling

---

## Implementation Order

1. ✅ **Phase 1.1:** Create `core/input_models.py` (1 hour)
2. ✅ **Phase 1.2:** Enhance persona library (2 hours)
3. ✅ **Phase 1.3:** Enhance template library (1 hour)
4. ✅ **Phase 2:** Refactor UI to 6 tabs with enhanced inputs (3 hours)
5. ✅ **Phase 3.1:** Build unified generation pipeline (2 hours)
6. ✅ **Phase 3.2-3.3:** Multi-voice rendering + voice assignment (2 hours)
7. ✅ **Phase 4.1:** Integrate UI with pipeline (1 hour)
8. ✅ **Phase 4.4:** Testing (2 hours)
9. ✅ **Phase 5:** Documentation & polish (1 hour)

**Total Estimated Time:** ~15 hours

---

## Success Criteria

- [ ] 6 input modes all functional
- [ ] Topic mode uses all 4 input fields
- [ ] Text mode handles 10,000+ characters
- [ ] Source mode accepts file uploads
- [ ] Multi-character supports 2-5 characters with per-character voice selection
- [ ] Persona library has 15+ personas + custom creation
- [ ] Template library has 10+ templates
- [ ] Multi-voice audio renders distinct voices per character
- [ ] All modes save proper metadata
- [ ] UI is intuitive and well-documented
- [ ] Test scenarios pass

---

## Files to Create/Modify

**New Files:**
- `core/input_models.py`
- `core/unified_generation.py`
- `core/multi_voice_audio.py`
- `core/voice_assignment.py`

**Modified Files:**
- `step44_web_ui.py` (major refactor)
- `step32_voice_persona_system.py` (expand personas)
- `step27_podcast_templates.py` (expand templates)
- `config.py` (add new constants)

**Documentation:**
- `REFACTOR_SUMMARY.md` (this file)
- `ARCHITECTURE.md` (updated)
- `UI_TESTING_GUIDE.md` (updated)
- `README.md` (updated)
