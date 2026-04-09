# Testing Plan: Phases 5A through 8 (Steps 25-42)

**Status**: READY TO TEST (requires valid API key)

---

## Prerequisites

**CRITICAL**: Update `.env` file with valid API key:

```bash
# Current (INVALID):
OPENAI_API_KEY=OPENAI_API_KEY

# Required (replace with actual key):
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

Get your key from: https://platform.openai.com/api-keys

---

## Test Coverage

### Phase 5A: Multi-Provider Support (Steps 25-26)
- ✅ Step 25: Multi-provider podcast generation
- ✅ Step 26: Provider documentation (doc file, no test needed)

### Phase 6: Better Script Quality (Steps 27-31)
- ✅ Step 27: Podcast templates
- ✅ Step 28: Multi-character mode
- ✅ Step 29: Grounding rules
- ✅ Step 30: Segment-aware generation
- ✅ Step 31: Citation support

### Phase 7: Better Audio Generation (Steps 32-36)
- ✅ Step 32: Voice persona system (BUG FIXED)
- ✅ Step 33: Audio chunking
- ✅ Step 34: Intro/outro branding
- ✅ Step 35: Multi-voice rendering
- ✅ Step 36: Audio post-processing

### Phase 8: Agent Automation (Steps 37-42)
- ✅ Step 37: Automated generation
- ✅ Step 38: Topic queue
- ✅ Step 39: Source selection agent
- ✅ Step 40: Summarize first
- ✅ Step 41: Quality check
- ✅ Step 42: Approval workflow

**Total**: 18 steps (17 executable + 1 documentation)

---

## Automated Test Script

Run all tests automatically:

```bash
python run_all_tests_phases_5a_to_8.py
```

This will:
1. Check API key validity
2. Run each step with predefined inputs
3. Generate episode outputs
4. Create summary report
5. Estimated time: 40-60 minutes

---

## Manual Test Commands

### Phase 5A

**Step 25: Multi-Provider Podcast**
```bash
python step25_multi_provider_podcast.py
# Input: 1, 1, "AI in Healthcare", casual, nova, short
```

### Phase 6

**Step 27: Podcast Templates**
```bash
python step27_podcast_templates.py
# Input: 1 (Solo Explainer), "Renewable Energy", casual, nova, short
```

**Step 28: Multi-Character Podcast**
```bash
python step28_multi_character_podcast.py
# Input: "Climate Change Debate", 2, casual, short
```

**Step 29: Grounding Rules**
```bash
python step29_grounding_rules.py
# Input: 2 (Balanced), "Space Exploration", paste text, casual, nova, short
```

**Step 30: Segment-Aware Generation**
```bash
python step30_segment_aware_generation.py
# Input: 1 (Basic structure), "Quantum Computing", professional, onyx, medium
```

**Step 31: Citation Support**
```bash
python step31_citation_support.py
# Input: 1 (Inline), "Artificial Intelligence", paste sources, professional, shimmer, short
```

### Phase 7

**Step 32: Voice Persona System**
```bash
python step32_voice_persona_system.py
# Input: 1 (Tech Enthusiast), "Future of AI", short
```

**Step 33: Audio Chunking**
```bash
python step33_audio_chunking.py
# Input: "Long Form Content", casual, nova, 4000
```

**Step 34: Intro/Outro Branding**
```bash
python step34_intro_outro_branding.py
# Input: 1 (tech), "AI News", casual, echo, short
```

**Step 35: Multi-Voice Rendering**
```bash
python step35_multi_voice_rendering.py
# Input: "AI Panel Discussion", 2, casual, short, n (auto voices)
```

**Step 36: Audio Post-Processing**
```bash
python step36_audio_post_processing.py
# Input: 2 (standard), "Processed Podcast", professional, alloy, short
```

### Phase 8

**Step 37: Automated Generation**
```bash
python step37_automated_generation.py
# Input: 1 (Daily Briefing), "Tech News Today"
```

**Step 38: Topic Queue**
```bash
python step38_topic_queue.py
# Input: 7 (add demo topics), 4 (process batch), 3
```

**Step 39: Source Selection Agent**
```bash
python step39_source_selection_agent.py
# Input: "Future of Renewable Energy", n (don't create episode)
```

**Step 40: Summarize First**
```bash
python step40_summarize_first.py
# Input: "Blockchain Technology", professional, fable, short, a (approve)
```

**Step 41: Quality Check**
```bash
python step41_quality_check.py
# Input: 2 (paste script), "Test Topic", casual, [paste sample script], n
```

**Step 42: Approval Workflow**
```bash
python step42_approval_workflow.py
# Input: Interactive menu testing
```

---

## Expected Outputs

Each step should create an episode directory in `output/` with:

### Standard Files
- `script.txt` - Generated podcast script
- `show_notes.txt` - Episode show notes
- `podcast_[voice].mp3` - Audio file
- `metadata.json` - Episode metadata

### Step-Specific Files

**Step 27**: Uses template structure
**Step 28**: `voice_assignments.txt`
**Step 29**: `grounding_info.txt`, `sources/`
**Step 30**: `segment_breakdown.txt`
**Step 31**: `citation_map.json`, `sources/`
**Step 32**: `persona_profile.json`
**Step 33**: `audio_chunks/`, `chunk_info.json`
**Step 34**: `branding/` (intro.mp3, main_content.mp3, outro.mp3)
**Step 35**: `voice_segments/`, `segment_info.json`, `voice_assignments.json`
**Step 36**: `podcast_[voice]_raw.mp3`, `processing_info.json`
**Step 37**: Automation log in `automation_logs/`
**Step 38**: `topic_queue.json`
**Step 39**: Source selection in `source_selections/`
**Step 40**: `content_summary.txt`
**Step 41**: Quality report in `quality_reports/`
**Step 42**: `approval_workflow.json`

---

## Known Issues

1. **Step 32**: Fixed - `validate_choice()` bug
2. **All steps**: Require valid OpenAI API key
3. **Step 33, 34, 35, 36**: May require `pydub` for audio manipulation
   ```bash
   pip install pydub
   ```

---

## Bugs Fixed

- ✅ `providers/factory.py` - Added `load_dotenv()` import and call
- ✅ `step32_voice_persona_system.py` - Fixed `validate_choice()` call

---

## Post-Test Verification

After running tests, verify:

```bash
# Count generated episodes
ls -d output/*/ | wc -l

# List all episode directories
ls -la output/

# Check episode index
python -c "from core.episode_management import load_episode_index; from pathlib import Path; eps = load_episode_index(Path('output/episode_index.json')); print(f'{len(eps)} total episodes')"

# View latest episodes
python step17_episode_browser.py --list | tail -20
```

---

## Summary Report Location

After all tests complete, review:
- `TEST_RESULTS_PHASES_5A_TO_8.md` - Detailed test results
- `output/episode_index.json` - All episodes metadata
- Individual episode directories in `output/`

---

**NEXT STEP**: Update `.env` with valid API key, then run the automated test script.
