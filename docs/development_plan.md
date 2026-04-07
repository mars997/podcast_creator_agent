# AI Podcast Creator Agent — Development Plan

## Purpose
This document is the canonical step-by-step implementation plan for the `podcast_creator_agent` project.

## Working rules
- Progress strictly one step at a time.
- Do not begin the next step until the current step is implemented, tested, and validated.
- Prefer the smallest possible code change that satisfies the current step.
- Keep all work grounded in the current codebase and existing project structure.
- Preserve secrets and local environment files such as `.env`.

---

## Phase 0 — Setup and proof of connectivity

### Step 1. Environment setup
- Create project folder in VS Code
- Create Python virtual environment
- Install dependencies
- Add `.env` for API key
- Verify the API key loads correctly

### Step 2. Connectivity and TTS proof of concept
- Verify Python can reach the API
- Resolve SSL / cert issues if needed
- Generate the first test audio file from hard-coded text

---

## Phase 1 — Core podcast generation

### Step 3. Topic-to-script generation
- User enters a topic
- LLM generates a solo-host podcast script

### Step 4. Save generated script
- Write the generated script to a local `.txt` file

### Step 5. End-to-end MVP
- Topic → script → saved script → audio file

---

## Phase 2 — Better episode structure

### Step 6. Episode packaging
- Create per-episode folder
- Save script
- Save show notes
- Save audio in one place

### Step 7. User customization
- Let user choose:
  - tone
  - voice
  - length

---

## Phase 3 — Source-driven podcast creation

### Step 8. Podcast from one local source file
- Read one `.txt` file
- Ground the episode in source content

### Step 9. Podcast from multiple local source files
- Combine multiple text files into one episode

### Step 10. Podcast from one or more URLs
- Fetch article text from public webpages
- Convert web content into a podcast episode

### Step 10A. URL parsing hardening
- Better error handling for failed URLs
- More reliable extraction logic
- Clearer messages when scraping fails

### Step 11. Configurable app structure
- Move defaults to a config section
- Centralize models, output root, voices, tones

### Step 12. Hybrid source mode
- Support either URLs or files in one script

### Step 13. Mixed-source mode
- Support URLs and files together in one episode

---

## Phase 4 — Metadata, memory, and episode tracking

### Step 14. Episode metadata
- Save `metadata.json` for each episode
- Include:
  - topic
  - tone
  - voice
  - source info
  - output paths
  - timestamp

### Step 15. Global episode index
- Maintain `output/episode_index.json`
- Append one summary entry for each run

### Step 16. Unique episode IDs / timestamped folders
- Prevent overwriting episodes with the same topic
- Example:
  - `AI_overview_2026-04-06_101500`

### Step 17. Episode loader / history browser
- Read from `episode_index.json`
- List past episodes
- Open paths for script, notes, audio, metadata

### Step 18. Regenerate from prior metadata
- Rebuild script/audio from a previous episode’s metadata and sources

---

## Phase 5 — Better content ingestion

### Step 19. RSS feed ingestion
- Pull articles automatically from RSS feeds
- Convert newest items into episodes

### Step 20. Newsletter / pasted-content ingestion
- Support long pasted text directly in terminal or file
- Make article copy/paste easier than creating files manually

### Step 21. PDF ingestion
- Read PDFs and extract text
- Turn PDFs into podcast episodes

### Step 22. YouTube transcript ingestion
- Accept transcript text or subtitles
- Turn video content into podcast summaries

### Step 23. Folder ingestion
- Point to a folder full of `.txt` files
- Automatically ingest everything inside

---

## Phase 5A — Multi-Provider Support

### Step 21. Provider abstraction layer
- Create provider abstraction for LLM and TTS
- Support both OpenAI and Google Gemini
- Allow mixing providers (e.g., Gemini LLM + OpenAI TTS)
- Smart fallback if preferred provider unavailable
- Backward compatible with existing episodes

### Step 22. Multi-provider podcast generation
- Generate podcasts using either OpenAI or Gemini
- Support hybrid configurations
- Track provider info in metadata
- Cost optimization options

### Step 23. Provider documentation
- Setup guide for OpenAI
- Setup guide for Gemini
- Environment variable reference
- Cost comparison
- Troubleshooting

---

## Phase 6 — Better script quality

### Step 24. Stronger podcast templates
- Support styles like:
  - solo explainer
  - news recap
  - interview-style monologue
  - daily briefing
  - deep dive

### Step 25. Two-host conversation mode
- Generate a host/co-host dialogue script
- Later render with two different voices

### Step 26. Stronger grounding rules
- Reduce hallucinations
- Force script to stay faithful to source material
- Highlight unsupported claims

### Step 27. Segment-aware generation
- Generate:
  - title
  - intro
  - segment 1
  - segment 2
  - segment 3
  - outro
- This helps with long episodes and later editing

### Step 28. Citation / source trace support
- Track which source sections informed which talking points
- Helpful for factual episodes

---

## Phase 7 — Better audio generation

### Step 29. Voice presets
- Map friendly names to voices and styles
- Example:
  - “calm educator”
  - “news anchor”
  - “casual host”

### Step 30. Chunk long scripts into audio segments
- Split long scripts safely for TTS
- Merge or save segments cleanly

### Step 31. Intro / outro audio branding
- Add standard intro/outro text
- Prepare structure for music or branding later

### Step 32. Multi-voice rendering
- Different voices for host and co-host
- Needed for interview-style podcasts

### Step 33. Audio post-processing
- Normalize volume
- Merge segments
- Optionally add pauses or separators

---

## Phase 8 — Agent automation

### Step 34. Automated episode generation
- Run daily / weekly on a schedule
- Pull from feeds or saved sources automatically

### Step 35. Topic queue
- Maintain a queue of future episode ideas
- Process them one by one

### Step 36. Source selection agent
- Automatically choose the best URLs/files for a given topic

### Step 37. Summarize before script generation
- First summarize all sources
- Then generate the podcast from that summary
- Improves consistency and reduces token load

### Step 38. Quality check pass
- Secondary LLM pass to check:
  - clarity
  - redundancy
  - unsupported claims
  - awkward phrasing

### Step 39. Episode approval workflow
- Human reviews script before audio generation
- Useful for team collaboration

---

## Phase 9 — Productization and team use

### Step 40. CLI improvements
- Better prompts
- Menus
- Retry flow
- Cleaner errors

### Step 41. Web UI
- Build a Streamlit or React front end
- Upload files, paste URLs, generate episodes visually

### Step 42. Team config files
- Shared config for tones, models, output rules
- Easier handoff across team members

### Step 43. Project packaging
- Turn scripts into modules
- Create folders like:
  - `ingestion/`
  - `generation/`
  - `audio/`
  - `storage/`

### Step 44. Logging
- Add structured logs
- Make debugging and monitoring easier

### Step 45. Tests
- Unit tests for helpers
- Integration tests for key workflows

---

## Phase 10 — Publishing and distribution

### Step 46. Export clean publish package
- Episode folder with:
  - script
  - notes
  - audio
  - metadata
  - source list

### Step 47. Generate podcast-ready descriptions
- SEO-friendly summary
- Episode title
- Social copy

### Step 48. RSS publishing support
- Generate podcast feed items
- Prepare for hosting / syndication

### Step 49. Cloud storage
- Save outputs to shared drive or object storage

### Step 50. Share / handoff workflow
- Export final episode package for editors, producers, or stakeholders
