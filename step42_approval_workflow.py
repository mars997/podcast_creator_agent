"""
Step 42: Episode Approval Workflow

Multi-stage approval system for podcast episodes before publication.
Supports draft/review/approved/published states with quality gates.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

from step41_quality_check import QualityChecker
from providers.factory import create_llm_provider, ProviderConfig, detect_available_providers
from core.episode_management import load_episode_metadata
import config


# Episode states
EPISODE_STATES = ["draft", "review", "approved", "published", "rejected"]


class ApprovalWorkflow:
    """Manages episode approval workflow"""

    def __init__(self, approval_file: Path = None):
        if approval_file is None:
            approval_file = Path(config.OUTPUT_ROOT) / "approval_workflow.json"

        self.approval_file = approval_file
        self.episodes = self._load_workflow()

    def _load_workflow(self) -> Dict:
        """Load workflow state"""
        if self.approval_file.exists():
            with open(self.approval_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_workflow(self):
        """Save workflow state"""
        self.approval_file.parent.mkdir(exist_ok=True)
        with open(self.approval_file, 'w', encoding='utf-8') as f:
            json.dump(self.episodes, f, indent=2)

    def register_episode(self, episode_id: str, episode_dir: Path, state: str = "draft"):
        """Register episode in workflow"""

        self.episodes[episode_id] = {
            "episode_id": episode_id,
            "episode_dir": str(episode_dir),
            "state": state,
            "registered_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "state_history": [
                {
                    "state": state,
                    "timestamp": datetime.now().isoformat(),
                    "action": "registered"
                }
            ],
            "quality_checks": [],
            "approvals": [],
            "rejections": []
        }

        self._save_workflow()

    def get_episode(self, episode_id: str) -> Optional[Dict]:
        """Get episode workflow info"""
        return self.episodes.get(episode_id)

    def update_state(
        self,
        episode_id: str,
        new_state: str,
        actor: str = "system",
        notes: Optional[str] = None
    ):
        """Update episode state"""

        if episode_id not in self.episodes:
            raise ValueError(f"Episode not registered: {episode_id}")

        if new_state not in EPISODE_STATES:
            raise ValueError(f"Invalid state: {new_state}")

        episode = self.episodes[episode_id]

        # Record state change
        state_change = {
            "state": new_state,
            "timestamp": datetime.now().isoformat(),
            "actor": actor,
            "action": f"changed from {episode['state']} to {new_state}"
        }

        if notes:
            state_change["notes"] = notes

        episode["state"] = new_state
        episode["updated_at"] = datetime.now().isoformat()
        episode["state_history"].append(state_change)

        self._save_workflow()

    def add_quality_check(self, episode_id: str, quality_report: Dict):
        """Add quality check result"""

        if episode_id not in self.episodes:
            raise ValueError(f"Episode not registered: {episode_id}")

        self.episodes[episode_id]["quality_checks"].append({
            "timestamp": datetime.now().isoformat(),
            "report": quality_report
        })

        self._save_workflow()

    def approve(self, episode_id: str, approver: str, notes: Optional[str] = None):
        """Approve episode"""

        if episode_id not in self.episodes:
            raise ValueError(f"Episode not registered: {episode_id}")

        approval = {
            "timestamp": datetime.now().isoformat(),
            "approver": approver,
            "notes": notes
        }

        self.episodes[episode_id]["approvals"].append(approval)
        self.update_state(episode_id, "approved", approver, notes)

    def reject(self, episode_id: str, rejector: str, reason: str):
        """Reject episode"""

        if episode_id not in self.episodes:
            raise ValueError(f"Episode not registered: {episode_id}")

        rejection = {
            "timestamp": datetime.now().isoformat(),
            "rejector": rejector,
            "reason": reason
        }

        self.episodes[episode_id]["rejections"].append(rejection)
        self.update_state(episode_id, "rejected", rejector, reason)

    def list_episodes_by_state(self, state: str) -> List[Dict]:
        """List episodes in specific state"""
        return [ep for ep in self.episodes.values() if ep["state"] == state]

    def list_pending_review(self) -> List[Dict]:
        """List episodes awaiting review"""
        return self.list_episodes_by_state("review")


def display_episode_status(workflow: ApprovalWorkflow, episode_id: str):
    """Display detailed episode status"""

    episode = workflow.get_episode(episode_id)

    if not episode:
        print(f"[ERROR] Episode not found: {episode_id}")
        return

    print(f"\n{'='*70}")
    print(f"Episode: {episode_id}")
    print(f"{'='*70}")
    print(f"State: {episode['state'].upper()}")
    print(f"Registered: {episode['registered_at']}")
    print(f"Last Updated: {episode['updated_at']}")

    # State history
    if episode["state_history"]:
        print(f"\nState History:")
        for change in episode["state_history"]:
            print(f"  {change['timestamp']}: {change['action']}")
            if change.get("notes"):
                print(f"    Notes: {change['notes']}")

    # Quality checks
    if episode["quality_checks"]:
        print(f"\nQuality Checks ({len(episode['quality_checks'])}):")
        latest = episode["quality_checks"][-1]
        report = latest["report"]
        print(f"  Latest: {latest['timestamp']}")
        print(f"  Overall Pass: {report.get('overall_pass', 'N/A')}")

    # Approvals
    if episode["approvals"]:
        print(f"\nApprovals ({len(episode['approvals'])}):")
        for approval in episode["approvals"]:
            print(f"  {approval['timestamp']}: {approval['approver']}")
            if approval.get("notes"):
                print(f"    {approval['notes']}")

    # Rejections
    if episode["rejections"]:
        print(f"\nRejections ({len(episode['rejections'])}):")
        for rejection in episode["rejections"]:
            print(f"  {rejection['timestamp']}: {rejection['rejector']}")
            print(f"    Reason: {rejection['reason']}")


def main():
    """Approval workflow demo"""
    print("\n" + "="*70)
    print("Step 42: Episode Approval Workflow")
    print("="*70)

    # Initialize workflow
    workflow = ApprovalWorkflow()

    print("\n[OK] Approval workflow initialized")

    while True:
        print("\n" + "="*70)
        print("Approval Workflow Menu")
        print("="*70)
        print("1. Register new episode")
        print("2. View episode status")
        print("3. Submit for review")
        print("4. Run quality check")
        print("5. Approve episode")
        print("6. Reject episode")
        print("7. List pending reviews")
        print("8. Publish episode")
        print("9. Exit")
        print("="*70)

        choice = input("\nChoice (1-9): ").strip()

        if choice == "1":
            episode_id = input("\nEpisode ID: ").strip()
            if not episode_id:
                print("[ERROR] Episode ID required")
                continue

            episode_dir = Path(config.OUTPUT_ROOT) / episode_id

            if not episode_dir.exists():
                print(f"[ERROR] Episode directory not found: {episode_dir}")
                continue

            workflow.register_episode(episode_id, episode_dir, state="draft")
            print(f"[OK] Episode registered in workflow as 'draft'")

        elif choice == "2":
            episode_id = input("\nEpisode ID: ").strip()
            display_episode_status(workflow, episode_id)

        elif choice == "3":
            episode_id = input("\nEpisode ID: ").strip()
            episode = workflow.get_episode(episode_id)

            if not episode:
                print(f"[ERROR] Episode not found")
                continue

            if episode["state"] != "draft":
                print(f"[WARN] Episode is already in '{episode['state']}' state")

            workflow.update_state(episode_id, "review", "user", "Submitted for review")
            print(f"[OK] Episode submitted for review")

        elif choice == "4":
            episode_id = input("\nEpisode ID: ").strip()
            episode = workflow.get_episode(episode_id)

            if not episode:
                print(f"[ERROR] Episode not found")
                continue

            # Load script
            script_file = Path(episode["episode_dir"]) / "script.txt"

            if not script_file.exists():
                print(f"[ERROR] Script not found: {script_file}")
                continue

            with open(script_file, 'r', encoding='utf-8') as f:
                script = f.read()

            # Run quality check
            available = detect_available_providers()
            if not available:
                print("[ERROR] No providers available for quality check")
                continue

            provider_name = list(available.keys())[0]
            provider_config = ProviderConfig(llm_provider=provider_name)
            llm_provider = create_llm_provider(provider_config)

            checker = QualityChecker(llm_provider)

            print("\n[INFO] Running quality check...")

            # Load metadata for topic/tone
            metadata_file = Path(episode["episode_dir"]) / "metadata.json"
            if metadata_file.exists():
                metadata = load_episode_metadata(metadata_file)
                topic = metadata.get("topic", "Unknown")
                tone = metadata.get("tone", "professional")
            else:
                topic = episode_id
                tone = "professional"

            quality_result = checker.check_script_quality(script, topic, tone)
            prod_result = checker.check_production_readiness(script)

            overall_pass = quality_result["passes"] and prod_result["production_ready"]

            quality_report = {
                "overall_pass": overall_pass,
                "quality_check": quality_result,
                "production_check": prod_result
            }

            workflow.add_quality_check(episode_id, quality_report)

            print(f"\n[OK] Quality check complete")
            print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")

            if not overall_pass:
                print("\n[WARN] Episode did not pass quality checks")
                print("Review issues before approval")

        elif choice == "5":
            episode_id = input("\nEpisode ID: ").strip()
            approver = input("Approver name: ").strip() or "user"
            notes = input("Approval notes (optional): ").strip()

            try:
                workflow.approve(episode_id, approver, notes if notes else None)
                print(f"[OK] Episode approved by {approver}")
            except ValueError as e:
                print(f"[ERROR] {e}")

        elif choice == "6":
            episode_id = input("\nEpisode ID: ").strip()
            rejector = input("Rejector name: ").strip() or "user"
            reason = input("Rejection reason: ").strip()

            if not reason:
                print("[ERROR] Rejection reason required")
                continue

            try:
                workflow.reject(episode_id, rejector, reason)
                print(f"[OK] Episode rejected")
            except ValueError as e:
                print(f"[ERROR] {e}")

        elif choice == "7":
            pending = workflow.list_pending_review()

            if not pending:
                print("\n[INFO] No episodes pending review")
            else:
                print(f"\n{'='*70}")
                print(f"Episodes Pending Review ({len(pending)})")
                print(f"{'='*70}")

                for ep in pending:
                    print(f"\n{ep['episode_id']}")
                    print(f"  Submitted: {ep['updated_at']}")

                    # Check if quality checked
                    if ep["quality_checks"]:
                        latest_qc = ep["quality_checks"][-1]
                        passed = latest_qc["report"].get("overall_pass", False)
                        print(f"  Quality Check: {'PASS' if passed else 'FAIL'}")
                    else:
                        print(f"  Quality Check: Not run")

        elif choice == "8":
            episode_id = input("\nEpisode ID: ").strip()
            episode = workflow.get_episode(episode_id)

            if not episode:
                print(f"[ERROR] Episode not found")
                continue

            if episode["state"] != "approved":
                print(f"[ERROR] Episode must be approved before publishing")
                print(f"Current state: {episode['state']}")
                continue

            workflow.update_state(episode_id, "published", "user", "Published")
            print(f"[OK] Episode published")

        elif choice == "9":
            print("\n[OK] Exiting approval workflow")
            break

        else:
            print("\n[ERROR] Invalid choice")


if __name__ == "__main__":
    main()
