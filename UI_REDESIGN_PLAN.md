# UI Redesign Plan - Remove Text Tab, Expand Source Material

## Executive Summary

**Goal:** Consolidate from 6 tabs to 5 tabs by removing Text mode and expanding Source Material into a unified ingestion hub.

**Changes:**
1. Remove Tab 2 (Text Mode)
2. Expand Tab 3 (Source Material) into comprehensive ingestion hub
3. Keep Topic, Multi-Character, Persona, Template modes
4. Add audio upload capability (for transcription + style reference)
5. Normalize all inputs into unified backend structure

---

## Current State vs Proposed State

### Before (6 Tabs)
1. Topic Mode
2. **Text Mode** ← REMOVE
3. Source Material Mode ← EXPAND
4. Multi-Character
5. Persona Mode
6. Template Mode

### After (5 Tabs)
1. Topic Mode ← Keep, enhance
2. **Source Material Mode** ← Expand into unified hub
3. Multi-Character ← Keep, connect to sources
4. Persona Mode ← Keep, connect to sources
5. Template Mode ← Keep, connect to sources

---

## Detailed Design: Source Material Hub

### Section A: Paste Text
**What it replaces:** Current Text Mode tab

**UI Layout:**
```
┌─ Paste Text ────────────────────────────────────────────┐
│                                                           │
│  [Large text area - 500px height]                        │
│                                                           │
│  Placeholder:                                             │
│  "Paste your content here...                             │
│                                                           │
│  Examples:                                                │
│  • Article or blog post text                             │
│  • Meeting notes or transcripts                          │
│  • Research findings                                      │
│  • Book excerpts                                          │
│  • Documentation                                          │
│                                                           │
│  We'll transform this into an engaging podcast."         │
│                                                           │
│  Character count: 0                                       │
│                                                           │
│  ☐ Preserve original structure                           │
│  ☐ Add host commentary                                    │
└───────────────────────────────────────────────────────────┘
```

**Features:**
- Large textarea (minimum 500px height)
- Character/word count display
- Two checkboxes:
  - Preserve structure (yes/no)
  - Add commentary (yes/no)
- Minimum 100 characters validation

**Backend:** Maps to `text_content` field

---

### Section B: Upload Files
**What it extends:** Current file upload (txt, md only) → Support more types

**UI Layout:**
```
┌─ Upload Files ──────────────────────────────────────────┐
│                                                           │
│  [Drag & Drop Area or Browse...]                         │
│                                                           │
│  Supported formats:                                       │
│  📄 Documents: PDF, TXT, MD, DOCX                         │
│  📖 Ebooks: EPUB (if supported)                           │
│                                                           │
│  [File 1: report.pdf] [X]                                 │
│  [File 2: notes.txt] [X]                                  │
│                                                           │
│  Multiple files will be combined into one podcast.       │
└───────────────────────────────────────────────────────────┘
```

**Supported File Types:**

| Format | Status | Library | Notes |
|--------|--------|---------|-------|
| **.txt** | ✅ Built-in | Python native | Already supported |
| **.md** | ✅ Built-in | Python native | Already supported |
| **.pdf** | ✅ Built-in | pypdf | Already supported |
| **.docx** | ⚠️ Add | python-docx | Easy to add |
| **.epub** | ⚠️ Add | ebooklib | Easy to add |
| **.html** | ⚠️ Add | BeautifulSoup | Already available |

**Implementation:**
```python
def process_uploaded_file(file) -> str:
    """Extract text from uploaded file"""
    ext = file.name.split('.')[-1].lower()
    
    if ext == 'pdf':
        return extract_text_from_pdf(file)  # EXISTING
    elif ext in ['txt', 'md']:
        return file.read().decode('utf-8')  # EXISTING
    elif ext == 'docx':
        return extract_text_from_docx(file)  # NEW
    elif ext == 'epub':
        return extract_text_from_epub(file)  # NEW
    elif ext == 'html':
        return extract_text_from_html(file)  # NEW
    else:
        raise ValueError(f"Unsupported file type: {ext}")
```

**Backend:** Maps to `source_material` + `source_files` fields

---

### Section C: Add Links
**What it extends:** YouTube + URL support already exists

