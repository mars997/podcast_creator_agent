import sys
from pathlib import Path

from core.episode_management import load_episode_index
from core.episode_browser import (
    display_episode_list,
    display_episode_details,
    view_file_content,
    interactive_menu
)
import config


OUTPUT_ROOT = config.OUTPUT_ROOT
EPISODE_INDEX_FILE = "episode_index.json"


def main():
    """Main entry point for episode browser"""
    print("\n" + "=" * 70)
    print("Step 17: Episode Browser")
    print("=" * 70)

    output_root = Path(OUTPUT_ROOT)
    index_path = output_root / EPISODE_INDEX_FILE

    print(f"\nLoading episode index from: {index_path}")

    episodes = load_episode_index(index_path)

    if not episodes:
        print("\nNo episodes found. Create episodes using step16_unique_episode_ids.py")
        return

    print(f"Loaded {len(episodes)} episode(s)")

    # Check if running interactively
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        # Non-interactive mode: just list episodes
        display_episode_list(episodes)
    else:
        # Interactive mode
        interactive_menu(episodes)

    print("\nStep 17 complete.")


if __name__ == "__main__":
    main()
