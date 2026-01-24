@echo off
REM Quick deployment script for Windows
REM Packages and uploads the Airlines application to Digital Ocean

echo ========================================
echo Airlines Flight Tracker - Deployment
echo ========================================
echo.

REM Check if droplet IP is provided
if "%1"=="" (
    echo Usage: deploy_to_do.bat DROPLET_IP
    echo Example: deploy_to_do.bat 192.168.1.100
    exit /b 1
)

set DROPLET_IP=%1
set APP_DIR=c:\Projects\Airlines
set TEMP_DIR=%TEMP%\airlines_deploy

echo Step 1: Creating deployment package...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

echo Step 2: Copying files...
xcopy /E /I /Y "%APP_DIR%\*.py" "%TEMP_DIR%\"
xcopy /E /I /Y "%APP_DIR%\*.sh" "%TEMP_DIR%\"
xcopy /E /I /Y "%APP_DIR%\*.md" "%TEMP_DIR%\"
xcopy /E /I /Y "%APP_DIR%\requirements.txt" "%TEMP_DIR%\"
xcopy /E /I /Y "%APP_DIR%\.env.example" "%TEMP_DIR%\"
xcopy /E /I /Y "%APP_DIR%\data\.gitkeep" "%TEMP_DIR%\data\" 2>nul

echo Step 3: Creating tarball...
cd "%TEMP_DIR%"
tar -czf airlines.tar.gz *

echo Step 4: Uploading to droplet...
echo.
echo Uploading application files...
scp "%TEMP_DIR%\airlines.tar.gz" root@%DROPLET_IP%:/tmp/

echo.
echo Uploading SSH keys...
scp "%APP_DIR%\id_ed25519" root@%DROPLET_IP%:/tmp/
scp "%APP_DIR%\id_ed25519.pub" root@%DROPLET_IP%:/tmp/

echo.
echo Step 5: Running deployment on droplet...
ssh root@%DROPLET_IP% "mkdir -p /opt/airlines && cd /opt/airlines && tar -xzf /tmp/airlines.tar.gz && chmod +x deploy.sh && ./deploy.sh"

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Configure environment:
echo    ssh root@%DROPLET_IP% "nano /opt/airlines/.env"
echo.
echo 2. Test the application:
echo    ssh root@%DROPLET_IP% "sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/main.py collect --days-back 1"
echo.
echo 3. Check service status:
echo    ssh root@%DROPLET_IP% "systemctl status airlines-collector.timer"
echo.
echo 4. View logs:
echo    ssh root@%DROPLET_IP% "journalctl -u airlines-collector.service -f"
echo.

REM Cleanup
rmdir /s /q "%TEMP_DIR%"
