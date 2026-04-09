"""
Automated Test Runner for Phases 5A through 8 (Steps 25-42)

This script will:
1. Verify API keys are configured
2. Run each step with predefined test inputs
3. Generate episode outputs
4. Create comprehensive test report

Estimated runtime: 40-60 minutes
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment
load_dotenv()

# Test definitions
TESTS = [
    # Phase 5A
    {
        "step": "25",
        "name": "Multi-Provider Podcast",
        "file": "step25_multi_provider_podcast.py",
        "inputs": ["1", "1", "Multi-Provider AI Demo", "casual", "nova", "short"],
        "skip": False
    },

    # Phase 6
    {
        "step": "27",
        "name": "Podcast Templates",
        "file": "step27_podcast_templates.py",
        "inputs": ["1", "Renewable Energy Future", "casual", "nova", "short"],
        "skip": False
    },
    {
        "step": "28",
        "name": "Multi-Character Podcast",
        "file": "step28_multi_character_podcast.py",
        "inputs": ["Climate Change Solutions", "2", "casual", "short"],
        "skip": False
    },
    {
        "step": "29",
        "name": "Grounding Rules",
        "file": "step29_grounding_rules.py",
        "inputs": ["2", "Space Exploration", "1", "Space exploration is advancing rapidly with new missions to Mars and the Moon.", "", "", "casual", "nova", "short"],
        "skip": False
    },
    {
        "step": "30",
        "name": "Segment-Aware Generation",
        "file": "step30_segment_aware_generation.py",
        "inputs": ["1", "Quantum Computing Basics", "professional", "onyx", "short"],
        "skip": False
    },
    {
        "step": "31",
        "name": "Citation Support",
        "file": "step31_citation_support.py",
        "inputs": ["1", "AI in Healthcare", "Recent studies show AI improving diagnostics.", "DONE", "professional", "shimmer", "short"],
        "skip": False
    },

    # Phase 7
    {
        "step": "32",
        "name": "Voice Persona System",
        "file": "step32_voice_persona_system.py",
        "inputs": ["1", "Future of Technology", "", "short"],
        "skip": False
    },
    {
        "step": "33",
        "name": "Audio Chunking",
        "file": "step33_audio_chunking.py",
        "inputs": ["Long Form AI Discussion", "casual", "nova", "", ""],
        "skip": False
    },
    {
        "step": "34",
        "name": "Intro/Outro Branding",
        "file": "step34_intro_outro_branding.py",
        "inputs": ["1", "Tech News Daily", "casual", "echo", "short"],
        "skip": False
    },
    {
        "step": "35",
        "name": "Multi-Voice Rendering",
        "file": "step35_multi_voice_rendering.py",
        "inputs": ["AI Panel Discussion", "2", "casual", "short", "n"],
        "skip": False
    },
    {
        "step": "36",
        "name": "Audio Post-Processing",
        "file": "step36_audio_post_processing.py",
        "inputs": ["2", "Professionally Processed Podcast", "professional", "alloy", "short"],
        "skip": False
    },

    # Phase 8
    {
        "step": "37",
        "name": "Automated Generation",
        "file": "step37_automated_generation.py",
        "inputs": ["1", "Automated Tech Briefing"],
        "skip": False
    },
    {
        "step": "38",
        "name": "Topic Queue",
        "file": "step38_topic_queue.py",
        "inputs": ["7", "8"],  # Add demo topics, then exit
        "skip": False
    },
    {
        "step": "39",
        "name": "Source Selection Agent",
        "file": "step39_source_selection_agent.py",
        "inputs": ["Renewable Energy Innovation", "n"],
        "skip": False
    },
    {
        "step": "40",
        "name": "Summarize First",
        "file": "step40_summarize_first.py",
        "inputs": ["Blockchain Fundamentals", "professional", "fable", "short", "a"],
        "skip": False
    },
    {
        "step": "41",
        "name": "Quality Check",
        "file": "step41_quality_check.py",
        "inputs": ["2", "Quality Test", "casual", "This is a test podcast script about technology.", "", "", "n"],
        "skip": False
    },
    {
        "step": "42",
        "name": "Approval Workflow",
        "file": "step42_approval_workflow.py",
        "inputs": ["9"],  # Just exit
        "skip": False
    }
]


def check_api_key():
    """Verify API key is configured"""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "OPENAI_API_KEY":
        print("\n" + "="*70)
        print("ERROR: OpenAI API Key Not Configured")
        print("="*70)
        print("\nThe .env file has placeholder text instead of a real API key.")
        print("\nTo fix:")
        print("1. Get your API key from: https://platform.openai.com/api-keys")
        print("2. Edit .env file and replace:")
        print("   OPENAI_API_KEY=OPENAI_API_KEY")
        print("   with:")
        print("   OPENAI_API_KEY=sk-proj-your-actual-key")
        print("\n" + "="*70)
        return False

    # Basic format check
    if not api_key.startswith("sk-"):
        print(f"\n[WARN] API key format looks unusual (doesn't start with 'sk-')")
        print(f"[WARN] Key preview: {api_key[:15]}...")
        response = input("\nContinue anyway? (y/n): ").strip().lower()
        if response != 'y':
            return False

    print(f"\n[OK] API key found: {api_key[:15]}...")
    return True


def run_test(test):
    """Run a single test"""
    print(f"\n{'='*70}")
    print(f"Step {test['step']}: {test['name']}")
    print(f"{'='*70}")
    print(f"File: {test['file']}")
    print(f"Inputs: {test['inputs']}")

    if test['skip']:
        print("[SKIP] Test marked as skip")
        return {"status": "skipped", "reason": "Marked as skip"}

    # Prepare input
    input_str = "\n".join(test['inputs'])

    start_time = datetime.now()

    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, test['file']],
            input=input_str,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per step
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        success = result.returncode == 0

        return {
            "status": "pass" if success else "fail",
            "returncode": result.returncode,
            "duration": duration,
            "stdout": result.stdout[-1000:],  # Last 1000 chars
            "stderr": result.stderr[-1000:] if result.stderr else None
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "duration": 300,
            "stderr": "Test exceeded 5 minute timeout"
        }

    except Exception as e:
        return {
            "status": "error",
            "stderr": str(e)
        }


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("Automated Test Runner: Phases 5A-8 (Steps 25-42)")
    print("="*70)
    print(f"\nTotal tests: {len(TESTS)}")
    print(f"Estimated time: 40-60 minutes")

    # Check API key
    if not check_api_key():
        print("\n[ABORT] Cannot proceed without valid API key")
        return

    # Confirm start
    print("\n" + "="*70)
    response = input("\nStart testing? This will take a while. (y/n): ").strip().lower()
    if response != 'y':
        print("[ABORT] Testing cancelled")
        return

    # Run tests
    results = []
    start_time = datetime.now()

    for i, test in enumerate(TESTS, 1):
        print(f"\n\n[{i}/{len(TESTS)}] Running Step {test['step']}...")

        result = run_test(test)
        result["step"] = test["step"]
        result["name"] = test["name"]
        result["file"] = test["file"]
        results.append(result)

        # Show quick status
        status_symbol = {
            "pass": "[PASS]",
            "fail": "[FAIL]",
            "skip": "[SKIP]",
            "timeout": "[TIMEOUT]",
            "error": "[ERROR]"
        }.get(result["status"], "[?]")

        print(f"\n{status_symbol} Step {test['step']}: {result['status'].upper()}")
        if result.get("duration"):
            print(f"  Duration: {result['duration']:.1f}s")

    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    # Generate report
    print(f"\n\n{'='*70}")
    print("Test Results Summary")
    print(f"{'='*70}")

    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    errors = sum(1 for r in results if r["status"] in ["timeout", "error"])

    print(f"\nPassed:  {passed}/{len(TESTS)}")
    print(f"Failed:  {failed}/{len(TESTS)}")
    print(f"Skipped: {skipped}/{len(TESTS)}")
    print(f"Errors:  {errors}/{len(TESTS)}")
    print(f"\nTotal duration: {total_duration/60:.1f} minutes")

    # Save detailed report
    report_file = Path("TEST_RESULTS_PHASES_5A_TO_8.json")
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(TESTS),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "total_duration_seconds": total_duration,
            "results": results
        }, f, indent=2)

    print(f"\n[OK] Detailed report saved: {report_file}")

    # Create markdown report
    create_markdown_report(results, total_duration)

    # List generated episodes
    print(f"\n{'='*70}")
    print("Generated Episodes")
    print(f"{'='*70}")

    output_dirs = sorted(Path("output").glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)
    print(f"\nTotal episodes in output/: {len(output_dirs)}")
    print("\nLatest 10 episodes:")
    for ep_dir in output_dirs[:10]:
        print(f"  - {ep_dir.name}")

    print(f"\n{'='*70}")
    print("Testing Complete!")
    print(f"{'='*70}")


def create_markdown_report(results, total_duration):
    """Create markdown summary report"""

    report = f"""# Test Results: Phases 5A-8 (Steps 25-42)

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Duration**: {total_duration/60:.1f} minutes
**Tests Run**: {len(results)}

