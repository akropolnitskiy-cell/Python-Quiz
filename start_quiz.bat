@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    py -m venv .venv
    if errorlevel 1 (
        echo Could not create the Python environment. Is Python installed?
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" -c "import requests" 2>nul
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Could not install the required packages.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" python_quiz.py
pause
