# PowerShell deployment script for Airlines Flight Tracker
# Deploys to Digital Ocean droplet

param(
    [Parameter(Mandatory = $true)]
    [string]$DropletIP,
    
    [Parameter(Mandatory = $false)]
    [string]$SSHUser = "root"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Airlines Flight Tracker - Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$AppDir = "c:\Projects\Airlines"
$TempDir = Join-Path $env:TEMP "airlines_deploy"

# Check if required tools are available
$requiredCommands = @("ssh", "scp", "tar")
foreach ($cmd in $requiredCommands) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "Error: $cmd is not available. Please install OpenSSH or Git for Windows." -ForegroundColor Red
        exit 1
    }
}

try {
    Write-Host "Step 1: Creating deployment package..." -ForegroundColor Green
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
    New-Item -ItemType Directory -Path $TempDir | Out-Null

    Write-Host "Step 2: Copying application files..." -ForegroundColor Green
    
    # Files to include
    $filesToCopy = @(
        "*.py",
        "*.sh",
        "*.md",
        "requirements.txt",
        ".env.example"
    )
    
    foreach ($pattern in $filesToCopy) {
        Get-ChildItem -Path $AppDir -Filter $pattern | ForEach-Object {
            Copy-Item $_.FullName -Destination $TempDir
        }
    }
    
    # Create data directory structure
    New-Item -ItemType Directory -Path "$TempDir\data\raw" -Force | Out-Null
    New-Item -ItemType Directory -Path "$TempDir\data\processed" -Force | Out-Null
    New-Item -ItemType Directory -Path "$TempDir\data\reports" -Force | Out-Null
    
    # Create .gitkeep files
    New-Item -ItemType File -Path "$TempDir\data\raw\.gitkeep" -Force | Out-Null
    New-Item -ItemType File -Path "$TempDir\data\processed\.gitkeep" -Force | Out-Null
    New-Item -ItemType File -Path "$TempDir\data\reports\.gitkeep" -Force | Out-Null

    Write-Host "Step 3: Creating tarball..." -ForegroundColor Green
    Push-Location $TempDir
    tar -czf airlines.tar.gz *
    Pop-Location

    Write-Host "Step 4: Uploading to droplet..." -ForegroundColor Green
    Write-Host "  Uploading application files..." -ForegroundColor Yellow
    scp "$TempDir\airlines.tar.gz" "${SSHUser}@${DropletIP}:/tmp/"
    
    if (Test-Path "$AppDir\id_ed25519") {
        Write-Host "  Uploading SSH keys..." -ForegroundColor Yellow
        scp "$AppDir\id_ed25519" "${SSHUser}@${DropletIP}:/tmp/"
        scp "$AppDir\id_ed25519.pub" "${SSHUser}@${DropletIP}:/tmp/"
    }
    else {
        Write-Host "  Warning: SSH keys not found. You'll need to set them up manually." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "Step 5: Running deployment on droplet..." -ForegroundColor Green
    
    $deployCommands = @(
        "mkdir -p /opt/airlines",
        "cd /opt/airlines",
        "tar -xzf /tmp/airlines.tar.gz",
        "chmod +x deploy.sh",
        "./deploy.sh"
    )
    
    $deployScript = $deployCommands -join " && "
    ssh "${SSHUser}@${DropletIP}" $deployScript

    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "Deployment Complete!" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Configure environment:" -ForegroundColor White
    Write-Host "   ssh ${SSHUser}@${DropletIP}" -ForegroundColor Gray
    Write-Host "   nano /opt/airlines/.env" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Test the application:" -ForegroundColor White
    Write-Host "   sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/main.py collect --days-back 1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Check service status:" -ForegroundColor White
    Write-Host "   systemctl status airlines-collector.timer" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. View logs:" -ForegroundColor White
    Write-Host "   journalctl -u airlines-collector.service -f" -ForegroundColor Gray
    Write-Host ""
    
    # Offer to open SSH connection
    Write-Host "Would you like to connect to the droplet now? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        ssh "${SSHUser}@${DropletIP}"
    }

}
catch {
    Write-Host "Error during deployment: $_" -ForegroundColor Red
    exit 1
}
finally {
    # Cleanup
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
}
