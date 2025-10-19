# Windows Task Scheduler Setup Script
# Creates automated daily intelligence gathering

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Campervan Intelligence - Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  WARNING: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "   Some features may not work. Run PowerShell as Admin for full functionality." -ForegroundColor Yellow
    Write-Host ""
}

# Configuration
$projectPath = "C:\Projects\campervan-monitor"
$taskName = "CampervanIntel_Daily"
$scriptPath = "$projectPath\run_daily.bat"
$logPath = "$projectPath\logs"

# Verify paths exist
if (-not (Test-Path $projectPath)) {
    Write-Host "❌ ERROR: Project path not found: $projectPath" -ForegroundColor Red
    Write-Host "   Please update the `$projectPath variable in this script" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ ERROR: run_daily.bat not found: $scriptPath" -ForegroundColor Red
    exit 1
}

# Create logs directory if needed
if (-not (Test-Path $logPath)) {
    New-Item -ItemType Directory -Path $logPath -Force | Out-Null
    Write-Host "✅ Created logs directory" -ForegroundColor Green
}

Write-Host "📋 Task Configuration:" -ForegroundColor Cyan
Write-Host "   Name: $taskName" -ForegroundColor White
Write-Host "   Script: $scriptPath" -ForegroundColor White
Write-Host "   Schedule: Daily at 6:00 AM" -ForegroundColor White
Write-Host ""

# Remove existing task if present
$existingTask = schtasks /query /tn $taskName 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "🔄 Removing existing task..." -ForegroundColor Yellow
    schtasks /delete /tn $taskName /f | Out-Null
}

# Create scheduled task
Write-Host "📅 Creating scheduled task..." -ForegroundColor Cyan

$action = New-ScheduledTaskAction -Execute $scriptPath
$trigger = New-ScheduledTaskTrigger -Daily -At "06:00AM"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Daily campervan competitive intelligence gathering" -Force | Out-Null
    
    Write-Host "✅ Task created successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Display task info
    Write-Host "📊 Task Details:" -ForegroundColor Cyan
    schtasks /query /tn $taskName /fo LIST /v | Select-String "TaskName|Status|Next Run Time|Last Run Time"
    
    Write-Host ""
    Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📌 What happens now:" -ForegroundColor Cyan
    Write-Host "   • Intelligence gathering runs daily at 6:00 AM" -ForegroundColor White
    Write-Host "   • Results saved to database automatically" -ForegroundColor White
    Write-Host "   • Logs stored in: $logPath" -ForegroundColor White
    Write-Host "   • Dashboard updates with fresh data" -ForegroundColor White
    Write-Host ""
    Write-Host "🧪 To test immediately:" -ForegroundColor Cyan
    Write-Host "   schtasks /run /tn $taskName" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🗑️  To remove task:" -ForegroundColor Cyan
    Write-Host "   schtasks /delete /tn $taskName /f" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 To view all tasks:" -ForegroundColor Cyan
    Write-Host "   schtasks /query | findstr Campervan" -ForegroundColor Yellow
    Write-Host ""
    
    # Ask if user wants to test now
    $testNow = Read-Host "Do you want to test the task now? (Y/N)"
    if ($testNow -eq 'Y' -or $testNow -eq 'y') {
        Write-Host ""
        Write-Host "🧪 Running test..." -ForegroundColor Cyan
        schtasks /run /tn $taskName
        Write-Host "✅ Test started! Check logs folder for results" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ ERROR: Failed to create task" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Try running PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup complete! Your system is now automated." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
