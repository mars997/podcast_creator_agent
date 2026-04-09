```markdown
# Step 23: Folder Ingestion - Complete

**Date**: 2026-04-08  
**Phase**: Phase 5 - Better Content Ingestion  
**Status**: ✅ COMPLETE

---

## Objective

Enable folder batch processing - automatically ingest and process all files from a folder, supporting recursive scanning.

---

## Implementation Summary

### Core Functions Added

**File**: `core/source_management.py`

1. **`scan_folder_for_files(folder_path: Path, extensions: List[str] = None, recursive: bool = False) -> List[Path]`**
   - Scans folder for files with specific extensions
   - Supports recursive subdirectory scanning
   - Default extensions: `.txt`, `.pdf`, `.md`
   - Returns sorted list of file paths
   - Example:
     ```python
     files = scan_folder_for_files(Path("documents"))
     # Returns: [Path("documents/file1.txt"), Path("documents/file2.pdf"), ...]
     ```

2. **`process_folder_sources(folder_path: Path, extensions: List[str] = None, recursive: bool = False) -> Tuple[List[Path], Dict]`**
   - Processes folder and returns file list + metadata
   - Categorizes files by type (text, PDF, etc.)
   - Provides statistics (total files, by type)
   - Example:
     ```python
     files, info = process_folder_sources(Path("docs"))
     print(f"Found {info['total_files']} files")
     print(f"Text: {info['text_files']}, PDFs: {info['pdf_files']}")
     ```

3. **Existing `save_sources_to_directory()`**
   - Already supports batch file processing
   - Just pass list of files from folder scan
   - Handles mixed file types (text, PDF) automatically

---

## How to Use

### Option 1: Interactive Test (Recommended)

```bash
python test_folder_ingestion.py
```

**Menu options**:
1. Test folder scanning (creates sample folder with test files)
2. Test recursive scanning (includes subdirectories)
3. Create full episode from test folder
4. Create episode from custom folder path

### Option 2: Quick Folder Scan Test

```bash
python test_folder_ingestion.py
```

Then:
- Choose option `1` (Test folder scanning)
- Creates `test_folder_sources/` with 3 sample files
- Shows file list and statistics

### Option 3: Use Core Functions Directly

```python
from pathlib import Path
from core.source_management import scan_folder_for_files, process_folder_sources

# Scan folder for files
folder = Path("documents")
files = scan_folder_for_files(folder)
print(f"Found {len(files)} files")

# Get detailed info
files, info = process_folder_sources(folder)
print(f"Text files: {info['text_files']}")
print(f"PDF files: {info['pdf_files']}")

# Recursive scan
files_recursive = scan_folder_for_files(folder, recursive=True)
print(f"Recursive scan found {len(files_recursive)} files")
```

### Option 4: Create Episode from Folder

```python
from pathlib import Path
from core.source_management import scan_folder_for_files, save_sources_to_directory

# Scan folder
folder = Path("my_documents")
files = scan_folder_for_files(folder)

# Process all files at once
sources_dir = Path("output/episode/sources")
all_sources = []

successful, failed = save_sources_to_directory(
    sources_dir,
    all_sources,
    urls=None,
    files=files  # ← Batch process entire folder!
)

print(f"Processed {len(successful)} files")
# all_sources now contains content from all files
```

---

## Test Command

**Quick test with sample folder**:

```bash
python test_folder_ingestion.py
```

**What happens**:
1. Shows menu with 4 options
2. Choose option 1 to create test folder
3. View file list and statistics
4. Optionally create full episode (option 3)

---

## Expected Output

```
======================================================================
TEST: Folder Scanning
======================================================================

[OK] Test folder created: test_folder_sources
  Created 3 sample files

[OK] Found 3 files:
  - article1.txt (46 bytes)
  - article2.txt (50 bytes)
  - notes.md (47 bytes)

[OK] Folder info:
  Total files: 3
  Text files: 3
  PDF files: 0
```

---

## Files Created

### Core Module Updates
- ✅ `core/source_management.py` - Added `scan_folder_for_files()`
- ✅ `core/source_management.py` - Added `process_folder_sources()`

### Test Files
- ✅ `test_folder_ingestion.py` - Comprehensive folder ingestion test
- ✅ `test_folder_sources/` - Auto-created sample folder (during test)

### Documentation
- ✅ `STEP23_FOLDER_INGESTION.md` - This file

---

## Episode Structure (When Creating Full Episode)

```
output/
  └── test_folder_sources_2026-04-08_140530/
      ├── sources/
      │   ├── source_1_article1.txt          ← From folder file 1
      │   ├── source_2_article2.txt          ← From folder file 2
      │   └── source_3_notes.txt             ← From folder file 3
      ├── script.txt
      ├── show_notes.txt
      ├── podcast_nova.mp3
      └── metadata.json
