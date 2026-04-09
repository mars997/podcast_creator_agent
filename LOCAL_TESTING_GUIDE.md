# Local Testing Guide - Refactored Podcast Creator

## Quick Start

### 1. Launch the New UI

```bash
streamlit run step44_web_ui_refactored.py
```

Browser opens at: **http://localhost:8501**

---

## Testing Checklist

### ✅ Tab 1: Topic Mode

**Test Scenario:** Enhanced topic with all 4 fields

1. Enter **Main Topic:** "The Future of Electric Vehicles"
2. Enter **Topic Details:**
   ```
   Focus on recent battery technology breakthroughs and their impact on range anxiety. 
   Compare current EV adoption rates across different regions.
   ```
3. Enter **Focus Areas:**
   ```
   - Solid-state battery developments
   - Charging infrastructure expansion
   - Price parity with gas vehicles
   - Environmental impact comparison
   ```
4. Enter **Desired Style:** "optimistic but realistic"
5. Click **Generate Topic Podcast**

**Expected:**
- Script covers all 4 focus areas
- Optimistic tone throughout
- Context from topic details integrated
- ~500-700 words (medium length)
- Audio file generated

---

### ✅ Tab 2: Text Mode

**Test Scenario:** Long-form article conversion

1. Paste this sample text (or any 500+ word article):
   ```
   Artificial intelligence is transforming healthcare in unprecedented ways.
   From diagnostic imaging to drug discovery, AI systems are demonstrating 
   capabilities that augment and sometimes surpass human expertise.

   In radiology, deep learning models can now detect patterns in X-rays and 
   MRI scans with accuracy comparable to experienced radiologists. These 
   systems analyze thousands of images to learn subtle indicators of disease 
   that might escape human observation.

   [Add more paragraphs to reach 500+ words]
   ```

2. Check **Preserve original structure**
3. Leave **Add commentary** unchecked
4. Click **Generate Text Podcast**

**Expected:**
- Script follows original structure
- Key facts preserved
- Conversational audio-friendly language
- Character/word count displayed before generation

---

### ✅ Tab 3: Source Material Mode

**Test Scenario:** Business report coverage

1. Create a test file `test_source.txt`:
   ```
   Q1 2026 SALES REPORT
   
   Total Revenue: $2.3M (up 18% from Q4 2025)
   New Customers: 145 (target was 120)
   Customer Retention: 94% (industry avg: 85%)
   
   Top Performing Products:
   - Product A: $890K revenue
   - Product B: $640K revenue
   - Product C: $520K revenue
   
   Challenges:
   - Supply chain delays affecting Product D
   - Increased competition in mid-market segment
   
   Q2 Goals:
   - Launch Product E beta
   - Expand into EMEA region
   - Improve customer onboarding (currently 6 days avg)
   ```

2. Upload the file **OR** paste directly
3. **Source Title:** "Q1 2026 Sales Report"
4. **Target Audience:** "Business Leaders"
5. **Coverage Depth:** "Summary"
6. **Emphasis:** "Focus on wins and Q2 goals"
7. Click **Generate Source-Based Podcast**

**Expected:**
- Summary-level coverage (high-level)
- Business-friendly language
- Emphasis on wins and Q2 goals
- Audience-appropriate depth

---

### ✅ Tab 4: Multi-Character Mode

**Test Scenario:** 3-character debate

1. **Topic:** "Should AI Art Be Copyrightable?"
2. **Number of Characters:** 3
3. **Interaction Style:** "Debate (opposing viewpoints)"
4. **Configure Characters:**

   **Character 1:**
   - Name: "Moderator Jane"
   - Role: Moderator
   - Personality: "neutral and balanced"
   - Speaking Style: "asks clarifying questions"
   - Energy: Medium
   - Voice: nova
   - Humor: None

   **Character 2:**
   - Name: "Artist Pro"
   - Role: Guest
   - Personality: "passionate about creator rights"
   - Speaking Style: "uses artist examples"
   - Energy: High
   - Voice: echo
   - Humor: Witty

   **Character 3:**
   - Name: "Tech Advocate"
   - Role: Expert
   - Personality: "forward-thinking technologist"
   - Speaking Style: "data-driven arguments"
   - Energy: Medium
   - Voice: fable
   - Humor: Dry

5. Click **Generate Multi-Character Podcast**

**Expected:**
- Script with 3 distinct speaker labels
- Debate-style structure (moderator + opposing views)
- Each character's personality evident in dialogue
- Voice assignments saved to `voice_assignments.txt`
- Check `output/{episode}/voice_assignments.txt`

---

### ✅ Tab 5: Persona Mode

**Test Scenario 1:** Existing persona

1. **Persona Category:** "🎓 Informative & Educational"
2. **Select Persona:** "The Documentary Sage (documentary_narrator)"
3. Expand **Persona Details** - review energy, humor, pacing
4. **Topic:** "The Life Cycle of Ocean Currents"
5. **Fun ↔ Serious Balance:** 0.7 (more serious)
6. Click **Generate Persona Podcast**

**Expected:**
- Calm, wonder-filled tone
- Documentary-style narration
- Catchphrases like "Remarkable", "Consider, if you will"
- Slow pacing
- Persona profile saved to `persona_profile.json`

**Test Scenario 2:** Custom persona

