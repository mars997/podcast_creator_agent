"""
Quick test to validate that all UI dependencies are available
Run this before launching the UI to catch any import errors early.

Usage:
    python test_ui_imports.py
"""

import sys
from pathlib import Path

def test_imports():
    """Test all required imports for the UI"""
    print("[TEST] Testing UI Dependencies...\n")

    errors = []
    warnings = []

    # Test Streamlit
    try:
        import streamlit as st
        print("[OK] Streamlit imported successfully")
    except ImportError as e:
        errors.append(f"[ERROR] Streamlit not found: {e}")
        print(errors[-1])

    # Test core dependencies
    try:
        from dotenv import load_dotenv
        print("[OK] python-dotenv imported successfully")
    except ImportError as e:
        errors.append(f"[ERROR] python-dotenv not found: {e}")
        print(errors[-1])

    # Test providers
    try:
        from providers.factory import detect_available_providers, create_llm_provider, create_tts_provider
        print("[OK] Provider factory imported successfully")
    except ImportError as e:
        errors.append(f"[ERROR] Provider factory import failed: {e}")
        print(errors[-1])

    # Test core modules
    try:
        from core.unified_generation import UnifiedGenerationPipeline
        print("[OK] Unified generation pipeline imported successfully")
    except ImportError as e:
        errors.append(f"[ERROR] Unified generation import failed: {e}")
        print(errors[-1])

    try:
        from core.input_models import InputContext, GenerationMode, EpisodeResult
        print("[OK] Input models imported successfully")
    except ImportError as e:
        errors.append(f"[ERROR] Input models import failed: {e}")
        print(errors[-1])

    try:
        from core.source_management import extract_text_from_file, fetch_article_text
        print("[OK] Source management imported successfully")
    except ImportError as e:
        errors.append(f"[ERROR] Source management import failed: {e}")
        print(errors[-1])

    try:
        from core.episode_management import load_episode_index
        print("[OK] Episode management imported successfully")
    except ImportError as e:
        errors.append(f"[ERROR] Episode management import failed: {e}")
        print(errors[-1])

    try:
        import config
        print("[OK] Config imported successfully")
    except ImportError as e:
        errors.append(f"[ERROR] Config import failed: {e}")
        print(errors[-1])

    # Test optional dependencies
    try:
        import openai
        print("[OK] OpenAI SDK imported successfully")
    except ImportError:
        warnings.append("[WARN]  OpenAI SDK not found (optional)")
        print(warnings[-1])

    try:
        from providers.elevenlabs_provider import ElevenLabsTTSProvider
        print("[OK] ElevenLabs provider imported successfully")
    except ImportError:
        warnings.append("[WARN]  ElevenLabs provider not available (optional)")
        print(warnings[-1])

    # Check .env file
    print("\n[INFO] Checking configuration files...")
    env_file = Path(".env")
    if env_file.exists():
        print("[OK] .env file found")
    else:
        warnings.append("[WARN]  .env file not found (create from .env.example)")
        print(warnings[-1])

    # Check output directory
    output_dir = Path("output")
    if output_dir.exists():
        print(f"[OK] Output directory exists: {output_dir.absolute()}")
    else:
        print(f"[INFO]  Output directory will be created on first use")

    # Summary
    print("\n" + "="*50)
    print("[SUMMARY] Test Summary")
    print("="*50)

    if not errors:
        print("[OK] All required dependencies are available!")
        print("[READY] You can now run: streamlit run app.py")
        return 0
    else:
        print(f"[ERROR] Found {len(errors)} error(s):")
        for error in errors:
            print(f"   {error}")
        print("\n[TIP] Fix errors by running: pip install -r requirements.txt")
        return 1

    if warnings:
        print(f"\n[WARN]  {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"   {warning}")


if __name__ == "__main__":
    exit_code = test_imports()
    sys.exit(exit_code)
