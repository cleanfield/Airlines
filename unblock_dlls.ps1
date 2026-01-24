# PowerShell script to unblock NumPy DLL files
# Run this as Administrator if you encounter NumPy import errors

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "NumPy DLL Unblock Script" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARNING] This script should be run as Administrator for best results." -ForegroundColor Yellow
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then run this script again." -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne 'y') {
        exit
    }
}

Write-Host "[1/3] Checking virtual environment..." -ForegroundColor Green

$venvPath = ".\venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "[ERROR] Virtual environment not found at: $venvPath" -ForegroundColor Red
    Write-Host "Please run this script from the Airlines project directory." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Virtual environment found" -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] Unblocking NumPy DLL files..." -ForegroundColor Green

$numpyPath = Join-Path $venvPath "Lib\site-packages\numpy"

if (Test-Path $numpyPath) {
    try {
        Get-ChildItem -Path $numpyPath -Recurse -File | Unblock-File -ErrorAction SilentlyContinue
        Write-Host "[OK] NumPy files unblocked" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Some files could not be unblocked: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "[ERROR] NumPy not found at: $numpyPath" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/3] Unblocking other package DLL files..." -ForegroundColor Green

$packagesPath = Join-Path $venvPath "Lib\site-packages"

try {
    Get-ChildItem -Path $packagesPath -Recurse -Include "*.pyd","*.dll" | Unblock-File -ErrorAction SilentlyContinue
    Write-Host "[OK] Package DLL files unblocked" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Some files could not be unblocked: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] DLL files have been unblocked!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Test the installation: venv\Scripts\python.exe test_installation.py" -ForegroundColor White
Write-Host "  2. Run analysis: venv\Scripts\python.exe main.py analyze" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
