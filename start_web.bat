@echo off
REM Start Airlines Reliability Web Server

echo ========================================
echo Airlines Reliability - Web Server
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Run: python -m venv venv
    echo.
)

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask not found. Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo Starting web server...
echo.
echo Access the web interface at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python web_api.py
