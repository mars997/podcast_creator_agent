"""
Step 45: Team Config Files

Shared configuration for team collaboration.
Allows consistent settings across team members.
"""

from pathlib import Path
import json
from datetime import datetime

# Default team configuration
DEFAULT_TEAM_CONFIG = {
    "team_name": "Podcast Production Team",
    "created_at": datetime.now().isoformat(),
    "version": "1.0",
    
    "defaults": {
        "tone": "professional",
        "length": "medium",
        "voice": "nova",
        "provider": "openai"
    },
    
    "personas_enabled": [
        "tech_enthusiast",
        "science_explainer",
        "business_analyst"
    ],
    
    "templates_enabled": [
        "solo_explainer",
        "news_recap",
        "deep_dive"
    ],
    
    "quality_standards": {
        "min_word_count": 300,
        "max_word_count": 1500,
        "require_sources": False,
        "require_approval": True
    },
    
    "output_settings": {
        "output_root": "output",
        "naming_convention": "{topic}_{timestamp}",
        "save_sources": True,
        "save_metadata": True
    },
    
    "branding": {
        "show_name": "AI Insights Podcast",
        "intro_template": "tech",
        "outro_template": "tech"
    }
}


def create_team_config(config_file: Path = Path("team_config.json")):
    """Create team configuration file"""
    with open(config_file, 'w') as f:
        json.dump(DEFAULT_TEAM_CONFIG, f, indent=2)
    
    print(f"[OK] Team config created: {config_file}")
    return config_file


def load_team_config(config_file: Path = Path("team_config.json")):
    """Load team configuration"""
    if not config_file.exists():
        print(f"[WARN] Config not found, creating default: {config_file}")
        return create_team_config(config_file)
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print(f"[OK] Team config loaded: {config['team_name']}")
    return config


if __name__ == "__main__":
    print("Step 45: Team Config Files\n")
    
    # Create config
    config_file = create_team_config()
    
    # Load and display
    config = load_team_config(config_file)
    
    print(f"\nTeam: {config['team_name']}")
    print(f"Defaults: {config['defaults']}")
    print(f"Quality Standards: {config['quality_standards']}")
    
    print(f"\n[OK] Team config ready at: {config_file}")
