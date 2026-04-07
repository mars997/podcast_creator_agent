@echo off
echo ========================================
echo Quick RSS Podcast Test
echo ========================================
echo.
echo This will create a podcast from NYT Technology RSS feed
echo with 2 articles.
echo.
echo Press any key to start...
pause >nul

REM Create input file for automated testing
(
echo https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml
echo 2
echo tech_news_test
echo educational
echo nova
echo medium
) > temp_input.txt

echo.
echo Running step19_rss_podcast.py...
echo.

.venv\Scripts\python.exe step19_rss_podcast.py < temp_input.txt

del temp_input.txt

echo.
echo ========================================
echo Check the output folder for your podcast!
echo ========================================
pause
