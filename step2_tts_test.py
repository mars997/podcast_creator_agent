"""
DEPRECATED: This script is kept for backward compatibility and manual testing.

For automated testing of TTS functionality, use:
- Unit tests (fast, mocked): pytest tests/unit/test_tts_provider.py
- Integration tests (real API): pytest tests/integration/test_tts_integration.py -m integration

This script remains useful for quick manual validation but is not part of the test suite.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Import provider abstraction (Step 21+)
from providers import get_default_config, create_tts_provider

load_dotenv()

# Get provider configuration and create TTS provider
provider_config = get_default_config()
tts_provider = create_tts_provider(provider_config)

print(f"Using TTS provider: {tts_provider.provider_name.upper()} ({tts_provider.model_name})")

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "podcast_test.mp3"

script_text = """
Welcome to my first AI-generated podcast.
This is a short test episode created with Python in Visual Studio Code.
If you can hear this audio clearly, then step two is working successfully.
"""

# Use TTS provider instead of direct OpenAI client
tts_provider.generate_audio(script_text, "alloy", output_file)

print(f"Audio saved to: {output_file.resolve()}")