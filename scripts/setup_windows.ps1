# Windows Setup Script for Campervan Price Monitor
# Run with: .\scripts\setup_windows.ps1

Write-Host "🚐 Campervan Price Monitor - Windows Setup" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check Python
Write-Host "`n1️⃣ Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python not found! Install from python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`n2️⃣ Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ⚠️  Virtual environment exists, skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "   ✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n3️⃣ Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "   ✅ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "`n4️⃣ Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "   ✅ Dependencies installed" -ForegroundColor Green

# Install Playwright browsers
Write-Host "`n5️⃣ Installing Playwright browsers..." -ForegroundColor Yellow
python -m playwright install chromium
Write-Host "   ✅ Playwright Chromium installed" -ForegroundColor Green

# Initialize database
Write-Host "`n6️⃣ Initializing database..." -ForegroundColor Yellow
python -c "from database.models import init_database; init_database()"
Write-Host "   ✅ Database initialized" -ForegroundColor Green

# Create directories
Write-Host "`n7️⃣ Creating data directories..." -ForegroundColor Yellow
$directories = @("logs", "data\screenshots", "data\html")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "   ✅ Directories created" -ForegroundColor Green

# Summary
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "   1. Review .env file for API configuration" -ForegroundColor White
Write-Host "   2. Test: python campervan_price_monitor.py" -ForegroundColor White
Write-Host "   3. Run dashboard: streamlit run dashboard\app.py" -ForegroundColor White
Write-Host "   4. Run tests: pytest tests\ -v" -ForegroundColor White
Write-Host "`n🚀 Happy monitoring!" -ForegroundColor Cyan
