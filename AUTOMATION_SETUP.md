# 🤖 Automated Daily Crawl Setup Guide

**Quick Start:** Double-click `setup_daily_crawl.bat` and follow the prompts!

---

## 🚀 Automatic Setup (Recommended)

### Step 1: Run Setup Script
```powershell
# Right-click and "Run as administrator"
setup_daily_crawl.bat
```

### Step 2: Choose Schedule
```
Choose your preferred schedule:
--------------------------------
1) Daily at 8:00 AM (Recommended)  ← Best for most users
2) Daily at 6:00 AM (Early bird)   ← For early morning reports
3) Daily at 10:00 AM (Late morning) ← After competitors update
4) Twice daily (8:00 AM and 6:00 PM) ← Maximum coverage
5) Custom time                      ← Your preferred time
6) Skip automation setup            ← Manual only
```

### Step 3: Done!
The system will automatically crawl competitors every day at your chosen time.

---

## 📋 What Gets Automated

### Daily Tasks (Automatic)
1. ✅ Launch browser(s)
2. ✅ Scrape all 8 Tier 1 competitors
3. ✅ Extract 35+ data points each
4. ✅ Save to database
5. ✅ Generate screenshots
6. ✅ Create HTML backups
7. ✅ Update metrics
8. ✅ Log results

### Your Tasks (Manual)
1. Review dashboard: `streamlit run dashboard/app.py`
2. Check logs: `logs\daily_crawl.log`
3. Act on insights: Pricing decisions, promotions, etc.

**Time Investment:** 5-10 minutes/day to review results

---

## 🔧 Manual Setup (Advanced)

### Option 1: Windows Task Scheduler GUI

**Step 1: Open Task Scheduler**
```
Press Win+R → type "taskschd.msc" → Enter
```

**Step 2: Create Basic Task**
```
Action → Create Basic Task
Name: "Campervan Competitive Crawl"
Description: "Daily competitive intelligence gathering"
```

**Step 3: Set Trigger**
```
Trigger: Daily
Start: [Today's date]
Recur every: 1 days
Time: 08:00:00 (or your preference)
```

**Step 4: Set Action**
```
Action: Start a program
Program/script: C:\Projects\campervan-monitor\run_daily_crawl_auto.bat
Start in: C:\Projects\campervan-monitor
```

**Step 5: Finish**
```
✓ Open Properties dialog when I click Finish
```

**Step 6: Advanced Settings**
```
General tab:
  ✓ Run whether user is logged on or not
  ✓ Run with highest privileges

Settings tab:
  ✓ Allow task to be run on demand
  ✓ If task fails, restart every: 1 hour
  ✓ Attempt to restart up to: 3 times
  □ Stop task if it runs longer than: (uncheck)
```

### Option 2: Command Line

**Create Task:**
```powershell
schtasks /create /tn "Campervan Competitive Crawl" /tr "C:\Projects\campervan-monitor\run_daily_crawl_auto.bat" /sc daily /st 08:00 /rl HIGHEST /f
```

**Verify Created:**
```powershell
schtasks /query /tn "Campervan Competitive Crawl"
```

---

## 📊 Monitoring Automation

### Check Task Status
```powershell
# View in Task Scheduler
taskschd.msc

# Or via command line
schtasks /query /tn "Campervan Competitive Crawl" /v /fo list
```

### View Execution History
```
Task Scheduler → Task Scheduler Library → "Campervan Competitive Crawl"
→ History tab (enable if disabled)
```

### Check Logs
```powershell
# Daily crawl logs
type logs\daily_crawl.log

# Error logs
type logs\daily_crawl_errors.log

# Full system logs
type logs\intel_2025-10-16.log
```

---

## 🎯 Task Management

### Test Run Immediately
```powershell
# Trigger scheduled task now
schtasks /run /tn "Campervan Competitive Crawl"

# Or run manually
python live_crawl_demo.py
```

### Disable Task Temporarily
```powershell
schtasks /change /tn "Campervan Competitive Crawl" /disable
```

### Re-enable Task
```powershell
schtasks /change /tn "Campervan Competitive Crawl" /enable
```

### Delete Task
```powershell
schtasks /delete /tn "Campervan Competitive Crawl" /f
```

### Change Schedule Time
```powershell
# Delete and recreate with new time
schtasks /delete /tn "Campervan Competitive Crawl" /f
schtasks /create /tn "Campervan Competitive Crawl" /tr "C:\Projects\campervan-monitor\run_daily_crawl_auto.bat" /sc daily /st 10:00 /f
```

---

## 🐛 Troubleshooting

### Issue: Task doesn't run
**Possible causes:**
1. Computer is off/sleeping at scheduled time
2. Task Scheduler service stopped
3. Incorrect path in task action

**Solutions:**
```powershell
# 1. Check Task Scheduler service
services.msc → Find "Task Scheduler" → Status should be "Running"

# 2. Verify task configuration
schtasks /query /tn "Campervan Competitive Crawl" /v /fo list

# 3. Run task manually to test
schtasks /run /tn "Campervan Competitive Crawl"

# 4. Check logs for errors
type logs\daily_crawl_errors.log
```

### Issue: Task runs but fails
**Check execution log:**
```powershell
type logs\daily_crawl.log
```

**Common problems:**
- Python not in PATH → Use full path in bat file
- Virtual env not activated → Check bat file
- Missing dependencies → Run `pip install -r requirements.txt`

