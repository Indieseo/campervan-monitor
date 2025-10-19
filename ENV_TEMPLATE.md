# Environment Configuration Template

Copy this content to a new file named `.env` in the project root:

```bash
# =====================================================
# CAMPERVAN INTELLIGENCE SYSTEM - ENVIRONMENT CONFIGURATION
# =====================================================

# BROWSERLESS.IO
BROWSERLESS_API_KEY=your_key_here
BROWSERLESS_REGION=production-sfo
USE_BROWSERLESS=true

# SCRAPING
SCRAPING_TIMEOUT=60000
SCRAPING_DELAY=2
MAX_RETRIES=3
MAX_CONCURRENT_SCRAPERS=3

# EMAIL ALERTS (Gmail)
ENABLE_EMAIL_ALERTS=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_RECIPIENTS=recipient@example.com

# SLACK ALERTS
ENABLE_SLACK_ALERTS=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK

# SMS ALERTS (Twilio)
ENABLE_SMS_ALERTS=false
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_FROM=+1234567890
SMS_RECIPIENTS=+1234567890

# DATA QUALITY
MIN_PRICE=20.0
MAX_PRICE=500.0
MAX_DISCOUNT=90.0
STALENESS_DAYS=7
RETENTION_DAYS=90

# LOGGING
LOG_LEVEL=INFO
```

See detailed instructions in the full `.env.example` file.