---

## Summary

| Status | Count |
|--------|-------|
| PASS | {sum(1 for r in results if r['status'] == 'pass')} |
| FAIL | {sum(1 for r in results if r['status'] == 'fail')} |
| SKIP | {sum(1 for r in results if r['status'] == 'skipped')} |
| ERROR | {sum(1 for r in results if r['status'] in ['timeout', 'error'])} |

---

## Test Details

"""

    for result in results:
        status_emoji = {
            "pass": "[PASS]",
            "fail": "[FAIL]",
            "skipped": "[SKIP]",
            "timeout": "[TIMEOUT]",
            "error": "[ERROR]"
        }.get(result["status"], "[?]")

        report += f"### {status_emoji} Step {result['step']}: {result['name']}\n\n"
        report += f"- **File**: `{result['file']}`\n"
        report += f"- **Status**: {result['status'].upper()}\n"

        if result.get("duration"):
            report += f"- **Duration**: {result['duration']:.1f}s\n"

        if result.get("returncode") is not None:
            report += f"- **Return Code**: {result['returncode']}\n"

        if result.get("stderr") and result["status"] != "pass":
            report += f"\n**Error Output**:\n```\n{result['stderr'][:500]}\n```\n"

        report += "\n---\n\n"

    # Save report
    report_file = Path("TEST_RESULTS_PHASES_5A_TO_8.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[OK] Markdown report saved: {report_file}")


if __name__ == "__main__":
    main()
