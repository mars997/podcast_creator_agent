# Created Persona Implementation Plan

## Overview
Implement a system that analyzes uploaded audio to extract speaking style traits and creates reusable custom personas (NOT voice cloning).

## Core Principle
**Style reference ONLY** - extract speaking patterns, energy, pacing, tone, etc., and map to existing voice archetypes. No exact voice cloning.

---

## Phase 1: Data Model & Storage

### Created Persona Data Model
```python
@dataclass
class CreatedPersona:
    persona_id: str
    persona_name: str
    persona_description: str
    reference_audio_filename: str
    voice_archetype: str  # Maps to VOICE_STYLES
    preferred_tts_voice: str  # e.g., "nova", "onyx"
    energy: str  # "low", "medium", "high"
    pacing: str  # "slow", "moderate", "fast"
    humor_level: str  # "none", "subtle", "moderate", "high"
    tone: str  # "warm", "professional", "energetic", etc.
    intensity: str  # "relaxed", "moderate", "intense"
    conversational_style: str  # "formal", "casual", "conversational"
    style_notes: str  # Free-form notes
    system_prompt_guidance: str  # For script generation
    created_by_user: str
    created_at: datetime
    last_modified: datetime
```

### Storage
- **File:** `personas/created_personas.json`
- **Format:** JSON array of Created Persona objects
- **Functions:**
  - `save_created_persona(persona: CreatedPersona)`
  - `load_created_personas() -> List[CreatedPersona]`
  - `get_created_persona(persona_id: str) -> CreatedPersona`
  - `update_created_persona(persona: CreatedPersona)`
  - `delete_created_persona(persona_id: str)`

---

## Phase 2: Audio Style Analysis Enhancement

### Enhanced analyze_audio_style()
Current: Returns basic traits (energy, pacing, humor, tone)
**New:** Return comprehensive style profile:

```python
def analyze_audio_style_detailed(audio_file: Path, api_key=None) -> Dict:
    """
    Enhanced audio style analysis for persona creation.
    
    Returns:
    {
        "energy": "high",
        "pacing": "fast",
        "humor_level": "moderate",
        "tone": "energetic",
        "intensity": "moderate",
        "conversational_style": "casual",
        "confidence": "high",
        "warmth": "moderate",
        "dramatic_level": "moderate",
        "voice_characteristics": {
            "pitch": "medium-high",
            "rhythm": "varied",
            "emphasis_pattern": "frequent"
        },
        "recommended_archetype": "rapid_fire_comedian",
        "recommended_tts_voice": "nova",
        "style_summary": "High-energy, fast-paced..."
    }
    ```

### Analysis Method
1. Transcribe audio (Whisper API)
2. Use LLM to analyze transcript for:
   - Speaking patterns
   - Word choice
   - Sentence structure
   - Emotional tone
   - Energy level
   - Pacing indicators
3. Map to existing voice archetypes
4. Recommend TTS voice

---

## Phase 3: UI Integration

### Source Material Tab - Section D Updates

**Current:**
```
Purpose:
○ Transcribe as source material
○ Use as speaking style reference
○ Clone voice for podcast generation
```

**New:**
```
Purpose:
○ Transcribe as source material
○ Analyze style and create persona ← NEW
```

### Persona Creation Flow

When "Analyze style and create persona" selected:

1. **Upload audio** → Show progress
2. **Analyze** → Display extracted traits
3. **Preview & Edit:**
   ```
   ┌─────────────────────────────────────┐
   │ Create Persona from Audio           │
   ├─────────────────────────────────────┤
   │ Persona Name: [New Energetic Host ] │
   │ Description: [Auto-filled...      ] │
   │                                     │
   │ Detected Style:                     │
   │ ✓ Energy: High                      │
   │ ✓ Pacing: Fast                      │
   │ ✓ Humor: Moderate                   │
   │ ✓ Tone: Energetic                   │
   │ ✓ Archetype: rapid_fire_comedian    │
   │ ✓ TTS Voice: nova                   │
   │                                     │
   │ [Edit Traits] [Save Persona] [Cancel]
   └─────────────────────────────────────┘
   ```

4. **Save** → Add to persona library
5. **Success** → "Persona saved! Use in Persona Mode."

---

## Phase 4: Persona Mode Integration

### Updated Persona Selection

**Current:**
- Dropdown with built-in personas

**New:**
```
Persona Selection:
├── Built-in Personas
│   ├── Documentary Narrator
│   ├── Calm Educator
│   └── ...
├── Created Personas ← NEW SECTION
│   ├── My Energetic Host
│   ├── Professional Analyst
│   └── [+ Create New from Audio]
```

