@echo off
echo Stopping all running Python processes...
taskkill /F /IM python.exe /T
echo.
echo All Python processes stopped.
echo.
echo Restarting GitHub Repo AI Agent...
streamlit run app.py
pause
