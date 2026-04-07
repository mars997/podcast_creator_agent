# Multi-Provider Guide

## Overview

As of Step 21, the podcast_creator_agent supports multiple AI providers for both LLM (script generation) and TTS (audio generation). This guide explains how to set up and use different providers.

## Supported Providers

### OpenAI
- **LLM Models**: gpt-4.1-mini, gpt-4-turbo, etc.
- **TTS Models**: gpt-4o-mini-tts, tts-1, tts-1-hd
- **Voices**: alloy, echo, fable, onyx, nova, shimmer
- **Cost**: ~$0.01/1K tokens (LLM), ~$15/1M characters (TTS)
- **Quality**: Proven, widely used, high quality

### Google Gemini
- **LLM Models**: gemini-1.5-flash, gemini-1.5-pro
- **TTS Models**: gemini-2.5-flash (experimental)
- **Voices**: Natural language style prompts, 380+ voices available
- **Cost**: ~$0.0001/1K tokens (Flash), TTS included
- **Quality**: Excellent, significantly cheaper for LLM

## Quick Start

### 1. Choose Your Configuration

You need at least ONE of the following API keys:

**Option A: OpenAI Only (Default)**
- Best for: Users who want proven, battle-tested workflow
- Cost: Standard OpenAI pricing
- Setup time: 5 minutes

**Option B: Gemini Only**
- Best for: Cost optimization (100x cheaper LLM)
- Cost: Lowest overall cost
- Setup time: 10 minutes
- Note: Gemini TTS is experimental

**Option C: Hybrid (Recommended)**
- Best for: Maximum cost savings with proven TTS quality
- Cost: 90% savings on script generation
- Setup time: 10 minutes
- Uses: Gemini for LLM, OpenAI for TTS

## Setup Instructions

### OpenAI Setup

1. Get your API key:
   - Visit: https://platform.openai.com/api-keys
   - Sign in or create an account
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

2. Add to `.env` file:
   ```bash
   OPENAI_API_KEY=sk-your_actual_key_here
   ```

3. That's it! The system defaults to OpenAI.

### Gemini Setup

1. Get your API key:
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Click "Create API key"
   - Copy the key

2. Add to `.env` file:
   ```bash
   GOOGLE_API_KEY=your_google_api_key_here
   ```

3. Install the Gemini SDK:
   ```bash
   pip install google-generativeai
   ```

4. Configure provider preference:
   ```bash
   # Add to .env
   PODCAST_LLM_PROVIDER=gemini
   PODCAST_TTS_PROVIDER=gemini
   ```

### Hybrid Setup (Recommended)

1. Get both API keys (see above)

2. Configure `.env`:
   ```bash
   OPENAI_API_KEY=sk-your_openai_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Use Gemini for LLM (cheap), OpenAI for TTS (quality)
   PODCAST_LLM_PROVIDER=gemini
   PODCAST_TTS_PROVIDER=openai
   ```

3. This gives you:
   - 100x cost savings on script generation
   - Proven OpenAI TTS quality
   - Best of both worlds

## Environment Variables Reference

### Required (at least one)

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Google Gemini API Key
GOOGLE_API_KEY=...
```

### Optional Provider Selection

```bash
# Which provider to use for LLM
# Options: "openai" or "gemini"
# Default: "openai"
PODCAST_LLM_PROVIDER=gemini

# Which provider to use for TTS
# Options: "openai" or "gemini"
# Default: "openai"
PODCAST_TTS_PROVIDER=openai
```

### Optional Model Overrides

```bash
# Override default LLM model
# OpenAI: gpt-4.1-mini, gpt-4-turbo, gpt-4o
# Gemini: gemini-1.5-flash, gemini-1.5-pro
PODCAST_LLM_MODEL=gemini-1.5-pro

# Override default TTS model
# OpenAI: gpt-4o-mini-tts, tts-1, tts-1-hd
# Gemini: gemini-2.5-flash
PODCAST_TTS_MODEL=tts-1-hd
```

## Cost Comparison

Based on typical podcast episode (500-word script):

| Configuration | LLM Cost | TTS Cost | Total | Notes |
|---------------|----------|----------|-------|-------|
| Pure OpenAI | ~$0.005 | ~$0.08 | ~$0.085 | Standard |
| Pure Gemini | ~$0.00005 | Included | ~$0.00005 | Cheapest |
| Hybrid | ~$0.00005 | ~$0.08 | ~$0.08 | Recommended |

**Key Insights:**
- Gemini LLM is ~100x cheaper than OpenAI
- TTS is the major cost component
- Hybrid gives you 90% of Gemini's savings with proven TTS

## Voice Configuration

### OpenAI Voices

Available voices (use voice ID directly):
- `alloy` - Neutral, balanced
- `echo` - Male, clear
- `fable` - British accent
- `onyx` - Deep, authoritative
- `nova` - Female, friendly (default)
- `shimmer` - Soft, warm

Example:
```python
voice = "nova"
```

### Gemini Voices

Gemini uses natural language style prompts:

Examples:
- `"professional news anchor"`
- `"friendly teacher"`
- `"calm narrator"`
- `"energetic podcast host"`

The system converts these to Gemini's voice configuration.

## Smart Fallback

The system automatically handles missing API keys:

1. **Preferred provider missing**:
   - Falls back to available provider
   - Displays warning message
   - Continues without error

2. **No providers available**:
   - Clear error message
   - Setup instructions
   - Links to get API keys

Example:
```bash
# You set: PODCAST_LLM_PROVIDER=gemini
# But only have: OPENAI_API_KEY

