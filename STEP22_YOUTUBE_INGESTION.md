# Step 22: YouTube Transcript Ingestion - Complete

**Date**: 2026-04-08  
**Phase**: Phase 5 - Better Content Ingestion  
**Status**: ✅ COMPLETE

---

## Objective

Enable YouTube video transcript/subtitle ingestion - fetch transcripts from YouTube videos and convert them into podcast episodes.

---

## Implementation Summary

### Core Functions Added

**File**: `core/source_management.py`

1. **`extract_video_id(youtube_url: str) -> Optional[str]`**
   - Extracts video ID from various YouTube URL formats
   - Supports: youtube.com/watch, youtu.be, youtube.com/embed, mobile URLs
   - Example:
     ```python
     extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
     # Returns: "dQw4w9WgXcQ"
     ```

2. **`fetch_youtube_transcript(youtube_url: str, languages: List[str] = None) -> str`**
   - Fetches available transcripts (auto-generated or manual)
   - Default language: English
   - Returns formatted text with video metadata
   - Example output:
     ```
     YouTube Video: dQw4w9WgXcQ
     URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
     Transcript:
     
     Hello everyone, today we're discussing...
     ```

3. **Enhanced `save_sources_to_directory()`**
   - Automatically detects YouTube URLs
   - Fetches transcripts instead of scraping HTML
   - Saves transcript as text file
   - Works seamlessly with existing URL/file ingestion

### Dependencies Added

**Library**: `youtube-transcript-api>=0.6.0`
- Installed: ✅
- Added to: `requirements.txt`
- Purpose: Fetch YouTube video transcripts

---

## How to Use

### Option 1: Interactive Test (Recommended)

```bash
python test_youtube_ingestion.py
```

**Menu options**:
1. Test video ID extraction (various URL formats)
2. Test transcript fetching (sample videos provided)
3. Create full episode from YouTube URL
4. Enter custom YouTube URL

### Option 2: Quick Transcript Test

```bash
python test_youtube_ingestion.py
```

Then:
- Choose option `2` (Test transcript fetching)
- Select a sample video (1-3)
- View transcript preview
- Optionally create full episode

### Option 3: Use Core Functions Directly

```python
from core.source_management import extract_video_id, fetch_youtube_transcript

# Extract video ID
video_id = extract_video_id("https://www.youtube.com/watch?v=aircAruvnKk")
print(video_id)  # "aircAruvnKk"

# Fetch transcript
transcript = fetch_youtube_transcript("https://www.youtube.com/watch?v=aircAruvnKk")
print(f"Transcript length: {len(transcript)} characters")
print(transcript[:500])  # Preview
```

### Option 4: Integrate with Existing Scripts

Any script using `save_sources_to_directory()` now supports YouTube URLs automatically:

```python
from core.source_management import save_sources_to_directory
from pathlib import Path

sources_dir = Path("output/episode/sources")
all_sources = []

# Mix YouTube URLs with articles and files
successful, failed = save_sources_to_directory(
    sources_dir,
    all_sources,
    urls=[
        "https://www.youtube.com/watch?v=aircAruvnKk",  # ← YouTube!
        "https://example.com/article"                    # Regular URL
    ],
    files=[Path("document.pdf")]
)

# all_sources now contains YouTube transcript + other sources
```

---

## Test Command

**Quick test with sample videos**:

```bash
python test_youtube_ingestion.py
```

**What happens**:
1. Shows menu with 4 options
2. Choose option 2 to test transcript fetching
3. Select a sample video (AI/ML related)
4. View transcript preview
5. Optionally create full episode

**Sample videos included**:
- 3Blue1Brown - Neural Networks Explained
- Visual explanation of ChatGPT
- Andrej Karpathy - Intro to Large Language Models

---

## Expected Output

```
======================================================================
TEST: YouTube Transcript Extraction
======================================================================

Video URL: https://www.youtube.com/watch?v=aircAruvnKk
Video ID: aircAruvnKk

Fetching transcript...

[OK] Transcript fetched successfully
  Total length: 15234 characters
  Word count: 2456 words

[PREVIEW] First 400 characters:
----------------------------------------------------------------------
YouTube Video: aircAruvnKk
URL: https://www.youtube.com/watch?v=aircAruvnKk
Transcript:

This is a neural network. It's made up of these things called neurons
which are connected together in layers. The first layer takes in some
input data like the pixels of an image...
----------------------------------------------------------------------
```

---

## Files Created

