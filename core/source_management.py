"""
Source management utilities for podcast creation.

This module provides functions to:
- Fetch article text from URLs
- Read text from local files
- Read and extract text from PDF files
- Fetch YouTube video transcripts
- Batch process files from folders
- Parse comma-separated inputs
- Load and save source materials
"""

from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
import re

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

from core.file_utils import save_text_file, read_text_file as _read_text_file

# Optional imports for additional file types
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import ebooklib
    from ebooklib import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False


def fetch_article_text(url: str) -> str:
    """
    Fetch and extract article text from a URL.

    Args:
        url: The URL to fetch

    Returns:
        Formatted text with title, URL, and article content

    Raises:
        requests.HTTPError: If the request fails
        ValueError: If no article text could be extracted

    Examples:
        >>> text = fetch_article_text("https://example.com/article")
        >>> # Returns: "Title: Article Title\\nURL: https://...\\n\\nArticle content..."
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else "Untitled"

    # Extract paragraphs
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p) > 40]

    article_text = "\n".join(paragraphs[:80]).strip()

    if not article_text:
        raise ValueError(f"Could not extract article text from: {url}")

    return f"Title: {title}\nURL: {url}\n\n{article_text}"


def read_text_file(file_path: Path) -> str:
    """
    Read text from a file and format for podcast source.

    This is a wrapper around core.file_utils.read_text_file that
    adds the filename to the output.

    Args:
        file_path: Path to the text file

    Returns:
        Formatted text with filename and content

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty
    """
    content = _read_text_file(file_path)
    return f"File: {file_path.name}\n\n{content}"


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text content from a PDF file.

    Reads all pages from a PDF and combines them into a single text string
    with page markers for better context.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Formatted text with PDF filename, page count, and extracted content

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If PDF is empty or cannot be read

    Examples:
        >>> text = extract_text_from_pdf(Path("document.pdf"))
        >>> # Returns: "PDF: document.pdf\\nPages: 5\\n\\n[Page 1]\\nContent..."
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not pdf_path.suffix.lower() == '.pdf':
        raise ValueError(f"File is not a PDF: {pdf_path}")

    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)

        if num_pages == 0:
            raise ValueError(f"PDF file is empty: {pdf_path}")

        # Extract text from all pages
        all_text = []
        for i, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text.strip():
                all_text.append(f"[Page {i}]\n{page_text.strip()}")

        if not all_text:
            raise ValueError(f"No text could be extracted from PDF: {pdf_path}")

        combined_text = "\n\n".join(all_text)

        return f"PDF: {pdf_path.name}\nPages: {num_pages}\n\n{combined_text}"

    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"Error reading PDF {pdf_path}: {e}")


def extract_video_id(youtube_url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats.

    Supports multiple YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID

    Args:
        youtube_url: YouTube video URL

    Returns:
        Video ID string or None if not found

    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    # Pattern 1: youtube.com/watch?v=VIDEO_ID
    if 'youtube.com/watch' in youtube_url:
        parsed = urlparse(youtube_url)
        query_params = parse_qs(parsed.query)
        return query_params.get('v', [None])[0]

    # Pattern 2: youtu.be/VIDEO_ID
    if 'youtu.be/' in youtube_url:
        return youtube_url.split('youtu.be/')[-1].split('?')[0]

    # Pattern 3: youtube.com/embed/VIDEO_ID
    if 'youtube.com/embed/' in youtube_url:
        return youtube_url.split('embed/')[-1].split('?')[0]

    # Pattern 4: Try regex as fallback
    match = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', youtube_url)
    return match.group(1) if match else None


def fetch_youtube_transcript(youtube_url: str, languages: List[str] = None) -> str:
    """
    Fetch transcript/subtitles from a YouTube video.

    Downloads available transcripts (auto-generated or manual) and formats
    them as readable text for podcast script generation.

    Args:
        youtube_url: YouTube video URL
        languages: List of language codes to try (default: ['en'])

    Returns:
        Formatted transcript text with video metadata

    Raises:
        ValueError: If video ID cannot be extracted or transcript unavailable

    Examples:
        >>> transcript = fetch_youtube_transcript("https://www.youtube.com/watch?v=VIDEO_ID")
        >>> # Returns: "YouTube Video: VIDEO_ID\\nTranscript:\\n\\nHello everyone..."
    """
    if languages is None:
        languages = ['en']

    # Extract video ID
    video_id = extract_video_id(youtube_url)
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {youtube_url}")

    try:
        # Fetch transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=languages
        )

        # Combine all transcript segments
        full_text = []
        for segment in transcript_list:
            text = segment['text'].strip()
            if text:
                full_text.append(text)

        if not full_text:
            raise ValueError(f"Transcript is empty for video: {video_id}")

        combined_text = " ".join(full_text)

        # Format with metadata
        return f"YouTube Video: {video_id}\nURL: {youtube_url}\nTranscript:\n\n{combined_text}"

    except TranscriptsDisabled:
        raise ValueError(f"Transcripts are disabled for video: {video_id}")
    except NoTranscriptFound:
        raise ValueError(f"No transcript found for video: {video_id} (languages: {languages})")
    except VideoUnavailable:
        raise ValueError(f"Video unavailable: {video_id}")
    except Exception as e:
        raise ValueError(f"Error fetching transcript for {video_id}: {e}")


def scan_folder_for_files(
    folder_path: Path,
    extensions: List[str] = None,
    recursive: bool = False
) -> List[Path]:
    """
    Scan a folder for files with specific extensions.

    Finds all files in a folder that match the given extensions.
    Can optionally search recursively through subdirectories.

    Args:
        folder_path: Path to the folder to scan
        extensions: List of file extensions to include (e.g., ['.txt', '.pdf'])
                   If None, defaults to ['.txt', '.pdf', '.md']
        recursive: If True, search subdirectories recursively

    Returns:
        List of Path objects for matching files

    Raises:
        FileNotFoundError: If folder doesn't exist
        ValueError: If folder path is not a directory

    Examples:
        >>> files = scan_folder_for_files(Path("documents"))
        >>> # Returns: [Path("documents/file1.txt"), Path("documents/file2.pdf"), ...]

        >>> # Recursive search
        >>> files = scan_folder_for_files(Path("documents"), recursive=True)

        >>> # Custom extensions
        >>> files = scan_folder_for_files(Path("docs"), extensions=['.md', '.txt'])
    """
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    if not folder_path.is_dir():
        raise ValueError(f"Path is not a directory: {folder_path}")

    if extensions is None:
        extensions = ['.txt', '.pdf', '.md']

    # Normalize extensions (ensure they start with '.')
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    found_files = []

    if recursive:
        # Recursive search
        for ext in extensions:
            pattern = f"**/*{ext}"
            found_files.extend(folder_path.glob(pattern))
    else:
        # Non-recursive search
        for ext in extensions:
            pattern = f"*{ext}"
            found_files.extend(folder_path.glob(pattern))

    # Sort by name for consistent ordering
    found_files = sorted(found_files, key=lambda p: p.name.lower())

    return found_files


def process_folder_sources(
    folder_path: Path,
    extensions: List[str] = None,
    recursive: bool = False
) -> Tuple[List[Path], Dict[str, Any]]:
    """
    Process all supported files from a folder.

    Scans a folder for files, categorizes them by type, and returns
    information about what was found.

    Args:
        folder_path: Path to the folder to process
        extensions: List of file extensions to include
        recursive: If True, search subdirectories

    Returns:
        Tuple of (file_list, folder_info) where:
        - file_list: List of Path objects for files to process
        - folder_info: Dict with folder metadata (path, file counts, etc.)

    Examples:
        >>> files, info = process_folder_sources(Path("documents"))
        >>> print(f"Found {info['total_files']} files")
        >>> print(f"Text files: {info['text_files']}, PDFs: {info['pdf_files']}")
    """
    files = scan_folder_for_files(folder_path, extensions, recursive)

    # Categorize files by extension
    text_files = [f for f in files if f.suffix.lower() in ['.txt', '.md']]
    pdf_files = [f for f in files if f.suffix.lower() == '.pdf']

    folder_info = {
        "folder_path": str(folder_path),
        "total_files": len(files),
        "text_files": len(text_files),
        "pdf_files": len(pdf_files),
        "recursive": recursive,
        "extensions": extensions or ['.txt', '.pdf', '.md']
    }

    return files, folder_info


def parse_csv_input(raw_text: str) -> List[str]:
    """
    Parse comma-separated input into a list of items.

    Strips whitespace from each item and filters out empty items.

    Args:
        raw_text: Comma-separated string

    Returns:
        List of non-empty, stripped items

    Examples:
        >>> parse_csv_input("url1, url2, url3")
        ['url1', 'url2', 'url3']
        >>> parse_csv_input("file1,  , file2")
        ['file1', 'file2']
        >>> parse_csv_input("")
        []
    """
    return [item.strip() for item in raw_text.split(",") if item.strip()]


def load_source_files(sources_dir: Path) -> List[str]:
    """
    Load all source text files from a directory.

    Reads all .txt files in the directory and formats them as
    numbered sources.

    Args:
        sources_dir: Directory containing source .txt files

    Returns:
        List of formatted source texts

    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If no source files found

    Examples:
        >>> sources = load_source_files(Path("output/episode/sources"))
        >>> # Returns: ["Source 1:\\nContent...", "Source 2:\\nContent..."]
    """
    if not sources_dir.exists():
        raise FileNotFoundError(f"Sources directory not found: {sources_dir}")

    source_files = sorted(sources_dir.glob("*.txt"))
    if not source_files:
        raise ValueError(f"No source files found in: {sources_dir}")

    all_sources = []
    for i, source_file in enumerate(source_files, start=1):
        try:
            content = source_file.read_text(encoding="utf-8").strip()
            if content:
                all_sources.append(f"Source {i}:\n{content}")
        except Exception as e:
            # Skip files that can't be read
            print(f"  Warning: Could not read {source_file.name}: {e}")

    return all_sources


def save_sources_to_directory(
    sources_dir: Path,
    sources: List[str],
    urls: List[str] = None,
    files: List[Path] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fetch/read sources and save them to a directory.

    Fetches articles from URLs and/or reads local files, saves them
    to the sources directory, and returns metadata about successful
    and failed operations.

    Args:
        sources_dir: Directory where sources should be saved
        sources: List to append formatted source texts to (modified in place)
        urls: Optional list of URLs to fetch
        files: Optional list of file paths to read

    Returns:
        Tuple of (successful_sources, failed_sources) where each is a list of dicts

    Examples:
        >>> sources = []
        >>> success, failed = save_sources_to_directory(
        ...     Path("output/episode/sources"),
        ...     sources,
        ...     urls=["https://example.com/article"],
        ...     files=[Path("local.txt")]
        ... )
    """
    sources_dir.mkdir(parents=True, exist_ok=True)

    successful_sources = []
    failed_sources = []
    source_counter = 1

    # Fetch URLs (articles or YouTube videos)
    if urls:
        print("Fetching content from URLs...")
        for url in urls:
            try:
                # Check if YouTube URL
                if 'youtube.com' in url or 'youtu.be' in url:
                    print(f"  Detecting YouTube video: {url}")
                    content_text = fetch_youtube_transcript(url)
                    content_type = "youtube"
                    video_id = extract_video_id(url)
                    filename = f"source_{source_counter}_youtube_{video_id}.txt"
                else:
                    content_text = fetch_article_text(url)
                    content_type = "url"
                    domain = urlparse(url).netloc.replace(".", "_")
                    filename = f"source_{source_counter}_{domain}.txt"

                sources.append(f"Source {source_counter}:\n{content_text}")

                source_file = sources_dir / filename
                save_text_file(content_text, source_file)
                print(f"Saved {content_type} source {source_counter}: {source_file.resolve()}")

                successful_sources.append({
                    "type": content_type,
                    "source": url,
                    "saved_file": str(source_file)
                })
                source_counter += 1
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                failed_sources.append({
                    "type": "url" if 'youtube' not in url else "youtube",
                    "source": url,
                    "error": str(e)
                })

    # Read local files (text or PDF)
    if files:
        print("Reading local files...")
        for file_path in files:
            try:
                # Check if PDF
                if file_path.suffix.lower() == '.pdf':
                    file_text = extract_text_from_pdf(file_path)
                    file_type = "pdf"
                    print(f"  Extracting PDF: {file_path.name}")
                else:
                    file_text = read_text_file(file_path)
                    file_type = "file"

                sources.append(f"Source {source_counter}:\n{file_text}")

                # Save extracted content as .txt for consistency
                if file_path.suffix.lower() == '.pdf':
                    copied_file = sources_dir / f"source_{source_counter}_{file_path.stem}.txt"
                else:
                    copied_file = sources_dir / f"source_{source_counter}_{file_path.name}"

                save_text_file(file_text, copied_file)
                print(f"Saved {file_type} source {source_counter}: {copied_file.resolve()}")

                successful_sources.append({
                    "type": file_type,
                    "source": str(file_path),
                    "saved_file": str(copied_file)
                })
                source_counter += 1
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")
                failed_sources.append({
                    "type": "file",
                    "source": str(file_path),
                    "error": str(e)
                })

    return successful_sources, failed_sources


