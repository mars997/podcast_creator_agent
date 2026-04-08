# Test Plan: Steps 1-20 Regression Validation

## Objective
Validate that all functionality from Steps 1-20 works correctly after the `refactor_steps` branch refactoring, which introduced provider abstraction and core module organization.

## Scope
**IN SCOPE**: Steps 1-20 functionality only  
**OUT OF SCOPE**: Step 21+ features (provider abstraction testing beyond basic backward compatibility)

## Refactor Summary
The refactor introduced:
- `providers/` module (Step 21 - but used by Steps 1-20 for backward compat)
- `core/` module (extracted common utilities)
- `config.py` (centralized configuration)
- Migrated all step files to use provider abstraction

## Test Strategy
1. Verify environment/config loading works
2. Test each step script can execute basic functionality
3. Validate output files are created correctly
4. Check backward compatibility with existing .env
5. Use lightweight test inputs to avoid API costs/failures

---

## Test Cases

### Phase 0: Setup and Connectivity

#### Step 1: Environment Setup
- **Test ID**: T01
- **Description**: Verify .env loads correctly, virtual environment works
- **Test Method**: Check .env file exists, venv activated, dependencies installed
- **Success Criteria**: 
  - `.env` file present with API keys
  - `venv` activated
  - Required packages installed (feedparser, beautifulsoup4, requests)
- **Input**: N/A
- **Expected Output**: Config loads without errors

#### Step 2: TTS Proof of Concept  
- **Test ID**: T02
- **Description**: Generate test audio from hardcoded text
- **Test Method**: Run script with minimal input
- **Success Criteria**: Audio file created, playable format
- **Input**: Hardcoded text in script
- **Expected Output**: `podcast_test.mp3` or similar
- **Note**: May skip if SSL issues persist

---

### Phase 1: Core Podcast Generation

#### Step 3: Topic-to-Script Generation
- **Test ID**: T03
- **Description**: Generate script from topic
- **Test Method**: Run step3 with simple topic
- **Success Criteria**: Script text generated
- **Input**: Topic: "test topic"
- **Expected Output**: Script text returned
- **Note**: May fail due to SSL/API issues

#### Step 4: Save Generated Script
- **Test ID**: T04
- **Description**: Script saved to file
- **Test Method**: Run step4, check file created
- **Success Criteria**: `.txt` file with script content
- **Input**: Generated script
- **Expected Output**: `script.txt` file

#### Step 5: End-to-End MVP
- **Test ID**: T05
- **Description**: Topic → script → audio
- **Test Method**: Run step5 with test topic
- **Success Criteria**: Script and audio files created
- **Input**: Test topic
- **Expected Output**: `script.txt`, `podcast.mp3`
- **Note**: May fail due to SSL/API issues

---

### Phase 2: Episode Structure

#### Step 6: Episode Packaging
- **Test ID**: T06
- **Description**: Per-episode folder with script, notes, audio
- **Test Method**: Run step6, verify folder structure
- **Success Criteria**: 
  - Episode folder created
  - Contains script.txt, show_notes.txt, audio file
- **Input**: Test topic
- **Expected Output**: `output/topic_name/` folder with files

#### Step 7: User Customization
- **Test ID**: T07
- **Description**: Tone, voice, length customization
- **Test Method**: Run step7 with custom settings
- **Success Criteria**: Settings reflected in output
- **Input**: 
  - Topic: "test"
  - Tone: professional
  - Voice: alloy
  - Length: short
- **Expected Output**: Customized episode

---

### Phase 3: Source-Driven Creation

#### Step 8: Single Local Source File
- **Test ID**: T08
- **Description**: Create podcast from one .txt file
- **Test Method**: Run step8 with test source file
- **Success Criteria**: Podcast created from file content
- **Input**: `source.txt` (existing)
- **Expected Output**: Episode grounded in source content

#### Step 9: Multiple Local Source Files
- **Test ID**: T09
- **Description**: Create podcast from multiple .txt files
- **Test Method**: Run step9 with 2+ source files
- **Success Criteria**: Podcast combines multiple sources
- **Input**: `source.txt`, `source2.txt`
- **Expected Output**: Combined episode

#### Step 10: URL Ingestion
- **Test ID**: T10
- **Description**: Create podcast from URL(s)
- **Test Method**: Run step10 with test URL
- **Success Criteria**: Article fetched and processed
- **Input**: Sample URL (stable, simple)
- **Expected Output**: Episode from URL content
- **Note**: Use simple, stable URL or skip if network issues

#### Step 10A: URL Parsing Hardening
- **Test ID**: T10A
- **Description**: Better error handling for failed URLs
- **Test Method**: Verify error messages, partial success
- **Success Criteria**: Clear errors, continues with valid URLs
- **Input**: Mix of valid/invalid URLs
- **Expected Output**: Processed valid URLs, reported failures

#### Step 11: Configurable App Structure
- **Test ID**: T11
- **Description**: Config-based defaults (models, voices, tones)
- **Test Method**: Check config.py loads correctly
- **Success Criteria**: Defaults accessible from config module
- **Input**: N/A
- **Expected Output**: Config values available

