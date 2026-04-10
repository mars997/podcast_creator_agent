# 🎙️ AI Podcast Creator - Web UI

A beautiful, production-ready web interface for creating AI-powered podcasts from any content source.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red)

---

## 🚀 Quick Start

### Windows

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the UI
launch_ui.bat
```

### Mac/Linux

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the UI
streamlit run app.py
```

The UI will automatically open in your browser at **http://localhost:8501**

---

## ✨ Features

### 🎨 Three Creation Modes

#### 1. From Topic
- Enter any topic or idea
- AI generates complete podcast content
- Customize tone, length, and style
- Perfect for quick podcast creation

#### 2. From Sources
Combine multiple content sources:
- 📝 **Paste Text**: Articles, notes, transcripts
- 📎 **Upload Files**: PDF, DOCX, TXT, MD, HTML
- 🔗 **Add URLs**: Web articles and YouTube videos

#### 3. Multi-Character
- Create dynamic conversations
- 2-4 distinct speakers
- Multiple interaction styles (Interview, Debate, Comedy, Roundtable)
- Customizable character personalities

### 🎤 Voice Options

**OpenAI TTS** (Built-in)
- 6 high-quality voices
- Fast generation
- Included with OpenAI API

**ElevenLabs** (Premium)
- Studio-quality voices
- Voice cloning support
- Natural-sounding output
- Requires separate API key

### 📚 Episode Management

- Browse all generated episodes
- Search and filter
- Replay audio
- View scripts and show notes
- Access full metadata

### ⚙️ Settings & Configuration

- API key management
- Default preferences
- Output directory configuration
- System information dashboard

---

## 📋 Requirements

### Required
- Python 3.11 or higher
- OpenAI API key **OR** Google API key

### Optional
- ElevenLabs API key (for premium voices)

---

## 🔧 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/mars997/podcast_creator_agent.git
cd podcast_creator_agent
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure API Keys

Create a `.env` file in the project root:

```bash
# Required (choose at least one)
OPENAI_API_KEY=sk-your-key-here

# Optional (for premium voices)
ELEVENLABS_API_KEY=your-key-here
```

You can copy the example file:

```bash
cp .env.example .env
# Then edit .env with your API keys
```

### Step 4: Launch

**Windows:**
```bash
launch_ui.bat
```

**Mac/Linux:**
```bash
streamlit run app.py
```

---

## 💡 Usage Guide

### Creating a Topic Podcast

1. Navigate to **Create Podcast** → **From Topic**
2. Enter your topic (e.g., "The Future of Quantum Computing")
3. Add optional context and details
4. Choose tone, length, and style balance
5. Click **Generate Podcast**
6. Wait 30-60 seconds
7. Listen and download!

### Creating from Sources

1. Navigate to **Create Podcast** → **From Sources**
2. Add content using one or more methods:
   - **Paste**: Copy/paste text directly
   - **Upload**: Upload PDF, DOCX, or other files
   - **URLs**: Add web articles or YouTube links
3. Configure settings (tone, length, preserve structure)
4. Click **Generate Podcast**
5. Wait 1-3 minutes (depends on content size)
6. Listen and download!

### Creating Multi-Character Podcasts

1. Navigate to **Create Podcast** → **Multi-Character**
2. Enter discussion topic
3. Select number of characters (2-4)
4. Choose interaction style
5. Configure each character:
   - Name and role
   - Personality traits
   - Energy level
   - Speaking style
6. Click **Generate Multi-Character Podcast**
7. Listen to the conversation!

### Browsing History

1. Navigate to **Episode History**
2. Browse all generated episodes
3. Use search to find specific episodes
4. Click **Play** to listen
5. Click **Details** to view full information

---

## 🎯 Use Cases

### Education
- Convert lecture notes to audio
- Create study guides
- Generate topic overviews
- Review session podcasts

### Business
- Transform reports to briefings
- Create training materials
- Summarize meeting notes
- Generate product updates

### Content Creation
- Repurpose blog posts
- Create audio versions of articles
- Generate discussion content
- Produce news briefings

### Personal
- Learn about new topics
- Create custom news summaries
- Explore ideas through AI
- Personal knowledge management

---

## 📁 Output Structure

Each generated episode creates:

```
output/
└── topic_name_TIMESTAMP/
    ├── podcast.mp3        # Audio file
    ├── script.txt         # Full transcript
    ├── show_notes.txt     # Summary & key points
    └── metadata.json      # Episode details
```

Plus a global index:

```
output/
└── episode_index.json     # Catalog of all episodes
```

---

## 🔍 Advanced Features

### Voice Provider Selection

**When to use OpenAI:**
- Fast generation needed
- Good quality acceptable
- Limited budget

**When to use ElevenLabs:**
- Premium quality required
- Voice cloning needed
- Natural-sounding critical

### Content Optimization

**Best Practices:**

1. **Topic Mode**
   - Be specific with topics
   - Add context for better results
   - Use style slider wisely

