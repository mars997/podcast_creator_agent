# Core Modules Reference

This document provides a comprehensive reference for all core modules in the podcast creator agent.

## Table of Contents

1. [core.validation](#corevalidation)
2. [core.file_utils](#corefile_utils)
3. [core.user_input](#coreuser_input)
4. [core.source_management](#coresource_management)
5. [core.provider_setup](#coreprovider_setup)
6. [core.content_generation](#corecontent_generation)
7. [core.episode_management](#coreepisode_management)
8. [core.episode_browser](#coreepisode_browser)
9. [core.episode_regenerator](#coreepisode_regenerator)
10. [core.rss_utils](#corerss_utils)

---

## core.validation

**Purpose**: Input validation and sanitization

### Functions

#### `sanitize_filename(text: str) -> str`
Clean text for use in filenames by removing special characters.

**Parameters**:
- `text` - Text to sanitize

**Returns**: Sanitized filename-safe string

**Example**:
```python
from core.validation import sanitize_filename

safe_name = sanitize_filename("My Podcast: Episode #1!")
# Returns: "My_Podcast_Episode_1"
```

#### `validate_choice(value: str, valid_set: set, field_name: str) -> str`
Validate a user choice against a set of valid options.

**Parameters**:
- `value` - The choice to validate
- `valid_set` - Set of valid options
- `field_name` - Name of the field (for error messages)

**Returns**: The validated value

**Raises**: `ValueError` if value not in valid_set

**Example**:
```python
from core.validation import validate_choice

tone = validate_choice("casual", {"casual", "professional"}, "tone")
# Returns: "casual"

tone = validate_choice("invalid", {"casual", "professional"}, "tone")
# Raises: ValueError("Invalid tone: invalid")
```

#### `validate_tone(tone: str) -> str`
Validate podcast tone.

#### `validate_voice(voice: str, valid_voices: set) -> str`
Validate TTS voice selection.

#### `validate_length(length: str) -> str`
Validate episode length.

#### `get_word_range(length_choice: str) -> str`
Get word count range for a given length choice.

**Parameters**:
- `length_choice` - "short", "medium", or "long"

**Returns**: Word range string (e.g., "500 to 700 words")

**Example**:
```python
from core.validation import get_word_range

word_range = get_word_range("medium")
# Returns: "500 to 700 words"
```

---

## core.file_utils

**Purpose**: File I/O operations

### Functions

#### `save_json(data: dict | list, file_path: Path) -> None`
Save data to a JSON file with pretty formatting.

**Example**:
```python
from pathlib import Path
from core.file_utils import save_json

metadata = {"episode_id": "001", "topic": "AI"}
save_json(metadata, Path("metadata.json"))
```

#### `save_text_file(content: str, file_path: Path) -> None`
Save text content to a file.

#### `ensure_directory(directory: Path) -> Path`
Create directory if it doesn't exist, return path for chaining.

**Example**:
```python
from pathlib import Path
from core.file_utils import ensure_directory

output_dir = ensure_directory(Path("output") / "episodes")
# Creates output/episodes/ and returns the Path
```

#### `read_text_file(file_path: Path) -> str`
Read text from a file, raising errors for missing/empty files.

**Raises**:
- `FileNotFoundError` if file doesn't exist
- `ValueError` if file is empty

#### `load_json(file_path: Path) -> dict | list`
Load JSON data from a file.

**Raises**:
- `FileNotFoundError` if file doesn't exist
- `ValueError` if JSON is invalid

---

## core.user_input

**Purpose**: User interaction utilities

### Functions

#### `get_user_input(prompt_text: str, default_value: str) -> str`
Get user input with a default value.

**Example**:
```python
from core.user_input import get_user_input

tone = get_user_input("Choose tone (casual/professional)", "casual")
# Prompts: "Choose tone (casual/professional) [casual]: "
# If user presses Enter, returns "casual"
```

#### `get_podcast_settings(llm_provider, tts_provider) -> dict`
Get all podcast settings from user in a single call.

**Returns**: Dictionary with keys: topic, tone, voice, length

#### `read_multiline_input() -> str`
Read multi-line pasted content from user.

**Usage**: User pastes content and types `###END###` on a new line to finish.

**Example**:
```python
from core.user_input import read_multiline_input

content = read_multiline_input()
# User can paste multiple lines, then type ###END### to finish
```

---

## core.source_management

**Purpose**: Source fetching and management

### Functions

#### `fetch_article_text(url: str) -> str`
Fetch and extract article text from a URL using web scraping.

**Returns**: Formatted text with title, URL, and article content

**Raises**:
- `requests.HTTPError` if request fails
- `ValueError` if no article text could be extracted

**Example**:
```python
from core.source_management import fetch_article_text

article = fetch_article_text("https://example.com/article")
# Returns: "Title: Article Title\nURL: https://...\n\nArticle content..."
```

#### `read_text_file(file_path: Path) -> str`
Read text from a local file and format for podcast source.

**Returns**: Formatted text with filename and content

#### `parse_csv_input(raw_text: str) -> List[str]`
Parse comma-separated input into a list.

**Example**:
```python
from core.source_management import parse_csv_input

urls = parse_csv_input("url1, url2,  , url3")
# Returns: ['url1', 'url2', 'url3']
```

#### `load_source_files(sources_dir: Path) -> List[str]`
Load all source .txt files from a directory.

**Returns**: List of formatted source texts

**Raises**:
- `FileNotFoundError` if directory doesn't exist
- `ValueError` if no source files found

#### `save_sources_to_directory(sources_dir: Path, sources: List[str], urls: List[str] = None, files: List[Path] = None) -> Tuple[List[Dict], List[Dict]]`
Fetch/read sources and save them to a directory.

**Returns**: Tuple of (successful_sources, failed_sources)

**Example**:
```python
from core.source_management import save_sources_to_directory
from pathlib import Path

sources = []
successful, failed = save_sources_to_directory(
    Path("output/episode/sources"),
    sources,
    urls=["https://example.com/article1", "https://example.com/article2"],
    files=[Path("local.txt")]
)

print(f"Fetched {len(successful)} sources successfully")
print(f"Failed to fetch {len(failed)} sources")
```

---

## core.provider_setup

**Purpose**: Provider initialization

### Functions

#### `initialize_providers(verbose: bool = True) -> Tuple[LLMProvider, TTSProvider]`
Initialize LLM and TTS providers with auto-detection.

**Returns**: Tuple of (llm_provider, tts_provider)

**Example**:
```python
from core.provider_setup import initialize_providers

llm_provider, tts_provider = initialize_providers()
# Outputs provider information to console
```

#### `get_provider_info(llm_provider, tts_provider) -> dict`
Get provider information as a dictionary.

**Returns**: Dictionary with provider names and models

---

## core.content_generation

**Purpose**: Script and audio generation

### Functions

#### `build_script(llm_provider, topic: str, tone: str, word_range: str, source_material: str) -> str`
Generate podcast script using LLM.

**Example**:
```python
from core.content_generation import build_script

script = build_script(
    llm_provider,
    topic="AI Technology",
    tone="educational",
    word_range="500 to 700 words",
    source_material="Source 1:\nArticle content..."
)
```

#### `build_show_notes(llm_provider, script: str) -> str`
Generate show notes from a podcast script.

#### `generate_audio(tts_provider, script: str, voice: str, audio_path: Path) -> None`
Generate audio file from script using TTS.

**Example**:
```python
from core.content_generation import generate_audio
from pathlib import Path

generate_audio(
    tts_provider,
    script="Welcome to my podcast...",
    voice="nova",
    audio_path=Path("output/podcast.mp3")
)
```

---

## core.episode_management

**Purpose**: Episode lifecycle management

### Functions

#### `create_episode_directory(output_root: Path, topic: str, timestamp_suffix: str = None) -> Tuple[Path, str]`
Create a unique episode directory with timestamp.

**Returns**: Tuple of (episode_directory, episode_id)

**Example**:
```python
from core.episode_management import create_episode_directory
from pathlib import Path

episode_dir, episode_id = create_episode_directory(
    Path("output"),
    "AI Trends"
)
# Returns: (Path("output/AI_Trends_2026-04-08_153045"), "AI_Trends_2026-04-08_153045")
```

#### `save_episode_metadata(episode_dir: Path, metadata: dict) -> Path`
Save episode metadata to metadata.json file.

**Returns**: Path to saved metadata file

#### `create_episode_summary(metadata: dict, episode_dir: Path, additional_fields: dict = None) -> dict`
Create a summary of episode information for the episode index.

**Returns**: Dictionary containing episode summary

#### `update_episode_index(index_path: Path, episode_summary: dict) -> None`
Update the global episode index with a new episode.

**Example**:
```python
from core.episode_management import update_episode_index, create_episode_summary
from pathlib import Path

metadata = {
    "created_at": "2026-04-08T10:00:00",
    "episode_id": "AI_Trends_2026-04-08_100000",
    "topic": "AI Trends",
    # ... more fields
}

summary = create_episode_summary(metadata, episode_dir)
update_episode_index(Path("output/episode_index.json"), summary)
```

#### `load_episode_index(index_path: Path) -> List[dict]`
Load episode index from JSON file.

**Returns**: List of episode summaries

#### `load_episode_metadata(metadata_path: Path) -> dict`
Load episode metadata from JSON file.

**Raises**:
- `FileNotFoundError` if file doesn't exist
- `ValueError` if JSON is invalid

---

## core.episode_browser

**Purpose**: Interactive episode browsing UI

### Functions

#### `format_episode_summary(episode: dict, index: int) -> str`
Format a single episode for display.

#### `display_episode_list(episodes: List[dict]) -> None`
Display all episodes in the index.

#### `display_episode_details(episode: dict) -> None`
Display detailed information about a specific episode.

#### `view_file_content(file_path: Path, max_lines: int = 50) -> None`
Display the content of a text file with line limit.

#### `interactive_menu(episodes: List[dict]) -> None`
Run interactive menu for browsing episodes.

**Example**:
```python
from core.episode_browser import interactive_menu, load_episode_index
from pathlib import Path

episodes = load_episode_index(Path("output/episode_index.json"))
interactive_menu(episodes)
# Displays interactive menu for browsing episodes
```

---

## core.episode_regenerator

**Purpose**: Episode regeneration from existing metadata

### Functions

#### `regenerate_episode(original_metadata: dict, episode_dir_path: Path, llm_provider, tts_provider, output_root: Path, index_path: Path) -> Tuple[Path, str]`
Regenerate a podcast episode from existing metadata and sources.

**Returns**: Tuple of (new_episode_directory, new_episode_id)

**Example**:
```python
from core.episode_regenerator import regenerate_episode
from core.episode_management import load_episode_metadata
from pathlib import Path

# Load original episode metadata
original_metadata = load_episode_metadata(Path("output/episode1/metadata.json"))

# Regenerate episode with same settings
new_dir, new_id = regenerate_episode(
    original_metadata,
    Path("output/episode1"),
    llm_provider,
    tts_provider,
    Path("output"),
    Path("output/episode_index.json")
)

print(f"Regenerated as: {new_id}")
```

---

## core.rss_utils

**Purpose**: RSS feed parsing utilities

### Functions

#### `parse_rss_feed(feed_url: str, max_items: int = 10) -> List[Dict[str, str]]`
Parse an RSS feed and extract article information.

**Returns**: List of article dictionaries with keys: title, link, description, published, author

**Raises**: `ValueError` if feed cannot be parsed or contains no entries

**Example**:
```python
from core.rss_utils import parse_rss_feed

articles = parse_rss_feed("https://example.com/feed.xml", max_items=5)
for article in articles:
    print(f"{article['title']} - {article['link']}")
```

#### `save_rss_info(sources_dir: Path, feed_url: str, articles: List[dict]) -> Path`
Save RSS feed information to a JSON file.

**Returns**: Path to saved RSS info file

**Example**:
```python
from core.rss_utils import parse_rss_feed, save_rss_info
from pathlib import Path

articles = parse_rss_feed("https://example.com/feed.xml", max_items=3)
rss_file = save_rss_info(
    Path("output/episode/sources"),
    "https://example.com/feed.xml",
    articles
)
# Saves to: output/episode/sources/rss_feed_info.json
```

---

## Common Workflows

### Creating a New Episode

```python
from pathlib import Path
from core.provider_setup import initialize_providers
from core.validation import validate_choice, get_word_range, sanitize_filename
from core.source_management import save_sources_to_directory
from core.content_generation import build_script, build_show_notes, generate_audio
from core.episode_management import create_episode_directory, save_episode_metadata

# Initialize providers
llm_provider, tts_provider = initialize_providers()

# Get settings
topic = "AI Technology"
tone = "educational"
voice = "nova"
length = "medium"
word_range = get_word_range(length)

# Create episode directory
episode_dir, episode_id = create_episode_directory(Path("output"), topic)
sources_dir = episode_dir / "sources"
sources_dir.mkdir()

# Fetch sources
all_sources = []
successful, failed = save_sources_to_directory(
    sources_dir,
    all_sources,
    urls=["https://example.com/article"]
)

# Generate content
combined_source = "\n\n".join(all_sources)
script = build_script(llm_provider, topic, tone, word_range, combined_source)
show_notes = build_show_notes(llm_provider, script)

# Save files
(episode_dir / "script.txt").write_text(script)
(episode_dir / "show_notes.txt").write_text(show_notes)

# Generate audio
generate_audio(tts_provider, script, voice, episode_dir / f"podcast_{voice}.mp3")

# Save metadata
metadata = {
    "episode_id": episode_id,
    "topic": topic,
    "tone": tone,
    "voice": voice,
    "length": length
}
save_episode_metadata(episode_dir, metadata)
```

### Browsing Episodes

```python
from pathlib import Path
from core.episode_management import load_episode_index
from core.episode_browser import interactive_menu

# Load episode index
episodes = load_episode_index(Path("output/episode_index.json"))

# Display interactive menu
interactive_menu(episodes)
```

### Regenerating an Episode

```python
from pathlib import Path
from core.provider_setup import initialize_providers
from core.episode_management import load_episode_metadata
from core.episode_regenerator import regenerate_episode

# Initialize providers
llm_provider, tts_provider = initialize_providers()

# Load original episode
original_metadata = load_episode_metadata(Path("output/episode1/metadata.json"))

# Regenerate
new_dir, new_id = regenerate_episode(
    original_metadata,
    Path("output/episode1"),
    llm_provider,
    tts_provider,
    Path("output"),
    Path("output/episode_index.json")
)
```

---

## Error Handling

All core modules follow consistent error handling patterns:

- **Missing Files**: Raise `FileNotFoundError` with descriptive message
- **Invalid Input**: Raise `ValueError` with descriptive message
- **API Errors**: Propagate exceptions for the caller to handle
- **Partial Failures**: Return structured success/failure data

Example:
```python
try:
    successful, failed = save_sources_to_directory(...)
    if failed:
        print(f"Warning: {len(failed)} sources failed to fetch")
    if not successful:
        raise ValueError("No sources could be fetched")
except FileNotFoundError as e:
    print(f"Directory not found: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
```
