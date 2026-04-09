"""
Test Script for Refactored Podcast Creator System

Tests all 6 generation modes with the unified pipeline.
"""

import sys
from pathlib import Path
from datetime import datetime

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.unified_generation import UnifiedGenerationPipeline
from core.input_models import InputContext, GenerationMode, Character, InteractionStyle, DepthPreference
from step32_voice_persona_system import PERSONA_LIBRARY, create_custom_persona
from step27_podcast_templates import PODCAST_TEMPLATES
import config


def print_header(text):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def test_mode(mode_name, context, pipeline, output_root):
    """Test a single generation mode"""
    print(f"\n[TEST] {mode_name}")
    print(f"  Topic: {context.get_primary_topic()}")
    print(f"  Mode: {context.mode.value}")

    try:
        result = pipeline.generate(context, output_root)

        print(f"  [OK] Generated successfully")
        print(f"  Episode ID: {result.episode_id}")
        print(f"  Script length: {len(result.script)} chars")
        print(f"  Audio: {Path(result.audio_path).name}")
        print(f"  Location: {result.episode_dir}")

        return True

    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print_header("Refactored System Test Suite")

    # Detect providers
    available = detect_available_providers()
    if not available:
        print("\n[ERROR] No providers available. Set OPENAI_API_KEY or GOOGLE_API_KEY")
        sys.exit(1)

    provider_name = list(available.keys())[0]
    print(f"\n[INFO] Using provider: {provider_name}")

    # Initialize providers
    provider_config = ProviderConfig(
        llm_provider=provider_name,
        tts_provider=provider_name
    )
    llm_provider = create_llm_provider(provider_config)
    tts_provider = create_tts_provider(provider_config)

    print(f"[INFO] Available voices: {', '.join(tts_provider.available_voices[:3])}...")

    # Initialize pipeline
    pipeline = UnifiedGenerationPipeline(llm_provider, tts_provider)
    output_root = Path(config.OUTPUT_ROOT)

    results = {}

    # ===== TEST 1: Topic Mode =====
    print_header("Test 1: Topic Mode (Enhanced)")

    context = InputContext(
        mode=GenerationMode.TOPIC,
        main_topic="Quantum Computing Basics",
        topic_details="Focus on recent breakthroughs and practical applications",
        focus_areas=["Qubit technology", "Error correction", "Real-world use cases"],
        desired_style="educational but accessible",
        tone="educational",
        length="short",
        voice_provider=provider_name
    )

    results["topic_mode"] = test_mode("Topic Mode", context, pipeline, output_root)

    # ===== TEST 2: Text Mode =====
    print_header("Test 2: Text Mode (Long-form)")

    sample_text = """
    Artificial Intelligence has transformed how we approach problem-solving in the 21st century.
    From healthcare diagnostics to financial modeling, AI systems are now integral to modern society.

    The key breakthrough came with deep learning, which allows machines to learn patterns from data
    without explicit programming. This has enabled remarkable achievements in image recognition,
    natural language processing, and game playing.

    However, challenges remain. Bias in training data can lead to unfair outcomes. The "black box"
    nature of neural networks makes them difficult to interpret. And the energy consumption of
    large models raises environmental concerns.

    Looking forward, the field is moving toward more efficient architectures, better interpretability,
    and frameworks for ensuring AI systems align with human values.
    """

    context = InputContext(
        mode=GenerationMode.TEXT,
        text_content=sample_text,
        preserve_structure=True,
        add_commentary=False,
        tone="professional",
        length="short",
        voice_provider=provider_name
    )

    results["text_mode"] = test_mode("Text Mode", context, pipeline, output_root)

    # ===== TEST 3: Source Material Mode =====
    print_header("Test 3: Source Material Mode")

    source_material = """
    QUARTERLY REPORT - KEY FINDINGS

    Revenue: $45M (up 23% YoY)
    User Growth: 2.3M active users (up 15%)
    Churn Rate: 3.2% (down from 4.1%)

    Major Product Launches:
    - Mobile app redesign (released Q2)
    - Enterprise tier (beta testing)
    - API platform (developer preview)

    Challenges:
    - Increased competition in SMB segment
    - Infrastructure scaling costs rising
    - Regulatory compliance in EU markets

    Q4 Priorities:
    - Complete enterprise tier launch
    - Expand into APAC markets
    - Improve onboarding conversion (currently 45%)
    """

    context = InputContext(
        mode=GenerationMode.SOURCE,
        source_material=source_material,
        source_title="Q3 2026 Business Report",
        emphasis_instructions="Focus on growth metrics and Q4 priorities",
        target_audience="Business Leaders",
        depth_preference=DepthPreference.SUMMARY,
        tone="professional",
        length="short",
        voice_provider=provider_name
    )

    results["source_mode"] = test_mode("Source Material Mode", context, pipeline, output_root)

    # ===== TEST 4: Multi-Character Mode =====
    print_header("Test 4: Multi-Character Mode")

    characters = [
        Character(
            name="Dr. Chen",
            role="Expert",
            personality="analytical and precise",
            speaking_style="uses technical terms, explains with examples",
            preferred_voice=tts_provider.available_voices[0],
            energy_level="medium",
            humor_style=None
        ),
        Character(
            name="Alex",
            role="Host",
            personality="curious and enthusiastic",
            speaking_style="asks clarifying questions, makes connections",
            preferred_voice=tts_provider.available_voices[1 % len(tts_provider.available_voices)],
            energy_level="high",
            humor_style="playful"
        )
    ]

    context = InputContext(
        mode=GenerationMode.MULTI_CHARACTER,
        main_topic="The Future of Renewable Energy",
        characters=characters,
        interaction_style=InteractionStyle.INTERVIEW,
        tone="casual",
        length="short",
        voice_provider=provider_name
    )

    results["multi_character_mode"] = test_mode("Multi-Character Mode", context, pipeline, output_root)

    # ===== TEST 5: Persona Mode =====
    print_header("Test 5: Persona Mode")

    persona = PERSONA_LIBRARY["documentary_sage"]

    context = InputContext(
        mode=GenerationMode.PERSONA,
        main_topic="The Life Cycle of Stars",
        persona=persona,
        fun_vs_serious=0.7,  # More serious/informative
        tone="educational",
        length="short",
        voice_provider=provider_name
    )

    results["persona_mode"] = test_mode("Persona Mode", context, pipeline, output_root)

    # ===== TEST 6: Template Mode =====
    print_header("Test 6: Template Mode")

    context = InputContext(
        mode=GenerationMode.TEMPLATE,
        main_topic="Understanding Blockchain Technology",
        template_key="solo_explainer",
        tone="educational",
        length="short",
        voice_provider=provider_name
    )

    results["template_mode"] = test_mode("Template Mode", context, pipeline, output_root)

    # ===== SUMMARY =====
    print_header("Test Results Summary")

    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    for mode, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {mode}")

    print(f"\nPassed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")

    if failed == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failed} test(s) failed")

    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
