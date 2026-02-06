@echo off
echo =========================================
echo Deploying Web Updates to Digital Ocean
echo =========================================
echo.

echo Step 1: Pulling latest changes from GitHub...
plink -batch flights@178.128.241.64 "cd /opt/airlines && git pull origin main"

echo.
echo Step 2: Restarting web service...
plink -batch flights@178.128.241.64 "sudo systemctl restart airlines-web.service"

echo.
echo Step 3: Checking service status...
plink -batch flights@178.128.241.64 "sudo systemctl status airlines-web.service --no-pager"

echo.
echo =========================================
echo Deployment Complete!
echo =========================================
echo.
echo Your website should be updated at:
echo   https://alstorphius.com
echo.
pause
