"""
Step 41: Quality Check Pass

Automated quality checks for generated podcast content.
Validates script quality, accuracy, tone, coherence, and production readiness.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import json

from providers.factory import ProviderConfig, create_llm_provider, detect_available_providers
import config


class QualityChecker:
    """Automated quality checking for podcast content"""

    def __init__(self, llm_provider):
        self.llm_provider = llm_provider

    def check_script_quality(self, script: str, topic: str, tone: str) -> Dict:
        """Comprehensive script quality check"""

        prompt = f"""Perform a quality check on this podcast script.

TOPIC: {topic}
INTENDED TONE: {tone}

SCRIPT:
{script}

---

Evaluate the script on these criteria (rate 1-10 for each):

1. CLARITY: Is the content clear and easy to understand?
2. ENGAGEMENT: Is it engaging and interesting to listen to?
3. TONE_MATCH: Does it match the intended {tone} tone?
4. COHERENCE: Does it flow logically from point to point?
5. COMPLETENESS: Does it adequately cover the topic?
6. AUDIO_READY: Is it suitable for text-to-speech (no formatting issues)?
7. LENGTH: Is the length appropriate?
8. PROFESSIONALISM: Does it meet broadcast quality standards?

Provide scores in this format:
CLARITY: X
ENGAGEMENT: X
TONE_MATCH: X
COHERENCE: X
COMPLETENESS: X
AUDIO_READY: X
LENGTH: X
PROFESSIONALISM: X
OVERALL: X

ISSUES: [List any specific problems found]
SUGGESTIONS: [List improvement suggestions]
PASS: YES or NO (overall pass/fail)

Perform the quality check:"""

        response = self.llm_provider.generate_text(prompt)

        # Parse response
        scores = {
            "clarity": 5,
            "engagement": 5,
            "tone_match": 5,
            "coherence": 5,
            "completeness": 5,
            "audio_ready": 5,
            "length": 5,
            "professionalism": 5,
            "overall": 5
        }

        issues = []
        suggestions = []
        passes = False

        current_section = None

        for line in response.split('\n'):
            line = line.strip()

            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if key in scores:
                    try:
                        scores[key] = int(value)
                    except ValueError:
                        pass

                elif key == "issues":
                    current_section = "issues"
                    if value and value not in ["None", "[]", ""]:
                        issues.append(value)

                elif key == "suggestions":
                    current_section = "suggestions"
                    if value and value not in ["None", "[]", ""]:
                        suggestions.append(value)

                elif key == "pass":
                    passes = value.upper().startswith("YES")

            elif line.startswith('-') or line.startswith('*'):
                # Bullet point
                item = line.lstrip('-*').strip()
                if current_section == "issues":
                    issues.append(item)
                elif current_section == "suggestions":
                    suggestions.append(item)

        return {
            "scores": scores,
            "issues": issues,
            "suggestions": suggestions,
            "passes": passes,
            "raw_response": response
        }

    def check_factual_grounding(self, script: str, sources: List[str]) -> Dict:
        """Check if script stays grounded in source material"""

        sources_text = "\n\n---\n\n".join(sources)

        prompt = f"""Check if this podcast script stays grounded in the source material.

SOURCES:
{sources_text}

SCRIPT:
{script}

---

Evaluate:
1. Are claims in the script supported by the sources?
2. Are there unsupported claims or potential hallucinations?
3. Is information accurately represented from sources?

Provide:
GROUNDING_SCORE: (1-10, how well grounded in sources)
UNSUPPORTED_CLAIMS: [List any claims not found in sources]
MISREPRESENTATIONS: [List any inaccurate representations]
GROUNDING_PASS: YES or NO