### Issue: Task runs as different user
**Solution:** Re-create task with current user account
```
Task Properties → General → "Run whether user is logged on or not"
→ Enter your Windows password when prompted
```

### Issue: No log output
**Verify log directory exists:**
```powershell
mkdir logs
```

**Check bat file redirects correctly:**
```batch
python live_crawl_demo.py >> logs\daily_crawl.log 2>&1
```

---

## 📧 Email Notifications (Optional)

### Setup Email Alerts on Failure

**Create notification script: `send_alert.ps1`**
```powershell
param($TaskName, $Status)

$From = "crawl@yourcompany.com"
$To = "you@yourcompany.com"
$Subject = "Campervan Crawl $Status"
$Body = "Task $TaskName completed with status: $Status at $(Get-Date)"
$SMTPServer = "smtp.gmail.com"
$SMTPPort = 587

Send-MailMessage -From $From -To $To -Subject $Subject -Body $Body -SmtpServer $SMTPServer -Port $SMTPPort -UseSsl -Credential (Get-Credential)
```

**Add to Task Scheduler:**
```
Task Properties → Actions → Add
Action: Start a program
Program: powershell.exe
Arguments: -File "C:\Projects\campervan-monitor\send_alert.ps1" -TaskName "Campervan Competitive Crawl" -Status "Failed"
```

---

## 📊 Success Metrics

### Healthy Automation
- ✅ Task runs daily at scheduled time
- ✅ Completes in 10-15 minutes
- ✅ 7/8+ scrapers succeed
- ✅ Database updates with new data
- ✅ Logs show no critical errors

### Check Health Weekly
```powershell
# Run health check
python health_check.py

# View recent logs
Get-Content logs\daily_crawl.log -Tail 50

# Check database size (should grow daily)
Get-ChildItem database\campervan_intelligence.db
```

---

## 🔄 Advanced Scheduling

### Run at Multiple Times
```powershell
# Morning crawl
schtasks /create /tn "Campervan Crawl - Morning" /tr "C:\Projects\campervan-monitor\run_daily_crawl_auto.bat" /sc daily /st 08:00 /f

# Evening crawl
schtasks /create /tn "Campervan Crawl - Evening" /tr "C:\Projects\campervan-monitor\run_daily_crawl_auto.bat" /sc daily /st 18:00 /f
```

### Run on Specific Days
```powershell
# Monday, Wednesday, Friday only
schtasks /create /tn "Campervan Crawl - MWF" /tr "C:\Projects\campervan-monitor\run_daily_crawl_auto.bat" /sc weekly /d MON,WED,FRI /st 08:00 /f
```

### Run Every N Hours
```powershell
# Every 6 hours
schtasks /create /tn "Campervan Crawl - 6hourly" /tr "C:\Projects\campervan-monitor\run_daily_crawl_auto.bat" /sc hourly /mo 6 /f
```

---

## 💡 Best Practices

### 1. **Choose Smart Timing**
- Run when competitors typically update (early morning)
- Avoid high-traffic hours for better scraping success
- Consider your dashboard review time

### 2. **Monitor First Week**
- Check logs daily first week
- Verify all scrapers work
- Adjust schedule if needed

### 3. **Keep PC On**
- Don't put PC to sleep during scheduled time
- Or use "Wake to run" option in task properties

### 4. **Regular Maintenance**
```powershell
# Weekly: Check logs for errors
type logs\daily_crawl.log | findstr "ERROR"

# Monthly: Review and archive logs
move logs\daily_crawl.log logs\archive\daily_crawl_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log

# Quarterly: Test manual run
python live_crawl_demo.py
```

---

## 🎉 Quick Verification

**After Setup, Verify Everything Works:**

### 1. Test Manual Run (2 minutes)
```powershell
python live_crawl_demo.py
```
✅ Should complete successfully

### 2. Test Scheduled Task (1 minute)
```powershell
schtasks /run /tn "Campervan Competitive Crawl"
```
✅ Should trigger and run

### 3. Check Output (1 minute)
```powershell
# Check log created
dir logs\daily_crawl.log

# Check database updated
python -c "from database.models import get_latest_prices; print(len(get_latest_prices()))"
```
✅ Should show recent data

### 4. Verify Schedule (30 seconds)
```powershell
schtasks /query /tn "Campervan Competitive Crawl"
```
✅ Should show "Ready" status

**All green?** You're good to go! 🚀

---

## 📞 Need Help?

### Common Questions

**Q: Can I run this on a server?**  
A: Yes! Works on Windows Server. Use same setup process.

**Q: What if my PC is off at scheduled time?**  
A: Task will run next time PC is on, or set "Run as soon as possible after scheduled start is missed"

**Q: How much data does it generate?**  
A: ~50MB per day (screenshots + HTML + database). Plan for 1.5GB/month.

**Q: Can I run this on Mac/Linux?**  
A: Use `cron` instead of Task Scheduler. Similar setup process.

**Q: How do I stop getting emails/notifications?**  
A: Disable or delete the notification action in Task Scheduler.

---

## 🔐 Security Considerations

### Credentials
- Scrapers don't store credentials
- No login required for public pricing
- Task runs with your Windows account

### Data Privacy
- All data stored locally
- No cloud transmission (unless using Browserless)
- Screenshots saved locally only

### Network Security
- Uses standard HTTPS
- No special firewall rules needed
- Same as browsing websites manually

---

**Your automation is ready! Sit back and let the system gather intelligence daily while you focus on strategic decisions!** 🎯






