"""
Batch update all step files to use provider abstraction.
This script makes surgical replacements to maintain code integrity.
"""

from pathlib import Path


def update_imports(content: str) -> str:
    """Replace OpenAI import with provider imports"""
    return content.replace(
        "from openai import OpenAI",
        "# Import provider abstraction (Step 21+)\n"
        "from providers import get_default_config, create_llm_provider, create_tts_provider\n"
        "import config"
    )


def update_initialization(content: str) -> str:
    """Replace client initialization with provider initialization"""
    old_init = """load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)"""

    new_init = """load_dotenv()

# Get provider configuration (auto-detects available providers)
provider_config = get_default_config()

# Create LLM and TTS providers
llm_provider = create_llm_provider(provider_config)
tts_provider = create_tts_provider(provider_config)

# Display active providers
print(f"\\n[Provider Info]")
print(f"  LLM: {llm_provider.provider_name.upper()} ({llm_provider.model_name})")
print(f"  TTS: {tts_provider.provider_name.upper()} ({tts_provider.model_name})")
print()"""

    return content.replace(old_init, new_init)


def update_config_usage(content: str) -> str:
    """Update config variables to use config module"""
    # Update DEFAULT_VOICE to be dynamic
    content = content.replace(
        'DEFAULT_VOICE = "nova"',
        'DEFAULT_VOICE = config.PROVIDER_MODELS.get(tts_provider.provider_name, {}).get("default_voice", "nova")'
    )

    # Update VALID_VOICES to use provider
    content = content.replace(
        'VALID_VOICES = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}',
        'VALID_VOICES = set(tts_provider.available_voices)'
    )

    # Update get_word_range function
    content = content.replace(
        """def get_word_range(length_choice: str) -> str:
    mapping = {
        "short": "300 to 450 words",
        "medium": "500 to 700 words",
        "long": "800 to 1100 words",
    }
    return mapping.get(length_choice.lower(), "500 to 700 words")""",
        """def get_word_range(length_choice: str) -> str:
    return config.get_word_range(length_choice)"""
    )

    return content


def update_llm_calls(content: str) -> str:
    """Replace LLM API calls with provider calls"""
    # Pattern 1: response = client.responses.create(...); return response.output_text.strip()
    import re

    # Multi-line pattern
    pattern1 = r'response = client\.responses\.create\(\s*model=(\w+),\s*input=(\w+)\s*\)\s*return response\.output_text\.strip\(\)'
    replacement1 = r'return llm_provider.generate_text(\2)'
    content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)

    # Pattern 2: response = ...; script = response.output_text
    pattern2 = r'response = client\.responses\.create\(\s*model=(\w+),\s*input=(\w+)\s*\)\s*(\w+) = response\.output_text'
    replacement2 = r'\3 = llm_provider.generate_text(\2)'
    content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

    return content


def update_tts_calls(content: str) -> str:
    """Replace TTS API calls with provider calls"""
    import re

    # Pattern: with client.audio.speech.with_streaming_response.create(...) as response: response.stream_to_file(...)
    pattern = r'with client\.audio\.speech\.with_streaming_response\.create\(\s*model=([^,]+),\s*voice=([^,]+),\s*input=([^,]+),?\s*\) as response:\s*response\.stream_to_file\(([^)]+)\)'
    replacement = r'tts_provider.generate_audio(\3, \2, \4)'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    return content


def update_metadata(content: str) -> str:
    """Update metadata to include provider info"""
    old_metadata = """"models": {
            "script_model": SCRIPT_MODEL,
            "tts_model": TTS_MODEL
        },"""

    new_metadata = """"providers": {
            "llm_provider": llm_provider.provider_name,
            "llm_model": llm_provider.model_name,
            "tts_provider": tts_provider.provider_name,
            "tts_model": tts_provider.model_name
        },
        "models": {
            "script_model": llm_provider.model_name,
            "tts_model": tts_provider.model_name
        },"""

    return content.replace(old_metadata, new_metadata)


def update_file(file_path: Path) -> bool:
    """Update a single file"""
    print(f"Updating {file_path.name}...", end=" ")

    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # Apply updates in sequence
        content = update_imports(content)
        content = update_initialization(content)
        content = update_config_usage(content)
        content = update_llm_calls(content)
        content = update_tts_calls(content)
        content = update_metadata(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            print("[OK] UPDATED")
            return True
        else:
            print("- No changes")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    """Update all files"""
    files = [
        "step6_podcast_episode.py",
        "step7_custom_podcast.py",
        "step8_podcast_from_source.py",
        "step9_multi_source_podcast.py",
        "step10_podcast_from_urls.py",
        "step11_configurable_podcast.py",
        "step12_hybrid_sources_podcast.py",
        "step13_mixed_sources_podcast.py",
        "step14_episode_metadata.py",
        "step15_episode_index.py",
        "step16_unique_episode_ids.py",
        "step18_regenerate_episode.py",
        "step19_rss_podcast.py",
    ]

    print("=" * 70)
    print("Batch Updating Step Files to Use Provider Abstraction")
    print("=" * 70)
    print()

    updated = 0
    for filename in files:
        file_path = Path(filename)
        if file_path.exists():
            if update_file(file_path):
                updated += 1
        else:
            print(f"[MISSING] {filename} NOT FOUND")

    print()
    print("=" * 70)
    print(f"Summary: Updated {updated}/{len(files)} files")
    print("=" * 70)


if __name__ == "__main__":
    main()
