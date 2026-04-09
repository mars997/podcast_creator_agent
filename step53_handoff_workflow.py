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
