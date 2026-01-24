@echo off
REM Quick Start Script for Airline Reliability Tracker
REM This script helps you get started quickly

echo ================================================================================
echo AIRLINE RELIABILITY TRACKER - QUICK START
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/4] Testing API connection...
python -c "from schiphol_api import SchipholAPIClient; client = SchipholAPIClient(); print('API client initialized successfully')"
if errorlevel 1 (
    echo WARNING: API client test failed, but continuing...
)
echo.

echo [4/4] Setup complete!
echo.
echo ================================================================================
echo NEXT STEPS:
echo ================================================================================
echo.
echo Option 1: Run a quick test (collect today's data)
echo    python main.py analyze
echo.
echo Option 2: Analyze the past week
echo    python main.py analyze --days-back 7
echo.
echo Option 3: Just collect data without processing
echo    python main.py collect
echo.
echo For more options, see USAGE.md or run:
echo    python main.py --help
echo.
echo ================================================================================
pause
