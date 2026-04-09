# Step 21: PDF Ingestion - Complete

**Date**: 2026-04-08  
**Phase**: Phase 5 - Better Content Ingestion  
**Status**: ✅ COMPLETE

---

## Objective

Enable PDF file ingestion - extract text from PDFs and convert them into podcast episodes.

---

## Implementation Summary

### Core Functions Added

**File**: `core/source_management.py`

1. **`extract_text_from_pdf(pdf_path: Path) -> str`**
   - Extracts text from all pages of a PDF
   - Returns formatted text with page markers
   - Handles errors gracefully
   - Example output:
     ```
     PDF: document.pdf
     Pages: 5
     
     [Page 1]
     Content from first page...
     
     [Page 2]
     Content from second page...
     ```

2. **Enhanced `save_sources_to_directory()`**
   - Now automatically detects PDF files
   - Extracts text and saves as `.txt` for consistency
   - Tracks PDF vs text files in metadata
   - Works seamlessly with existing URL/file ingestion

### Dependencies Added

**Library**: `pypdf>=6.0.0`
- Installed: ✅
- Added to: `requirements.txt`
- Purpose: PDF text extraction

---

## How to Use

### Option 1: Test PDF Extraction Only

```bash
python test_pdf_ingestion.py
```

**What it does**:
1. Finds PDF files in current directory
2. Extracts and displays text preview
3. Shows stats (pages, characters, words)
4. Optionally creates full podcast episode

### Option 2: Create Episode from PDF (Interactive)

```bash
python test_pdf_ingestion.py
```

Then when prompted:
- Enter `y` to create full episode
- Choose tone/voice/length
- Episode created in `output/` folder

### Option 3: Use Core Functions Directly

```python
from pathlib import Path
from core.source_management import extract_text_from_pdf

# Extract text from PDF
pdf_path = Path("document.pdf")
text = extract_text_from_pdf(pdf_path)

print(f"Extracted {len(text)} characters")
print(text[:500])  # Preview
```

### Option 4: Integrate with Existing Scripts

Any script using `save_sources_to_directory()` now supports PDFs automatically:

```python
from core.source_management import save_sources_to_directory
from pathlib import Path

sources_dir = Path("output/episode/sources")
all_sources = []

# Mix PDFs with text files and URLs
successful, failed = save_sources_to_directory(
    sources_dir,
    all_sources,
    urls=["https://example.com/article"],
    files=[
        Path("document.pdf"),      # ← PDF support!
        Path("article.txt")
    ]
)

# all_sources now contains extracted PDF text + other sources
```

---

## Test Command

**Quick test with sample PDF**:

```bash
# Test extraction only (no episode creation)
python test_pdf_ingestion.py
```

**Expected output**:
```
======================================================================
TEST: PDF Text Extraction
======================================================================

[OK] Found PDF: sample_healthcare_ai.pdf

[OK] Text extracted successfully
  File: sample_healthcare_ai.pdf
  Size: 1971 bytes
  Extracted length: 1312 characters
  Word count: 178 words

[PREVIEW] First 300 characters:
----------------------------------------------------------------------
PDF: sample_healthcare_ai.pdf
Pages: 1

[Page 1]
AI in Healthcare: The Future of Medicine
Artificial Intelligence is revolutionizing healthcare...
----------------------------------------------------------------------
```

---

## Files Created

### Core Module Updates
- ✅ `core/source_management.py` - Added `extract_text_from_pdf()`
- ✅ `core/source_management.py` - Enhanced `save_sources_to_directory()` for PDFs
- ✅ `requirements.txt` - Added `pypdf>=6.0.0`

### Test Files
- ✅ `test_pdf_ingestion.py` - Comprehensive PDF test script
- ✅ `sample_healthcare_ai.pdf` - Sample PDF for testing

### Documentation
- ✅ `STEP21_PDF_INGESTION.md` - This file

---

## Episode Structure (When Creating Full Episode)

```
output/
  └── AI_in_Healthcare_2026-04-08_125430/
      ├── sources/
      │   └── source_1_sample_healthcare_ai.txt  ← Extracted PDF text
      ├── script.txt
      ├── show_notes.txt
      ├── podcast_nova.mp3
      └── metadata.json
```

### Metadata Example

```json
{
  "created_at": "2026-04-08T12:54:30",
  "episode_id": "AI_in_Healthcare_2026-04-08_125430",
  "topic": "AI in Healthcare",
  "source_type": "pdf",
  "pdf_info": {
    "filename": "sample_healthcare_ai.pdf",
    "size_bytes": 1971,
    "extracted_chars": 1312,
    "extracted_words": 178
  },
  "outputs": {
    "episode_dir": "output/AI_in_Healthcare_2026-04-08_125430",
    "script_file": "output/AI_in_Healthcare_2026-04-08_125430/script.txt"
  }
}
```

---

## Features

✅ **Multi-page PDF support** - Extracts text from all pages  
✅ **Page markers** - Each page labeled for context  
✅ **Error handling** - Graceful failures with clear messages  
✅ **Automatic detection** - PDF files detected by `.pdf` extension  
✅ **Seamless integration** - Works with existing source management  
✅ **Metadata tracking** - PDF info saved in episode metadata  
✅ **Text normalization** - Extracted text saved as `.txt` for consistency  

---

## Supported PDF Types

✅ **Text-based PDFs** - PDFs with selectable text  
❌ **Image-only PDFs** - Scanned documents (would need OCR)  
✅ **Multi-page documents** - Any number of pages  
✅ **Reports, articles, papers** - Academic or business documents  

**Note**: For image-only PDFs, would need OCR library like `pytesseract`.

---

## Testing Checklist

- [x] Install pypdf library
- [x] Create `extract_text_from_pdf()` function
- [x] Enhance `save_sources_to_directory()` for PDF support
- [x] Create test script
- [x] Generate sample PDF
- [x] Test extraction only
- [x] Test full episode creation
- [x] Update requirements.txt
- [x] Create documentation

---

## Next Steps (Phase 5 Continued)

- **Step 22**: YouTube transcript ingestion
- **Step 23**: Folder ingestion (batch process multiple files)

---

## Quick Commands Reference

```bash
# Test PDF extraction
python test_pdf_ingestion.py

# Use directly in Python
python -c "from pathlib import Path; from core.source_management import extract_text_from_pdf; print(extract_text_from_pdf(Path('sample_healthcare_ai.pdf'))[:200])"

# Create episode from PDF (will prompt for settings)
python test_pdf_ingestion.py
# Then enter 'y' when asked

# View all episodes (including PDF-based ones)
python step17_episode_browser.py --list

# Check if PDF in episode index
python -c "from pathlib import Path; from core.episode_management import load_episode_index; episodes = load_episode_index(Path('output/episode_index.json')); pdf_eps = [e for e in episodes if e.get('source_type') == 'pdf']; print(f'PDF episodes: {len(pdf_eps)}')"
```

---

**Implementation**: Core functions only (no separate step file)  
**Test Status**: ✅ ALL TESTS PASSING  
**Ready for**: Step 22 (YouTube transcripts)