1. **Persona Category:** "✨ Custom"
2. **Select Persona:** "➕ Create Your Own"
3. **Persona Name:** "The Data Detective"
4. **Description:** "Analytical investigator who loves uncovering insights hidden in data. Speaks like a detective solving a mystery."
5. **Energy:** Moderate
6. **Humor Style:** Dry
7. **Pacing:** Moderate
8. **Tone:** Professional
9. **Topic:** "Uncovering Patterns in Consumer Behavior"
10. Click **Generate Persona Podcast**

**Expected:**
- Script in "detective investigating data" style
- Custom persona created and used
- Professional tone with dry humor
- Custom persona saved

---

### ✅ Tab 6: Template Mode

**Test Scenario:** Debate template

1. **Template Category:** "💬 Conversational"
2. **Select Template:** "Debate Match - Two opposing viewpoints with..."
3. Expand **Template Structure** - review speaker count, roles, structure
4. **Topic:** "Universal Basic Income: Necessity or Liability?"
5. Click **Generate Template Podcast**

**Expected:**
- Script follows debate structure
- 3 speakers: MODERATOR, PRO_SIDE, CON_SIDE
- Opening statements → Arguments → Rebuttals → Closing
- Moderator stays neutral
- Structured, balanced format

---

## Verification Steps

After each generation, verify:

### 1. Episode Directory Created
```
output/{topic}_{timestamp}/
├── script.txt                 # Generated script
├── show_notes.txt             # Show notes
├── podcast_{voice}.mp3        # Audio file
├── metadata.json              # Full metadata
├── voice_assignments.txt      # (multi-character only)
└── persona_profile.json       # (persona mode only)
```

### 2. Metadata Includes Mode-Specific Fields

**Topic Mode:**
- `topic_details`
- `focus_areas`
- `desired_style`

**Multi-Character:**
- `num_characters`
- `characters[]`
- `interaction_style`
- `voice_assignments`

**Persona:**
- `persona{}`
- `fun_vs_serious`

**Source:**
- `source_title`
- `target_audience`
- `depth_preference`

### 3. Audio Plays
- Click audio player in UI
- Or open MP3 file directly from episode directory

### 4. Episode Index Updated
```
output/episode_index.json
```
Should contain new episode entry

---

## Automated Testing

Run full test suite:

```bash
python test_refactored_system.py
```

**Expected Output:**
```
[PASS] topic_mode
[PASS] text_mode
[PASS] source_mode
[PASS] multi_character_mode
[PASS] persona_mode
[PASS] template_mode

Passed: 6/6
```

---

## Troubleshooting

### Issue: "No API keys configured"
**Fix:** Check `.env` file:
```
OPENAI_API_KEY=sk-...
```

### Issue: Generation fails with error
**Check:**
1. API key is valid
2. Internet connection active
3. Error details in expandable section of UI

### Issue: Audio file not playing
**Try:**
1. Download MP3 and play locally
2. Check file size > 0 bytes
3. Verify API has TTS access

### Issue: Custom persona doesn't save
**Ensure:**
1. Both Name and Description filled
2. Click Generate button
3. Check episode directory for `persona_profile.json`

### Issue: Multi-character voices all sound same
**Note:** 
- Multi-voice rendering not yet implemented
- Voice assignments ARE saved to `voice_assignments.txt`
- Future Phase 2 will render separate voices

---

## Performance Expectations

| Mode | Average Time | Script Length | Audio Length |
|------|--------------|---------------|--------------|
| Topic (short) | 20-30s | ~400 words | ~2 min |
| Topic (medium) | 30-45s | ~600 words | ~3.5 min |
| Topic (long) | 45-60s | ~900 words | ~5 min |
| Text | 30-50s | Varies | Varies |
| Source | 35-55s | Varies | Varies |
| Multi-Character | 40-60s | ~600 words | ~3.5 min |
| Persona | 30-50s | ~600 words | ~3.5 min |
| Template | 35-55s | ~600 words | ~3.5 min |

*Times include LLM generation + TTS rendering*

---

## What to Look For

### Good Signs ✅
- Script incorporates all input fields
- Character personalities distinct in dialogue
- Persona catchphrases appear
- Template structure followed
- Audio sounds natural
- Metadata complete

### Issues to Report ❌
- Script ignores input fields
- Characters sound identical
- Persona doesn't match description
- Template structure not followed
- Audio cuts off or distorted
- Missing metadata fields

---

## Next Steps After Testing

1. **Review generated episodes** in `output/` directory
2. **Listen to audio files** - check quality and adherence to style
3. **Compare modes** - which modes work best for different use cases
4. **Try edge cases:**
   - Very long text (5000+ chars)
   - 5 characters with different voices
   - Custom persona with extreme settings
   - Multiple focus areas (10+)

5. **Provide feedback:**
   - Which personas are most engaging?
   - Which templates are most useful?
   - What interaction styles work best?
   - Any bugs or unexpected behavior?

---

## Quick Reference

### Launch Refactored UI
```bash
streamlit run step44_web_ui_refactored.py
```

### Run Tests
```bash
python test_refactored_system.py
```

### Check Episode Output
```bash
cd output
ls -lt  # View recent episodes (newest first)
```

### Play Audio
```bash
# Example
"output/Quantum_Computing_Basics_2026-04-08_165349/podcast_alloy.mp3"
```

---

**Ready to test!** Start with Topic Mode and work through all 6 tabs. 🎙️