```

### Metadata Example

```json
{
  "created_at": "2026-04-08T14:05:30",
  "episode_id": "test_folder_sources_2026-04-08_140530",
  "topic": "test_folder_sources",
  "source_type": "folder",
  "folder_info": {
    "folder_path": "test_folder_sources",
    "total_files": 3,
    "successful_files": 3,
    "failed_files": 0,
    "combined_chars": 1250,
    "combined_words": 195
  },
  "outputs": {
    "episode_dir": "output/test_folder_sources_2026-04-08_140530"
  }
}
```

---

## Features

✅ **Batch file processing** - Process entire folder at once  
✅ **Recursive scanning** - Include subdirectories  
✅ **Multiple file types** - Text, PDF, Markdown  
✅ **Custom extensions** - Specify which file types to include  
✅ **File statistics** - Count files by type  
✅ **Sorted output** - Files processed in alphabetical order  
✅ **Error handling** - Continue processing if individual files fail  
✅ **Metadata tracking** - Folder path and file counts saved  

---

## Supported File Types

✅ **Text files** (`.txt`)  
✅ **PDF files** (`.pdf`)  
✅ **Markdown files** (`.md`)  
✅ **Custom extensions** (specify in function call)  

---

## Scanning Options

### Non-Recursive (Default)
```python
# Scans only top-level folder
files = scan_folder_for_files(Path("docs"))
```

**Structure**:
```
docs/
  - file1.txt      ← Included
  - file2.pdf      ← Included
  subfolder/
    - file3.txt    ← NOT included
```

### Recursive
```python
# Scans all subdirectories
files = scan_folder_for_files(Path("docs"), recursive=True)
```

**Structure**:
```
docs/
  - file1.txt      ← Included
  - file2.pdf      ← Included
  subfolder/
    - file3.txt    ← Included!
    nested/
      - file4.txt  ← Included!
```

### Custom Extensions
```python
# Only scan for specific file types
files = scan_folder_for_files(
    Path("docs"),
    extensions=['.md', '.txt']  # Only markdown and text
)
```

---

## Use Cases

### 1. Research Papers Folder
```python
# Process all PDFs in research folder
papers = scan_folder_for_files(
    Path("research_papers"),
    extensions=['.pdf']
)
# Create podcast summarizing all papers
```

### 2. Blog Posts Collection
```python
# Process all markdown blog posts
posts = scan_folder_for_files(
    Path("blog_posts"),
    extensions=['.md'],
    recursive=True
)
# Create podcast from blog content
```

### 3. Notes Compilation
```python
# Process all text notes
notes = scan_folder_for_files(
    Path("meeting_notes"),
    extensions=['.txt', '.md']
)
# Create podcast summary of all notes
```

---

## Error Handling

### Folder Not Found
```
FileNotFoundError: Folder not found: /path/to/folder
```
**Solution**: Verify folder path exists

### Not a Directory
```
ValueError: Path is not a directory: /path/to/file.txt
```
**Solution**: Provide a folder path, not a file path

### No Files Found
```python
files = scan_folder_for_files(Path("empty_folder"))
# Returns: []  (empty list, not an error)
```

### Individual File Failures
- Folder processing continues even if some files fail
- Failed files tracked in `failed_sources` list
- Successful files still processed

---

## Testing Checklist

- [x] Create `scan_folder_for_files()` function
- [x] Create `process_folder_sources()` function
- [x] Test non-recursive scanning
- [x] Test recursive scanning
- [x] Test custom extensions
- [x] Test with mixed file types (text + PDF)
- [x] Test folder statistics
- [x] Test full episode creation from folder
- [x] Create comprehensive test script
- [x] Create documentation

---

## Performance Notes

- **File sorting**: Files are sorted alphabetically for consistent processing order
- **Lazy loading**: Files are scanned but not read until processed
- **Memory efficient**: Processes files one at a time, not all in memory
- **Large folders**: Can handle hundreds of files efficiently

---

## Quick Commands Reference

```bash
# Interactive test (recommended)
python test_folder_ingestion.py

# Scan folder in Python
python -c "from pathlib import Path; from core.source_management import scan_folder_for_files; files = scan_folder_for_files(Path('test_folder_sources')); print(f'Found {len(files)} files')"

# Get folder statistics
python -c "from pathlib import Path; from core.source_management import process_folder_sources; files, info = process_folder_sources(Path('test_folder_sources')); print(info)"

# Recursive scan
python -c "from pathlib import Path; from core.source_management import scan_folder_for_files; files = scan_folder_for_files(Path('.'), recursive=True, extensions=['.py']); print(f'Found {len(files)} Python files')"

# View all episodes (including folder-based ones)
python step17_episode_browser.py --list

# Check folder episodes in index
python -c "from pathlib import Path; from core.episode_management import load_episode_index; episodes = load_episode_index(Path('output/episode_index.json')); folder_eps = [e for e in episodes if e.get('source_type') == 'folder']; print(f'Folder episodes: {len(folder_eps)}')"
```

---

## Next Steps

**Phase 5 Complete!** ✅

All Better Content Ingestion steps done:
- ✅ Step 21: PDF Ingestion
- ✅ Step 22: YouTube Transcript Ingestion
- ✅ Step 23: Folder Ingestion

**Next Phase**: Phase 6 or other advanced features

---

**Implementation**: Core functions only (no separate step file)  
**Test Status**: ✅ ALL TESTS PASSING  
**Phase 5 Status**: ✅ COMPLETE
```
