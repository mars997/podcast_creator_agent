# Create all remaining steps

# Step 47
cat > step47_logging.py << 'EOF'
"""Step 47: Logging System"""
import logging
from pathlib import Path
from datetime import datetime

log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'podcast_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('podcast_creator')

if __name__ == '__main__':
    logger.info('Step 47: Logging system initialized')
    logger.info(f'Log directory: {log_dir.absolute()}')
    print('[OK] Logging configured')
EOF

# Step 48
cat > step48_tests.py << 'EOF'
"""Step 48: Test Framework"""
import unittest
from pathlib import Path
from core.validation import sanitize_filename, validate_choice

class TestValidation(unittest.TestCase):
    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename('Test Podcast!'), 'Test_Podcast')
        self.assertEqual(sanitize_filename('AI & ML'), 'AI__ML')
    
    def test_validate_choice(self):
        result = validate_choice('casual', {'casual', 'professional'}, 'tone')
        self.assertEqual(result, 'casual')

if __name__ == '__main__':
    print('Step 48: Running tests...')
    unittest.main(verbosity=2)
EOF

# Step 49
cat > step49_export_package.py << 'EOF'
"""Step 49: Export Clean Publish Package"""
from pathlib import Path
import shutil
import json

def export_episode(episode_dir: Path, export_dir: Path):
    export_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_copy = ['script.txt', 'show_notes.txt', 'metadata.json']
    files_to_copy += list(episode_dir.glob('podcast_*.mp3'))
    
    for file in files_to_copy:
        if isinstance(file, str):
            src = episode_dir / file
        else:
            src = file
        if src.exists():
            shutil.copy(src, export_dir / src.name)
    
    manifest = {
        'episode': episode_dir.name,
        'exported_at': str(Path.ctime(episode_dir)),
        'files': [f.name for f in export_dir.glob('*')]
    }
    
    with open(export_dir / 'MANIFEST.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return export_dir

if __name__ == '__main__':
    print('Step 49: Export Package')
    print('[OK] Export function ready')
EOF

# Step 50
cat > step50_marketing_descriptions.py << 'EOF'
"""Step 50: Generate Podcast-Ready Descriptions"""
from providers.factory import ProviderConfig, create_llm_provider, detect_available_providers

def generate_marketing_content(topic, script):
    available = detect_available_providers()
    if not available:
        return None
    
    provider = list(available.keys())[0]
    config = ProviderConfig(llm_provider=provider, tts_provider=provider)
    llm = create_llm_provider(config)
    
    prompt = f"""Generate marketing content for this podcast:

Topic: {topic}

Script excerpt: {script[:500]}...

Generate:
1. SEO-friendly title (60 chars max)
2. Episode description (150 chars)
3. Full description (300 words)
4. Social media post (280 chars)
5. Keywords (10 keywords)
"""
    
    return llm.generate_text(prompt)

if __name__ == '__main__':
    print('Step 50: Marketing Descriptions')
    print('[OK] Marketing generator ready')
EOF

# Step 51
cat > step51_rss_feed.py << 'EOF'
"""Step 51: RSS Publishing Support"""
from datetime import datetime

def generate_rss_item(episode_metadata, audio_url):
    item = f"""
    <item>
        <title>{episode_metadata.get('topic', 'Untitled')}</title>
        <description>{episode_metadata.get('description', '')}</description>
        <pubDate>{episode_metadata.get('created_at', '')}</pubDate>
        <enclosure url="{audio_url}" type="audio/mpeg"/>
        <guid>{episode_metadata.get('episode_id', '')}</guid>
    </item>
    """
    return item

if __name__ == '__main__':
    print('Step 51: RSS Feed Generator')
    print('[OK] RSS function ready')
EOF

# Step 53
cat > step53_handoff_workflow.py << 'EOF'
"""Step 53: Share/Handoff Workflow"""
from pathlib import Path
import zipfile
import json

def create_handoff_package(episode_dir: Path, output_zip: Path):
    with zipfile.ZipFile(output_zip, 'w') as zf:
        for file in episode_dir.rglob('*'):
            if file.is_file():
                zf.write(file, file.relative_to(episode_dir))
        
        readme = '''# Podcast Episode Package

## Contents
- script.txt: Podcast script
- podcast_*.mp3: Audio file
- show_notes.txt: Show notes
- metadata.json: Episode metadata

## Usage
Extract and review all files before publishing.
'''
        zf.writestr('README.txt', readme)
    
    return output_zip

if __name__ == '__main__':
    print('Step 53: Handoff Workflow')
    print('[OK] Packaging function ready')
EOF

echo "All files created"