# System automatically:
# - Falls back to OpenAI
# - Shows warning
# - Generates podcast successfully
```

## Provider Metadata

All episodes now track which provider was used:

```json
{
  "providers": {
    "llm_provider": "gemini",
    "llm_model": "gemini-1.5-flash",
    "tts_provider": "openai",
    "tts_model": "gpt-4o-mini-tts"
  }
}
```

This allows:
- Reproducibility
- Cost tracking
- Provider comparison
- Episode regeneration with different providers

## Troubleshooting

### "No API keys found"

**Problem**: Neither OPENAI_API_KEY nor GOOGLE_API_KEY is set.

**Solution**:
1. Check your `.env` file exists
2. Verify the key name is spelled correctly
3. Ensure no extra spaces around the `=`
4. Restart your terminal/IDE

### "google-generativeai package not installed"

**Problem**: Trying to use Gemini without the SDK.

**Solution**:
```bash
pip install google-generativeai
```

### "openai package not installed"

**Problem**: Trying to use OpenAI without the SDK.

**Solution**:
```bash
pip install openai
```

### Gemini TTS Errors

**Problem**: Gemini TTS API may be experimental or changed.

**Solution**:
```bash
# Switch to OpenAI for TTS
PODCAST_TTS_PROVIDER=openai
```

### API Key Invalid

**Problem**: "Authentication failed" or "Invalid API key"

**Solution**:
1. Verify the key is correct (check for copy/paste errors)
2. Ensure the key hasn't expired
3. Check your account has credits/is active
4. Try regenerating the API key

### Rate Limiting

**Problem**: "Rate limit exceeded"

**Solution**:
- Wait a few minutes
- Upgrade your API plan
- Switch providers temporarily

## Migration from Existing Setup

If you're upgrading from an OpenAI-only setup:

1. **No changes required** - Everything works as before
2. **To try Gemini**:
   ```bash
   # Add to .env
   GOOGLE_API_KEY=your_key
   PODCAST_LLM_PROVIDER=gemini
   ```
3. **To optimize costs**:
   ```bash
   # Hybrid configuration
   PODCAST_LLM_PROVIDER=gemini
   PODCAST_TTS_PROVIDER=openai
   ```

## Best Practices

### For Cost Optimization
- Use Gemini Flash for LLM
- Use OpenAI for TTS
- Monitor usage in provider dashboards

### For Quality
- Use OpenAI for both (proven)
- Use `nova` or `shimmer` voice
- Generate show notes from same provider as script

### For Experimentation
- Try Gemini Pro for complex scripts
- Test different voice combinations
- Compare outputs in metadata

## Advanced Configuration

### Per-Episode Provider Override

You can override providers per episode by setting environment variables before running:

```bash
# Generate one episode with Gemini
PODCAST_LLM_PROVIDER=gemini python step22_multi_provider_podcast.py

# Generate next episode with OpenAI
PODCAST_LLM_PROVIDER=openai python step22_multi_provider_podcast.py
```

### Custom Models

```bash
# Use Gemini Pro for higher quality
PODCAST_LLM_MODEL=gemini-1.5-pro

# Use OpenAI HD TTS for better audio
PODCAST_TTS_MODEL=tts-1-hd
```

## FAQs

**Q: Can I use different providers for different episodes?**
A: Yes! Just change the environment variables between runs.

**Q: Will my old episodes still work?**
A: Yes! All existing OpenAI episodes are fully compatible.

**Q: Can I regenerate an old episode with a different provider?**
A: Yes! Step 22+ supports provider override during regeneration.

**Q: Is Gemini TTS as good as OpenAI?**
A: It's experimental. We recommend testing both and comparing.

**Q: How do I know which provider was used?**
A: Check the episode's `metadata.json` file, or use the episode browser.

**Q: Can I add more providers later?**
A: Yes! The architecture is extensible. See `providers/base.py` for the interface.

## Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Verify your `.env` file syntax
3. Run the validation script: `python validate_step21.py`
4. Check episode metadata for provider info
5. Review the provider-specific documentation:
   - OpenAI: https://platform.openai.com/docs
   - Gemini: https://ai.google.dev/docs

## Next Steps

- See `docs/development_plan.md` for future features
- Try Step 22 to generate your first multi-provider podcast
- Experiment with different provider combinations
- Compare costs and quality for your use case

---

**Last Updated**: 2026-04-07 (Step 21 completed)
