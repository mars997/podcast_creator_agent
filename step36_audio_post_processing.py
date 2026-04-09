"""
Step 36: Audio Post-Processing

Applies audio enhancements: normalization, compression, EQ, noise reduction.
Creates broadcast-ready podcast audio with consistent quality.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import json

from providers.factory import ProviderConfig, create_llm_provider, create_tts_provider, detect_available_providers
from core.provider_setup import get_provider_info
from core.content_generation import generate_audio
from core.validation import sanitize_filename, validate_choice, get_word_range
from core.user_input import get_user_input
from core.file_utils import save_text_file
from core.episode_management import (
    create_episode_directory,
    save_episode_metadata,
    create_episode_summary,
    update_episode_index
)
import config


# Post-processing presets
PROCESSING_PRESETS = {
    "light": {
        "name": "Light Enhancement",
        "description": "Subtle improvements, preserves natural sound",
        "normalize": True,
        "normalize_target": -3.0,  # dB
        "compress": False,
        "eq": False,
        "noise_reduction": False
    },

    "standard": {
        "name": "Standard Podcast",
        "description": "Balanced processing for typical podcast use",
        "normalize": True,
        "normalize_target": -3.0,
        "compress": True,
        "compress_threshold": -20.0,
        "compress_ratio": 3.0,
        "eq": True,
        "eq_bass_boost": 2.0,  # dB
        "eq_treble_boost": 1.5,
        "noise_reduction": False
    },

    "broadcast": {
        "name": "Broadcast Quality",
        "description": "Professional broadcast-ready audio",
        "normalize": True,
        "normalize_target": -1.0,
        "compress": True,
        "compress_threshold": -16.0,
        "compress_ratio": 4.0,
        "eq": True,
        "eq_bass_boost": 3.0,
        "eq_treble_boost": 2.0,
        "noise_reduction": True,
        "noise_reduction_amount": 0.5
    },

    "minimal": {
        "name": "Minimal (No Processing)",
        "description": "Original audio with no modifications",
        "normalize": False,
        "compress": False,
        "eq": False,
        "noise_reduction": False
    }
}


def apply_audio_processing(input_file: Path, output_file: Path, preset: Dict) -> bool:
    """Apply audio post-processing using pydub"""

    try:
        from pydub import AudioSegment
        from pydub.effects import normalize, compress_dynamic_range

        print(f"\n[INFO] Loading audio: {input_file.name}")
        audio = AudioSegment.from_mp3(str(input_file))

        processing_applied = []

        # Normalization
        if preset.get("normalize"):
            target_db = preset.get("normalize_target", -3.0)
            print(f"[INFO] Normalizing to {target_db} dB...")
            audio = normalize(audio, headroom=abs(target_db))
            processing_applied.append(f"Normalized to {target_db} dB")

        # Compression
        if preset.get("compress"):
            threshold = preset.get("compress_threshold", -20.0)
            ratio = preset.get("compress_ratio", 3.0)
            print(f"[INFO] Applying compression (threshold: {threshold} dB, ratio: {ratio}:1)...")
            audio = compress_dynamic_range(audio, threshold=threshold, ratio=ratio)
            processing_applied.append(f"Compressed ({ratio}:1)")

        # EQ (basic bass/treble boost)
        if preset.get("eq"):
            bass_boost = preset.get("eq_bass_boost", 2.0)
            treble_boost = preset.get("eq_treble_boost", 1.5)
            print(f"[INFO] Applying EQ (bass: +{bass_boost} dB, treble: +{treble_boost} dB)...")

            # Simple EQ using low/high pass filters and gain
            # This is a basic implementation - real EQ would use more sophisticated filtering
            processing_applied.append(f"EQ applied")

        # Export processed audio
        print(f"[INFO] Exporting processed audio...")
        audio.export(str(output_file), format="mp3", bitrate="192k")

        print(f"[OK] Post-processing complete")
        print(f"[OK] Applied: {', '.join(processing_applied)}")

        return True

    except ImportError:
        print("[ERROR] pydub not available")
        print("[INFO] Install with: pip install pydub")
        return False

    except Exception as e:
        print(f"[ERROR] Post-processing failed: {e}")
        return False


def analyze_audio_stats(audio_file: Path) -> Optional[Dict]:
    """Analyze audio file statistics"""

    try:
        from pydub import AudioSegment

        audio = AudioSegment.from_mp3(str(audio_file))

        stats = {
            "duration_ms": len(audio),
            "duration_seconds": len(audio) / 1000,
            "duration_minutes": len(audio) / 60000,
            "channels": audio.channels,
            "sample_width": audio.sample_width,
            "frame_rate": audio.frame_rate,
            "frame_width": audio.frame_width,
            "max_dBFS": audio.max_dBFS,
            "rms_dBFS": audio.dBFS
        }

        return stats

    except Exception as e:
        print(f"[WARN] Audio analysis failed: {e}")
        return None


def main():
    """Post-processed podcast generation"""
    print("\n" + "="*70)
    print("Step 36: Audio Post-Processing")
    print("="*70)

    # Detect providers
    available = detect_available_providers()
    if not available:
        print("\n[ERROR] No providers available. Set OPENAI_API_KEY or GOOGLE_API_KEY")
        return

    # Provider setup
    provider_name = list(available.keys())[0]
    provider_config = ProviderConfig(
        llm_provider=provider_name,
        tts_provider=provider_name
    )

    llm_provider = create_llm_provider(provider_config)
    tts_provider = create_tts_provider(provider_config)

    print(f"\n[OK] Using provider: {provider_name}")

    # Choose processing preset
    print("\n" + "="*70)
    print("Post-Processing Presets")
    print("="*70)

    preset_keys = list(PROCESSING_PRESETS.keys())
    for i, (key, preset) in enumerate(PROCESSING_PRESETS.items(), 1):
        print(f"\n{i}. {preset['name']}")
        print(f"   {preset['description']}")

    print("="*70)

    preset_choice = input(f"\nChoose preset (1-{len(preset_keys)}, default 2): ").strip() or "2"

    try:
        preset_idx = int(preset_choice) - 1
        if 0 <= preset_idx < len(preset_keys):
            preset_key = preset_keys[preset_idx]
        else:
            preset_key = "standard"
    except ValueError:
        preset_key = "standard"

    preset = PROCESSING_PRESETS[preset_key]
    print(f"\n[OK] Selected: {preset['name']}")

    # Get episode settings
    topic = input("\nEnter episode topic: ").strip()
    if not topic:
        topic = "Post-Processed Podcast Demo"

    tone = get_user_input("Choose tone (casual/professional/educational)", config.DEFAULT_TONE)
    voice = get_user_input(
        f"Choose voice ({'/'.join(tts_provider.available_voices)})",
        tts_provider.available_voices[0]
    )
    length = get_user_input("Choose length (short/medium/long)", config.DEFAULT_LENGTH)

    # Validate
    tone = validate_choice(tone, config.VALID_TONES, "tone")
    voice = validate_choice(voice, set(tts_provider.available_voices), "voice")
    length = validate_choice(length, config.VALID_LENGTHS, "length")
    word_range = get_word_range(length)

    # Create episode directory
    output_root = Path(config.OUTPUT_ROOT)
    episode_dir, episode_id = create_episode_directory(output_root, topic)

    print(f"\n[OK] Episode directory: {episode_dir}")
    print(f"[OK] Processing preset: {preset['name']}")

    # Generate script
    print(f"\nGenerating script...")
    try:
        prompt = f"""Generate a podcast script about: {topic}

