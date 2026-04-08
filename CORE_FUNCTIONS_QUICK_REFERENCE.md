# Core Functions Quick Reference - Steps 1-20

**Quick Guide**: How to achieve all Steps 1-20 functionality using ONLY core module functions.

---

## Step 1: Environment Setup

```python
import config

# Access configuration
tone = config.DEFAULT_TONE           # "educational"
length = config.DEFAULT_LENGTH       # "medium"
output = config.OUTPUT_ROOT          # "output"
tones = config.VALID_TONES          # {'casual', 'professional', 'educational'}
lengths = config.VALID_LENGTHS      # {'short', 'medium', 'long'}
```

---

## Step 2: Initialize Providers

```python
from core.provider_setup import initialize_providers, get_provider_info

# Initialize LLM and TTS providers
llm_provider, tts_provider = initialize_providers(verbose=True)

# Get provider information
provider_info = get_provider_info(llm_provider, tts_provider)
# Returns: {'llm': {...}, 'tts': {...}}
```

---

## Step 3: Generate Script

```python
from core.content_generation import build_script

# Generate podcast script
script = build_script(
    llm_provider=llm_provider,
    topic="AI Trends",
    tone="educational",
    word_range="300 to 500 words",
    source_material=None  # Optional: provide source text
)
```

---

## Step 4: Save Script to File

```python
from core.file_utils import save_text_file, ensure_directory
from pathlib import Path

# Ensure directory exists
output_dir = ensure_directory(Path("output"))

# Save script
script_file = output_dir / "script.txt"
save_text_file(script, script_file)
```

---

## Step 5: End-to-End (Script + Notes + Audio)

```python
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import validate_choice, get_word_range
import config

# Validate inputs
tone = validate_choice("casual", config.VALID_TONES, "tone")
voice = validate_choice("nova", set(tts_provider.available_voices), "voice")
length = validate_choice("medium", config.VALID_LENGTHS, "length")
word_range = get_word_range(length)  # "500 to 700 words"

# Generate content
script = build_script(llm_provider, topic, tone, word_range)
show_notes = build_show_notes(llm_provider, script)
audio_file = Path("output/podcast.mp3")
generate_audio(tts_provider, script, voice, audio_file)
```

---

## Step 6: Episode Packaging (Folders)

```python
from core.file_utils import ensure_directory
from core.validation import sanitize_filename
from pathlib import Path

# Create episode folder
topic = "AI Trends"
safe_topic = sanitize_filename(topic)  # "AI_Trends"

output_root = Path("output")
episode_dir = ensure_directory(output_root / safe_topic)
# Creates: output/AI_Trends/

# Save files
save_text_file(script, episode_dir / "script.txt")
save_text_file(show_notes, episode_dir / "show_notes.txt")
```

---

## Step 7: User Customization

```python
from core.user_input import get_user_input
from core.validation import validate_choice, get_word_range

# Get user input with defaults
tone = get_user_input("Choose tone", config.DEFAULT_TONE)
voice = get_user_input("Choose voice", "nova")
length = get_user_input("Choose length", config.DEFAULT_LENGTH)

# Validate
tone = validate_choice(tone, config.VALID_TONES, "tone")
voice = validate_choice(voice, set(tts_provider.available_voices), "voice")
length = validate_choice(length, config.VALID_LENGTHS, "length")

# Get word range
word_range = get_word_range(length)  # Returns appropriate range
```

---

## Step 8: Single Source File

```python
from core.file_utils import read_text_file
from pathlib import Path

# Read source file
source_file = Path("source.txt")
content = read_text_file(source_file)

# Use as source material
script = build_script(llm_provider, topic, tone, word_range, content)
```

---

## Step 9: Multiple Source Files

```python
from core.file_utils import read_text_file
from pathlib import Path

# Read multiple files
files = [Path("source.txt"), Path("source2.txt")]
all_content = []

for file_path in files:
    content = read_text_file(file_path)
    all_content.append(content)

# Combine sources
combined = "\n\n".join(all_content)

# Use combined content
script = build_script(llm_provider, topic, tone, word_range, combined)
```

---

## Step 10: URL Parsing

```python
from core.source_management import parse_csv_input, fetch_article_text

# Parse comma-separated URLs
url_input = "url1, url2, url3"
urls = parse_csv_input(url_input)  # ['url1', 'url2', 'url3']

# Fetch article from URL
article_text = fetch_article_text("https://example.com/article")
# Returns formatted text with title, URL, and content
```

---

## Step 11: Config-Based App

```python
import config

# Access provider models
provider_models = config.PROVIDER_MODELS
# Returns: {'openai': {...}, 'gemini': {...}}

# Get OpenAI config
openai_config = config.PROVIDER_MODELS['openai']
llm_model = openai_config['llm_model']      # 'gpt-4.1-mini'
tts_model = openai_config['tts_model']      # 'gpt-4o-mini-tts'
voices = openai_config['voices']            # ['alloy', 'echo', ...]

# Get word ranges
word_ranges = config.WORD_RANGES
# Returns: {'short': '300 to 450', 'medium': '500 to 700', 'long': '800 to 1000'}
```