**UI Layout:**
```
┌─ Add Links ─────────────────────────────────────────────┐
│                                                           │
│  Paste URL:                                               │
│  [Text input ─────────────────────────────] [Add]        │
│                                                           │
│  Examples:                                                │
│  • https://youtube.com/watch?v=...                       │
│  • https://article-website.com/post                      │
│  • https://blog.example.com/...                          │
│                                                           │
│  Added links:                                             │
│  [🎥 YouTube: AI Trends 2026] [X]                         │
│  [🔗 Article: Future of Tech] [X]                         │
│                                                           │
│  We'll extract transcripts and article text              │
│  automatically.                                           │
└───────────────────────────────────────────────────────────┘
```

**Features:**
- URL input field with "Add" button
- Auto-detect URL type (YouTube vs article)
- Display added URLs with icons
- Remove button per URL
- Support multiple URLs

**Auto-Detection Logic:**
```python
def detect_url_type(url: str) -> str:
    """Detect URL type"""
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    else:
        return 'article'
```

**Supported URL Types:**

| Type | Status | Function | Notes |
|------|--------|----------|-------|
| **YouTube** | ✅ Built-in | `fetch_youtube_transcript()` | Already works |
| **Web articles** | ✅ Built-in | `fetch_article_text()` | Already works |
| **Twitter/X** | ❌ Future | - | Needs API integration |
| **Reddit** | ❌ Future | - | Needs API/scraping |

**Backend:** Maps to URL list → fetched to `source_material`

---

### Section D: Upload Audio (NEW)
**What it adds:** Audio ingestion for transcription + style reference

**UI Layout:**
```
┌─ Upload Audio Reference ────────────────────────────────┐
│                                                           │
│  [Drag & Drop Area or Browse...]                         │
│                                                           │
│  Supported formats: MP3, WAV, M4A, OGG                    │
│                                                           │
│  [Audio 1: interview.mp3] [X]                             │
│                                                           │
│  Purpose:                                                 │
│  ( ) Transcribe as source material                       │
│  ( ) Use as speaking style reference                     │
│                                                           │
│  ⚠️ Note: We analyze speaking style (energy, pacing,     │
│    tone) and map to our voice archetypes. We do NOT     │
│    clone the exact voice.                                │
│                                                           │
│  If "Style Reference" selected:                          │
│  Detected traits:                                         │
│  • Energy: High                                           │
│  • Pacing: Fast                                           │
│  • Humor: Moderate                                        │
│  → Recommended archetype: Rapid-Fire Comedian            │
└───────────────────────────────────────────────────────────┘
```

**Purpose Options:**
1. **Transcribe as source material**
   - Uses Whisper API to convert audio → text
   - Text becomes source material for podcast generation
   - Use case: Convert existing podcast/lecture → new podcast

2. **Use as speaking style reference**
   - Analyzes audio for traits: energy, pacing, humor, tone
   - Maps traits to existing voice archetypes
   - Does NOT clone voice (ethical constraint)
   - Use case: "Make it sound like this vibe"

**Implementation Requirements:**

**For Transcription:**
```python
def transcribe_audio(audio_file) -> str:
    """Transcribe audio using Whisper API"""
    from openai import OpenAI
    
    client = OpenAI()
    
    with open(audio_file, 'rb') as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text"
        )
    
    return transcript
```

**For Style Analysis:**
```python
def analyze_audio_style(audio_file) -> dict:
    """Analyze audio for style traits (NO voice cloning)"""
    # Option 1: Use Whisper to transcribe, then LLM to analyze text traits
    transcript = transcribe_audio(audio_file)
    
    # Use LLM to analyze speaking style from transcript
    prompt = f"""Analyze this transcript for speaking style traits:

{transcript}

Extract:
- Energy level (low/medium/high/extreme)
- Pacing (slow/moderate/fast/rapid)
- Humor level (none/subtle/moderate/high)
- Tone (warm/cool/sharp/smooth)
- Intensity (calm/moderate/intense/chaotic)

Respond in JSON format."""
    
    analysis = llm.generate_text(prompt)
    
    # Map to closest voice archetype
    return match_to_archetype(analysis)

def match_to_archetype(traits: dict) -> str:
    """Map traits to voice archetype (not exact clone)"""
    # Match based on energy + pacing + humor
    # Return archetype ID like "rapid_fire_comedian"
    from core.voice_styles import VOICE_STYLES
    
    # Simple matching logic
    for style_id, style in VOICE_STYLES.items():
        if (style.energy_level.value == traits['energy'] and
            style.pacing.value == traits['pacing']):
            return style_id
    
    return "warm_educator"  # Default fallback
```