### Core Module Updates
- ✅ `core/source_management.py` - Added `extract_video_id()`
- ✅ `core/source_management.py` - Added `fetch_youtube_transcript()`
- ✅ `core/source_management.py` - Enhanced `save_sources_to_directory()` for YouTube
- ✅ `requirements.txt` - Added `youtube-transcript-api>=0.6.0`

### Test Files
- ✅ `test_youtube_ingestion.py` - Comprehensive YouTube test script

### Documentation
- ✅ `STEP22_YOUTUBE_INGESTION.md` - This file

---

## Episode Structure (When Creating Full Episode)

```
output/
  └── YouTube_aircAruvnKk_2026-04-08_130215/
      ├── sources/
      │   └── source_1_youtube_aircAruvnKk.txt  ← Transcript
      ├── script.txt
      ├── show_notes.txt
      ├── podcast_nova.mp3
      └── metadata.json
```

### Metadata Example

```json
{
  "created_at": "2026-04-08T13:02:15",
  "episode_id": "YouTube_aircAruvnKk_2026-04-08_130215",
  "topic": "Neural Networks Explained",
  "source_type": "youtube",
  "youtube_info": {
    "video_url": "https://www.youtube.com/watch?v=aircAruvnKk",
    "video_id": "aircAruvnKk",
    "transcript_chars": 15234,
    "transcript_words": 2456
  },
  "outputs": {
    "episode_dir": "output/YouTube_aircAruvnKk_2026-04-08_130215"
  }
}
```

---

## Features

✅ **Multiple URL formats** - youtube.com, youtu.be, embed, mobile  
✅ **Auto-generated transcripts** - Fetches YouTube's auto-captions  
✅ **Manual transcripts** - Uses creator-provided subtitles if available  
✅ **Language support** - Default English, customizable  
✅ **Error handling** - Graceful failures with clear messages  
✅ **Automatic detection** - YouTube URLs detected automatically  
✅ **Metadata tracking** - Video info saved in episode metadata  
✅ **Seamless integration** - Works with existing source management  

---

## Supported Features

✅ **Public videos with transcripts**  
✅ **Auto-generated captions**  
✅ **Creator-uploaded subtitles**  
✅ **Multiple languages** (specify in function call)  
❌ **Videos with disabled transcripts**  
❌ **Private/unlisted videos without permission**  
❌ **Live streams** (limited transcript support)  

---

## Error Messages & Solutions

### "Transcripts are disabled for video"
**Solution**: Try a different video. Creator has disabled transcripts.

### "No transcript found"
**Solution**: Video may not have English transcripts. Try:
```python
fetch_youtube_transcript(url, languages=['en', 'auto'])
```

### "Video unavailable"
**Solution**: Video is private, deleted, or region-locked.

---

## URL Format Examples

All these formats work:

```python
# Standard format
"https://www.youtube.com/watch?v=aircAruvnKk"

# Short URL
"https://youtu.be/aircAruvnKk"

# Embed URL
"https://www.youtube.com/embed/aircAruvnKk"

# Mobile URL
"https://m.youtube.com/watch?v=aircAruvnKk"

# With timestamp
"https://www.youtube.com/watch?v=aircAruvnKk&t=123s"
```

---

## Testing Checklist

- [x] Install youtube-transcript-api library
- [x] Create `extract_video_id()` function
- [x] Create `fetch_youtube_transcript()` function
- [x] Enhance `save_sources_to_directory()` for YouTube
- [x] Create comprehensive test script
- [x] Test with multiple URL formats
- [x] Test transcript fetching
- [x] Test full episode creation
- [x] Update requirements.txt
- [x] Create documentation

---

## Next Steps (Phase 5 Continued)

- **Step 23**: Folder ingestion (batch process multiple files from folder)

---

## Quick Commands Reference

```bash
# Interactive test (recommended)
python test_youtube_ingestion.py

# Extract video ID in terminal
python -c "from core.source_management import extract_video_id; print(extract_video_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ'))"

# Fetch transcript in terminal
python -c "from core.source_management import fetch_youtube_transcript; print(fetch_youtube_transcript('https://www.youtube.com/watch?v=aircAruvnKk')[:500])"

# View all episodes (including YouTube-based ones)
python step17_episode_browser.py --list

# Check YouTube episodes in index
python -c "from pathlib import Path; from core.episode_management import load_episode_index; episodes = load_episode_index(Path('output/episode_index.json')); yt_eps = [e for e in episodes if e.get('source_type') == 'youtube']; print(f'YouTube episodes: {len(yt_eps)}')"
```

---

**Implementation**: Core functions only (no separate step file)  
**Test Status**: ✅ ALL TESTS PASSING  
**Ready for**: Step 23 (Folder ingestion)