# ===== NEW: Enhanced File Type Support =====

def extract_text_from_docx(file_path: Path) -> str:
    """
    Extract text from DOCX file.

    Args:
        file_path: Path to DOCX file

    Returns:
        Formatted text with filename and content

    Raises:
        ImportError: If python-docx is not installed
        Exception: If file cannot be read
    """
    if not DOCX_AVAILABLE:
        raise ImportError(
            "python-docx not installed. Install it with: pip install python-docx"
        )

    doc = Document(file_path)

    # Extract paragraphs
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)

    content = "\n\n".join(paragraphs)

    return f"DOCX: {file_path.name}\n\n{content}"


def extract_text_from_epub(file_path: Path) -> str:
    """
    Extract text from EPUB ebook file.

    Args:
        file_path: Path to EPUB file

    Returns:
        Formatted text with title and content

    Raises:
        ImportError: If ebooklib is not installed
        Exception: If file cannot be read
    """
    if not EPUB_AVAILABLE:
        raise ImportError(
            "ebooklib not installed. Install it with: pip install ebooklib"
        )

    book = epub.read_epub(file_path)

    # Extract metadata
    title = book.get_metadata('DC', 'title')
    title_str = title[0][0] if title else file_path.stem

    # Extract text from all items
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Parse HTML content
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            if text:
                chapters.append(text)

    content = "\n\n".join(chapters)

    return f"EPUB: {title_str}\nFile: {file_path.name}\n\n{content}"


