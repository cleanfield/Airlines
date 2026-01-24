# Start Airlines Reliability Web Server
# PowerShell script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Airlines Reliability - Web Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
}
else {
    Write-Host "Warning: Virtual environment not found" -ForegroundColor Yellow
    Write-Host "Run: python -m venv venv" -ForegroundColor Yellow
    Write-Host ""
}

# Check if Flask is installed
try {
    python -c "import flask" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Flask not installed"
    }
}
catch {
    Write-Host "Flask not found. Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host ""
}

Write-Host "Starting web server..." -ForegroundColor Green
Write-Host ""
Write-Host "Access the web interface at:" -ForegroundColor White
Write-Host "  http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "API endpoints:" -ForegroundColor White
Write-Host "  http://localhost:5000/api/rankings" -ForegroundColor Gray
Write-Host "  http://localhost:5000/api/stats" -ForegroundColor Gray
Write-Host "  http://localhost:5000/api/health" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
python web_api.py
