"""
Step 38: Topic Queue

Manages a queue of podcast topics for automated generation.
Topics can be added, prioritized, scheduled, and processed in batch.
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from step37_automated_generation import generate_automated_episode, AUTOMATION_PROFILES
from providers.factory import detect_available_providers
import config


# Topic queue file location
QUEUE_FILE = Path(config.OUTPUT_ROOT) / "topic_queue.json"


class TopicQueue:
    """Manages podcast topic queue"""

    def __init__(self, queue_file: Path = QUEUE_FILE):
        self.queue_file = queue_file
        self.topics = self._load_queue()

    def _load_queue(self) -> List[Dict]:
        """Load queue from file"""
        if self.queue_file.exists():
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_queue(self):
        """Save queue to file"""
        self.queue_file.parent.mkdir(exist_ok=True)
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(self.topics, f, indent=2)

    def add_topic(
        self,
        topic: str,
        priority: int = 5,
        profile: str = "solo_explainer",
        scheduled_date: Optional[str] = None,
        sources: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Add topic to queue"""

        topic_id = f"topic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        topic_entry = {
            "id": topic_id,
            "topic": topic,
            "priority": priority,
            "profile": profile,
            "scheduled_date": scheduled_date,
            "sources": sources or [],
            "tags": tags or [],
            "status": "queued",
            "added_at": datetime.now().isoformat(),
            "processed_at": None,
            "episode_id": None
        }

        self.topics.append(topic_entry)
        self._save_queue()

        return topic_id

    def get_next_topic(self) -> Optional[Dict]:
        """Get next topic to process"""

        # Filter to queued topics
        queued = [t for t in self.topics if t["status"] == "queued"]

        if not queued:
            return None

        # Check for scheduled topics that are due
        now = datetime.now()
        for topic in queued:
            if topic.get("scheduled_date"):
                scheduled = datetime.fromisoformat(topic["scheduled_date"])
                if scheduled <= now:
                    return topic

        # Otherwise, return highest priority
        return max(queued, key=lambda t: t["priority"])

    def mark_processed(self, topic_id: str, episode_id: str, success: bool = True):
        """Mark topic as processed"""

        for topic in self.topics:
            if topic["id"] == topic_id:
                topic["status"] = "completed" if success else "failed"
                topic["processed_at"] = datetime.now().isoformat()
                topic["episode_id"] = episode_id
                break

        self._save_queue()

    def list_topics(self, status: Optional[str] = None) -> List[Dict]:
        """List topics, optionally filtered by status"""

        if status:
            return [t for t in self.topics if t["status"] == status]

        return self.topics

    def remove_topic(self, topic_id: str) -> bool:
        """Remove topic from queue"""

        initial_len = len(self.topics)
        self.topics = [t for t in self.topics if t["id"] != topic_id]

        if len(self.topics) < initial_len:
            self._save_queue()
            return True

        return False

    def update_priority(self, topic_id: str, new_priority: int):
        """Update topic priority"""

        for topic in self.topics:
            if topic["id"] == topic_id:
                topic["priority"] = new_priority
                break

        self._save_queue()


def display_queue(queue: TopicQueue):
    """Display current queue"""

    topics = queue.list_topics()

    if not topics:
        print("\n[INFO] Queue is empty")
        return

    print(f"\n{'='*70}")
    print(f"Topic Queue ({len(topics)} topics)")
    print(f"{'='*70}")

    # Group by status
    statuses = ["queued", "processing", "completed", "failed"]

    for status in statuses:
        status_topics = [t for t in topics if t["status"] == status]

        if status_topics:
            print(f"\n{status.upper()} ({len(status_topics)}):")

            for topic in status_topics:
                print(f"\n  ID: {topic['id']}")
                print(f"  Topic: {topic['topic']}")
                print(f"  Priority: {topic['priority']}")
                print(f"  Profile: {topic['profile']}")

                if topic.get("scheduled_date"):
                    print(f"  Scheduled: {topic['scheduled_date']}")

                if topic.get("tags"):
                    print(f"  Tags: {', '.join(topic['tags'])}")

                if topic.get("episode_id"):
                    print(f"  Episode: {topic['episode_id']}")


def process_queue_batch(queue: TopicQueue, max_topics: int = 5):
    """Process multiple topics from queue"""

    print(f"\n{'='*70}")
    print(f"Batch Processing (max {max_topics} topics)")
    print(f"{'='*70}")

    processed = 0

    while processed < max_topics:
        topic_entry = queue.get_next_topic()

        if not topic_entry:
            print(f"\n[INFO] No more topics to process")
            break

        print(f"\n\n{'='*70}")
        print(f"Processing: {topic_entry['topic']}")
        print(f"Priority: {topic_entry['priority']}")
        print(f"{'='*70}")

        # Get profile
        profile_key = topic_entry.get("profile", "solo_explainer")
        profile = AUTOMATION_PROFILES.get(profile_key, AUTOMATION_PROFILES["trending_topics"])

        # Mark as processing
        topic_entry["status"] = "processing"
        queue._save_queue()

        # Generate episode
        try:
            result = generate_automated_episode(
                topic=topic_entry["topic"],
                profile=profile,
                sources=topic_entry.get("sources")
            )

            if result["success"]:
                queue.mark_processed(topic_entry["id"], result["episode_id"], success=True)
                print(f"\n[OK] Topic processed successfully")
                processed += 1
            else:
                queue.mark_processed(topic_entry["id"], None, success=False)
                print(f"\n[ERROR] Topic processing failed")

        except Exception as e:
            queue.mark_processed(topic_entry["id"], None, success=False)
            print(f"\n[ERROR] Topic processing failed: {e}")

    print(f"\n{'='*70}")
    print(f"Batch Processing Complete")
    print(f"{'='*70}")
    print(f"Processed: {processed} topics")