### Persona Details Display
When created persona selected:
```
📝 Created Persona: "My Energetic Host"
   Created: 2026-04-08
   Based on: reference_audio.mp3
   
   Style: High energy, fast pacing, moderate humor
   Voice: nova (rapid_fire_comedian archetype)
   
   [Edit] [Delete] [Test Preview]
```

---

## Phase 5: Multi-Character Integration

### Created Personas in Character Assignment

Allow created personas as character options:

```python
# Example: Multi-Character with created persona
characters = [
    Character(
        name="Alex",
        role="Host",
        persona="created_persona_energetic_host",  # Reference to created persona
        background="Enthusiastic podcast host"
    ),
    Character(
        name="Sam",
        role="Expert",
        persona="calm_educator",  # Built-in persona
        background="Subject matter expert"
    )
]
```

---

## Phase 6: Implementation Files

### New Files
1. **`core/created_personas.py`** - Data model and storage
2. **`core/audio_style_analyzer.py`** - Enhanced analysis
3. **`ui/persona_creator.py`** - UI component for creation
4. **`personas/created_personas.json`** - Storage file

### Modified Files
1. **`step44_web_ui_v2.py`** - UI integration
2. **`core/source_management.py`** - Audio processing routing
3. **`step32_voice_persona_system.py`** - Persona library expansion
4. **`core/unified_generation.py`** - Created persona support

---

## Implementation Steps

### Step 1: Data Model (core/created_personas.py)
- [x] Define CreatedPersona dataclass
- [ ] Implement save/load functions
- [ ] Implement CRUD operations
- [ ] Add validation

### Step 2: Enhanced Audio Analysis (core/audio_style_analyzer.py)
- [ ] Implement detailed style extraction
- [ ] LLM-based trait analysis
- [ ] Archetype mapping algorithm
- [ ] TTS voice recommendation

### Step 3: Storage System
- [ ] Create `personas/` directory
- [ ] Implement JSON persistence
- [ ] Add migration for existing data
- [ ] Add backup/restore

### Step 4: UI - Persona Creator (ui/persona_creator.py)
- [ ] Analysis progress display
- [ ] Trait preview/edit form
- [ ] Save confirmation
- [ ] Error handling

### Step 5: UI - Integration (step44_web_ui_v2.py)
- [ ] Add "Create persona" option to audio upload
- [ ] Integrate persona creator component
- [ ] Update Persona Mode dropdown
- [ ] Add created persona management

### Step 6: Persona Mode Updates (step32_voice_persona_system.py)
- [ ] Load created personas alongside built-in
- [ ] Support created persona selection
- [ ] Apply created persona traits to generation

### Step 7: Multi-Character Updates
- [ ] Add created personas to character options
- [ ] Support mixed built-in + created personas

### Step 8: Testing
- [ ] Test persona creation flow
- [ ] Test saving/loading
- [ ] Test usage in Persona Mode
- [ ] Test usage in Multi-Character Mode
- [ ] Test editing/deletion

---

## Safety & Ethics

### Style Reference Only
- ✅ Extract speaking patterns, NOT voice identity
- ✅ Map to existing TTS voices
- ✅ No biometric voice cloning
- ✅ Clear user messaging: "Style reference, not voice clone"

### User Consent
- Require explicit opt-in for persona creation
- Show what data is being extracted
- Allow deletion of created personas
- Don't store raw audio (only traits)

### Transparency
```
⚠️ Creating Persona from Audio

This will analyze the speaking STYLE from your audio:
✓ Energy, pacing, tone, humor
✓ Mapped to existing voice archetypes
✗ NOT cloning the exact voice
✗ NOT recreating speaker identity

The persona will use our standard TTS voices
configured to match the detected style.

[Cancel] [I Understand, Proceed]
```

---

## Example Workflow

1. **User uploads** 30-second audio clip
2. **System analyzes** → "High energy, fast pacing, warm tone"
3. **System suggests:** "This matches 'rapid_fire_comedian' archetype, using 'nova' voice"
4. **User edits:** Changes name to "My Morning Show Host"
5. **User saves** → Persona added to library
6. **Later use:** Select "My Morning Show Host" in Persona Mode
7. **Generation:** Script generated with energetic style, audio uses 'nova' voice at faster speed

---

## Success Metrics

- ✅ Users can create personas from audio in < 2 minutes
- ✅ Created personas appear in Persona Mode dropdown
- ✅ Personas persist across sessions
- ✅ Style traits accurately reflected in generated content
- ✅ No voice cloning - only style mapping
- ✅ Users can edit/delete personas
- ✅ Works seamlessly with Multi-Character mode

---

## Status

**Phase:** Planning Complete  
**Next:** Implement Phase 1 (Data Model)  
**Timeline:** 4-6 hours total implementation
