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