---

## Step 12-13: Hybrid/Mixed Sources (URLs + Files)

```python
from core.source_management import parse_csv_input, save_sources_to_directory
from pathlib import Path

# Parse inputs
url_input = "url1, url2"
file_input = "file1.txt, file2.txt"

urls = parse_csv_input(url_input) if url_input else None
file_paths = [Path(p) for p in parse_csv_input(file_input)] if file_input else None

# Save all sources to directory
sources_dir = Path("output/episode/sources")
all_sources = []

successful, failed = save_sources_to_directory(
    sources_dir=sources_dir,
    sources=all_sources,  # Will be populated
    urls=urls,
    files=file_paths
)

# Use combined sources
combined = "\n\n".join(all_sources)
script = build_script(llm_provider, topic, tone, word_range, combined)
```

---

## Step 14: Episode Metadata

```python
from core.episode_management import save_episode_metadata
from core.provider_setup import get_provider_info
from datetime import datetime
from pathlib import Path

# Create metadata
metadata = {
    "created_at": datetime.now().isoformat(),
    "topic": topic,
    "tone": tone,
    "voice": voice,
    "length": length,
    "word_range_target": word_range,
    "providers": get_provider_info(llm_provider, tts_provider),
    "models": {
        "script_model": llm_provider.model_name,
        "tts_model": tts_provider.model_name
    },
    "outputs": {
        "episode_dir": str(episode_dir),
        "script_file": str(script_file),
        "show_notes_file": str(show_notes_file),
        "audio_file": str(audio_file)
    }
}

# Save metadata
episode_dir = Path("output/episode")
metadata_file = save_episode_metadata(episode_dir, metadata)
# Creates: output/episode/metadata.json
```

---

## Step 15: Episode Index

```python
from core.episode_management import (
    create_episode_summary,
    update_episode_index,
    load_episode_index
)
from pathlib import Path

# Create episode summary from metadata
episode_summary = create_episode_summary(
    metadata=metadata,
    episode_dir=episode_dir,
    additional_fields={
        "num_successful_urls": 2,
        "num_successful_files": 1
    }
)

# Update global episode index
index_file = Path("output/episode_index.json")
update_episode_index(index_file, episode_summary)

# Load episode index
episodes = load_episode_index(index_file)
print(f"Total episodes: {len(episodes)}")
```

---

## Step 16: Unique Episode IDs

```python
from core.episode_management import create_episode_directory
from pathlib import Path

# Create unique episode directory with timestamp
output_root = Path("output")
topic = "AI Trends"

episode_dir, episode_id = create_episode_directory(output_root, topic)
# Creates: output/AI_Trends_2026-04-08_123456/
# Returns: (Path(...), "AI_Trends_2026-04-08_123456")

print(f"Episode ID: {episode_id}")
print(f"Episode Dir: {episode_dir}")

# Add episode_id to metadata
metadata["episode_id"] = episode_id
```

---

## Step 17: Episode Browser

```python
from core.episode_management import load_episode_index
from core.episode_browser import (
    display_episode_list,
    display_episode_details,
    view_file_content,
    format_episode_summary
)
from pathlib import Path

# Load episode index
index_file = Path("output/episode_index.json")
episodes = load_episode_index(index_file)

# Display all episodes
display_episode_list(episodes)

# Display specific episode details
episode = episodes[0]
display_episode_details(episode)

# View episode file
script_file = Path(episode['script_file'])
view_file_content(script_file, max_lines=50)

# Format episode summary
summary = format_episode_summary(episode, index=0)
print(summary)
```

---

## Step 18: Regenerate Episode

```python
from core.episode_regenerator import regenerate_episode
from core.episode_management import load_episode_metadata
from pathlib import Path

# Load original episode metadata
metadata_file = Path("output/episode/metadata.json")
metadata = load_episode_metadata(metadata_file)

# Get original episode directory
episode_dir = Path("output/episode")

# Regenerate episode
output_root = Path("output")
index_file = output_root / "episode_index.json"

new_dir, new_id = regenerate_episode(
    original_metadata=metadata,
    episode_dir_path=episode_dir,
    llm_provider=llm_provider,
    tts_provider=tts_provider,
    output_root=output_root,
    index_path=index_file
)

print(f"New episode created: {new_id}")
print(f"Location: {new_dir}")
```

---

## Step 19: RSS Feed

