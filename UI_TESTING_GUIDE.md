# UI Testing Guide - Step 44: Web UI

**Your Mission**: Manually test the Streamlit web interface and generate podcasts visually!

---

## 🚀 Quick Start

### 1. Install Streamlit (if not installed)

```bash
pip install streamlit
```

### 2. Launch the UI

```bash
streamlit run step44_web_ui.py
```

### 3. Open Browser

The UI will automatically open at: **http://localhost:8501**

If not, manually navigate to that URL.

---

## 🎮 What You Can Test

The UI has **4 main tabs**:

### Tab 1: 📝 Topic/Text (Simple Mode)
**Test this**:
1. Enter a topic (e.g., "Artificial Intelligence in Healthcare")
2. Optionally paste some source text
3. Configure voice, tone, length in sidebar
4. Click "Generate Simple Podcast"
5. Wait ~30-60 seconds
6. **Review**: Script appears, show notes appear, audio player loads
7. **Listen**: Click play on the audio

**Expected Output**: Complete episode in `output/` directory

---

### Tab 2: 👥 Multi-Character (Conversation Mode)
**Test this**:
1. Enter a discussion topic (e.g., "Ethics of AI")
2. Use slider to select 2-4 speakers
3. See character role preview
4. Click "Generate Multi-Character Podcast"
5. **Review**: Dialogue script with HOST:, GUEST: labels
6. **Listen**: Audio of the conversation

**Expected Output**: Multi-speaker episode

---

### Tab 3: 🎭 Persona Mode (Host Personality)
**Test this**:
1. Select a persona from dropdown
   - Try "Alex the Tech Enthusiast"
   - Or "Dr. Jordan"
2. Expand "Persona Details" to see personality
3. Enter a topic
4. Click "Generate Persona Podcast"
5. **Review**: Script should match persona's style
6. **Listen**: Audio in persona's voice

**Expected Output**: Persona-driven episode with `persona_profile.json`

---

### Tab 4: 📄 Template Mode (Structured Format)
**Test this**:
1. Select a template (e.g., "Solo Explainer")
2. Expand "Template Structure" to see format
3. Enter a topic
4. Click "Generate Template Podcast"
5. **Review**: Script follows template structure
6. **Listen**: Audio

**Expected Output**: Template-formatted episode

---

## ⚙️ Sidebar Configuration

**Always visible on left**:
- **AI Provider**: OpenAI or Gemini (if both configured)
- **Voice**: Select from available voices
- **Tone**: casual / professional / educational
- **Length**: short / medium / long

**Try different combinations!**

---

## 🧪 Suggested Test Scenarios

### Test 1: Quick Simple Podcast
- Tab: Topic/Text
- Topic: "The Future of Electric Vehicles"
- Tone: Professional
- Voice: Nova
- Length: Short
- **Expected time**: ~30 seconds

### Test 2: Tech Enthusiast Persona
- Tab: Persona Mode
- Persona: Alex the Tech Enthusiast
- Topic: "Quantum Computing Explained"
- **Check**: Script should be energetic and tech-focused

### Test 3: Interview Format
- Tab: Multi-Character
- Topic: "Climate Change Solutions"
- Speakers: 2 (HOST + GUEST)
- **Check**: Natural back-and-forth dialogue

### Test 4: News Template
- Tab: Template Mode
- Template: News Recap
- Topic: "AI Developments This Week"
- **Check**: News-style structure

---

## 📊 What to Look For

### ✅ Success Indicators
- Progress bar completes
- Green success message appears
- Script text displays
- Show notes display
- Audio player loads
- Can play audio file
- Episode directory created in `output/`

### ❌ Error Indicators
- Red error message
- Traceback displayed
- Generation hangs (>3 minutes)
- No audio player
- Empty script/show notes

---

## 🐛 Known Issues & Workarounds

### Issue: "No API keys configured"
**Fix**: Check `.env` file has valid `OPENAI_API_KEY`

### Issue: Generation takes too long
**Solution**: 
- Use "short" length
- This is normal for first-time generation
- Subsequent generations are faster

### Issue: Unicode characters in terminal
**Fix**: Ignore - UI handles this properly

### Issue: Audio doesn't play
**Check**:
- MP3 file exists in episode directory
- Browser supports MP3 playback
- Try downloading and playing locally

---

## 📁 Where Outputs Are Saved

All generated episodes go to:
```
output/[Topic_Name]_[Timestamp]/
├── script.txt
├── podcast_[voice].mp3
├── show_notes.txt
├── metadata.json
└── [step-specific files]
```

---

## 🎯 Testing Checklist

**Basic Functionality**:
- [ ] UI launches successfully
- [ ] Sidebar controls work
- [ ] All 4 tabs visible and switchable
- [ ] Can enter text in input fields
- [ ] Generate button clickable

**Simple Mode (Tab 1)**:
- [ ] Enter topic
- [ ] Paste source text (optional)
- [ ] Click generate
- [ ] Script appears
- [ ] Show notes appear
- [ ] Audio plays
- [ ] Episode saved to output/

**Multi-Character Mode (Tab 2)**:
- [ ] Select 2 speakers
- [ ] Character roles shown
- [ ] Generate multi-character dialogue
- [ ] Script has speaker labels (HOST:, GUEST:)
- [ ] Audio plays

**Persona Mode (Tab 3)**:
- [ ] Select persona
- [ ] View persona details
- [ ] Generate persona podcast
- [ ] Script matches personality
- [ ] Audio plays

**Template Mode (Tab 4)**:
- [ ] Select template
- [ ] View template structure
- [ ] Generate template podcast
- [ ] Script follows template format
- [ ] Audio plays

**Configuration (Sidebar)**:
- [ ] Can change voice
- [ ] Can change tone
- [ ] Can change length
- [ ] Settings apply to generation

---

## 📝 Manual Testing Report

**After testing, note**:

**What worked**:
- 

**What didn't work**:
-

**Favorite feature**:
-

**Suggestions**:
-

---

## 🔄 Re-running Tests

To test again:
1. Stop the server (Ctrl+C in terminal)
2. Re-run: `streamlit run step44_web_ui.py`
3. Browser auto-refreshes

Or just click "Rerun" button in top-right of UI.

---

## 🎬 Next Steps After Testing

1. Review generated episodes in `output/`
2. Listen to audio files
3. Check metadata.json files
4. Provide feedback on what worked/didn't work

---

**Ready to test!** Launch the UI and start creating podcasts visually! 🎙️

```bash
streamlit run step44_web_ui.py
```
