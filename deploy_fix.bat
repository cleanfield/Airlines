@echo off
echo =========================================
echo Deploying Destination Filter Fix
echo =========================================
echo.
echo This will:
echo 1. Pull latest changes from GitHub
echo 2. Restart the web service
echo 3. Show service status
echo.
echo Server: 178.128.241.64
echo User: flights
echo.
pause
echo.
echo Connecting to server...
echo.

REM Try to execute deployment commands
ssh -o StrictHostKeyChecking=no flights@178.128.241.64 "cd /opt/airlines && git pull origin main && sudo systemctl restart airlines-web.service && sudo systemctl status airlines-web.service --no-pager -l"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =========================================
    echo Deployment Successful!
    echo =========================================
    echo.
    echo Test at: https://alstorphius.com
    echo.
    echo 1. Select 'Vertrek' flight type
    echo 2. Choose Continent, Country, Airport
    echo 3. Verify filtering works
    echo.
) else (
    echo.
    echo =========================================
    echo Deployment Failed!
    echo =========================================
    echo.
    echo Please deploy manually:
    echo   ssh flights@178.128.241.64
    echo   cd /opt/airlines
    echo   git pull origin main
    echo   sudo systemctl restart airlines-web.service
    echo.
)

pause
