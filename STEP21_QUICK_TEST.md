# Step 21: PDF Ingestion - Quick Test Guide

## ✅ COMPLETE - Test It Now!

---

## 🚀 Quick Test (30 seconds)

**Single command to test everything**:

```bash
python test_pdf_ingestion.py
```

**What you'll see**:
1. PDF found: `sample_healthcare_ai.pdf`
2. Text extracted successfully
3. Preview of first 300 characters
4. Option to create full episode

---

## 📝 Sample Output

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

## 🎯 What Was Added

### Core Functions (No Step File!)

**File**: `core/source_management.py`

```python
# New function - extract PDF text
from core.source_management import extract_text_from_pdf

text = extract_text_from_pdf(Path("document.pdf"))
# Returns: "PDF: document.pdf\nPages: 5\n\n[Page 1]\nContent..."
```

### Automatic PDF Detection

Any script using `save_sources_to_directory()` now supports PDFs:

```python
from core.source_management import save_sources_to_directory

# This now works with PDFs!
save_sources_to_directory(
    sources_dir,
    all_sources,
    files=[Path("document.pdf")]  # ← Automatically detected!
)
```

---

## 🔧 How to Use in Your Code

```python
from pathlib import Path
from core.source_management import extract_text_from_pdf

# Extract text from any PDF
pdf_path = Path("your_document.pdf")
text = extract_text_from_pdf(pdf_path)

print(f"Extracted: {len(text)} characters")
print(f"Words: {len(text.split())}")
```

---

## 📁 Output Files Location

After creating episode from PDF:

```
output/
  └── AI_in_Healthcare_2026-04-08_HHMMSS/
      ├── sources/
      │   └── source_1_sample_healthcare_ai.txt  ← PDF text here
      ├── script.txt                             ← Generated script
      ├── show_notes.txt                         ← Generated notes
      ├── podcast_nova.mp3                       ← Audio file
      └── metadata.json                          ← Includes PDF info
```

---

## ✨ Quick Commands

```bash
# Test PDF extraction
python test_pdf_ingestion.py

# View episode with PDF source
python step17_episode_browser.py --list

# Extract PDF directly in terminal
python -c "from pathlib import Path; from core.source_management import extract_text_from_pdf; print(extract_text_from_pdf(Path('sample_healthcare_ai.pdf')))"
```

---

## 📊 What Gets Tracked

Metadata includes PDF-specific info:

```json
{
  "source_type": "pdf",
  "pdf_info": {
    "filename": "sample_healthcare_ai.pdf",
    "size_bytes": 1971,
    "extracted_chars": 1312,
    "extracted_words": 178
  }
}
```

---

## ✅ Status

- **Library installed**: pypdf ✅
- **Core functions added**: ✅
- **Test script created**: ✅
- **Sample PDF created**: ✅
- **Tested and working**: ✅

---

**Ready to test?** Run this:

```bash
python test_pdf_ingestion.py
```

**Want to create full episode?** When prompted, enter `y` and follow the prompts!
