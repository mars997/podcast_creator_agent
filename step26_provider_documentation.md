```markdown
# Step 26: Provider Documentation

Complete guide for setting up and using OpenAI and Google Gemini providers.

---

## Overview

The podcast creator supports two AI providers:
- **OpenAI** - GPT models for LLM, TTS models for audio
- **Google Gemini** - Gemini models for both LLM and TTS

You can mix providers (e.g., Gemini LLM + OpenAI TTS) for cost optimization.

---

## Setup Guide

### Option 1: OpenAI Setup

1. **Get API Key**
   - Go to: https://platform.openai.com/api-keys
   - Create new secret key
   - Copy the key (starts with `sk-proj-...`)

2. **Add to `.env` file**
   ```bash
   OPENAI_API_KEY=sk-proj-your-key-here
   ```

3. **Models Used**
   - LLM: `gpt-4.1-mini` (script generation)
   - TTS: `gpt-4o-mini-tts` (audio generation)

4. **Available Voices**
   - alloy, echo, fable, onyx, nova, shimmer

---

### Option 2: Google Gemini Setup

1. **Get API Key**
   - Go to: https://aistudio.google.com/app/apikey
   - Create API key
   - Copy the key

2. **Add to `.env` file**
   ```bash
   GOOGLE_API_KEY=your-gemini-key-here
   ```

3. **Install SDK**
   ```bash
   pip install google-genai
   ```

4. **Models Used**
   - LLM: `gemini-1.5-flash` (script generation)
   - TTS: `gemini-2.5-flash` (audio generation)

5. **Available Voices**
   - Kore, Charon, Aoede, Puck, Fenrir, Orbit

---

### Option 3: Hybrid Setup (Recommended)

Use both providers for cost optimization:

**`.env` file:**
```bash
OPENAI_API_KEY=sk-proj-your-openai-key
GOOGLE_API_KEY=your-gemini-key
```

**Recommended Configuration:**
- LLM: Gemini (100x cheaper than OpenAI)
- TTS: OpenAI (better voice quality)

---

## Cost Comparison

### OpenAI Pricing (approximate)
- **GPT-4.1-mini**: $0.15 per 1M input tokens, $0.60 per 1M output tokens
- **TTS (gpt-4o-mini-tts)**: $15 per 1M characters

### Gemini Pricing (approximate)
- **Gemini 1.5 Flash**: $0.002 per 1M input tokens, $0.008 per 1M output tokens
- **TTS (Gemini 2.5 Flash)**: $1 per 1M characters

### Cost Savings
Using Gemini for LLM: **~75x cheaper** than OpenAI  
Using Gemini for TTS: **~15x cheaper** than OpenAI

**Hybrid recommendation**: Gemini LLM + OpenAI TTS
- Significant cost savings on script generation
- Premium voice quality for audio

---

## Environment Variables Reference

### Required (at least one)
```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...

# OR Gemini
GOOGLE_API_KEY=...

# OR both for hybrid mode
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=...
```

### Optional
```bash
# Override default models
OPENAI_LLM_MODEL=gpt-4.1-mini
OPENAI_TTS_MODEL=gpt-4o-mini-tts
GEMINI_LLM_MODEL=gemini-1.5-flash
GEMINI_TTS_MODEL=gemini-2.5-flash

# Default provider preference
PREFERRED_LLM_PROVIDER=gemini
PREFERRED_TTS_PROVIDER=openai
```

---

## Usage Examples

### Example 1: Pure OpenAI
```python
from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider

config = ProviderConfig(
    llm_provider="openai",
    tts_provider="openai"
)

llm = create_llm_provider(config)
tts = create_tts_provider(config)
```

### Example 2: Pure Gemini
```python
config = ProviderConfig(
    llm_provider="gemini",
    tts_provider="gemini"
)

llm = create_llm_provider(config)
tts = create_tts_provider(config)
```

### Example 3: Hybrid (Recommended)
```python
config = ProviderConfig(
    llm_provider="gemini",     # Cheaper
    tts_provider="openai"      # Better quality
)

llm = create_llm_provider(config)
tts = create_tts_provider(config)
```

### Example 4: Auto-detect with Fallback
```python
from providers.factory import get_default_config

# Automatically detects available providers
config = get_default_config()