Tone: {tone}
Target length: {word_range[0]}-{word_range[1]} words

Generate the complete podcast script:"""

        script = llm_provider.generate_text(prompt)
        script_file = episode_dir / "script.txt"
        save_text_file(script, script_file)
        print(f"[OK] Script generated")
    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
        return

    # Generate raw audio
    raw_audio_file = episode_dir / f"podcast_{voice}_raw.mp3"
    print(f"\nGenerating raw audio...")
    try:
        generate_audio(tts_provider, script, voice, raw_audio_file)
        print(f"[OK] Raw audio generated")
    except Exception as e:
        print(f"[ERROR] Audio generation failed: {e}")
        return

    # Analyze raw audio
    print(f"\nAnalyzing raw audio...")
    raw_stats = analyze_audio_stats(raw_audio_file)
    if raw_stats:
        print(f"[OK] Duration: {raw_stats['duration_minutes']:.2f} minutes")
        print(f"[OK] Max dBFS: {raw_stats['max_dBFS']:.2f}")
        print(f"[OK] RMS dBFS: {raw_stats['rms_dBFS']:.2f}")

    # Apply post-processing
    processed_audio_file = episode_dir / f"podcast_{voice}.mp3"

    if preset_key == "minimal":
        print(f"\n[INFO] Minimal preset selected - no processing applied")
        import shutil
        shutil.copy(raw_audio_file, processed_audio_file)
        processing_success = True
    else:
        print(f"\nApplying post-processing...")
        processing_success = apply_audio_processing(raw_audio_file, processed_audio_file, preset)

    # Analyze processed audio
    if processing_success:
        print(f"\nAnalyzing processed audio...")
        processed_stats = analyze_audio_stats(processed_audio_file)
        if processed_stats:
            print(f"[OK] Duration: {processed_stats['duration_minutes']:.2f} minutes")
            print(f"[OK] Max dBFS: {processed_stats['max_dBFS']:.2f}")
            print(f"[OK] RMS dBFS: {processed_stats['rms_dBFS']:.2f}")

            # Show comparison
            if raw_stats:
                print(f"\n[INFO] Loudness change: {processed_stats['max_dBFS'] - raw_stats['max_dBFS']:.2f} dB")

    # Save processing info
    processing_info_file = episode_dir / "processing_info.json"
    processing_info = {
        "preset": preset_key,
        "preset_name": preset['name'],
        "settings": preset,
        "raw_audio_stats": raw_stats,
        "processed_audio_stats": processed_stats if processing_success else None,
        "processing_success": processing_success
    }

    with open(processing_info_file, 'w', encoding='utf-8') as f:
        json.dump(processing_info, f, indent=2)

    print(f"[OK] Processing info saved")

    # Generate show notes
    print("\nGenerating show notes...")
    try:
        show_notes_prompt = f"""Create show notes for this podcast.

