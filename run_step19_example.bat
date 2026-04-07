@echo off
REM Helper script to run step19 with the virtual environment
REM This will create a real RSS podcast with actual audio

echo ========================================
echo Running Step 19: RSS Podcast Generator
echo ========================================
echo.
echo This will create a podcast from an RSS feed.
echo The audio file will be real and playable.
echo.
echo Example RSS feeds you can use:
echo   - NYT Technology: https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml
echo   - BBC News Tech: http://feeds.bbci.co.uk/news/technology/rss.xml
echo   - TechCrunch: https://techcrunch.com/feed/
echo   - Wired: https://www.wired.com/feed/rss
echo.

REM Run with virtual environment Python
.venv\Scripts\python.exe step19_rss_podcast.py

echo.
echo ========================================
echo Done!
echo ========================================
pause