#### Step 12: Hybrid Source Mode
- **Test ID**: T12
- **Description**: Support URLs OR files (not both)
- **Test Method**: Run with URL only, then file only
- **Success Criteria**: Both modes work independently
- **Input**: URL xor file
- **Expected Output**: Episode from chosen source type

#### Step 13: Mixed Source Mode
- **Test ID**: T13
- **Description**: URLs AND files together
- **Test Method**: Run with both URL and file
- **Success Criteria**: Combined episode from both types
- **Input**: URL + file
- **Expected Output**: Episode combining both sources

---

### Phase 4: Metadata and History

#### Step 14: Episode Metadata
- **Test ID**: T14
- **Description**: Save metadata.json for each episode
- **Test Method**: Run episode generation, check metadata file
- **Success Criteria**: 
  - `metadata.json` created
  - Contains: topic, tone, voice, sources, outputs, timestamp
- **Input**: Any episode generation
- **Expected Output**: Complete metadata.json

#### Step 15: Global Episode Index
- **Test ID**: T15
- **Description**: Maintain episode_index.json
- **Test Method**: Generate multiple episodes, check index
- **Success Criteria**:
  - `output/episode_index.json` exists
  - Contains all episodes
  - Appends new entries
- **Input**: Multiple episodes
- **Expected Output**: Updated index file

#### Step 16: Unique Episode IDs
- **Test ID**: T16
- **Description**: Timestamped folders prevent overwrites
- **Test Method**: Run same topic twice, verify 2 folders
- **Success Criteria**:
  - Folder name: `{topic}_{YYYY-MM-DD_HHMMSS}`
  - No overwrites
  - Both episodes preserved
- **Input**: Same topic, run twice
- **Expected Output**: 2 distinct episode folders

#### Step 17: Episode Browser
- **Test ID**: T17
- **Description**: Browse episode history from index
- **Test Method**: Run step17_episode_browser.py
- **Success Criteria**:
  - Lists all episodes
  - Shows details
  - Views files
- **Input**: N/A (reads index)
- **Expected Output**: Interactive browser or list view

#### Step 18: Regenerate from Metadata
- **Test ID**: T18
- **Description**: Rebuild episode from metadata+sources
- **Test Method**: Select existing episode, regenerate
- **Success Criteria**:
  - Loads metadata
  - Loads sources
  - Creates new timestamped episode
  - Original preserved
- **Input**: Existing episode selection
- **Expected Output**: New regenerated episode

#### Step 19: RSS Feed Ingestion
- **Test ID**: T19
- **Description**: Create podcast from RSS feed
- **Test Method**: Run step19 with test RSS feed
- **Success Criteria**:
  - Feed parsed
  - Articles extracted
  - Episode created
  - `rss_feed_info.json` saved
- **Input**: Sample RSS feed URL
- **Expected Output**: Episode with RSS metadata

#### Step 20: Pasted Content Ingestion
- **Test ID**: T20
- **Description**: Create podcast from pasted text
- **Test Method**: Run step20 with test content
- **Success Criteria**:
  - Accepts multi-line input or file path
  - Saves to `pasted_content.txt`
  - Generates episode
- **Input**: Text content (paste or file)
- **Expected Output**: Episode from pasted content

---

## Testing Constraints

### SSL/API Issues
- Current environment has SSL certificate issues blocking OpenAI API
- Some tests will use demo/mock mode
- Focus on validating code structure and file I/O

### Test Data
- Use existing test files: `source.txt`, `source2.txt`
- Use stable RSS feeds: NYT Technology
- Use simple, static content for pasting
- Avoid fragile external dependencies

### Success Thresholds
- **Critical**: Core file I/O, module imports, config loading
- **Important**: Episode structure, metadata, indexing
- **Nice-to-have**: Full API integration (blocked by SSL)

---

## Test Execution Order
1. Environment validation (T01)
2. Config loading (T11)
3. Core utilities (file ops, validation funcs)
4. Simple scripts first (T04, T06, T11, T14, T15, T16, T17)
5. Source-based scripts (T08, T09, T12, T13)
6. Complex workflows (T18, T19, T20)
7. API-dependent scripts last (T02, T03, T05, T07, T10) - may skip

---

## Pass/Fail Criteria

### PASS
- Script runs without import errors
- Expected files created in correct locations
- File contents reasonable/expected
- No regressions vs. original behavior

### FAIL
- Import errors from refactoring
- Missing expected output files
- Incorrect file structure
- Behavior different from Steps 1-20 spec

### SKIP
- API calls fail due to SSL (acceptable if structure validated)
- Network-dependent tests if network unavailable
- Non-critical edge cases

---

## Deliverables
1. `TEST_RESULTS_STEP1_20.md` - Detailed results for each test
2. `KNOWN_ISSUES_STEP1_20.md` - Documented issues/risks
3. Fixed code (if regressions found)
4. Merge recommendation

---

**Created**: 2026-04-08  
**Branch**: refactor_steps  
**Scope**: Steps 1-20 only  
**Status**: Ready to execute