**Supported Audio Formats:**

| Format | Status | Notes |
|--------|--------|-------|
| **.mp3** | ⚠️ Add | Whisper API supports |
| **.wav** | ⚠️ Add | Whisper API supports |
| **.m4a** | ⚠️ Add | Whisper API supports |
| **.ogg** | ⚠️ Add | Whisper API supports |

**Backend:** New fields:
- `audio_files: List[Path]`
- `audio_purpose: str` (transcribe or style_reference)
- `detected_style_traits: Optional[Dict]`

---

## Unified Source Material Input Structure

### Normalized Internal Format

```python
@dataclass
class SourceMaterialInput:
    """Normalized source material from any input method"""
    
    # Input metadata
    input_type: str  # "text", "file", "url", "audio"
    source_name: str  # User-provided or auto-generated
    raw_content: Optional[str] = None  # Original input
    
    # Extracted/processed content
    extracted_text: str = ""  # Final text for generation
    
    # Metadata
    file_type: Optional[str] = None  # pdf, docx, mp3, etc.
    url: Optional[str] = None
    audio_purpose: Optional[str] = None  # transcribe or style_reference
    
    # User instructions
    emphasis_instructions: Optional[str] = None
    target_audience: Optional[str] = None
    depth_preference: Optional[str] = None  # summary or deep_dive
    preserve_structure: bool = True
    add_commentary: bool = False
    
    # Audio style analysis (if applicable)
    detected_style: Optional[Dict] = None
    recommended_archetype: Optional[str] = None
```

### Processing Pipeline

```
User Input
  ↓
┌─────────────────────────────┐
│ Input Method Detection      │
├─────────────────────────────┤
│ • Pasted text?              │
│ • Uploaded file?            │
│ • Added URL?                │
│ • Uploaded audio?           │
└────────────┬────────────────┘
             ↓
┌─────────────────────────────┐
│ Content Extraction          │
├─────────────────────────────┤
│ • Text: Direct use          │
│ • File: Extract via library │
│ • URL: Fetch + parse        │
│ • Audio: Transcribe         │
└────────────┬────────────────┘
             ↓
┌─────────────────────────────┐
│ Normalization               │
├─────────────────────────────┤
│ Create SourceMaterialInput  │
│ with extracted_text         │
└────────────┬────────────────┘
             ↓
┌─────────────────────────────┐
│ Unified Generation Pipeline │
├─────────────────────────────┤
│ All modes consume           │
│ normalized source           │
└─────────────────────────────┘
```

---

## Topic Mode Enhancements

**Keep existing 4-field structure:**
1. Main Topic (required)
2. Topic Details / Context
3. Focus Areas (multi-line)
4. Desired Tone

**No changes needed** - already rich enough

---

## Multi-Character, Persona, Template Integration

### Connect to Source Material

**UI Addition:** "Use source material from Source Material tab"

```python
# In Multi-Character tab
use_source = st.checkbox("Use source material from Source Material tab")

if use_source:
    st.info("This podcast will incorporate source material you provided")
    # Context will include source_material field
```

**Backend:**
- Check if `source_material` field is populated in InputContext
- If yes, include in multi-character prompt:
  ```
  Generate a multi-character discussion about {topic}.
  
  Base the discussion on this source material:
  {source_material}
  
  Characters: ...
  ```

---

## Implementation Checklist

### Phase 1: Core Ingestion Enhancements

**1.1 Add File Type Support**
- [ ] Install python-docx library
- [ ] Install ebooklib library
- [ ] Create `extract_text_from_docx()` in source_management.py
- [ ] Create `extract_text_from_epub()` in source_management.py
- [ ] Create `extract_text_from_html()` in source_management.py
- [ ] Update file upload UI to accept new types

**1.2 Add Audio Support**
- [ ] Install openai (already exists) for Whisper
- [ ] Create `transcribe_audio()` in source_management.py
- [ ] Create `analyze_audio_style()` in source_management.py
- [ ] Create `match_to_archetype()` in voice_styles.py
- [ ] Add audio upload UI component
- [ ] Add purpose selector (transcribe vs style)

