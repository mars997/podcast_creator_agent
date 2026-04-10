# AI Podcast Creator - UI Quick Start Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create or edit your `.env` file:

```bash
# Required (choose one or both)
OPENAI_API_KEY=sk-...

# Optional (for premium voices)
ELEVENLABS_API_KEY=...
```

### 3. Launch the UI

```bash
streamlit run app.py
```

The UI will open in your browser at: **http://localhost:8501**

---

## 📖 User Guide

### Creating Your First Podcast

The UI has **3 creation modes**:

#### 1. 📝 From Topic
- Enter any topic or idea
- Add optional context and details
- Choose tone, length, and style
- Click "Generate Podcast"

**Example:**
- Topic: "The Future of Renewable Energy"
- Context: "Focus on solar and wind power breakthroughs in 2026"
- Tone: Professional
- Length: Medium

#### 2. 📚 From Sources
Create podcasts from existing content using three input methods:

**A. Paste Text**
- Copy/paste articles, notes, or any text content
- Great for newsletters, blog posts, documentation

**B. Upload Files**
- PDF, TXT, DOCX, MD, HTML supported
- Upload multiple files to combine content

**C. Add URLs**
- Web articles: Automatically extracts content
- YouTube videos: Fetches transcripts
- Multiple URLs supported

**Settings:**
- Choose tone and length
- Enable "Preserve structure" to keep original flow

#### 3. 👥 Multi-Character
Create dynamic conversations with 2-4 speakers:

**Setup:**
1. Enter discussion topic
2. Choose number of characters (2-4)
3. Select interaction style:
   - Interview: Host + Guest Q&A
   - Debate: Opposing viewpoints
   - Comedy Banter: Playful conversation
   - Roundtable: Panel discussion

**Character Configuration:**
- Name and role
- Personality traits
- Energy level
- Speaking style

---

## 📚 Episode History

View and manage all your generated podcasts:

**Features:**
- Browse all episodes
- Search by topic, mode, or ID
- Sort by date or alphabetically
- Play audio directly
- View scripts and show notes
- Access full metadata

**Actions:**
- Click "▶️ Play" to listen
- Click "📊 Details" to view full episode info
- Use search to find specific episodes

---

## ⚙️ Settings

Configure your podcast creator:

### API Keys
- View connection status
- Instructions for adding keys to `.env`

### Default Settings
- Set preferred tone
- Set default length

### Output Settings
- Configure where episodes are saved
- View current output directory

### System Info
- View total episodes created
- Check storage usage
- See system versions

---

## 🎨 Features

### Voice Options

**OpenAI TTS (Default):**
- alloy, echo, fable, onyx, nova, shimmer
- Good quality, fast generation
- Included with OpenAI API key

**ElevenLabs (Premium):**
- Higher quality voices
- Custom voice cloning
- More natural-sounding
- Requires ELEVENLABS_API_KEY

### Podcast Modes

| Mode | Best For | Features |
|------|----------|----------|
| Topic | Quick ideas, research topics | AI generates all content |
| Sources | Existing content | Upload/paste/link content |
| Multi-Character | Conversations, debates | Multiple distinct speakers |

### Output Files

Each episode generates:
- 🎧 **podcast.mp3** - Audio file
- 📝 **script.txt** - Full transcript
- 📋 **show_notes.txt** - Summary and key points
- 📊 **metadata.json** - Episode details

---

## 💡 Tips & Best Practices

### For Best Results

**Topic Mode:**
- Be specific with your topic
- Add context in the "Additional Context" field
- Use the style slider to balance fun vs. serious

**Sources Mode:**
- Combine multiple sources for richer content
- Paste the most important content directly
- Use "Preserve structure" for well-organized source material

**Multi-Character Mode:**
- Give characters distinct personalities
- Choose complementary energy levels
- Match interaction style to your content

### Content Guidelines

**Good Topics:**
- "How quantum computing will change cryptography by 2030"
- "The rise of vertical farming in urban areas"
- "Understanding the James Webb Space Telescope discoveries"

**Good Source Material:**
- Research papers or summaries
- News articles
- Technical documentation
- Meeting transcripts
- Book chapters

### Voice Selection

**Choose voice provider based on:**
- **OpenAI**: Fast, reliable, good for most use cases
- **ElevenLabs**: Premium quality, custom voices, longer processing

---

## 🐛 Troubleshooting

### "No API keys configured"
**Solution:** Add API keys to `.env` file:
```bash
OPENAI_API_KEY=sk-...
```

### Generation fails
**Check:**
1. API key is valid and has credits
2. Internet connection is active
3. Source content is accessible (for URLs)
4. File uploads are valid formats

### Audio not playing
**Try:**
1. Refresh the page
2. Check if file exists in episode folder
3. Ensure browser supports MP3 playback

### Slow generation
**Normal times:**
- Topic mode: 30-60 seconds
- Sources mode: 1-3 minutes (depending on content size)
- Multi-character: 1-2 minutes

**If slower:**
- Large source files take longer
- ElevenLabs is slower than OpenAI TTS
- Check your internet connection

---

## 📁 File Structure

```
podcast_creator_agent/
├── app.py                  # Main UI application
├── output/                 # Generated episodes
│   ├── episode_index.json  # Episode catalog
│   └── topic_name_TIMESTAMP/
│       ├── podcast.mp3
│       ├── script.txt
│       ├── show_notes.txt
│       └── metadata.json
├── core/                   # Core functionality
├── providers/              # AI provider integrations
└── .env                    # API keys (create this)
```

---

## 🎯 Use Cases

### Education
- Convert course notes into study podcasts
- Create review sessions from textbooks
- Generate topic overviews

### Business
- Transform reports into audio briefings
- Create training materials
- Summarize meeting notes

### Content Creation
- Repurpose blog posts as podcasts
- Create audio versions of articles
- Generate discussion content

### Personal
- Learn about new topics
- Create custom news briefings
- Explore ideas through AI conversation

---

## 🔗 Resources

- **Main README**: `README.md`
- **Step Tracker**: `docs/step_tracker.md`
- **Development Plan**: `docs/development_plan.md`
- **Core Functions**: `CORE_FUNCTIONS_QUICK_REFERENCE.md`

---

## 📞 Support

For issues or questions:
1. Check this guide
2. Review error messages in the UI
3. Check `CLAUDE.md` for project guidelines
4. Review episode metadata for debugging info

---

## 🎉 Getting Started Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file with API keys
- [ ] Launch UI: `streamlit run app.py`
- [ ] Create your first podcast
- [ ] Explore different creation modes
- [ ] Check Episode History
- [ ] Customize settings

**Ready to create amazing podcasts!** 🎙️
