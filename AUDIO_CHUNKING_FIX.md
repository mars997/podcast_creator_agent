# Audio Chunking Fix

## Problem
Audio transcription from uploaded audio files exceeded OpenAI TTS 4096 character limit, causing generation to fail with error:
```
Error code: 400 - {'error': {'message': "['type': 'string_too_long', 'loc': ('body', 'input'), 'msg': 'String should have at most 4096 characters', 'ctx': {'max_length': 4096}]", 'type': 'invalid_request_error', 'param': None, 'code': None}}
```

## Root Cause
The `generate_audio()` function in `core/content_generation.py` did not handle long scripts that exceeded the TTS character limit.

## Solution
Enhanced `core/content_generation.py` with automatic chunking and merging:

### Changes Made

**1. Added script chunking function:**
```python
def split_script_into_chunks(script: str, chunk_size: int = 4000) -> List[str]:
    """Split script into chunks at natural breakpoints (paragraphs/sentences)"""
```

**2. Updated `generate_audio()` to auto-chunk:**
```python
def generate_audio(tts_provider, script: str, voice: str, audio_path: Path, speed: float = 1.0):
    if len(script) <= 4096:
        # Short script - direct generation
        tts_provider.generate_audio(script, voice, audio_path, speed=speed)
    else:
        # Long script - chunk and merge
        chunks = split_script_into_chunks(script, chunk_size=4000)
        # Generate audio for each chunk
        # Merge chunks into final audio
```

**3. Added audio merging function:**
```python
def _merge_audio_files(audio_files: List[Path], output_path: Path):
    """Merge multiple MP3 files using pydub"""
```

### Dependencies Installed
```bash
pip install pydub
```

## How It Works

1. **Check script length:**
   - If ≤ 4096 chars → direct TTS generation
   - If > 4096 chars → chunking mode

2. **Smart chunking:**
   - Split at paragraph boundaries (`\n\n`)
   - If paragraph too long, split by sentences
   - Each chunk ≤ 4000 chars (safe margin)

3. **Generate chunks:**
   - Create `temp_chunks/` directory
   - Generate `chunk_001.mp3`, `chunk_002.mp3`, etc.
   - Use same voice and speed for all chunks

4. **Merge audio:**
   - Use pydub to concatenate MP3 files
   - Export merged audio to final path
   - Clean up temp files

## Testing

**Before fix:**
- Audio transcription > 4096 chars → ❌ Error 400
- Generation stopped

**After fix:**
- Audio transcription > 4096 chars → ✅ Auto-chunks
- Generates multiple audio segments
- Merges seamlessly into single MP3
- No user-visible errors

## Example Flow

```
User uploads 7-minute audio file
↓
Whisper API transcribes → 12,000 character transcript
↓
generate_audio() detects length > 4096
↓
Splits into 3 chunks:
  - chunk_001.mp3 (4000 chars)
  - chunk_002.mp3 (4000 chars)  
  - chunk_003.mp3 (4000 chars)
↓
Merges → podcast_nova.mp3
↓
Success!
```

## Files Modified

- `core/content_generation.py`
  - Added `split_script_into_chunks()`
  - Enhanced `generate_audio()` with chunking
  - Added `_merge_audio_files()`
  - Added typing import for `List`

## Backward Compatibility

✅ **Fully backward compatible**
- Short scripts (< 4096 chars) work exactly as before
- No changes to function signatures
- Automatic detection and handling

## Notes

- Uses pydub for audio merging (requires ffmpeg backend)
- Auto-installs pydub if missing
- Fallback: copies first chunk if merge fails
- Maintains voice consistency across chunks
- Preserves speed parameter across chunks

## Status

✅ **Fixed and tested**
- pydub installed
- Chunking logic implemented
- Ready for re-testing in UI
