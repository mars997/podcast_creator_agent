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
