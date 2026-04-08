from pathlib import Path

from core.provider_setup import initialize_providers
from core.episode_management import load_episode_index, load_episode_metadata
from core.episode_browser import display_episode_list
from core.episode_regenerator import regenerate_episode
import config


OUTPUT_ROOT = config.OUTPUT_ROOT
EPISODE_INDEX_FILE = "episode_index.json"


# Initialize providers
llm_provider, tts_provider = initialize_providers()


def main():
    """Main entry point for episode regeneration"""
    print("\n" + "=" * 70)
    print("Step 18: Regenerate Episode from Metadata")
    print("=" * 70)

    output_root = Path(OUTPUT_ROOT)
    index_path = output_root / EPISODE_INDEX_FILE

    # Load episode index
    print(f"\nLoading episode index from: {index_path}")
    episodes = load_episode_index(index_path)

    if not episodes:
        print("\nNo episodes found. Create episodes first using step16_unique_episode_ids.py")
        return

    print(f"Found {len(episodes)} episode(s)")

    # Display episodes for selection
    display_episode_list(episodes)

    # Get user selection
    try:
        choice = int(input(f"Select episode to regenerate (1-{len(episodes)}): ").strip())
        if choice < 1 or choice > len(episodes):
            print(f"Invalid choice. Must be 1-{len(episodes)}")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    selected_episode = episodes[choice - 1]

    # Load metadata
    metadata_file = selected_episode.get('metadata_file')
    if not metadata_file:
        print("Error: Episode does not have metadata_file path")
        return

    metadata_path = Path(metadata_file)
    print(f"\nLoading metadata from: {metadata_path}")

    try:
        metadata = load_episode_metadata(metadata_path)
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return

    # Get episode directory
    episode_dir = selected_episode.get('episode_dir')
    if not episode_dir:
        print("Error: Episode does not have episode_dir path")
        return

    episode_dir_path = Path(episode_dir)
    if not episode_dir_path.exists():
        print(f"Error: Episode directory not found: {episode_dir_path}")
        return

    # Confirm regeneration
    print(f"\nYou are about to regenerate episode: {selected_episode.get('topic')}")
    confirm = input("This will create a NEW episode with the same sources. Continue? (y/n): ").strip().lower()

    if confirm != 'y':
        print("Regeneration cancelled.")
        return

    # Regenerate episode using core module
    try:
        regenerate_episode(llm_provider, tts_provider, metadata, episode_dir_path, Path(OUTPUT_ROOT))
        print("\nStep 18 complete.")
    except Exception as e:
        print(f"\nError during regeneration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