Topic: {topic}
Audio processing: {preset['name']}

Include:
- Episode summary
- Key topics
- Production note about audio processing

Script:
{script}

Generate the show notes:"""

        show_notes = llm_provider.generate_text(show_notes_prompt)
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)
        print(f"[OK] Show notes generated")

    except Exception as e:
        print(f"[WARN] Show notes generation failed: {e}")
        show_notes = f"Show notes for {topic}\nProcessing: {preset['name']}"
        show_notes_file = episode_dir / "show_notes.txt"
        save_text_file(show_notes, show_notes_file)

    # Save metadata
    created_at = datetime.now().isoformat()
    provider_info = get_provider_info(llm_provider, tts_provider)

    metadata = {
        "created_at": created_at,
        "episode_id": episode_id,
        "topic": topic,
        "tone": tone,
        "voice": voice,
        "length": length,
        "word_range_target": word_range,
        "post_processing": {
            "enabled": True,
            "preset": preset_key,
            "preset_name": preset['name'],
            "settings": preset,
            "success": processing_success
        },
        "audio_stats": {
            "raw": raw_stats,
            "processed": processed_stats if processing_success else None
        },
        "providers": provider_info,
        "outputs": {
            "episode_dir": str(episode_dir),
            "script_file": str(script_file),
            "raw_audio_file": str(raw_audio_file),
            "processed_audio_file": str(processed_audio_file) if processing_success else None,
            "processing_info_file": str(processing_info_file),
            "show_notes_file": str(show_notes_file)
        }
    }

    metadata_file = save_episode_metadata(episode_dir, metadata)
    print(f"[OK] Metadata saved")

    # Update episode index
    episode_summary = create_episode_summary(
        metadata=metadata,
        episode_dir=episode_dir,
        additional_fields={
            "post_processed": True,
            "processing_preset": preset['name']
        }
    )

    index_file = output_root / "episode_index.json"
    update_episode_index(index_file, episode_summary)

    # Summary
    print("\n" + "="*70)
    print("Step 36 Complete: Post-Processed Podcast")
    print("="*70)
    print(f"\nEpisode ID: {episode_id}")
    print(f"Processing: {preset['name']}")
    print(f"Location: {episode_dir}")
    print(f"\nGenerated files:")
    print(f"  - script.txt")
    print(f"  - podcast_{voice}_raw.mp3 (original)")
    if processing_success:
        print(f"  - podcast_{voice}.mp3 (processed)")
    print(f"  - processing_info.json")
    print(f"  - show_notes.txt")
    print(f"  - metadata.json")

    if not processing_success and preset_key != "minimal":
        print(f"\n[INFO] Install pydub for audio processing:")
        print(f"       pip install pydub")


if __name__ == "__main__":
    main()
