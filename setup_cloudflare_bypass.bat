@echo off
REM Cloudflare Bypass Setup Script
REM Created: October 17, 2025
REM Purpose: Quick setup for Puppeteer + Browserless bypass system

echo ========================================
echo  Cloudflare Bypass Setup
echo ========================================
echo.

REM Check for Docker
echo [1/6] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [!] Docker not found. Please install Docker Desktop for Windows.
    echo     Download: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [✓] Docker found

REM Check for Node.js
echo.
echo [2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [!] Node.js not found. Please install Node.js.
    echo     Download: https://nodejs.org/
    pause
    exit /b 1
)
echo [✓] Node.js found

REM Create docker-compose file
echo.
echo [3/6] Creating docker-compose configuration...
(
echo version: '3.8'
echo services:
echo   browserless:
echo     image: browserless/chrome:latest
echo     ports:
echo       - "3000:3000"
echo     environment:
echo       - MAX_CONCURRENT_SESSIONS=5
echo       - CONNECTION_TIMEOUT=300000
echo       - ENABLE_CORS=true
echo       - PREBOOT_CHROME=true
echo     volumes:
echo       - ./browser-data:/data
echo     restart: unless-stopped
echo.
echo   flaresolverr:
echo     image: ghcr.io/flaresolverr/flaresolverr:latest
echo     ports:
echo       - "8191:8191"
echo     environment:
echo       - LOG_LEVEL=info
echo       - LOG_HTML=false
echo       - CAPTCHA_SOLVER=none
echo     restart: unless-stopped
) > docker-compose-browserless.yml
echo [✓] docker-compose-browserless.yml created

REM Install Node.js packages
echo.
echo [4/6] Installing Node.js packages...
if not exist package.json (
    echo [i] Initializing npm...
    call npm init -y
)
echo [i] Installing puppeteer and plugins...
call npm install puppeteer puppeteer-extra puppeteer-extra-plugin-stealth puppeteer-extra-plugin-adblocker --save
echo [✓] Node.js packages installed

REM Install Python packages
echo.
echo [5/6] Installing Python packages...
echo [i] Installing pyppeteer...
call pip install pyppeteer --quiet
echo [✓] Python packages installed

REM Start Docker containers
echo.
echo [6/6] Starting Docker containers...
echo [i] This may take a few minutes on first run...
docker-compose -f docker-compose-browserless.yml pull
docker-compose -f docker-compose-browserless.yml up -d
echo [✓] Docker containers started

REM Wait for services to be ready
echo.
echo [i] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo.
echo [✓] Checking service health...
docker ps | findstr browserless >nul 2>&1
if errorlevel 1 (
    echo [!] Browserless container not running
) else (
    echo [✓] Browserless running on http://localhost:3000
)

docker ps | findstr flaresolverr >nul 2>&1
if errorlevel 1 (
    echo [!] FlareSolverr container not running
) else (
    echo [✓] FlareSolverr running on http://localhost:8191
)

REM Create test script
echo.
echo [i] Creating test script...
(
echo const puppeteer = require('puppeteer-extra'^);
echo const StealthPlugin = require('puppeteer-extra-plugin-stealth'^);
echo.
echo puppeteer.use(StealthPlugin(^)^);
echo.
echo ^(async (^) =^> {
echo     try {
echo         console.log('Connecting to Browserless...'^);
echo         const browser = await puppeteer.connect({
echo             browserWSEndpoint: 'ws://localhost:3000'
echo         }^);
echo.
echo         console.log('Opening page...'^);
echo         const page = await browser.newPage(^);
echo.
echo         console.log('Testing stealth on bot detection site...'^);
echo         await page.goto('https://bot.sannysoft.com/', {
echo             waitUntil: 'networkidle2'
echo         }^);
echo.
echo         await page.screenshot({ path: 'stealth-test.png', fullPage: true }^);
echo         console.log('✓ Screenshot saved: stealth-test.png'^);
echo.
echo         console.log('Testing Apollo Motorhomes...'^);
echo         await page.goto('https://apollocamper.com/', {
echo             waitUntil: 'networkidle2',
echo             timeout: 60000
echo         }^);
echo.
echo         await page.waitForTimeout(3000^);
echo.
echo         const content = await page.content(^);
echo         if ^(content.includes('Just a moment'^) ^|^| content.includes('Checking your browser'^)^) {
echo             console.log('⚠  Cloudflare challenge detected'^);
echo         } else {
echo             console.log('✓ No Cloudflare challenge!'^);
echo         }
echo.
echo         await page.screenshot({ path: 'apollo-test.png', fullPage: true }^);
echo         console.log('✓ Screenshot saved: apollo-test.png'^);
echo.
echo         await browser.close(^);
echo         console.log('✓ Test completed successfully!'^);
echo     } catch ^(error^) {
echo         console.error('✗ Test failed:', error.message^);
echo         process.exit(1^);
echo     }
echo }^)(^);
) > test_cloudflare_bypass.js
echo [✓] Test script created: test_cloudflare_bypass.js

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run test: node test_cloudflare_bypass.js
echo   2. View screenshots: stealth-test.png and apollo-test.png
echo   3. Check services: docker ps
echo.
echo Service URLs:
echo   - Browserless: http://localhost:3000
echo   - FlareSolverr: http://localhost:8191
echo.
echo To stop services:
echo   docker-compose -f docker-compose-browserless.yml down
echo.
echo For more info, see:
echo   - CLOUDFLARE_BYPASS_ADVANCED_PLAN.md
echo   - CLOUDFLARE_BYPASS_NEXT_STEPS.md
echo   - CLAUDE_CODE_CLOUDFLARE_ANALYSIS_PROMPT.md
echo.

pause