Perform the check:"""

        response = self.llm_provider.generate_text(prompt)

        # Parse response
        grounding_score = 5
        unsupported = []
        misreps = []
        grounding_pass = False

        for line in response.split('\n'):
            line = line.strip()

            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if "grounding_score" in key:
                    try:
                        grounding_score = int(value)
                    except ValueError:
                        pass

                elif "grounding_pass" in key:
                    grounding_pass = value.upper().startswith("YES")

            elif line.startswith('-') or line.startswith('*'):
                item = line.lstrip('-*').strip()
                if item and "unsupported" in line.lower():
                    unsupported.append(item)
                elif item and "misrepresentation" in line.lower():
                    misreps.append(item)

        return {
            "grounding_score": grounding_score,
            "unsupported_claims": unsupported,
            "misrepresentations": misreps,
            "grounding_pass": grounding_pass
        }

    def check_production_readiness(self, script: str) -> Dict:
        """Check if script is ready for audio production"""

        checks = {
            "no_formatting_marks": True,
            "no_urls": True,
            "no_special_chars": True,
            "reasonable_length": True,
            "no_code_blocks": True
        }

        issues = []

        # Check for markdown/formatting
        if "```" in script or "##" in script or "**" in script:
            checks["no_formatting_marks"] = False
            issues.append("Contains markdown formatting")

        # Check for URLs
        if "http://" in script or "https://" in script:
            checks["no_urls"] = False
            issues.append("Contains URLs (won't read well in TTS)")

        # Check for code blocks
        if "```" in script or "def " in script or "class " in script:
            checks["no_code_blocks"] = False
            issues.append("Contains code blocks")

        # Check length
        if len(script) < 100:
            checks["reasonable_length"] = False
            issues.append("Script too short")
        elif len(script) > 50000:
            checks["reasonable_length"] = False
            issues.append("Script too long for single TTS call")

        production_ready = all(checks.values())

        return {
            "checks": checks,
            "issues": issues,
            "production_ready": production_ready
        }


def main():
    """Quality check demo"""
    print("\n" + "="*70)
    print("Step 41: Quality Check Pass")
    print("="*70)

    # Detect providers
    available = detect_available_providers()
    if not available:
        print("\n[ERROR] No providers available")
        return

    # Provider setup
    provider_name = list(available.keys())[0]
    provider_config = ProviderConfig(llm_provider=provider_name)
    llm_provider = create_llm_provider(provider_config)

    print(f"\n[OK] Quality checker initialized with {provider_name}")

    checker = QualityChecker(llm_provider)

    # Get script to check
    print("\nOptions:")
    print("1. Load existing episode")
    print("2. Paste script directly")

    choice = input("\nChoice (1-2, default 2): ").strip() or "2"

    if choice == "1":
        episode_id = input("Enter episode ID or directory name: ").strip()
        script_file = Path(config.OUTPUT_ROOT) / episode_id / "script.txt"

        if not script_file.exists():
            print(f"[ERROR] Script not found: {script_file}")
            return

        with open(script_file, 'r', encoding='utf-8') as f:
            script = f.read()

        topic = episode_id
        tone = "professional"  # Default if not known

    else:
        topic = input("\nTopic: ").strip() or "Demo Topic"
        tone = input("Intended tone (casual/professional/educational): ").strip() or "professional"

        print("\nPaste script (press Enter twice when done):")
        lines = []
        empty_count = 0
        while True:
            line = input()
            if not line:
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)

        script = "\n".join(lines)

        if not script.strip():
            print("[ERROR] No script provided")
            return

    # Run quality checks
    print(f"\n{'='*70}")
    print("Running Quality Checks")
    print(f"{'='*70}")

    # Check 1: Script Quality
    print("\n[1/3] Checking script quality...")
    quality_result = checker.check_script_quality(script, topic, tone)

    print(f"\n[OK] Quality scores:")
    for criterion, score in quality_result["scores"].items():
        status = "[PASS]" if score >= 7 else "[WARN]" if score >= 5 else "[FAIL]"
        print(f"  {status} {criterion.replace('_', ' ').title()}: {score}/10")

    if quality_result["issues"]:
        print(f"\n[WARN] Issues found:")
        for issue in quality_result["issues"]:
            print(f"  - {issue}")

    if quality_result["suggestions"]:
        print(f"\n[INFO] Suggestions:")
        for suggestion in quality_result["suggestions"]:
            print(f"  - {suggestion}")

    # Check 2: Production Readiness
    print("\n[2/3] Checking production readiness...")
    prod_result = checker.check_production_readiness(script)

    print(f"\n[OK] Production checks:")
    for check, passed in prod_result["checks"].items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {check.replace('_', ' ').title()}")

    if prod_result["issues"]:
        print(f"\n[WARN] Production issues:")
        for issue in prod_result["issues"]:
            print(f"  - {issue}")

    # Check 3: Factual Grounding (if sources available)
    print("\n[3/3] Checking factual grounding...")

    has_sources = input("Are there source materials to check against? (y/n): ").strip().lower() == 'y'

    if has_sources:
        print("Paste source text (press Enter twice when done):")
        source_lines = []
        empty_count = 0
        while True:
            line = input()
            if not line:
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                source_lines.append(line)

        source_text = "\n".join(source_lines)

        if source_text.strip():
            grounding_result = checker.check_factual_grounding(script, [source_text])

            print(f"\n[OK] Grounding score: {grounding_result['grounding_score']}/10")

            if grounding_result["unsupported_claims"]:
                print(f"\n[WARN] Unsupported claims:")
                for claim in grounding_result["unsupported_claims"]:
                    print(f"  - {claim}")

            if grounding_result["misrepresentations"]:
                print(f"\n[ERROR] Misrepresentations:")
                for misrep in grounding_result["misrepresentations"]:
                    print(f"  - {misrep}")

            grounding_pass = grounding_result["grounding_pass"]
        else:
            grounding_pass = True  # Skip if no sources
    else:
        print("[INFO] Skipping grounding check (no sources)")
        grounding_pass = True

    # Overall result
    print(f"\n{'='*70}")
    print("Quality Check Summary")
    print(f"{'='*70}")

    overall_pass = (
        quality_result["passes"] and
        prod_result["production_ready"] and
        grounding_pass
    )

    if overall_pass:
        print("\n[PASS] Overall quality check PASSED")
        print("Episode is ready for production")
    else:
        print("\n[FAIL] Overall quality check FAILED")
        print("Review issues and revise before production")

    # Save quality report
    output_dir = Path(config.OUTPUT_ROOT) / "quality_reports"
    output_dir.mkdir(exist_ok=True)

    report_file = output_dir / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "tone": tone,
        "script_length": len(script),
        "quality_check": quality_result,
        "production_check": prod_result,
        "grounding_check": grounding_result if has_sources else None,
        "overall_pass": overall_pass
    }

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n[OK] Quality report saved: {report_file}")


if __name__ == "__main__":
    main()