2. **Sources Mode**
   - Combine complementary sources
   - Use "Preserve structure" for organized content
   - Paste most important content directly

3. **Multi-Character**
   - Give distinct personalities
   - Balance energy levels
   - Match interaction style to content

### Performance Tips

- Shorter podcasts generate faster
- Source mode takes longer with many sources
- ElevenLabs is slower but higher quality
- Large files (PDFs) increase processing time

---

## 🐛 Troubleshooting

### "No API keys configured"

**Solution:**
1. Create `.env` file
2. Add your API key:
   ```bash
   OPENAI_API_KEY=sk-...
   ```
3. Restart the UI

### Generation fails

**Check:**
- API key is valid
- API key has available credits
- Internet connection is stable
- Source URLs are accessible

### Slow generation

**Normal times:**
- Topic: 30-60 seconds
- Sources: 1-3 minutes
- Multi-character: 1-2 minutes

**If slower:**
- Check internet connection
- Reduce source content size
- Switch to OpenAI TTS (faster)

### Import errors

**Solution:**
```bash
# Run validation test
python test_ui_imports.py

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 🔐 Security & Privacy

- API keys stored in `.env` (not committed to git)
- Local generation (no data sent to third parties except AI providers)
- Episodes stored locally
- No tracking or analytics

**Never share your `.env` file or commit it to version control!**

---

## 🛠️ Technical Details

### Architecture

```
app.py                          # Main Streamlit application
├── Sidebar                     # Navigation & settings
│   ├── Provider selection
│   ├── Voice settings
│   └── Quick stats
├── Create Page                 # Podcast generation
│   ├── Topic mode
│   ├── Sources mode
│   └── Multi-character mode
├── History Page               # Episode management
│   ├── Browse episodes
│   ├── Search & filter
│   └── Episode details
└── Settings Page              # Configuration
    ├── API keys
    ├── Defaults
    └── System info
```

### Dependencies

**Core:**
- `streamlit` - Web framework
- `openai` - OpenAI API client
- `python-dotenv` - Environment management

**Content Processing:**
- `beautifulsoup4` - Web scraping
- `pypdf` - PDF extraction
- `youtube-transcript-api` - YouTube transcripts

**Audio:**
- `elevenlabs` - Premium TTS (optional)
- `pydub` - Audio processing

**Testing:**
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting

---

## 📞 Support

### Getting Help

1. **Check Documentation**
   - [Quick Start Guide](UI_QUICKSTART.md)
   - [Main README](README.md)
   - [Development Plan](docs/development_plan.md)

2. **Run Diagnostics**
   ```bash
   python test_ui_imports.py
   ```

3. **Check Error Messages**
   - UI shows detailed error information
   - Check browser console for JavaScript errors
   - Review terminal output for backend errors

### Common Issues

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| API key errors | Check `.env` file |
| Generation fails | Verify API credits |
| Slow performance | Reduce content size or switch provider |

---

## 🚀 Next Steps

### After First Use

1. ✅ Create your first podcast
2. ✅ Explore different modes
3. ✅ Try multi-character generation
4. ✅ Browse episode history
5. ✅ Customize settings

### Advanced Usage

- Experiment with voice providers
- Create custom personas (if using step44_web_ui_v2.py)
- Batch process multiple topics
- Integrate with existing workflows

---

## 📊 Performance Metrics

**Typical Generation Times:**

| Mode | Content Size | Time |
|------|--------------|------|
| Topic | N/A | 30-60s |
| Sources (text) | 1-5 pages | 1-2min |
| Sources (PDF) | 10-20 pages | 2-4min |
| Sources (URLs) | 1-3 articles | 1-3min |
| Multi-character | N/A | 1-2min |

*Times vary based on provider, content complexity, and internet speed*

---

## 🎓 Learning Resources

### Understanding the System

- **Core Modules**: See `CORE_FUNCTIONS_QUICK_REFERENCE.md`
- **Architecture**: See `docs/development_plan.md`
- **Provider System**: See `docs/multi_provider_guide.md`

### Best Practices

1. **Start simple** - Try topic mode first
2. **Iterate** - Refine based on results
3. **Experiment** - Try different tones and lengths
4. **Organize** - Use descriptive topics for easy browsing

---

## 🤝 Contributing

This is a demonstration project. For production use:

1. Review security settings
2. Add authentication if deploying publicly
3. Implement rate limiting
4. Add monitoring and logging
5. Consider cloud storage for episodes

---

## 📄 License

MIT License - See main repository for details

---

## 🎉 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [OpenAI](https://openai.com/) - AI models
- [ElevenLabs](https://elevenlabs.io/) - Premium TTS
- [Claude AI](https://anthropic.com/) - Development assistance

---

## 📧 Contact

For issues or questions, please refer to the main repository.

---

**Ready to create amazing podcasts? Launch the UI and get started!** 🎙️

```bash
streamlit run app.py
```
