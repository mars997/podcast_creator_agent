"""
Script to update all step*.py files to use provider abstraction.
"""

import re
from pathlib import Path

# Files to update (excluding already updated ones)
FILES_TO_UPDATE = [
    "step4_save_script.py",
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


def update_file(file_path: Path) -> bool:
    """Update a single file to use provider abstraction"""
    print(f"Updating {file_path.name}...")

    content = file_path.read_text(encoding="utf-8")
    original_content = content

    # Replace OpenAI import
    content = re.sub(
        r'from openai import OpenAI',
        '# Import provider abstraction (Step 21+)\nfrom providers import get_default_config, create_llm_provider, create_tts_provider',
        content
    )

    # Replace client initialization (various patterns)
    # Pattern 1: Simple initialization
    content = re.sub(
        r'api_key = os\.getenv\("OPENAI_API_KEY"\)\s*\n'
        r'if not api_key:\s*\n'
        r'\s+raise ValueError\("OPENAI_API_KEY not found.*?"\)\s*\n'
        r'\s*\n'
        r'client = OpenAI\(api_key=api_key\)',
        '# Get provider configuration\n'
        'provider_config = get_default_config()\n'
        'llm_provider = create_llm_provider(provider_config)\n'
        'tts_provider = create_tts_provider(provider_config)\n\n'
        'print(f"LLM: {llm_provider.provider_name.upper()} ({llm_provider.model_name})")\n'
        'print(f"TTS: {tts_provider.provider_name.upper()} ({tts_provider.model_name})")',
        content,
        flags=re.DOTALL
    )

    # Replace client.responses.create() calls
    content = re.sub(
        r'response = client\.responses\.create\(\s*\n'
        r'\s+model=(\w+),\s*\n'
        r'\s+input=(\w+)\s*\n'
        r'\s+\)\s*\n'
        r'\s+return response\.output_text\.strip\(\)',
        r'return llm_provider.generate_text(\2)',
        content,
        flags=re.DOTALL
    )

    # Replace client.responses.create() inline
    content = re.sub(
        r'response = client\.responses\.create\(\s*model=(\w+),\s*input=(\w+)\s*\)\s*\n'
        r'\s*(\w+) = response\.output_text',
        r'\3 = llm_provider.generate_text(\2)',
        content,
        flags=re.DOTALL
    )

    # Replace TTS calls
    content = re.sub(
        r'with client\.audio\.speech\.with_streaming_response\.create\(\s*\n'
        r'\s+model=([^,]+),\s*\n'
        r'\s+voice=([^,]+),\s*\n'
        r'\s+input=([^,]+),?\s*\n'
        r'\s+\) as response:\s*\n'
        r'\s+response\.stream_to_file\(([^)]+)\)',
        r'tts_provider.generate_audio(\3, \2, \4)',
        content,
        flags=re.DOTALL
    )

    # Replace models metadata in JSON
    content = re.sub(
        r'"models": \{\s*\n'
        r'\s+"script_model": SCRIPT_MODEL,\s*\n'
        r'\s+"tts_model": TTS_MODEL\s*\n'
        r'\s+\}',
        '"providers": {\n'
        '            "llm_provider": llm_provider.provider_name,\n'
        '            "llm_model": llm_provider.model_name,\n'
        '            "tts_provider": tts_provider.provider_name,\n'
        '            "tts_model": tts_provider.model_name\n'
        '        },\n'
        '        "models": {\n'
        '            "script_model": llm_provider.model_name,\n'
        '            "tts_model": tts_provider.model_name\n'
        '        }',
        content,
        flags=re.DOTALL
    )

    # Check if anything changed
    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        print(f"  ✓ Updated {file_path.name}")
        return True
    else:
        print(f"  - No changes needed for {file_path.name}")
        return False


def main():
    """Update all step files"""
    print("=" * 70)
    print("Updating step files to use provider abstraction")
    print("=" * 70)
    print()

    updated_count = 0

    for filename in FILES_TO_UPDATE:
        file_path = Path(filename)

        if not file_path.exists():
            print(f"  ⚠ File not found: {filename}")
            continue

        if update_file(file_path):
            updated_count += 1

    print()
    print("=" * 70)
    print(f"Updated {updated_count}/{len(FILES_TO_UPDATE)} files")
    print("=" * 70)


if __name__ == "__main__":
    main()