llm = create_llm_provider(config)
tts = create_tts_provider(config)
```

---

## Command Line Usage

### Step 25: Interactive Provider Selection
```bash
python step25_multi_provider_podcast.py
```

This will:
1. Detect available providers
2. Let you choose LLM provider
3. Let you choose TTS provider
4. Generate episode with selected configuration

---

## Troubleshooting

### Error: "No providers available"
**Solution**: Set at least one API key in `.env`
```bash
OPENAI_API_KEY=your-key
# OR
GOOGLE_API_KEY=your-key
```

### Error: "Unknown LLM provider"
**Solution**: Only "openai" and "gemini" are supported
```python
config = ProviderConfig(
    llm_provider="openai",  # or "gemini"
    tts_provider="openai"   # or "gemini"
)
```

### Error: "API key not found"
**Solution**: Make sure `.env` file is in project root
```bash
# Check current directory
pwd

# Verify .env exists
ls -la .env

# Check .env content (don't share this!)
cat .env
```

### SSL/Certificate Errors
**Solution**: Corporate proxy/firewall issue
- Not a provider issue
- Contact IT for proxy configuration
- Or test from different network

---

## Provider Feature Comparison

| Feature | OpenAI | Gemini |
|---------|--------|--------|
| **Script Generation** | ✓ Excellent | ✓ Excellent |
| **Show Notes** | ✓ Excellent | ✓ Excellent |
| **Audio Quality** | ✓ High | ✓ Good |
| **Voice Options** | 6 voices | 6 voices |
| **Speed** | Fast | Very Fast |
| **Cost (LLM)** | $$$ | $ |
| **Cost (TTS)** | $$ | $ |

---

## Best Practices

### For Development/Testing
- Use Gemini for both (cheapest)
- Fast iterations, lower cost

### For Production Episodes
- LLM: Gemini (cost savings)
- TTS: OpenAI (better quality)

### For Premium Content
- Use OpenAI for both (best quality)
- Higher cost but premium output

---

## Metadata Tracking

Provider information is automatically saved in episode metadata:

```json
{
  "providers": {
    "llm": {
      "name": "gemini",
      "model": "gemini-1.5-flash"
    },
    "tts": {
      "name": "openai",
      "model": "gpt-4o-mini-tts"
    }
  },
  "provider_config": {
    "llm_provider": "gemini",
    "tts_provider": "openai",
    "hybrid_mode": true
  }
}
```

---

## Migration Guide

### From OpenAI-only to Hybrid

1. **Add Gemini API key**
   ```bash
   # .env file
   OPENAI_API_KEY=existing-key  # Keep this
   GOOGLE_API_KEY=new-gemini-key  # Add this
   ```

2. **Run multi-provider script**
   ```bash
   python step25_multi_provider_podcast.py
   ```

3. **Choose providers**
   - LLM: Select "gemini"
   - TTS: Select "openai"

4. **Existing episodes still work**
   - Backward compatible
   - Old episodes keep working
   - New episodes can use new providers

---

## Security Notes

### API Key Safety
- ✓ Never commit `.env` to git
- ✓ Use `.env.example` for documentation
- ✓ Rotate keys regularly
- ✗ Don't share keys in screenshots
- ✗ Don't paste keys in chat/Slack

### `.gitignore` should include
```
.env
*.env
.env.*
```

---

## Quick Start

**1. Choose your provider(s)**
- Testing? → Gemini only
- Production? → Hybrid (Gemini LLM + OpenAI TTS)
- Premium? → OpenAI only

**2. Get API key(s)**
- OpenAI: https://platform.openai.com/api-keys
- Gemini: https://aistudio.google.com/app/apikey

**3. Add to `.env`**
```bash
OPENAI_API_KEY=...
GOOGLE_API_KEY=...
```

**4. Run test**
```bash
python step25_multi_provider_podcast.py
```

**Done!** You now have multi-provider support.

---

## Support

### OpenAI Support
- Docs: https://platform.openai.com/docs
- Status: https://status.openai.com/

### Gemini Support
- Docs: https://ai.google.dev/docs
- Forum: https://discuss.ai.google.dev/

---

**Step 26 Complete**: Provider documentation ready  
**Next Step**: Step 27 - Stronger podcast templates
```