**1.3 Enhance URL Support**
- [ ] Keep existing YouTube + article support
- [ ] Add URL list management UI
- [ ] Add auto-detection display

### Phase 2: UI Redesign

**2.1 Remove Text Tab**
- [ ] Delete Tab 2 from step44_web_ui_refactored.py
- [ ] Update tab numbering

**2.2 Expand Source Material Tab**
- [ ] Add Section A: Paste Text (large textarea + options)
- [ ] Add Section B: Upload Files (multi-type support)
- [ ] Add Section C: Add Links (URL list)
- [ ] Add Section D: Upload Audio (with purpose selector)
- [ ] Add clear section headers/dividers

**2.3 Update Input Models**
- [ ] Add `audio_files` field to InputContext
- [ ] Add `audio_purpose` field
- [ ] Add `detected_style` field
- [ ] Remove TEXT mode enum (or deprecate)
- [ ] Merge text mode fields into SOURCE mode

### Phase 3: Backend Integration

**3.1 Unified Processing**
- [ ] Create `SourceMaterialInput` dataclass
- [ ] Create `normalize_source_inputs()` function
- [ ] Update UnifiedGenerationPipeline to handle merged mode

**3.2 Update Generation Logic**
- [ ] Merge _generate_text_script() into _generate_source_script()
- [ ] Add source material support to multi-character mode
- [ ] Add source material support to persona mode
- [ ] Add source material support to template mode

**3.3 Audio Style Integration**
- [ ] Connect detected style to voice assignment
- [ ] Override persona voice based on audio analysis
- [ ] Display recommended archetype in UI

### Phase 4: Testing

- [ ] Test paste text (5000+ chars)
- [ ] Test upload PDF
- [ ] Test upload DOCX (if added)
- [ ] Test upload EPUB (if added)
- [ ] Test YouTube URL
- [ ] Test article URL
- [ ] Test multiple URLs
- [ ] Test audio transcription
- [ ] Test audio style analysis
- [ ] Test multi-character with source material
- [ ] Test persona with source material

---

## Dependencies to Add

```txt
# requirements.txt additions

# Document processing
python-docx>=1.0.0        # For DOCX support
ebooklib>=0.18           # For EPUB support (optional)

# Audio (if not already present)
# openai>=1.0.0          # Already exists (includes Whisper)
```

---

## Migration Strategy

### Backward Compatibility

**Option 1: Deprecate TEXT mode gradually**
- Keep TEXT enum for now
- Map TEXT inputs to SOURCE internally
- Show deprecation warning

**Option 2: Remove TEXT mode immediately**
- Delete from InputContext
- Update all references
- Force users to Source Material tab

**Recommendation:** Option 2 (clean break)

### User Migration

**Old workflow:**
```
Tab 2 (Text) → Paste long text → Generate
```

**New workflow:**
```
Tab 2 (Source Material) → Section A: Paste Text → Generate
```

**User message:**
"Text mode has been merged into Source Material for a unified experience!"

---

## Timeline Estimate

| Phase | Tasks | Time |
|-------|-------|------|
| Phase 1.1 | File type support | 2 hours |
| Phase 1.2 | Audio support | 3 hours |
| Phase 1.3 | URL enhancements | 1 hour |
| Phase 2 | UI redesign | 3 hours |
| Phase 3 | Backend integration | 3 hours |
| Phase 4 | Testing | 2 hours |
| **Total** | | **14 hours** |

---

## Success Criteria

- [ ] 5 tabs instead of 6
- [ ] Source Material tab has 4 clear sections
- [ ] Can paste text (100+ chars)
- [ ] Can upload PDF, TXT, MD
- [ ] Can upload DOCX (stretch goal)
- [ ] Can add YouTube URL
- [ ] Can add article URL
- [ ] Can upload audio for transcription
- [ ] Can upload audio for style analysis
- [ ] Audio style maps to voice archetype
- [ ] Multi-character can use source material
- [ ] All inputs normalize to SourceMaterialInput
- [ ] Episode metadata tracks input type

---

## Next Steps

1. **Review this plan** - Approve or request changes
2. **Prioritize features** - Must-have vs nice-to-have
3. **Begin Phase 1.1** - Add file type support
4. **Build incrementally** - Test each phase
5. **Deploy UI changes** - Update refactored UI

**Status:** 📋 PLAN READY - Awaiting approval to proceed
