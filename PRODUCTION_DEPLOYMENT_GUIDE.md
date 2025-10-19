# Production Deployment Guide
**Campervan Competitive Intelligence System**

**Version:** 2.0.0 (Production-Ready)
**Date:** October 14, 2025
**Status:** Ready for Production Deployment

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Deployment Steps](#deployment-steps)
6. [Verification & Testing](#verification--testing)
7. [Monitoring Setup](#monitoring-setup)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### ✅ Requirements Check

**System Requirements:**
- [ ] Python 3.10+ installed
- [ ] 4GB+ RAM available
- [ ] 10GB+ disk space available
- [ ] Internet connection (stable, 10Mbps+)
- [ ] Windows/Linux/MacOS

**Dependencies:**
- [ ] All Python packages installed (`pip install -r requirements.txt`)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] Database directory writable (`data/` folder)

**Accounts & API Keys:**
- [ ] Browserless.io API key (recommended for production)
- [ ] Environment variables configured
- [ ] Email/alerting credentials (if using notifications)

**Code Validation:**
- [ ] All tests pass (`python test_critical_fixes.py`)
- [ ] Tier 1 tests pass (`python test_all_tier1_competitors.py`)
- [ ] No critical linting errors
- [ ] Latest code from repository

---

## Environment Setup

### 1. Production Server Setup

**Recommended Specifications:**
```
CPU: 2+ cores
RAM: 4GB minimum, 8GB recommended
Storage: 50GB SSD
OS: Ubuntu 22.04 LTS, Windows Server 2022, or MacOS
```

### 2. Install Python & Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3-pip git -y

# Windows (via Chocolatey)
choco install python git

# MacOS (via Homebrew)
brew install python@3.10 git
```

### 3. Clone Repository & Install Dependencies

```bash
# Clone repository
git clone https://github.com/your-org/campervan-monitor.git
cd campervan-monitor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 4. Create Required Directories

```bash
# Create data directories
mkdir -p data/backups
mkdir -p data/screenshots
mkdir -p data/html
mkdir -p data/metrics
mkdir -p logs
```

---

## Configuration

### 1. Environment Variables

Create `.env` file in project root:

```bash
# Environment Configuration
ENVIRONMENT=production

# Database Configuration
DATABASE_URL=sqlite:///data/campervan_intel.db

# Browserless Configuration (RECOMMENDED for production)
BROWSERLESS_API_KEY=your_api_key_here
BROWSERLESS_REGION=production-sfo

# Email Notifications (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL=alerts@yourcompany.com

# Scraping Configuration
SCRAPING_TIMEOUT=90000
MAX_CONCURRENT_SCRAPERS=5
ENABLE_PARALLEL=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 2. Production Configuration

The system uses `config/environments.py` for environment-specific settings.

**To use production configuration:**

```python
# Automatically loads production config when ENVIRONMENT=production
from config.environments import get_config

config = get_config()  # Loads PRODUCTION_CONFIG
```

**Production Settings:**
- Browserless.io enabled (cloud browsers)
- 5 concurrent scrapers
- 90-second timeout
- Caching enabled
- Screenshots disabled (save space)
- JSON logging enabled

### 3. Competitor Configuration

Review and update competitor configurations in `competitor_config.py`:

```python
TIER_1_COMPETITORS = [
    {
        "name": "Roadsurfer",
        "tier": 1,
        "urls": {
            "homepage": "https://roadsurfer.com/",
            "pricing": "https://roadsurfer.com/rv-rental/prices/",
            # ...
        }
    },
    # ... other competitors
]
```

**No changes needed unless:**
- Competitor URLs have changed
- Adding new competitors
- Customizing scraping behavior

---

## Database Setup

### 1. Initialize Database

```bash
# Run database initialization
python -c "from models import create_tables; create_tables()"
```

### 2. Create Database Indexes

```bash
# Create performance indexes
python -c "from database.optimization import create_database_indexes; create_database_indexes()"
```

### 3. Verify Database

```bash
# Check database stats
python -c "from database.optimization import print_database_stats; print_database_stats()"
```

### 4. Configure Automated Backups

Add to crontab (Linux/Mac) or Task Scheduler (Windows):

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/campervan-monitor && python -c "from database.optimization import backup_database; backup_database()"

# Weekly cleanup (delete old data, keep 90 days)
0 3 * * 0 cd /path/to/campervan-monitor && python -c "from database.optimization import cleanup_old_data; cleanup_old_data(days_to_keep=90)"

# Monthly database vacuum
0 4 1 * * cd /path/to/campervan-monitor && python -c "from database.optimization import vacuum_database; vacuum_database()"
```

---

## Deployment Steps

### Step 1: Prepare Production Environment

```bash
# 1. Set environment to production
export ENVIRONMENT=production  # Linux/Mac
set ENVIRONMENT=production     # Windows

# 2. Verify configuration
python -c "from config.environments import ConfigurationManager; ConfigurationManager.print_config()"

# 3. Validate configuration
python -c "from config.environments import ConfigurationManager; print(ConfigurationManager.validate_config(ConfigurationManager.get_config()))"
```

### Step 2: Run Initial Test Scrape

```bash
# Test single competitor
python -c "
from scrapers.tier1_scrapers import RoadsurferScraper
import asyncio

async def test():
    scraper = RoadsurferScraper(use_browserless=True)  # Use Browserless in production
    result = await scraper.scrape()
    print(f'Price: EUR{result.get(\"base_nightly_rate\")}/night')
    print(f'Completeness: {result.get(\"data_completeness_pct\")}%')

asyncio.run(test())
"
```

Expected output:
```
Price: EUR115.0/night
Completeness: 52.4%
```

### Step 3: Run Full Intelligence Gathering

```bash
# Run all Tier 1 competitors
python run_intelligence.py
```

Expected output:
```
[TARGET] Focused Intelligence Scrapers v2.0.0
Starting intelligence gathering...
Scraping 5 Tier 1 competitors...
[PASS] Roadsurfer: 52.4% complete
[PASS] McRent: 58.5% complete
[PASS] Goboony: 45.2% complete
[PASS] Yescapa: 53.7% complete
[PASS] Camperdays: 68.3% complete
Intelligence gathering complete: 5/5 successful
```

### Step 4: Verify Data in Database

```bash
# Check database stats
python -c "from database.optimization import print_database_stats; print_database_stats()"
```

Expected output:
```
============================================================
DATABASE STATISTICS
============================================================

Total Records: 5
Database Size: 2.5 MB

Records by Company:
  Roadsurfer: 1
  McRent: 1
  Goboony: 1
  Yescapa: 1
  Camperdays: 1
============================================================
```

### Step 5: Set Up Automated Scheduling

**Option A: Crontab (Linux/Mac)**

```bash
# Edit crontab
crontab -e

# Add daily scraping at 6 AM
0 6 * * * cd /path/to/campervan-monitor && /path/to/venv/bin/python run_intelligence.py >> logs/cron.log 2>&1
```

**Option B: Task Scheduler (Windows)**

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Campervan Intelligence Gathering"
4. Trigger: Daily at 6:00 AM
5. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `run_intelligence.py`
   - Start in: `C:\path\to\campervan-monitor`
6. Save

**Option C: Systemd Service (Linux)**

Create `/etc/systemd/system/campervan-intelligence.service`:

```ini
[Unit]
Description=Campervan Intelligence Gathering
After=network.target

[Service]
Type=oneshot
User=youruser
WorkingDirectory=/path/to/campervan-monitor
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python run_intelligence.py

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/campervan-intelligence.timer`:

```ini
[Unit]
Description=Run Campervan Intelligence Daily
Requires=campervan-intelligence.service

[Timer]
OnCalendar=daily
OnCalendar=06:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable campervan-intelligence.timer
sudo systemctl start campervan-intelligence.timer
sudo systemctl status campervan-intelligence.timer
```

---

## Verification & Testing

### 1. Health Check

```bash
# Run health check
python health_check.py
```

Expected output:
```
System Health Check
===================
Database: OK
Browser: OK
API Keys: OK
Disk Space: OK (45GB free)
Recent Scrapes: OK (last: 5 minutes ago)
Data Quality: OK (avg: 55.6% completeness)

Overall Status: HEALTHY
```

### 2. Test All Competitors

```bash
# Run comprehensive test suite
python test_all_tier1_competitors.py
```

Expected: 100% success rate (5/5 pass)

### 3. Test Parallel Scraping

```bash
# Test parallel execution
python -c "
from scrapers.parallel_scraper import ParallelScraper
from competitor_config import TIER_1_COMPETITORS
import asyncio

async def test():
    parallel = ParallelScraper(max_concurrent=5)
    results = await parallel.scrape_all(TIER_1_COMPETITORS[:5])
    print(f'Scraped {len(results)} competitors in parallel')
    print(f'Success rate: {sum(1 for r in results if r.get(\"base_nightly_rate\")) / len(results) * 100}%')

asyncio.run(test())
"
```

Expected: ~15-20 seconds total (5x faster than sequential)

### 4. Verify Metrics Collection

```bash
# Check metrics
python -c "from monitoring.metrics_collector import get_metrics; get_metrics().print_summary()"
```

Expected output:
```
============================================================
SCRAPING METRICS SUMMARY
============================================================

Operations:
  Total Scrapes: 5
  Successful: 5 (100%)
  Partial: 0
  Failed: 0

Performance:
  Avg Duration: 12.4s
  Scrapes/min: 4.8

Data Extraction:
  Prices Extracted: 4 (80%)
  Reviews Extracted: 5 (100%)
============================================================
```

---

## Monitoring Setup

### 1. Log Files

**Location:** `logs/` directory

**Log Files:**
- `scraping.log` - Main scraping logs
- `errors.log` - Error logs only
- `cron.log` - Scheduled task logs

**Log Rotation:**

Create `/etc/logrotate.d/campervan-monitor`:

```
/path/to/campervan-monitor/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

### 2. Metrics Export

```bash
# Export metrics to file (for monitoring tools)
python -c "
from monitoring.metrics_collector import get_metrics
metrics = get_metrics()
metrics.save_to_file('data/metrics/latest.json')
"
```

Automate with cron:
```bash
# Export metrics every hour
0 * * * * cd /path/to/campervan-monitor && python -c "from monitoring.metrics_collector import get_metrics; get_metrics().save_to_file()"
```

### 3. Database Monitoring

```bash
# Monitor database size
watch -n 300 'python -c "from database.optimization import get_database_stats; stats = get_database_stats(); print(f\"Size: {stats[\"database_size_mb\"]} MB, Records: {stats[\"total_records\"]}\")"'
```

### 4. Alerting (Optional)

Create `alerts.py` for email notifications:

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'alerts@yourcompany.com'
    msg['To'] = 'your-email@yourcompany.com'

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-app-password')
        server.send_message(msg)

# Usage in scraping script
try:
    results = run_intelligence()
    if success_rate < 0.5:
        send_alert('Low Success Rate', f'Only {success_rate*100}% succeeded')
except Exception as e:
    send_alert('Scraping Failed', str(e))
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: "Browserless API Key Invalid"
**Symptoms:** 401 Unauthorized errors
**Solution:**
```bash
# Verify API key is set
echo $BROWSERLESS_API_KEY

# Test API key
curl -X GET https://production-sfo.browserless.io/status \
  -H "Authorization: Bearer $BROWSERLESS_API_KEY"
```

#### Issue 2: "Database Locked"
**Symptoms:** `sqlite3.OperationalError: database is locked`
**Solution:**
```bash
# Close all connections and vacuum
python -c "
from database.optimization import vacuum_database
vacuum_database()
"

# If persists, backup and recreate
python -c "from database.optimization import backup_database; backup_database()"
mv data/campervan_intel.db data/campervan_intel.db.old
python -c "from models import create_tables; create_tables()"
```

#### Issue 3: "Access Denied / Bot Detection"
**Symptoms:** HTTP 403 or captcha pages
**Solution:**
```python
# Enable Browserless.io (has better IP reputation)
use_browserless=True

# Or add delays and randomization
import random
await asyncio.sleep(random.uniform(2, 5))
```

#### Issue 4: "Low Data Completeness"
**Symptoms:** Completeness < 40%
**Solution:**
```bash
# Check which fields are missing
python -c "
from scrapers.tier1_scrapers import RoadsurferScraper
import asyncio

async def debug():
    scraper = RoadsurferScraper()
    result = await scraper.scrape()
    missing = [k for k, v in result.items() if v is None or v == 0]
    print(f'Missing fields: {missing}')

asyncio.run(debug())
"

# Review and update selectors in scrapers/tier1_scrapers.py
```

#### Issue 5: "Slow Performance"
**Symptoms:** Scraping takes > 30s per competitor
**Solution:**
```bash
# Enable parallel scraping
export ENABLE_PARALLEL=true

# Reduce timeout if competitors load quickly
export SCRAPING_TIMEOUT=60000

# Use Browserless (faster than local browser)
export BROWSERLESS_API_KEY=your_key
```

### Logs & Debugging

**Enable debug logging:**
```bash
export LOG_LEVEL=DEBUG
python run_intelligence.py
```

**Check recent errors:**
```bash
tail -n 50 logs/errors.log
```

**Monitor live scraping:**
```bash
tail -f logs/scraping.log | grep -E "(ERROR|WARNING|✅|❌)"
```

---

## Performance Tuning

### 1. Optimize Concurrent Scrapers

```python
# config/environments.py - adjust max_concurrent_scrapers
PRODUCTION_CONFIG = EnvironmentConfig(
    performance=PerformanceConfig(
        max_concurrent_scrapers=10,  # Increase for faster scraping
        enable_parallel_scraping=True
    )
)
```

**Guidelines:**
- 5 concurrent: Safe default (recommended)
- 10 concurrent: If you have good bandwidth
- 15+ concurrent: Only with Browserless premium

### 2. Optimize Database

```bash
# Run monthly maintenance
python -c "
from database.optimization import run_maintenance
run_maintenance(
    create_indexes=True,
    cleanup_data=True,  # Keep last 90 days
    backup=True,
    vacuum=True
)
"
```

### 3. Optimize Screenshots

```python
# Disable screenshots in production to save space
PRODUCTION_CONFIG = EnvironmentConfig(
    scraping=ScrapingConfig(
        save_screenshots=False,  # Only save on errors
        save_html=False
    )
)
```

---

## Security Best Practices

### 1. Secrets Management

**Never commit secrets to git:**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
```

**Use environment variables:**
```bash
# Store in system environment, not in code
export BROWSERLESS_API_KEY=xxx
export DATABASE_URL=xxx
```

### 2. Database Backup Encryption

```bash
# Encrypt backups
gpg --symmetric --cipher-algo AES256 data/backups/campervan_intel_20251014.db

# Decrypt when needed
gpg --decrypt data/backups/campervan_intel_20251014.db.gpg > restored.db
```

### 3. Access Control

```bash
# Restrict file permissions (Linux/Mac)
chmod 600 .env
chmod 600 data/*.db
chmod 700 data/backups
```

---

## Rollback Procedure

If deployment fails:

### 1. Stop Automated Tasks

```bash
# Linux: Disable cron
crontab -e  # Comment out campervan-monitor lines

# Or stop systemd timer
sudo systemctl stop campervan-intelligence.timer

# Windows: Disable Task Scheduler task
```

### 2. Restore Previous Database

```bash
# List backups
ls -lh data/backups/

# Restore from backup
cp data/backups/campervan_intel_YYYYMMDD.db data/campervan_intel.db

# Or restore from compressed backup
gunzip -c data/backups/campervan_intel_YYYYMMDD.db.gz > data/campervan_intel.db
```

### 3. Revert Code Changes

```bash
# Git revert to previous version
git log --oneline  # Find previous commit
git revert HEAD    # Or specific commit hash
```

---

## Post-Deployment

### Week 1 Checklist

- [ ] Monitor daily scraping success rate (target: 80%+)
- [ ] Review data completeness (target: 55%+)
- [ ] Check disk space usage
- [ ] Verify backups are working
- [ ] Review logs for errors
- [ ] Test dashboard (if deployed)

### Week 2-4 Checklist

- [ ] Analyze data quality trends
- [ ] Fine-tune selectors if needed
- [ ] Optimize performance based on metrics
- [ ] Implement any missing features
- [ ] Train team on operations

---

## Support & Contacts

**Documentation:**
- Production Plan: `PRODUCTION_READY_PLAN.md`
- Implementation Guide: `IMPLEMENTATION_GUIDE.md`
- Test Results: `TIER1_TEST_RESULTS.md`
- Operational Runbook: `OPERATIONAL_RUNBOOK.md`

**Issue Tracking:**
- GitHub Issues: https://github.com/your-org/campervan-monitor/issues

**Emergency Contacts:**
- Development Team: dev-team@yourcompany.com
- DevOps: devops@yourcompany.com

---

## Conclusion

Following this guide will result in a production-ready deployment of the Campervan Competitive Intelligence System.

**Expected Results:**
- ✅ Daily automated scraping of 5 Tier 1 competitors
- ✅ 80%+ price extraction accuracy
- ✅ 100% review extraction
- ✅ 55%+ data completeness average
- ✅ ~15-20 seconds total scraping time (parallel)
- ✅ Automated backups and maintenance
- ✅ Comprehensive monitoring and logging

**System is ready for production use.**

---

**Last Updated:** October 14, 2025
**Version:** 2.0.0 (Production-Ready)
