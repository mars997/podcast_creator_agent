# Episode to Step Mapping - Quick Reference

This document maps each generated episode to its corresponding step for easy review.

---

## ✅ Successful Test Episodes (10 steps)

| Step | Feature | Episode Directory | Status |
|------|---------|-------------------|--------|
| **27** | Podcast Templates | `Renewable_Energy_Future_2026-04-08_150458` | ✅ PASS |
| **28** | Multi-Character | `Climate_Change_Solutions_2026-04-08_150544` | ✅ PASS |
| **29** | Grounding Rules | `Space_Exploration_2026-04-08_150621` | ✅ PASS |
| **32** | Voice Persona | `Future_of_Technology_2026-04-08_150654` | ✅ PASS |
| **34** | Intro/Outro | `1_2026-04-08_150753` | ✅ PASS |
| **36** | Audio Processing | `Professionally_Processed_Podcast_2026-04-08_150848` | ✅ PASS |
| **37** | Automated Gen | _(no episode, automation only)_ | ✅ PASS |
| **38** | Topic Queue | _(creates queue file only)_ | ✅ PASS |
| **40** | Summarize First | `Blockchain_Fundamentals_2026-04-08_151006` | ✅ PASS |
| **42** | Approval Workflow | _(creates workflow file only)_ | ✅ PASS |

---

## ❌ Failed Tests (7 steps - no episodes)

| Step | Feature | Error | Status |
|------|---------|-------|--------|
| **25** | Multi-Provider | Unicode encoding | ❌ FAIL |
| **30** | Segment-Aware | Type error (word_range) | ❌ FAIL |
| **31** | Citations | EOF on input | ❌ FAIL |
| **33** | Audio Chunking | Missing import (Dict) | ❌ FAIL |
| **35** | Multi-Voice | Unicode encoding | ❌ FAIL |
| **39** | Source Selection | ProviderConfig error | ❌ FAIL |
| **41** | Quality Check | ProviderConfig error | ❌ FAIL |

---

## Review Guide by Step

### Step 27: Podcast Templates
**Directory**: `output/Renewable_Energy_Future_2026-04-08_150458`

**What to Review**:
- Check if script follows "Solo Explainer" template structure
- Look for: Hook → Introduction → Main Points → Examples → Takeaways

**Key Files**:
- script.txt - Should have template-structured content
- metadata.json - Should show `"template": "Solo Explainer"`

---

### Step 28: Multi-Character Podcast
**Directory**: `output/Climate_Change_Solutions_2026-04-08_150544`

**What to Review**:
- Check for multi-speaker dialogue (HOST:, GUEST: format)
- Verify natural conversation flow

**Key Files**:
- script.txt - Should have speaker labels
- Look for character interaction

---

### Step 29: Grounding Rules
**Directory**: `output/Space_Exploration_2026-04-08_150621`

**What to Review**:
- Check if script stays grounded in source material
- Verify no hallucinated information

**Key Files**:
- **grounding_info.txt** - Shows which rules were applied
- **sources/source_1.txt** - Original source material
- script.txt - Should reference source content
- metadata.json - Shows grounding mode used

---

### Step 32: Voice Persona System
**Directory**: `output/Future_of_Technology_2026-04-08_150654`

**What to Review**:
- Check if script reflects "Alex the Tech Enthusiast" persona
- Look for energetic, tech-focused language
- Check for signature phrases

**Key Files**:
- **persona_profile.json** - Persona definition
  ```json
  {
    "name": "Alex the Tech Enthusiast",
    "personality": "Energetic, curious, excited about new technology",
    "speaking_style": "Conversational, uses analogies, geeky references"
  }
  ```
- script.txt - Should match persona style
- metadata.json - Shows persona used

---

### Step 34: Intro/Outro Branding
**Directory**: `output/1_2026-04-08_150753`

**What to Review**:
- Check for separate intro and outro segments
- Verify branded opening/closing

**Key Files**:
- branding/ directory (if created)
- script.txt - Should have intro and outro sections

---

### Step 36: Audio Post-Processing
**Directory**: `output/Professionally_Processed_Podcast_2026-04-08_150848`

**What to Review**:
- Compare raw vs processed audio quality
- Check processing settings used

**Key Files**:
- **podcast_alloy_raw.mp3** - Original unprocessed audio
- **podcast_alloy.mp3** - Processed audio (should be louder/clearer)
- **processing_info.json** - Processing settings and stats
  ```json
  {
    "preset": "standard",
    "settings": {
      "normalize": true,
      "compress": true,
      "eq": true
    }
  }
  ```

---

### Step 40: Summarize Before Script
**Directory**: `output/Blockchain_Fundamentals_2026-04-08_151006`

**What to Review**:
- Compare summary outline vs final script
- Verify script follows outline structure

**Key Files**:
- **content_summary.txt** - Stage 1: Summary/outline
- script.txt - Stage 2: Full script (should follow summary)
- metadata.json - Shows two-stage generation

---

### Step 38: Topic Queue
**File**: `output/topic_queue.json`

**What to Review**:
- Check queue structure
- Verify demo topics were added

**Expected Content**:
```json
{
  "topic_123": {
    "topic": "The Future of AI in Healthcare",
    "priority": 8,
    "status": "queued"
  }
}
```

---

### Step 42: Approval Workflow
**File**: `output/approval_workflow.json`

**What to Review**:
- Check workflow state structure
- Verify episode state tracking

---

## Quick Access Commands

```bash
# View all test episodes
ls -la output/*_2026-04-08_15*/

# Count episodes created
ls -d output/*_2026-04-08_15*/ | wc -l

# Check specific step
ls -la output/Space_Exploration_2026-04-08_150621/  # Step 29

# View episode index
python -c "from pathlib import Path; from core.episode_management import load_episode_index; eps = load_episode_index(Path('output/episode_index.json')); print(f'Total: {len(eps)} episodes')"

# Play audio (Windows)
start output/Future_of_Technology_2026-04-08_150654/podcast_nova.mp3
```

---

## Summary Statistics

- **Total Episodes Created**: 8
- **Steps with Full Episodes**: 7
- **Steps with Files Only**: 3 (queue, workflow, automation logs)
- **Total Audio Files**: 10 MP3s
- **Total Size**: ~15 MB
- **Longest Script**: Step 32 (3,493 bytes)
- **Shortest Script**: Step 29 (1,007 bytes)

---

**For Questions**: Check `FINAL_TEST_SUMMARY_PHASES_5A_8.md` for detailed results