def main():
    """Topic queue management"""
    print("\n" + "="*70)
    print("Step 38: Topic Queue")
    print("="*70)

    # Check providers
    available = detect_available_providers()
    if not available:
        print("\n[ERROR] No providers available")
        return

    # Initialize queue
    queue = TopicQueue()

    while True:
        print("\n" + "="*70)
        print("Topic Queue Menu")
        print("="*70)
        print("1. View queue")
        print("2. Add topic")
        print("3. Process next topic")
        print("4. Process batch (multiple topics)")
        print("5. Remove topic")
        print("6. Update priority")
        print("7. Add demo topics")
        print("8. Exit")
        print("="*70)

        choice = input("\nChoice (1-8): ").strip()

        if choice == "1":
            display_queue(queue)

        elif choice == "2":
            print("\n--- Add Topic ---")
            topic = input("Topic: ").strip()
            if not topic:
                print("[ERROR] Topic required")
                continue

            priority = input("Priority (1-10, default 5): ").strip() or "5"
            try:
                priority = int(priority)
            except ValueError:
                priority = 5

            profile_keys = list(AUTOMATION_PROFILES.keys())
            print("\nProfiles:")
            for i, key in enumerate(profile_keys, 1):
                print(f"  {i}. {AUTOMATION_PROFILES[key]['name']}")

            profile_choice = input(f"Profile (1-{len(profile_keys)}, default 1): ").strip() or "1"
            try:
                profile_idx = int(profile_choice) - 1
                profile_key = profile_keys[profile_idx] if 0 <= profile_idx < len(profile_keys) else profile_keys[0]
            except ValueError:
                profile_key = profile_keys[0]

            topic_id = queue.add_topic(topic, priority, profile_key)
            print(f"\n[OK] Topic added: {topic_id}")

        elif choice == "3":
            topic_entry = queue.get_next_topic()

            if not topic_entry:
                print("\n[INFO] No topics in queue")
                continue

            print(f"\n[INFO] Next topic: {topic_entry['topic']}")
            confirm = input("Process this topic? (y/n): ").strip().lower()

            if confirm == 'y':
                profile_key = topic_entry.get("profile", "solo_explainer")
                profile = AUTOMATION_PROFILES.get(profile_key, AUTOMATION_PROFILES["trending_topics"])

                try:
                    result = generate_automated_episode(
                        topic=topic_entry["topic"],
                        profile=profile,
                        sources=topic_entry.get("sources")
                    )

                    if result["success"]:
                        queue.mark_processed(topic_entry["id"], result["episode_id"], success=True)
                        print(f"\n[OK] Topic processed")
                    else:
                        queue.mark_processed(topic_entry["id"], None, success=False)
                        print(f"\n[ERROR] Processing failed")

                except Exception as e:
                    queue.mark_processed(topic_entry["id"], None, success=False)
                    print(f"\n[ERROR] Processing failed: {e}")

        elif choice == "4":
            max_topics = input("Max topics to process (default 3): ").strip() or "3"
            try:
                max_topics = int(max_topics)
            except ValueError:
                max_topics = 3

            process_queue_batch(queue, max_topics)

        elif choice == "5":
            topic_id = input("Topic ID to remove: ").strip()
            if queue.remove_topic(topic_id):
                print(f"[OK] Topic removed")
            else:
                print(f"[ERROR] Topic not found")

        elif choice == "6":
            topic_id = input("Topic ID: ").strip()
            new_priority = input("New priority (1-10): ").strip()
            try:
                new_priority = int(new_priority)
                queue.update_priority(topic_id, new_priority)
                print(f"[OK] Priority updated")
            except ValueError:
                print(f"[ERROR] Invalid priority")

        elif choice == "7":
            print("\n[INFO] Adding demo topics...")

            demo_topics = [
                ("The Future of AI in Healthcare", 8, "daily_briefing"),
                ("Understanding Quantum Computing", 6, "weekly_deep_dive"),
                ("Climate Change Solutions 2026", 7, "trending_topics"),
                ("Cryptocurrency Market Update", 5, "daily_briefing"),
                ("Space Exploration Milestones", 6, "weekly_deep_dive")
            ]

            for topic, priority, profile in demo_topics:
                queue.add_topic(topic, priority, profile)

            print(f"[OK] Added {len(demo_topics)} demo topics")

        elif choice == "8":
            print("\n[OK] Exiting queue manager")
            break

        else:
            print("\n[ERROR] Invalid choice")


if __name__ == "__main__":
    main()
