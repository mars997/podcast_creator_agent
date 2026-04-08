@echo off
echo ================================================================
echo Quick Manual Regression Test - Steps 1-20
echo ================================================================
echo.
echo This script runs non-API tests to validate the refactor
echo.

echo [TEST 1] Config Loading
echo ----------------------------------------
python -c "import config; print('PASS: Config loaded'); print(f'  DEFAULT_TONE: {config.DEFAULT_TONE}'); print(f'  DEFAULT_LENGTH: {config.DEFAULT_LENGTH}'); print(f'  OUTPUT_ROOT: {config.OUTPUT_ROOT}')"
if errorlevel 1 (
    echo FAIL: Config loading failed
    goto end
)
echo.

echo [TEST 2] Core Module Imports
echo ----------------------------------------
python -c "from core.provider_setup import initialize_providers; from core.content_generation import build_script; from core.episode_management import load_episode_index; from core.validation import sanitize_filename; print('PASS: All core modules imported successfully')"
if errorlevel 1 (
    echo FAIL: Core module imports failed
    goto end
)
echo.

echo [TEST 3] Episode Index Loading
echo ----------------------------------------
python -c "from pathlib import Path; from core.episode_management import load_episode_index; episodes = load_episode_index(Path('output/episode_index.json')); print(f'PASS: Loaded {len(episodes)} episodes'); print(f'  Topics: {[e.get(\"topic\") for e in episodes]}')"
if errorlevel 1 (
    echo FAIL: Episode index loading failed
    goto end
)
echo.

echo [TEST 4] File Reading (Step 8-9)
echo ----------------------------------------
python -c "from pathlib import Path; from core.file_utils import read_text_file; content = read_text_file(Path('source.txt')); print(f'PASS: Read source.txt ({len(content)} chars, {len(content.split())} words)')"
if errorlevel 1 (
    echo FAIL: File reading failed
    goto end
)
echo.

echo [TEST 5] Episode Browser (Step 17)
echo ----------------------------------------
python step17_episode_browser.py --list
if errorlevel 1 (
    echo FAIL: Episode browser failed
    goto end
)
echo.

echo [TEST 6] Unique ID Generation (Step 16)
echo ----------------------------------------
python -c "from datetime import datetime; from core.validation import sanitize_filename; topic = 'Test Episode'; safe = sanitize_filename(topic); ts = datetime.now().strftime('%%Y-%%m-%%d_%%H%%M%%S'); id = f'{safe}_{ts}'; print(f'PASS: Generated unique ID: {id}')"
if errorlevel 1 (
    echo FAIL: Unique ID generation failed
    goto end
)
echo.

echo ================================================================
echo All Tests PASSED!
echo ================================================================
echo.
echo The refactor is working correctly. You can now test:
echo   - View episode files in: output\ai_trending\
echo   - Play audio: output\ai_trending\podcast_nova.mp3
echo   - Read script: output\ai_trending\script.txt
echo   - Check metadata: output\ai_trending\metadata.json
echo.
goto end

:end
echo.
pause
