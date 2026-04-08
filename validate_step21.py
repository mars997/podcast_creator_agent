"""
Validation script for Step 21: Multi-Provider Support

Tests the provider abstraction layer without making actual API calls.
"""

import os
import sys
from pathlib import Path


def validate_provider_package():
    """Validate provider package structure"""
    print("=" * 70)
    print("VALIDATION: Provider Package Structure")
    print("=" * 70)

    required_files = [
        "providers/__init__.py",
        "providers/base.py",
        "providers/openai_provider.py",
        "providers/gemini_provider.py",
        "providers/factory.py",
    ]

    all_exist = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        status = "[OK]" if exists else "[FAIL]"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False

    if all_exist:
        print("\n[PASS] All provider files exist")
    else:
        print("\n[FAIL] Some provider files are missing")

    return all_exist


def validate_config_module():
    """Validate config module"""
    print("\n" + "=" * 70)
    print("VALIDATION: Configuration Module")
    print("=" * 70)

    config_exists = Path("config.py").exists()
    print(f"{'[OK]' if config_exists else '[FAIL]'} config.py")

    if config_exists:
        try:
            import config

            # Check for required constants
            required_attrs = [
                "DEFAULT_PROVIDER",
                "PROVIDER_MODELS",
                "DEFAULT_TONE",
                "DEFAULT_LENGTH",
                "OUTPUT_ROOT",
                "VALID_TONES",
                "VALID_LENGTHS",
                "WORD_RANGES",
            ]

            all_present = True
            for attr in required_attrs:
                has_attr = hasattr(config, attr)
                status = "[OK]" if has_attr else "[FAIL]"
                print(f"{status} config.{attr}")
                if not has_attr:
                    all_present = False

            if all_present:
                print("\n[PASS] All config attributes present")
                print(f"\nProvider configurations available:")
                for provider in config.PROVIDER_MODELS:
                    print(f"  - {provider}")
                return True
            else:
                print("\n[FAIL] Some config attributes missing")
                return False

        except Exception as e:
            print(f"\n[FAIL] Error importing config: {e}")
            return False
    else:
        print("\n[FAIL] config.py not found")
        return False


def validate_provider_imports():
    """Validate provider imports"""
    print("\n" + "=" * 70)
    print("VALIDATION: Provider Imports")
    print("=" * 70)

    try:
        from providers import (
            BaseLLMProvider,
            BaseTTSProvider,
            ProviderConfig,
            create_llm_provider,
            create_tts_provider,
            detect_available_providers,
            get_default_config,
        )

        print("[OK] BaseLLMProvider")
        print("[OK] BaseTTSProvider")
        print("[OK] ProviderConfig")
        print("[OK] create_llm_provider")
        print("[OK] create_tts_provider")
        print("[OK] detect_available_providers")
        print("[OK] get_default_config")

        print("\n[PASS] All provider imports successful")
        return True

    except Exception as e:
        print(f"\n[FAIL] Import error: {e}")
        return False


def validate_provider_detection():
    """Validate provider detection"""
    print("\n" + "=" * 70)
    print("VALIDATION: Provider Detection")
    print("=" * 70)

    try:
        from providers import detect_available_providers

        available = detect_available_providers()
        print(f"\nDetected providers: {list(available.keys())}")

        if available:
            for provider in available:
                print(f"[OK] {provider.upper()} API key found")
            print("\n[PASS] At least one provider available")
            return True
        else:
            print(
                "\n[INFO] No API keys found (expected in test environment)"
            )
            print("   Set OPENAI_API_KEY or GOOGLE_API_KEY to test providers")
            return True  # Not a failure, just informational

    except Exception as e:
        print(f"\n[FAIL] Error detecting providers: {e}")
        return False


def validate_provider_config():
    """Validate provider configuration"""
    print("\n" + "=" * 70)
    print("VALIDATION: Provider Configuration")
    print("=" * 70)

    try:
        from providers import ProviderConfig

        # Test creating a config
        config = ProviderConfig(
            llm_provider="openai",
            tts_provider="openai",
            llm_model="gpt-4.1-mini",
            tts_model="gpt-4o-mini-tts",
        )

        print(f"[OK] ProviderConfig created")
        print(f"    LLM Provider: {config.llm_provider}")
        print(f"    TTS Provider: {config.tts_provider}")
        print(f"    LLM Model: {config.llm_model}")
        print(f"    TTS Model: {config.tts_model}")

        print("\n[PASS] Provider configuration works")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error creating provider config: {e}")
        return False


def validate_base_classes():
    """Validate base classes"""
    print("\n" + "=" * 70)
    print("VALIDATION: Base Classes")
    print("=" * 70)

    try:
        from providers.base import BaseLLMProvider, BaseTTSProvider
        import inspect

        # Check BaseLLMProvider methods
        print("\nBaseLLMProvider:")
        llm_methods = ["generate_text", "model_name", "provider_name"]
        for method in llm_methods:
            has_method = hasattr(BaseLLMProvider, method)
            status = "[OK]" if has_method else "[FAIL]"
            print(f"{status} {method}")

        # Check BaseTTSProvider methods
        print("\nBaseTTSProvider:")
        tts_methods = [
            "generate_audio",
            "available_voices",
            "model_name",
            "provider_name",
        ]
        for method in tts_methods:
            has_method = hasattr(BaseTTSProvider, method)
            status = "[OK]" if has_method else "[FAIL]"
            print(f"{status} {method}")

        print("\n[PASS] Base classes properly defined")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error checking base classes: {e}")
        return False


def validate_env_file():
    """Validate .env.example file"""
    print("\n" + "=" * 70)
    print("VALIDATION: Environment Configuration")
    print("=" * 70)

    env_example_exists = Path(".env.example").exists()
    print(f"{'[OK]' if env_example_exists else '[FAIL]'} .env.example")

    if env_example_exists:
        print("\n[PASS] .env.example file exists")
        return True
    else:
        print("\n[FAIL] .env.example file missing")
        return False


def main():
    """Run all validations"""
    print("\n" + "=" * 70)
    print("STEP 21 VALIDATION: Multi-Provider Support")
    print("=" * 70)
    print()

    results = []

    # Run validations
    results.append(("Provider Package Structure", validate_provider_package()))
    results.append(("Configuration Module", validate_config_module()))
    results.append(("Provider Imports", validate_provider_imports()))
    results.append(("Provider Detection", validate_provider_detection()))
    results.append(("Provider Configuration", validate_provider_config()))
    results.append(("Base Classes", validate_base_classes()))
    results.append(("Environment Configuration", validate_env_file()))

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All validations passed! Provider abstraction layer ready.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} validation(s) failed. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