```python
from core.rss_utils import parse_rss_feed, save_rss_info
from pathlib import Path

# Parse RSS feed
feed_url = "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
articles = parse_rss_feed(feed_url, max_items=10)
# Returns: [{'title': ..., 'link': ..., 'description': ..., ...}, ...]

print(f"Fetched {len(articles)} articles")

# Save RSS info to episode sources
sources_dir = Path("output/episode/sources")
rss_info_file = save_rss_info(
    sources_dir=sources_dir,
    feed_url=feed_url,
    articles=articles
)
# Creates: output/episode/sources/rss_feed_info.json

# Use article content
article_texts = []
for article in articles:
    text = f"Title: {article['title']}\n\n{article['description']}"
    article_texts.append(text)

combined = "\n\n".join(article_texts)
script = build_script(llm_provider, topic, tone, word_range, combined)
```

---

## Step 20: Pasted Content

```python
from core.user_input import read_multiline_input
from core.file_utils import save_text_file, read_text_file
from pathlib import Path

# Method 1: Multi-line paste input
print("Paste your content (Ctrl+Z then Enter when done):")
content = read_multiline_input()

# Method 2: Read from file path
file_path = Path("content.txt")
content = read_text_file(file_path)

# Save pasted content
sources_dir = Path("output/episode/sources")
source_file = sources_dir / "pasted_content.txt"
save_text_file(content, source_file)

# Use pasted content
script = build_script(llm_provider, topic, tone, word_range, content)
```

---

## Complete Example: Full Episode Generation

```python
from datetime import datetime
from pathlib import Path
from core.provider_setup import initialize_providers, get_provider_info
from core.content_generation import build_script, build_show_notes, generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.file_utils import save_text_file, read_text_file
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config

# 1. Initialize providers
llm_provider, tts_provider = initialize_providers()

# 2. Get settings
topic = "AI in Healthcare"
tone = "educational"
voice = "nova"
length = "medium"

# 3. Validate
tone = validate_choice(tone, config.VALID_TONES, "tone")
voice = validate_choice(voice, set(tts_provider.available_voices), "voice")
length = validate_choice(length, config.VALID_LENGTHS, "length")
word_range = get_word_range(length)

# 4. Create unique episode directory
output_root = Path(config.OUTPUT_ROOT)
episode_dir, episode_id = create_episode_directory(output_root, topic)

# 5. Read source content
source_file = Path("healthcare_article.txt")
source_content = read_text_file(source_file)

# 6. Generate script
script = build_script(llm_provider, topic, tone, word_range, source_content)
script_file = episode_dir / "script.txt"
save_text_file(script, script_file)

# 7. Generate show notes
show_notes = build_show_notes(llm_provider, script)
show_notes_file = episode_dir / "show_notes.txt"
save_text_file(show_notes, show_notes_file)

# 8. Generate audio
audio_file = episode_dir / f"podcast_{voice}.mp3"
generate_audio(tts_provider, script, voice, audio_file)

# 9. Save metadata
metadata = {
    "created_at": datetime.now().isoformat(),
    "episode_id": episode_id,
    "topic": topic,
    "tone": tone,
    "voice": voice,
    "length": length,
    "word_range_target": word_range,
    "providers": get_provider_info(llm_provider, tts_provider),
    "models": {
        "script_model": llm_provider.model_name,
        "tts_model": tts_provider.model_name
    },
    "outputs": {
        "episode_dir": str(episode_dir),
        "script_file": str(script_file),
        "show_notes_file": str(show_notes_file),
        "audio_file": str(audio_file)
    }
}
metadata_file = save_episode_metadata(episode_dir, metadata)

# 10. Update episode index
episode_summary = create_episode_summary(
    metadata=metadata,
    episode_dir=episode_dir,
    additional_fields={
        "num_successful_files": 1,
        "num_successful_urls": 0
    }
)
index_file = output_root / "episode_index.json"
update_episode_index(index_file, episode_summary)

print(f"Episode created: {episode_id}")
print(f"Location: {episode_dir}")
```

---

## Quick Command Line Tests

```bash
# Test config loading
python -c "import config; print(config.DEFAULT_TONE)"

# Test provider initialization
python -c "from core.provider_setup import initialize_providers; llm, tts = initialize_providers()"

# Test file reading
python -c "from core.file_utils import read_text_file; from pathlib import Path; print(read_text_file(Path('source.txt'))[:100])"

# Test sanitize filename
python -c "from core.validation import sanitize_filename; print(sanitize_filename('Test! Episode @2024'))"

# Test episode index
python -c "from core.episode_management import load_episode_index; from pathlib import Path; print(len(load_episode_index(Path('output/episode_index.json'))))"

# Run comprehensive test suite
python manual_test_core_functions.py
```

---

## Key Takeaways

1. **Never duplicate code** - Use core modules instead
2. **All 20 steps** can be achieved with core functions
3. **No step scripts needed** - Core modules are self-sufficient
4. **Clean imports** - Import only what you need from core
5. **Consistent patterns** - All step files follow same structure

---

**See Also**:
- `manual_test_core_functions.py` - Comprehensive test examples
- `docs/core_modules_reference.md` - Detailed API documentation
- `FIXES_APPLIED_SUMMARY.md` - Recent improvements
