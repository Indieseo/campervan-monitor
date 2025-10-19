"""
Centralized Configuration Management
Single source of truth for all system configuration
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.resolve()
DATABASE_DIR = BASE_DIR / "database"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"
EXPORTS_DIR = BASE_DIR / "exports"

# Ensure directories exist
for directory in [DATABASE_DIR, DATA_DIR, LOGS_DIR, CACHE_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data subdirectories
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
HTML_DIR = DATA_DIR / "html"
DAILY_SUMMARIES_DIR = DATA_DIR / "daily_summaries"

for directory in [SCREENSHOTS_DIR, HTML_DIR, DAILY_SUMMARIES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class DatabaseConfig:
    """Database configuration"""
    
    # Single source of truth for database path
    DATABASE_PATH = DATABASE_DIR / "campervan_intelligence.db"
    DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
    
    # Connection settings
    POOL_SIZE = 5
    MAX_OVERFLOW = 10
    POOL_TIMEOUT = 30
    ECHO_SQL = os.getenv('DATABASE_ECHO', 'false').lower() == 'true'


class ScrapingConfig:
    """Scraping configuration"""
    
    # Browserless.io configuration
    BROWSERLESS_API_KEY = os.getenv('BROWSERLESS_API_KEY', '')
    BROWSERLESS_REGION = os.getenv('BROWSERLESS_REGION', 'production-sfo')
    USE_BROWSERLESS = os.getenv('USE_BROWSERLESS', 'true').lower() == 'true'
    
    # Scraping behavior
    SCRAPING_TIMEOUT = int(os.getenv('SCRAPING_TIMEOUT', '60000'))
    SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY', '2'))  # seconds between requests
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_BACKOFF = float(os.getenv('RETRY_BACKOFF', '2.0'))
    
    # User agent
    USER_AGENT = os.getenv('USER_AGENT', 
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Rate limiting
    MAX_CONCURRENT_SCRAPERS = int(os.getenv('MAX_CONCURRENT_SCRAPERS', '3'))
    RATE_LIMIT_DELAY = int(os.getenv('RATE_LIMIT_DELAY', '1'))  # seconds


class AlertConfig:
    """Alert system configuration"""
    
    # Email configuration
    ENABLE_EMAIL_ALERTS = os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    ALERT_RECIPIENTS = [r.strip() for r in os.getenv('ALERT_RECIPIENTS', '').split(',') if r.strip()]
    
    # Slack configuration
    ENABLE_SLACK_ALERTS = os.getenv('ENABLE_SLACK_ALERTS', 'false').lower() == 'true'
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
    
    # SMS configuration (Twilio)
    ENABLE_SMS_ALERTS = os.getenv('ENABLE_SMS_ALERTS', 'false').lower() == 'true'
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_FROM = os.getenv('TWILIO_PHONE_FROM', '')
    SMS_RECIPIENTS = [r.strip() for r in os.getenv('SMS_RECIPIENTS', '').split(',') if r.strip()]
    
    # Alert thresholds
    PRICE_DROP_THRESHOLD = float(os.getenv('PRICE_DROP_THRESHOLD', '10.0'))  # percentage
    PRICE_SPIKE_THRESHOLD = float(os.getenv('PRICE_SPIKE_THRESHOLD', '15.0'))  # percentage
    ALERT_COOLDOWN = int(os.getenv('ALERT_COOLDOWN', '3600'))  # seconds


class DataQualityConfig:
    """Data quality configuration"""
    
    # Validation thresholds
    MIN_PRICE = float(os.getenv('MIN_PRICE', '20.0'))  # €/night
    MAX_PRICE = float(os.getenv('MAX_PRICE', '500.0'))  # €/night
    MAX_DISCOUNT = float(os.getenv('MAX_DISCOUNT', '90.0'))  # percentage
    STALENESS_DAYS = int(os.getenv('STALENESS_DAYS', '7'))
    
    # Quality scoring weights
    FRESHNESS_WEIGHT = float(os.getenv('FRESHNESS_WEIGHT', '0.4'))
    COMPLETENESS_WEIGHT = float(os.getenv('COMPLETENESS_WEIGHT', '0.3'))
    VALIDITY_WEIGHT = float(os.getenv('VALIDITY_WEIGHT', '0.3'))
    
    # Data retention
    RETENTION_DAYS = int(os.getenv('RETENTION_DAYS', '90'))
    AUTO_CLEANUP = os.getenv('AUTO_CLEANUP', 'true').lower() == 'true'


class AnalysisConfig:
    """Analysis and intelligence configuration"""
    
    # Trend analysis
    DEFAULT_TREND_DAYS = int(os.getenv('DEFAULT_TREND_DAYS', '30'))
    MIN_DATA_POINTS_FOR_TREND = int(os.getenv('MIN_DATA_POINTS_FOR_TREND', '5'))
    
    # Prediction
    PREDICTION_DAYS = int(os.getenv('PREDICTION_DAYS', '7'))
    PREDICTION_CONFIDENCE_THRESHOLD = float(os.getenv('PREDICTION_CONFIDENCE_THRESHOLD', '0.7'))
    
    # Market analysis
    MARKET_VOLATILITY_THRESHOLD = float(os.getenv('MARKET_VOLATILITY_THRESHOLD', '15.0'))


class DashboardConfig:
    """Dashboard configuration"""
    
    # Streamlit settings
    PAGE_TITLE = os.getenv('PAGE_TITLE', 'Indie Campers Intelligence')
    PAGE_ICON = os.getenv('PAGE_ICON', '🚐')
    LAYOUT = os.getenv('LAYOUT', 'wide')
    
    # Data refresh
    REFRESH_INTERVAL = int(os.getenv('DASHBOARD_REFRESH_INTERVAL', '300'))  # seconds
    
    # Cache settings
    ENABLE_CACHING = os.getenv('ENABLE_DASHBOARD_CACHING', 'true').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # seconds


class LoggingConfig:
    """Logging configuration"""
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 
        '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>')
    LOG_ROTATION = os.getenv('LOG_ROTATION', '1 day')
    LOG_RETENTION = os.getenv('LOG_RETENTION', '30 days')
    LOG_COMPRESSION = os.getenv('LOG_COMPRESSION', 'zip')


class ExportConfig:
    """Export configuration"""
    
    # Export formats
    ENABLE_EXCEL_EXPORT = os.getenv('ENABLE_EXCEL_EXPORT', 'true').lower() == 'true'
    ENABLE_PDF_EXPORT = os.getenv('ENABLE_PDF_EXPORT', 'true').lower() == 'true'
    ENABLE_CSV_EXPORT = os.getenv('ENABLE_CSV_EXPORT', 'true').lower() == 'true'
    ENABLE_JSON_EXPORT = os.getenv('ENABLE_JSON_EXPORT', 'true').lower() == 'true'
    
    # Export scheduling
    DAILY_EXPORT = os.getenv('DAILY_EXPORT', 'false').lower() == 'true'
    WEEKLY_EXPORT = os.getenv('WEEKLY_EXPORT', 'true').lower() == 'true'
    MONTHLY_EXPORT = os.getenv('MONTHLY_EXPORT', 'true').lower() == 'true'


class Config:
    """Main configuration class - aggregates all configs"""
    
    # Sub-configurations
    database = DatabaseConfig()
    scraping = ScrapingConfig()
    alerts = AlertConfig()
    data_quality = DataQualityConfig()
    analysis = AnalysisConfig()
    dashboard = DashboardConfig()
    logging = LoggingConfig()
    export = ExportConfig()
    
    # Directories
    BASE_DIR = BASE_DIR
    DATABASE_DIR = DATABASE_DIR
    DATA_DIR = DATA_DIR
    LOGS_DIR = LOGS_DIR
    CACHE_DIR = CACHE_DIR
    EXPORTS_DIR = EXPORTS_DIR
    SCREENSHOTS_DIR = SCREENSHOTS_DIR
    HTML_DIR = HTML_DIR
    DAILY_SUMMARIES_DIR = DAILY_SUMMARIES_DIR
    
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate configuration
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required environment variables
        if cls.scraping.USE_BROWSERLESS and not cls.scraping.BROWSERLESS_API_KEY:
            issues.append("BROWSERLESS_API_KEY is required when USE_BROWSERLESS=true")
        
        if cls.alerts.ENABLE_EMAIL_ALERTS:
            if not cls.alerts.SMTP_USER:
                issues.append("SMTP_USER is required for email alerts")
            if not cls.alerts.SMTP_PASSWORD:
                issues.append("SMTP_PASSWORD is required for email alerts")
            if not cls.alerts.ALERT_RECIPIENTS:
                issues.append("ALERT_RECIPIENTS is required for email alerts")
        
        if cls.alerts.ENABLE_SLACK_ALERTS and not cls.alerts.SLACK_WEBHOOK_URL:
            issues.append("SLACK_WEBHOOK_URL is required for Slack alerts")
        
        if cls.alerts.ENABLE_SMS_ALERTS:
            if not cls.alerts.TWILIO_ACCOUNT_SID:
                issues.append("TWILIO_ACCOUNT_SID is required for SMS alerts")
            if not cls.alerts.TWILIO_AUTH_TOKEN:
                issues.append("TWILIO_AUTH_TOKEN is required for SMS alerts")
            if not cls.alerts.SMS_RECIPIENTS:
                issues.append("SMS_RECIPIENTS is required for SMS alerts")
        
        # Check directories exist
        for name, directory in [
            ('BASE_DIR', cls.BASE_DIR),
            ('DATABASE_DIR', cls.DATABASE_DIR),
            ('DATA_DIR', cls.DATA_DIR),
            ('LOGS_DIR', cls.LOGS_DIR),
        ]:
            if not directory.exists():
                issues.append(f"{name} does not exist: {directory}")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    @classmethod
    def print_summary(cls):
        """Print configuration summary"""
        print("\n" + "=" * 70)
        print("⚙️  SYSTEM CONFIGURATION SUMMARY")
        print("=" * 70)
        
        print(f"\n📁 Directories:")
        print(f"   Base: {cls.BASE_DIR}")
        print(f"   Database: {cls.DATABASE_DIR}")
        print(f"   Data: {cls.DATA_DIR}")
        print(f"   Logs: {cls.LOGS_DIR}")
        
        print(f"\n🗄️  Database:")
        print(f"   Path: {cls.database.DATABASE_PATH}")
        print(f"   Exists: {cls.database.DATABASE_PATH.exists()}")
        
        print(f"\n🔍 Scraping:")
        print(f"   Use Browserless: {cls.scraping.USE_BROWSERLESS}")
        print(f"   API Key Set: {bool(cls.scraping.BROWSERLESS_API_KEY)}")
        print(f"   Max Retries: {cls.scraping.MAX_RETRIES}")
        print(f"   Timeout: {cls.scraping.SCRAPING_TIMEOUT}ms")
        
        print(f"\n🚨 Alerts:")
        print(f"   Email: {cls.alerts.ENABLE_EMAIL_ALERTS}")
        print(f"   Slack: {cls.alerts.ENABLE_SLACK_ALERTS}")
        print(f"   SMS: {cls.alerts.ENABLE_SMS_ALERTS}")
        
        print(f"\n✅ Data Quality:")
        print(f"   Price Range: €{cls.data_quality.MIN_PRICE}-€{cls.data_quality.MAX_PRICE}")
        print(f"   Max Discount: {cls.data_quality.MAX_DISCOUNT}%")
        print(f"   Auto Cleanup: {cls.data_quality.AUTO_CLEANUP}")
        
        print(f"\n🎯 Environment:")
        print(f"   Mode: {cls.ENVIRONMENT}")
        print(f"   Debug: {cls.DEBUG}")
        
        print("\n" + "=" * 70 + "\n")


# Create global config instance
config = Config()


def get_config() -> Config:
    """Get global configuration instance"""
    return config


if __name__ == "__main__":
    # Test configuration
    config.print_summary()
    
    # Validate configuration
    is_valid, issues = config.validate()
    
    if is_valid:
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"   • {issue}")


