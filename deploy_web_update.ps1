# Quick deployment script to update web files on Digital Ocean
# This script pulls latest changes from GitHub and restarts the web service

param(
    [string]$DropletIP = "178.128.241.64",
    [string]$SSHUser = "flights"
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deploying Web Updates to Digital Ocean" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Pulling latest changes from GitHub..." -ForegroundColor Green
ssh ${SSHUser}@${DropletIP} "cd /opt/airlines && git pull origin main"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error pulling from GitHub!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Restarting web service..." -ForegroundColor Green
ssh ${SSHUser}@${DropletIP} "sudo systemctl restart airlines-web.service"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error restarting service!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Checking service status..." -ForegroundColor Green
ssh ${SSHUser}@${DropletIP} "sudo systemctl status airlines-web.service --no-pager -l"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your website should be updated at:" -ForegroundColor Yellow
Write-Host "  https://alstorphius.com" -ForegroundColor White
Write-Host ""
Write-Host "Test the destination filter:" -ForegroundColor Yellow
Write-Host "  1. Select 'Vertrek' (Departures)" -ForegroundColor White
Write-Host "  2. Choose a Continent, Country, and Airport" -ForegroundColor White
Write-Host "  3. Rankings should filter accordingly" -ForegroundColor White
Write-Host ""
