import json
import os
import sys
from pathlib import Path
from datetime import datetime


OUTPUT_ROOT = "output"
EPISODE_INDEX_FILE = "episode_index.json"


def load_episode_index(index_path: Path) -> list[dict]:
    """Load the episode index from JSON file"""
    if not index_path.exists():
        print(f"Episode index not found: {index_path}")
        return []

    try:
        content = index_path.read_text(encoding="utf-8")
        episodes = json.loads(content)

        if not isinstance(episodes, list):
            print("Warning: Episode index is not a list")
            return []

        return episodes
    except json.JSONDecodeError as e:
        print(f"Error parsing episode index: {e}")
        return []
    except Exception as e:
        print(f"Error reading episode index: {e}")
        return []


def format_episode_summary(episode: dict, index: int) -> str:
    """Format a single episode for display"""
    created_at = episode.get("created_at", "Unknown date")
    topic = episode.get("topic", "No topic")
    episode_id = episode.get("episode_id", topic)  # Fallback to topic for old episodes
    tone = episode.get("tone", "N/A")
    voice = episode.get("voice", "N/A")
    length = episode.get("length", "N/A")

    # Try to format the date nicely
    try:
        dt = datetime.fromisoformat(created_at)
        date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        date_str = created_at

    lines = [
        f"[{index}] {topic}",
        f"    Episode ID: {episode_id}",
        f"    Created: {date_str}",
        f"    Settings: {tone} tone, {voice} voice, {length} length",
    ]

    return "\n".join(lines)


def display_episode_list(episodes: list[dict]) -> None:
    """Display all episodes in the index"""
    if not episodes:
        print("\nNo episodes found in the index.")
        return

    print("\n" + "=" * 70)
    print(f"Episode History ({len(episodes)} episode{'s' if len(episodes) != 1 else ''})")
    print("=" * 70)

    for i, episode in enumerate(episodes, start=1):
        print(format_episode_summary(episode, i))
        print()


def display_episode_details(episode: dict) -> None:
    """Display detailed information about a specific episode"""
    print("\n" + "=" * 70)
    print(f"Episode Details: {episode.get('topic', 'Unknown')}")
    print("=" * 70)

    # Basic info
    print(f"\nEpisode ID: {episode.get('episode_id', episode.get('topic', 'N/A'))}")
    print(f"Created: {episode.get('created_at', 'Unknown')}")
    print(f"Topic: {episode.get('topic', 'N/A')}")
    print(f"Tone: {episode.get('tone', 'N/A')}")
    print(f"Voice: {episode.get('voice', 'N/A')}")
    print(f"Length: {episode.get('length', 'N/A')}")

    # Source stats
    print(f"\nSources:")
    print(f"  Successful URLs: {episode.get('num_successful_urls', 0)}")
    print(f"  Successful files: {episode.get('num_successful_files', 0)}")
    print(f"  Failed URLs: {episode.get('num_failed_urls', 0)}")
    print(f"  Failed files: {episode.get('num_failed_files', 0)}")

    # File paths
    print(f"\nFiles:")

    episode_dir = episode.get('episode_dir', '')
    if episode_dir:
        dir_path = Path(episode_dir)
        exists_marker = "[EXISTS]" if dir_path.exists() else "[MISSING]"
        print(f"  Episode folder: {episode_dir} {exists_marker}")

    script_file = episode.get('script_file', '')
    if script_file:
        script_path = Path(script_file)
        exists_marker = "[EXISTS]" if script_path.exists() else "[MISSING]"
        print(f"  Script: {script_file} {exists_marker}")

    show_notes_file = episode.get('show_notes_file', '')
    if show_notes_file:
        notes_path = Path(show_notes_file)
        exists_marker = "[EXISTS]" if notes_path.exists() else "[MISSING]"
        print(f"  Show notes: {show_notes_file} {exists_marker}")

    audio_file = episode.get('audio_file', '')
    if audio_file:
        audio_path = Path(audio_file)
        exists_marker = "[EXISTS]" if audio_path.exists() else "[MISSING]"
        size_str = ""
        if audio_path.exists():
            size_kb = audio_path.stat().st_size // 1024
            size_str = f" ({size_kb} KB)"
        print(f"  Audio: {audio_file} {exists_marker}{size_str}")

    metadata_file = episode.get('metadata_file', '')
    if metadata_file:
        meta_path = Path(metadata_file)
        exists_marker = "[EXISTS]" if meta_path.exists() else "[MISSING]"
        print(f"  Metadata: {metadata_file} {exists_marker}")


def view_file_content(file_path: Path, max_lines: int = 50) -> None:
    """Display the content of a text file"""
    if not file_path.exists():
        print(f"\nFile not found: {file_path}")
        return

    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        print(f"\n--- Content of {file_path.name} ---")

        if len(lines) <= max_lines:
            print(content)
        else:
            print("\n".join(lines[:max_lines]))
            print(f"\n... ({len(lines) - max_lines} more lines)")

        print(f"--- End of {file_path.name} ---")
    except Exception as e:
        print(f"\nError reading file: {e}")


def interactive_menu(episodes: list[dict]) -> None:
    """Interactive menu for browsing episodes"""
    while True:
        print("\n" + "=" * 70)
        print("Episode Browser Menu")
        print("=" * 70)
        print("1. List all episodes")
        print("2. View episode details")
        print("3. View episode script")
        print("4. View episode show notes")
        print("5. View episode metadata")
        print("6. Exit")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == "1":
            display_episode_list(episodes)

        elif choice == "2":
            display_episode_list(episodes)
            if episodes:
                try:
                    ep_num = int(input(f"\nEnter episode number (1-{len(episodes)}): ").strip())
                    if 1 <= ep_num <= len(episodes):
                        display_episode_details(episodes[ep_num - 1])
                    else:
                        print(f"Invalid episode number. Must be 1-{len(episodes)}")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        elif choice == "3":
            display_episode_list(episodes)
            if episodes:
                try:
                    ep_num = int(input(f"\nEnter episode number (1-{len(episodes)}): ").strip())
                    if 1 <= ep_num <= len(episodes):
                        script_file = episodes[ep_num - 1].get('script_file', '')
                        if script_file:
                            view_file_content(Path(script_file))
                        else:
                            print("Script file path not found in episode data")
                    else:
                        print(f"Invalid episode number. Must be 1-{len(episodes)}")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        elif choice == "4":
            display_episode_list(episodes)
            if episodes:
                try:
                    ep_num = int(input(f"\nEnter episode number (1-{len(episodes)}): ").strip())
                    if 1 <= ep_num <= len(episodes):
                        notes_file = episodes[ep_num - 1].get('show_notes_file', '')
                        if notes_file:
                            view_file_content(Path(notes_file))
                        else:
                            print("Show notes file path not found in episode data")
                    else:
                        print(f"Invalid episode number. Must be 1-{len(episodes)}")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        elif choice == "5":
            display_episode_list(episodes)
            if episodes:
                try:
                    ep_num = int(input(f"\nEnter episode number (1-{len(episodes)}): ").strip())
                    if 1 <= ep_num <= len(episodes):
                        metadata_file = episodes[ep_num - 1].get('metadata_file', '')
                        if metadata_file:
                            view_file_content(Path(metadata_file), max_lines=100)
                        else:
                            print("Metadata file path not found in episode data")
                    else:
                        print(f"Invalid episode number. Must be 1-{len(episodes)}")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        elif choice == "6":
            print("\nExiting episode browser.")
            break

        else:
            print("Invalid choice. Please enter 1-6.")


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
