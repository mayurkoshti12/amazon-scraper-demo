@echo off
cd /d D:\python_projects\playwright-demo

:loop
echo Starting scraper...
python main.py

echo Script crashed or finished. Restarting in 10 seconds...
timeout /t 10

goto loop