# Operational Runbook
**Campervan Competitive Intelligence System**

**Version:** 2.0.0
**Last Updated:** October 14, 2025
**Purpose:** Day-to-day operations, maintenance, and troubleshooting guide

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Weekly Maintenance](#weekly-maintenance)
3. [Monthly Maintenance](#monthly-maintenance)
4. [Monitoring & Alerts](#monitoring--alerts)
5. [Common Issues & Solutions](#common-issues--solutions)
6. [Emergency Procedures](#emergency-procedures)
7. [Performance Optimization](#performance-optimization)
8. [Data Quality Checks](#data-quality-checks)

---

## Daily Operations

### Morning Routine (15 minutes)

#### 1. Check System Health

```bash
python health_check.py
```

**Expected Output:**
```
System Health Check
===================
Database: OK
Browser: OK
Recent Scrapes: OK
Data Quality: OK
Overall Status: HEALTHY
```

**Action if NOT healthy:**
- Check specific failed component
- Review error logs: `tail -n 100 logs/errors.log`
- Follow troubleshooting steps (see below)

#### 2. Review Latest Scraping Results

```bash
python -c "
from database.optimization import get_database_stats
stats = get_database_stats()
print(f'Latest: {stats[\"newest_record\"]}')
print(f'Total Records: {stats[\"total_records\"]}')
"
```

**Expected:**
- Latest scrape within last 24 hours
- 5 new records per day (one per Tier 1 competitor)

**Action if stale:**
- Check automated task (cron/scheduler)
- Run manual scrape: `python run_intelligence.py`

#### 3. Check Data Quality Metrics

```bash
python -c "
from monitoring.metrics_collector import get_metrics
metrics = get_metrics()
summary = metrics.get_summary()
print(f'Success Rate: {summary[\"success_rate\"]*100:.1f}%')
print(f'Price Extraction: {summary[\"price_extraction_rate\"]*100:.1f}%')
print(f'Avg Completeness: {summary.get(\"avg_data_completeness\", 0):.1f}%')
"
```

**Expected:**
- Success Rate: 80%+
- Price Extraction: 75%+
- Avg Completeness: 50%+

**Action if below targets:**
- See "Data Quality Issues" section
- Review competitor-specific issues

#### 4. Check for Alerts

```bash
# Check error log for today
tail -n 50 logs/errors.log | grep $(date +%Y-%m-%d)
```

**No output = no errors (good!)**

**If errors present:**
- Review error messages
- Follow troubleshooting guide
- Document any new issues

---

## Weekly Maintenance

### Every Monday (30 minutes)

#### 1. Review Weekly Summary

```bash
python -c "
from database.optimization import get_database_stats
from monitoring.metrics_collector import get_metrics

# Database stats
db_stats = get_database_stats()
print('=== WEEKLY DATABASE SUMMARY ===')
print(f'Total Records: {db_stats[\"total_records\"]}')
print(f'Database Size: {db_stats[\"database_size_mb\"]:.2f} MB')
print(f'Date Range: {db_stats[\"oldest_record\"]} to {db_stats[\"newest_record\"]}')

# Company breakdown
print('\n=== RECORDS BY COMPANY ===')
for company, count in sorted(db_stats[\"company_counts\"].items()):
    print(f'{company}: {count}')

# Metrics
metrics = get_metrics()
summary = metrics.get_summary()
print('\n=== PERFORMANCE METRICS ===')
print(f'Success Rate: {summary[\"success_rate\"]*100:.1f}%')
print(f'Avg Duration: {summary[\"avg_duration_seconds\"]:.1f}s')
print(f'Price Extraction: {summary[\"price_extraction_rate\"]*100:.1f}%')
"
```

#### 2. Export Weekly Report

```bash
# Export metrics to file
python -c "
from monitoring.metrics_collector import get_metrics
from datetime import datetime

metrics = get_metrics()
metrics.save_to_file(f'data/metrics/weekly_report_{datetime.now().strftime(\"%Y%m%d\")}.json')
"
```

#### 3. Verify Backups

```bash
# List recent backups
ls -lh data/backups/ | head -n 10

# Check last backup date
ls -t data/backups/ | head -n 1
```

**Expected:**
- At least 7 backups (one per day)
- Most recent within last 24 hours

**Action if missing:**
- Run manual backup: `python -c "from database.optimization import backup_database; backup_database()"`
- Check automated backup task

#### 4. Disk Space Check

```bash
# Check disk usage
df -h data/

# Check data directory size
du -sh data/
```

**Expected:**
- < 5GB for data directory
- > 10GB free disk space

**Action if low:**
- Run cleanup: `python -c "from database.optimization import cleanup_old_data; cleanup_old_data(days_to_keep=60)"`
- Review old screenshots: `ls -lh data/screenshots/ | wc -l`

#### 5. Review Competitor-Specific Issues

**Check each competitor's success rate:**

```bash
python -c "
from models import CompetitorPrice, get_session
from datetime import datetime, timedelta

session = get_session()
week_ago = datetime.now() - timedelta(days=7)

for company in ['Roadsurfer', 'McRent', 'Goboony', 'Yescapa', 'Camperdays']:
    count = session.query(CompetitorPrice).filter(
        CompetitorPrice.company_name == company,
        CompetitorPrice.scrape_timestamp >= week_ago
    ).count()

    print(f'{company}: {count} scrapes this week (expected: 7)')

session.close()
"
```

**Expected:** 7 scrapes per competitor per week

**Action if < 7:**
- Competitor may be failing consistently
- Review error logs for specific competitor
- Update selectors if needed

---

## Monthly Maintenance

### First Sunday of Month (1 hour)

#### 1. Run Full Maintenance

```bash
python -c "
from database.optimization import run_maintenance

results = run_maintenance(
    create_indexes=True,
    cleanup_data=True,
    backup=True,
    vacuum=True,
    days_to_keep=90
)

print('=== MAINTENANCE COMPLETE ===')
print(f'Indexes Created: {results[\"indexes_created\"]}')
print(f'Records Deleted: {results.get(\"records_deleted\", 0)}')
print(f'Backup Created: {results[\"backup_created\"]}')
print(f'Database Vacuumed: {results[\"vacuumed\"]}')
print(f'Duration: {results[\"duration\"]:.2f}s')
"
```

#### 2. Performance Review

```bash
python -c "
from monitoring.metrics_collector import ScrapeMetrics
import json

# Load monthly metrics (if saved)
try:
    with open('data/metrics/monthly_metrics.json') as f:
        metrics = json.load(f)
    print('=== MONTHLY PERFORMANCE ===')
    print(f'Total Scrapes: {metrics[\"scrapes_total\"]}')
    print(f'Success Rate: {metrics[\"success_rate\"]*100:.1f}%')
    print(f'Avg Duration: {metrics[\"avg_duration_seconds\"]:.1f}s')
    print(f'Price Extraction: {metrics[\"price_extraction_rate\"]*100:.1f}%')
except FileNotFoundError:
    print('No monthly metrics file found')
"
```

#### 3. Competitor URL Validation

```bash
# Test all competitor URLs are still valid
python -c "
import requests
from competitor_config import TIER_1_COMPETITORS

print('=== URL VALIDATION ===')
for comp in TIER_1_COMPETITORS:
    try:
        response = requests.get(comp['urls']['homepage'], timeout=10)
        status = 'OK' if response.status_code == 200 else f'ERROR {response.status_code}'
        print(f'{comp[\"name\"]}: {status}')
    except Exception as e:
        print(f'{comp[\"name\"]}: ERROR - {str(e)}')
"
```

#### 4. Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update if needed (test in staging first!)
# pip install --upgrade package_name
```

#### 5. Generate Monthly Report

```bash
python -c "
from database.optimization import get_database_stats
from monitoring.metrics_collector import get_metrics
from datetime import datetime
import json

# Collect all data
db_stats = get_database_stats()
metrics_summary = get_metrics().get_summary()

report = {
    'date': datetime.now().isoformat(),
    'database': db_stats,
    'metrics': metrics_summary
}

# Save report
with open(f'data/metrics/monthly_report_{datetime.now().strftime(\"%Y%m\")}.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

print(f'Monthly report saved: monthly_report_{datetime.now().strftime(\"%Y%m\")}.json')
"
```

---

## Monitoring & Alerts

### Key Metrics to Monitor

#### 1. Success Rate
**Target:** 80%+
**Frequency:** Daily
**Command:**
```bash
python -c "from monitoring.metrics_collector import get_metrics; print(f'{get_metrics().get_summary()[\"success_rate\"]*100:.1f}%')"
```

**Alert if:** < 70% for 2+ consecutive days

#### 2. Price Extraction Rate
**Target:** 75%+
**Frequency:** Daily
**Command:**
```bash
python -c "from monitoring.metrics_collector import get_metrics; print(f'{get_metrics().get_summary()[\"price_extraction_rate\"]*100:.1f}%')"
```

**Alert if:** < 60% for 2+ consecutive days

#### 3. Database Size
**Target:** < 10GB
**Frequency:** Weekly
**Command:**
```bash
du -sh data/campervan_intel.db
```

**Alert if:** > 10GB or growing >1GB/week

#### 4. Scraping Duration
**Target:** < 20s per competitor
**Frequency:** Weekly
**Command:**
```bash
python -c "from monitoring.metrics_collector import get_metrics; print(f'{get_metrics().get_summary()[\"avg_duration_seconds\"]:.1f}s')"
```

**Alert if:** > 30s average

#### 5. Data Freshness
**Target:** < 24 hours
**Frequency:** Daily
**Command:**
```bash
python -c "from database.optimization import get_database_stats; from datetime import datetime; stats = get_database_stats(); print(f'Last: {stats[\"newest_record\"]} ({(datetime.now() - stats[\"newest_record\"]).total_seconds()/3600:.1f}h ago)')"
```

**Alert if:** > 36 hours

### Setting Up Automated Alerts

**Email Alert Script** (`send_alert.py`):

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from monitoring.metrics_collector import get_metrics
from datetime import datetime

def send_metrics_alert():
    metrics = get_metrics().get_summary()

    # Check thresholds
    alerts = []
    if metrics['success_rate'] < 0.7:
        alerts.append(f"Low success rate: {metrics['success_rate']*100:.1f}%")
    if metrics['price_extraction_rate'] < 0.6:
        alerts.append(f"Low price extraction: {metrics['price_extraction_rate']*100:.1f}%")

    if not alerts:
        return  # No alerts needed

    # Send email
    msg = MIMEMultipart()
    msg['Subject'] = f'Campervan Monitor Alert - {datetime.now().strftime(\"%Y-%m-%d\")}'
    msg['From'] = 'alerts@yourcompany.com'
    msg['To'] = 'team@yourcompany.com'

    body = "\\n".join(alerts)
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-app-password')
        server.send_message(msg)

if __name__ == '__main__':
    send_metrics_alert()
```

**Add to cron:**
```bash
# Check daily at 10 AM
0 10 * * * cd /path/to/campervan-monitor && python send_alert.py
```

---

## Common Issues & Solutions

### Issue 1: Scraping Failed for All Competitors

**Symptoms:**
- All scrapers returning errors
- Success rate 0%

**Diagnosis:**
```bash
# Check internet connection
ping google.com

# Check Browserless API
curl https://production-sfo.browserless.io/status

# Check browser installation
playwright install --dry-run chromium
```

**Solutions:**
1. Network issue: Check internet connection and firewall
2. Browserless API down: Switch to local browser temporarily
3. Browser not installed: Run `playwright install chromium`

### Issue 2: Low Price Extraction Rate

**Symptoms:**
- Prices showing as 0 or None
- Price extraction rate < 60%

**Diagnosis:**
```bash
# Test single competitor with debug output
python -c "
import asyncio
import logging
logging.basicConfig(level=logging.DEBUG)
from scrapers.tier1_scrapers import RoadsurferScraper

async def test():
    scraper = RoadsurferScraper()
    result = await scraper.scrape()
    print(f'Price: {result.get(\"base_nightly_rate\")}')

asyncio.run(test())
"
```

**Solutions:**
1. **Website structure changed:** Update selectors in `scrapers/tier1_scrapers.py`
2. **Timeout too short:** Increase SCRAPING_TIMEOUT in config
3. **Bot detection:** Enable Browserless.io or add delays

### Issue 3: Database Growing Too Fast

**Symptoms:**
- Database > 10GB
- Disk space warnings

**Diagnosis:**
```bash
# Check database size
du -sh data/campervan_intel.db

# Check record count
python -c "from database.optimization import get_database_stats; print(f'{get_database_stats()[\"total_records\"]:,} records')"
```

**Solutions:**
1. **Old data:** Run cleanup
   ```bash
   python -c "from database.optimization import cleanup_old_data; cleanup_old_data(days_to_keep=60)"
   ```

2. **Not vacuumed:** Run vacuum
   ```bash
   python -c "from database.optimization import vacuum_database; vacuum_database()"
   ```

3. **Too many screenshots:** Disable or delete old ones
   ```bash
   # Delete screenshots older than 30 days
   find data/screenshots/ -type f -mtime +30 -delete
   ```

### Issue 4: Specific Competitor Always Failing

**Symptoms:**
- One competitor consistently returns errors
- Others working fine

**Diagnosis:**
```bash
# Test specific competitor
python -c "
import asyncio
from scrapers.tier1_scrapers import RoadsurferScraper  # Change to failing competitor

async def test():
    scraper = RoadsurferScraper()
    try:
        result = await scraper.scrape()
        print(f'Success: {result}')
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(test())
"
```

**Solutions:**
1. **URL changed:** Check and update competitor URLs in `competitor_config.py`
2. **Selectors outdated:** Review and update selectors in scraper class
3. **Bot detection:** Add delays or switch to Browserless
4. **Site down:** Check if website is accessible: `curl -I https://competitor-url.com`

### Issue 5: Slow Performance

**Symptoms:**
- Scraping takes > 30s per competitor
- Total time > 2 minutes for all 5

**Diagnosis:**
```bash
# Check average duration
python -c "from monitoring.metrics_collector import get_metrics; print(f'{get_metrics().get_summary()[\"avg_duration_seconds\"]:.1f}s')"

# Test parallel vs sequential
time python run_intelligence.py
```

**Solutions:**
1. **Not using parallel:** Enable parallel scraping
   ```bash
   export ENABLE_PARALLEL=true
   ```

2. **Local browser slow:** Switch to Browserless.io
   ```bash
   export BROWSERLESS_API_KEY=your_key
   ```

3. **Too many screenshots:** Disable screenshots
   ```python
   # In config/environments.py
   save_screenshots=False
   ```

4. **Network slow:** Check bandwidth, reduce concurrent scrapers

### Issue 6: Missing Data Fields

**Symptoms:**
- Data completeness < 40%
- Many None values in database

**Diagnosis:**
```bash
# Check which fields are missing
python -c "
import asyncio
from scrapers.tier1_scrapers import RoadsurferScraper

async def test():
    scraper = RoadsurferScraper()
    result = await scraper.scrape()
    missing = [k for k, v in result.items() if v is None or v == 0]
    print(f'Missing {len(missing)} fields: {missing[:10]}')

asyncio.run(test())
"
```

**Solutions:**
1. **Selectors need updating:** Review HTML and update extraction logic
2. **Timeout too short:** Increase wait times for dynamic content
3. **Not visiting enough pages:** Ensure multi-page scraping is enabled
4. **Expected for competitor:** Some competitors don't publish all data (normal)

---

## Emergency Procedures

### Emergency 1: System Down / Not Scraping

**Priority:** HIGH
**Response Time:** 1 hour

**Steps:**
1. Check system health: `python health_check.py`
2. Review error logs: `tail -n 100 logs/errors.log`
3. Test manual scrape: `python run_intelligence.py`
4. If still failing:
   - Restart server/container
   - Check automated task (cron/scheduler)
   - Verify API keys and config
5. If critical, use backup data until fixed

### Emergency 2: Database Corruption

**Priority:** CRITICAL
**Response Time:** 30 minutes

**Steps:**
1. Stop all scraping immediately
2. Backup current database (even if corrupted):
   ```bash
   cp data/campervan_intel.db data/campervan_intel.db.corrupted
   ```
3. Try vacuum and repair:
   ```bash
   sqlite3 data/campervan_intel.db "PRAGMA integrity_check;"
   ```
4. If corruption confirmed, restore from backup:
   ```bash
   cp data/backups/latest_backup.db.gz .
   gunzip latest_backup.db.gz
   mv latest_backup.db data/campervan_intel.db
   ```
5. Verify restore: `python -c "from database.optimization import get_database_stats; print(get_database_stats())"`
6. Resume scraping

### Emergency 3: All Competitors Blocked / Bot Detection

**Priority:** HIGH
**Response Time:** 2 hours

**Steps:**
1. Confirm it's bot detection (403/captcha pages)
2. Immediate mitigation:
   - Add longer delays (2-5 seconds between requests)
   - Reduce concurrent scrapers to 1
   - Rotate user agents
3. Medium-term solution:
   - Enable Browserless.io premium (residential IPs)
   - Implement request throttling
   - Add randomization to scraping patterns
4. If persistent, pause scraping for 24 hours

### Emergency 4: Disk Space Full

**Priority:** HIGH
**Response Time:** 1 hour

**Steps:**
1. Check disk usage: `df -h`
2. Immediate cleanup:
   ```bash
   # Delete old screenshots
   rm -rf data/screenshots/*

   # Delete old HTML saves
   rm -rf data/html/*

   # Cleanup old database records
   python -c "from database.optimization import cleanup_old_data; cleanup_old_data(days_to_keep=30)"

   # Vacuum database
   python -c "from database.optimization import vacuum_database; vacuum_database()"
   ```
3. If still critical, delete old backups (keep last 7 only)
4. Plan for storage expansion

---

## Performance Optimization

### Optimization 1: Enable Parallel Scraping

**Impact:** 5x faster (60s → 12s)

```bash
# Enable in environment
export ENABLE_PARALLEL=true

# Test performance
time python run_intelligence.py
```

### Optimization 2: Use Browserless.io

**Impact:** 2x faster + better reliability

```bash
# Configure Browserless
export BROWSERLESS_API_KEY=your_key
export BROWSERLESS_REGION=production-sfo

# Test
python -c "
import asyncio
from scrapers.tier1_scrapers import RoadsurferScraper

async def test():
    scraper = RoadsurferScraper(use_browserless=True)
    result = await scraper.scrape()
    print(f'Success with Browserless')

asyncio.run(test())
"
```

### Optimization 3: Optimize Database

**Impact:** 5-10x faster queries

```bash
# Create indexes
python -c "from database.optimization import create_database_indexes; create_database_indexes()"

# Vacuum regularly
python -c "from database.optimization import vacuum_database; vacuum_database()"
```

### Optimization 4: Disable Screenshots

**Impact:** Saves 100MB+ per month, 10% faster

```python
# In config/environments.py
PRODUCTION_CONFIG = EnvironmentConfig(
    scraping=ScrapingConfig(
        save_screenshots=False,
        save_html=False
    )
)
```

---

## Data Quality Checks

### Daily Quality Check

```bash
python -c "
from models import CompetitorPrice, get_session
from datetime import datetime, timedelta

session = get_session()
yesterday = datetime.now() - timedelta(days=1)

# Get yesterday's scrapes
scrapes = session.query(CompetitorPrice).filter(
    CompetitorPrice.scrape_timestamp >= yesterday
).all()

print(f'=== YESTERDAY\'S DATA QUALITY ===')
print(f'Total Scrapes: {len(scrapes)}')

# Check price extraction
with_prices = [s for s in scrapes if s.base_nightly_rate and s.base_nightly_rate > 0]
print(f'With Prices: {len(with_prices)}/{len(scrapes)} ({len(with_prices)/len(scrapes)*100:.1f}%)')

# Check reviews
with_reviews = [s for s in scrapes if s.customer_review_avg]
print(f'With Reviews: {len(with_reviews)}/{len(scrapes)} ({len(with_reviews)/len(scrapes)*100:.1f}%)')

# Check completeness
avg_completeness = sum(s.data_completeness_pct for s in scrapes) / len(scrapes) if scrapes else 0
print(f'Avg Completeness: {avg_completeness:.1f}%')

session.close()
"
```

**Expected:**
- Total Scrapes: 5
- With Prices: 4-5 (80-100%)
- With Reviews: 5 (100%)
- Avg Completeness: 50-60%

**Action if below:**
- Review specific failures
- Update selectors
- Check for website changes

---

## Quick Reference Commands

### Health & Status
```bash
# System health
python health_check.py

# Database stats
python -c "from database.optimization import print_database_stats; print_database_stats()"

# Metrics summary
python -c "from monitoring.metrics_collector import get_metrics; get_metrics().print_summary()"
```

### Manual Operations
```bash
# Run scraping manually
python run_intelligence.py

# Test single competitor
python -c "from scrapers.tier1_scrapers import RoadsurferScraper; import asyncio; asyncio.run(RoadsurferScraper().scrape())"

# Run tests
python test_critical_fixes.py
python test_all_tier1_competitors.py
```

### Maintenance
```bash
# Backup database
python -c "from database.optimization import backup_database; backup_database()"

# Cleanup old data
python -c "from database.optimization import cleanup_old_data; cleanup_old_data(days_to_keep=90)"

# Vacuum database
python -c "from database.optimization import vacuum_database; vacuum_database()"

# Full maintenance
python -c "from database.optimization import run_maintenance; run_maintenance()"
```

### Debugging
```bash
# View recent errors
tail -n 50 logs/errors.log

# Monitor live
tail -f logs/scraping.log

# Enable debug logging
export LOG_LEVEL=DEBUG
python run_intelligence.py
```

---

## Escalation Contacts

**Level 1 - Operations Team**
- Email: ops@yourcompany.com
- Handles: Daily monitoring, routine issues

**Level 2 - Development Team**
- Email: dev@yourcompany.com
- Handles: Scraper issues, selector updates

**Level 3 - DevOps / Infrastructure**
- Email: devops@yourcompany.com
- Handles: Server issues, deployment problems

**Level 4 - Emergency / On-Call**
- Phone: +1-XXX-XXX-XXXX
- Handles: Critical system failures

---

## Appendix: Monthly Checklist

- [ ] Run full maintenance (`run_maintenance()`)
- [ ] Review monthly metrics
- [ ] Check competitor URL validity
- [ ] Review and update dependencies
- [ ] Generate monthly report
- [ ] Verify all backups exist and valid
- [ ] Review disk space usage
- [ ] Update documentation if needed
- [ ] Review and address any recurring issues
- [ ] Plan optimizations for next month

---

**End of Runbook**

**Remember:** This system is designed to be resilient and self-healing. Most issues resolve themselves or have automated fallbacks. Refer to this runbook for guidance, and escalate if needed.

---

**Last Updated:** October 14, 2025
**Version:** 2.0.0
