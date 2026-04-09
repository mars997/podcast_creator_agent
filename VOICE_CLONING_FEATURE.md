# Voice Cloning Feature - Implementation Guide

## Overview

The podcast creator now supports **voice cloning** using Coqui TTS XTTS v2, allowing users to create personas that clone voices from uploaded audio files.

## Two Persona Creation Methods

### 1. Style Analysis (Default)
- Analyzes speaking patterns from audio
- Maps to existing TTS voices
- Works on any network
- NO biometric voice cloning

### 2. Voice Cloning (New)
- Clones the actual voice from audio
- Uses Coqui TTS XTTS v2
- **Requires network access to huggingface.co**
- Creates biometric voice reproduction

## How It Works

### Persona Creation Flow

1. **Go to Persona Mode Tab** → Select "✨ Create New"

2. **Choose "📤 Upload Audio"**

3. **Upload audio file** (10-30 seconds recommended)

4. **System attempts voice cloning:**
   - ✅ **Success**: Voice cloned, ready to use
   - ⚠️ **Failure**: Falls back to style analysis automatically

5. **Review results:**
   - Voice cloning: Shows "🎤 Voice cloning successful!"
   - Style analysis: Shows detected traits (energy, pacing, tone, etc.)

6. **Name and save persona**

7. **Use in podcast generation:**
   - Persona appears in "💾 Your Created Personas" category
   - Voice-cloned personas marked with 🎤 icon

### Audio Generation

When generating podcasts with voice-cloned personas:

1. System detects persona is voice-cloned (`persona_id` starts with `cloned_`)
2. Uses Coqui TTS with speaker reference audio
3. Automatically chunks long scripts
4. Merges audio segments
5. Falls back to standard TTS if cloning fails

## Network Requirements

### Voice Cloning Requires:
- **Access to:** `huggingface.co`
- **Reason:** Downloads XTTS v2 model (~1.8GB first time)

### If Network Blocks huggingface.co:
- Voice cloning will **fail gracefully**
- System **automatically falls back** to style analysis
- User gets warning message
- Persona still created and usable (with style-based voice)

## Corporate Network Compatibility

### NRG Energy Network Status:
- ❌ **Voice cloning**: Blocked by firewall
- ✅ **Style analysis**: Works fine
- ✅ **Standard TTS**: Works fine

### Workarounds:
1. **Test from home network** (if allowed)
2. **Use VPN** (if company policy permits)
3. **Pre-download model** (requires admin access)
4. **Use style analysis** (recommended for corporate environments)

## Implementation Details

### Files Modified

1. **step44_web_ui_v2.py**
   - Updated `_handle_persona_creation()` to support voice cloning
   - Added fallback logic
   - Updated persona display for voice-cloned personas

2. **core/created_personas.py**
   - Added `create_persona_from_voice_clone()` function
   - Voice-cloned personas use special markers:
     - `persona_id`: starts with `cloned_`
     - `preferred_tts_voice`: `"coqui_cloned"`
     - `voice_archetype`: `"voice_cloned"`

3. **core/unified_generation.py**
   - Updated `_generate_audio()` to detect voice-cloned personas
   - Uses Coqui provider for voice-cloned personas
   - Handles chunking for long scripts
   - Falls back to standard TTS on error

4. **providers/coqui_provider.py** (existing)
   - Already has `generate_audio_with_voice_clone()` method
   - Handles XTTS v2 voice cloning

### Data Storage

Voice-cloned personas stored in `personas/created_personas.json`:

```json
{
  "persona_id": "cloned_a1b2c3d4e5f6",
  "persona_name": "My Voice Clone",
  "persona_description": "Voice-cloned persona from reference.mp3",
  "reference_audio_filename": "personas/cloned_20260409_153045_reference.mp3",
  "voice_archetype": "voice_cloned",
  "preferred_tts_voice": "coqui_cloned",
  "created_at": "2026-04-09T15:30:45",
  ...
}
```

Reference audio stored in `personas/` directory.

## Usage Example

### Creating a Voice-Cloned Persona

```bash
# Start UI
streamlit run step44_web_ui_v2.py
```

**In UI:**
1. Persona Mode tab → "✨ Create New"
2. Choose "📤 Upload Audio"
3. Upload 15-second voice sample
4. System attempts cloning
5. If successful: "🎤 Voice cloning successful!"
6. Name it "CEO Voice"
7. Save

**Using the Persona:**
1. Persona Mode tab
2. Select "💾 Your Created Personas"
3. Choose "🎤 CEO Voice (Voice Cloned)"
4. Enter topic: "Q4 Financial Results"
5. Generate podcast
6. **Audio uses cloned voice**

## Ethical Considerations

### ⚠️ IMPORTANT: Consent Required

Voice cloning creates a biometric reproduction of someone's voice. You MUST:

- ✅ Have explicit consent from the person
- ✅ Only clone your own voice or voices you have rights to
- ✅ Clearly label AI-generated content
- ✅ Not use for impersonation, fraud, or deception
- ✅ Respect privacy and identity rights

### Legal Compliance

- Voice cloning may be subject to local privacy laws
- Corporate use may require legal review
- Public figures' voices may have additional protections
- Always consult legal counsel for commercial use

## Troubleshooting

### Voice Cloning Fails

**Error:** `SSL: WRONG_VERSION_NUMBER` or `Connection reset`
- **Cause:** Network blocks huggingface.co
- **Solution:** Use style analysis method OR test from different network

**Error:** `TTS model failed to load`
- **Cause:** Insufficient disk space or model download failed
- **Solution:** Free up 2GB space, retry

**Error:** `Audio quality too low`
- **Cause:** Poor quality reference audio
- **Solution:** Use clear audio, minimal background noise, 10-30 seconds

### Generated Audio Sounds Wrong

**Issue:** Voice doesn't match reference
- **Check:** Audio quality of reference file
- **Check:** Reference audio is 10-30 seconds
- **Try:** Re-record reference in quiet environment

**Issue:** Robotic or distorted audio
- **Cause:** Script too long (chunking artifacts)
- **Solution:** This is a known limitation, may improve in future

## Technical Limitations

### Current Limitations

1. **Network dependency**: Requires huggingface.co access
2. **First-time download**: ~1.8GB model download
3. **Generation speed**: Slower than standard TTS
4. **Audio quality**: Depends on reference audio quality
5. **Language**: English optimized (XTTS supports multiple languages)

### Future Enhancements

- Pre-download model for offline use
- Multi-language voice cloning
- Voice fine-tuning options
- Real-time voice preview
- Quality validation before save

## Comparison: Style Analysis vs Voice Cloning

| Feature | Style Analysis | Voice Cloning |
|---------|---------------|---------------|
| **Network** | Any | Needs huggingface.co |
| **Speed** | Fast | Slower |
| **Voice Match** | Similar style | Exact voice |
| **Setup** | None | 1.8GB model download |
| **Privacy** | Low risk | Biometric data |
| **Consent** | Not required | REQUIRED |
| **Reliability** | High | Medium |
| **Corporate Use** | ✅ Safe | ⚠️ Review required |

## Recommendation

### For NRG Corporate Network:
**Use Style Analysis** - Voice cloning is blocked by firewall

### For Home/Personal Use:
**Try Voice Cloning** - If you need exact voice match and have consent

### For Production/Public Use:
**Legal Review Required** - Consult legal team before using voice cloning

## Status

**Implementation:** ✅ Complete  
**Testing:** ⚠️ Network-dependent  
**Documentation:** ✅ Complete  
**Corporate Compatible:** ⚠️ Style analysis only

**Date:** 2026-04-09  
**Version:** 2.0