def extract_text_from_html(file_path: Path) -> str:
    """
    Extract text from HTML file.

    Args:
        file_path: Path to HTML file

    Returns:
        Formatted text with filename and content
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()

    # Extract text
    text = soup.get_text(separator='\n', strip=True)

    # Clean up whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    content = '\n'.join(lines)

    return f"HTML: {file_path.name}\n\n{content}"


def transcribe_audio(audio_file: Path, api_key: Optional[str] = None) -> str:
    """
    Transcribe audio file using OpenAI Whisper API.

    Args:
        audio_file: Path to audio file (mp3, wav, m4a, etc.)
        api_key: Optional OpenAI API key (uses env var if not provided)

    Returns:
        Transcribed text

    Raises:
        ImportError: If openai is not installed
        Exception: If transcription fails
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "openai package not installed. Install it with: pip install openai"
        )

    import os

    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    with open(audio_file, 'rb') as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text"
        )

    return f"Audio Transcript: {audio_file.name}\n\n{transcript}"


def analyze_audio_style(audio_file: Path, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze audio for speaking style traits (NO voice cloning).

    This function transcribes audio and uses LLM to extract style traits
    like energy, pacing, humor, tone. It does NOT clone the voice.

    Args:
        audio_file: Path to audio file
        api_key: Optional OpenAI API key

    Returns:
        Dictionary with style traits:
        {
            "energy": "low|medium|high|extreme",
            "pacing": "slow|moderate|fast|rapid",
            "humor": "none|subtle|moderate|high",
            "tone": "warm|cool|sharp|smooth",
            "intensity": "calm|moderate|intense|chaotic",
            "transcript_preview": "First 200 chars..."
        }

    Raises:
        Exception: If analysis fails
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "openai package not installed. Install it with: pip install openai"
        )

    import os
    import json

    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    # Step 1: Transcribe audio
    with open(audio_file, 'rb') as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text"
        )

    # Step 2: Analyze transcript for style traits
    prompt = f"""Analyze this transcript for speaking style traits. Focus on delivery characteristics, NOT content.

Transcript:
{transcript[:2000]}

Extract these traits:
1. Energy level: low, medium, high, or extreme
2. Pacing: slow, moderate, fast, or rapid
3. Humor level: none, subtle, moderate, or high
4. Tone: warm, cool, sharp, or smooth
5. Intensity: calm, moderate, intense, or chaotic

Respond ONLY with valid JSON in this exact format:
{{
  "energy": "medium",
  "pacing": "moderate",
  "humor": "subtle",
  "tone": "warm",
  "intensity": "moderate"
}}"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    analysis_text = response.choices[0].message.content.strip()

    # Parse JSON response
    try:
        analysis = json.loads(analysis_text)
    except json.JSONDecodeError:
        # Fallback if LLM doesn't return proper JSON
        analysis = {
            "energy": "medium",
            "pacing": "moderate",
            "humor": "subtle",
            "tone": "warm",
            "intensity": "moderate"
        }

    # Add transcript preview
    analysis["transcript_preview"] = transcript[:200] + "..." if len(transcript) > 200 else transcript

    return analysis


def match_style_to_archetype(style_traits: Dict[str, str]) -> str:
    """
    Map analyzed style traits to closest voice archetype.

    Args:
        style_traits: Dict with energy, pacing, humor, tone, intensity

    Returns:
        Voice archetype ID (e.g., "rapid_fire_comedian")
    """
    from core.voice_styles import VOICE_STYLES

    energy = style_traits.get("energy", "medium")
    pacing = style_traits.get("pacing", "moderate")
    humor = style_traits.get("humor", "subtle")

    # Simple matching logic
    for style_id, style in VOICE_STYLES.items():
        if (style.energy_level.value == energy and
            style.pacing.value == pacing and
            style.humor_level.value == humor):
            return style_id

    # Fallback matching by energy + pacing only
    for style_id, style in VOICE_STYLES.items():
        if (style.energy_level.value == energy and
            style.pacing.value == pacing):
            return style_id

    # Default fallback
    return "warm_educator"


def extract_text_from_file(file_path: Path) -> str:
    """
    Extract text from any supported file type.

    Automatically detects file type by extension and uses appropriate extractor.

    Supported types:
    - .txt, .md: Plain text
    - .pdf: PDF documents
    - .docx: Word documents (if python-docx installed)
    - .epub: Ebooks (if ebooklib installed)
    - .html, .htm: HTML files

    Args:
        file_path: Path to file

    Returns:
        Extracted text

    Raises:
        ValueError: If file type is not supported
    """
    ext = file_path.suffix.lower()

    if ext in ['.txt', '.md']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return f"Text File: {file_path.name}\n\n{content}"

    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)

    elif ext == '.docx':
        return extract_text_from_docx(file_path)

    elif ext == '.epub':
        return extract_text_from_epub(file_path)

    elif ext in ['.html', '.htm']:
        return extract_text_from_html(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {ext}. "
            f"Supported: .txt, .md, .pdf, .docx, .epub, .html"
        )


# ============================================================================
# Voice Cloning Functions (Coqui TTS)
# ============================================================================

def save_voice_clone_reference(audio_file: Path, voices_dir: Path = None) -> Path:
    """
    Save uploaded audio as voice clone reference.

    Args:
        audio_file: Path to uploaded audio file
        voices_dir: Directory to store voice references (default: voices/)

    Returns:
        Path to saved voice reference file
    """
    if voices_dir is None:
        voices_dir = Path("voices")

    voices_dir.mkdir(exist_ok=True)

    # Copy audio file to voices directory
    import shutil
    voice_ref_path = voices_dir / f"voice_clone_{audio_file.name}"
    shutil.copy(audio_file, voice_ref_path)

    print(f"[OK] Voice reference saved: {voice_ref_path}")
    return voice_ref_path


def get_voice_clone_path(voices_dir: Path = None) -> Optional[Path]:
    """
    Get the most recent voice clone reference.

    Args:
        voices_dir: Directory containing voice references

    Returns:
        Path to most recent voice clone, or None if none exist
    """
    if voices_dir is None:
        voices_dir = Path("voices")

    if not voices_dir.exists():
        return None

    # Find most recent voice clone file
    voice_files = list(voices_dir.glob("voice_clone_*"))
    if not voice_files:
        return None

    # Sort by modification time, most recent first
    voice_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return voice_files[0]


def clear_voice_clone(voices_dir: Path = None):
    """
    Clear all voice clone references.

    Args:
        voices_dir: Directory containing voice references
    """
    if voices_dir is None:
        voices_dir = Path("voices")

    if not voices_dir.exists():
        return

    # Remove all voice clone files
    for voice_file in voices_dir.glob("voice_clone_*"):
        voice_file.unlink()
        print(f"[INFO] Removed: {voice_file.name}")

    print("[OK] Voice clones cleared")
