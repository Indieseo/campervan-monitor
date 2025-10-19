"""
Environment-Specific Configuration Management
Supports production, development, and testing environments
"""

import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional
from pathlib import Path


class Environment(str, Enum):
    """Supported environments"""
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TESTING = "testing"


@dataclass
class ScrapingConfig:
    """Scraping-specific configuration"""
    use_browserless: bool
    browserless_api_key: Optional[str]
    browserless_region: str
    scraping_timeout: int  # milliseconds
    max_retries: int
    retry_delay: float  # seconds
    save_screenshots: bool
    save_html: bool
    user_agent: str


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    pool_size: int
    max_overflow: int
    pool_pre_ping: bool
    echo: bool  # SQL logging


@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""
    log_level: str
    log_format: str
    enable_metrics: bool
    metrics_export_interval: int  # seconds
    enable_health_checks: bool
    health_check_interval: int  # seconds


@dataclass
class PerformanceConfig:
    """Performance and optimization settings"""
    max_concurrent_scrapers: int
    enable_caching: bool
    cache_ttl_seconds: int
    enable_parallel_scraping: bool


@dataclass
class EnvironmentConfig:
    """Complete environment configuration"""
    environment: Environment
    scraping: ScrapingConfig
    database: DatabaseConfig
    monitoring: MonitoringConfig
    performance: PerformanceConfig
    debug: bool = False


# Production Configuration
PRODUCTION_CONFIG = EnvironmentConfig(
    environment=Environment.PRODUCTION,
    debug=False,

    scraping=ScrapingConfig(
        use_browserless=True,
        browserless_api_key=os.getenv('BROWSERLESS_API_KEY'),
        browserless_region='production-sfo',
        scraping_timeout=90000,  # 90 seconds
        max_retries=5,
        retry_delay=10.0,
        save_screenshots=False,  # Save space in production
        save_html=False,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ),

    database=DatabaseConfig(
        url=os.getenv('DATABASE_URL', 'sqlite:///data/campervan_intel.db'),
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False  # No SQL logging in production
    ),

    monitoring=MonitoringConfig(
        log_level='INFO',
        log_format='json',  # Structured JSON logs
        enable_metrics=True,
        metrics_export_interval=300,  # 5 minutes
        enable_health_checks=True,
        health_check_interval=60
    ),

    performance=PerformanceConfig(
        max_concurrent_scrapers=5,
        enable_caching=True,
        cache_ttl_seconds=3600,  # 1 hour
        enable_parallel_scraping=True
    )
)


# Development Configuration
DEVELOPMENT_CONFIG = EnvironmentConfig(
    environment=Environment.DEVELOPMENT,
    debug=True,

    scraping=ScrapingConfig(
        use_browserless=False,  # Use local browser for dev
        browserless_api_key=None,
        browserless_region='',
        scraping_timeout=60000,  # 60 seconds
        max_retries=2,
        retry_delay=5.0,
        save_screenshots=True,  # Helpful for debugging
        save_html=True,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ),

    database=DatabaseConfig(
        url='sqlite:///data/dev_campervan_intel.db',
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=True  # Show SQL queries in development
    ),

    monitoring=MonitoringConfig(
        log_level='DEBUG',
        log_format='text',  # Human-readable logs
        enable_metrics=True,
        metrics_export_interval=60,  # 1 minute
        enable_health_checks=False
    ),

    performance=PerformanceConfig(
        max_concurrent_scrapers=2,  # Lower for local development
        enable_caching=False,  # Disable to always get fresh data
        cache_ttl_seconds=600,
        enable_parallel_scraping=False  # Easier debugging with sequential
    )
)


# Testing Configuration
TESTING_CONFIG = EnvironmentConfig(
    environment=Environment.TESTING,
    debug=True,

    scraping=ScrapingConfig(
        use_browserless=False,
        browserless_api_key=None,
        browserless_region='',
        scraping_timeout=30000,  # 30 seconds
        max_retries=1,
        retry_delay=1.0,
        save_screenshots=False,  # Don't save during tests
        save_html=False,
        user_agent='TestBot/1.0'
    ),

    database=DatabaseConfig(
        url='sqlite:///:memory:',  # In-memory database for tests
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=False,
        echo=False
    ),

    monitoring=MonitoringConfig(
        log_level='WARNING',  # Minimal logging during tests
        log_format='text',
        enable_metrics=False,
        metrics_export_interval=0,
        enable_health_checks=False
    ),

    performance=PerformanceConfig(
        max_concurrent_scrapers=1,  # Sequential for deterministic tests
        enable_caching=False,
        cache_ttl_seconds=0,
        enable_parallel_scraping=False
    )
)


class ConfigurationManager:
    """Manages environment-specific configurations"""

    _instance = None
    _current_config: Optional[EnvironmentConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_config(cls, environment: Optional[str] = None) -> EnvironmentConfig:
        """
        Get configuration for specified environment.

        Args:
            environment: Environment name (production/development/testing)
                        If None, reads from ENVIRONMENT env var

        Returns:
            EnvironmentConfig instance
        """
        if cls._current_config is not None:
            return cls._current_config

        # Determine environment
        if environment is None:
            environment = os.getenv('ENVIRONMENT', 'development').lower()

        # Load appropriate config
        if environment == 'production':
            config = PRODUCTION_CONFIG
        elif environment == 'testing':
            config = TESTING_CONFIG
        else:
            config = DEVELOPMENT_CONFIG

        cls._current_config = config
        return config

    @classmethod
    def set_config(cls, config: EnvironmentConfig):
        """Manually set configuration (useful for testing)"""
        cls._current_config = config

    @classmethod
    def validate_config(cls, config: EnvironmentConfig) -> tuple[bool, list[str]]:
        """
        Validate configuration.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Validate scraping config
        if config.scraping.use_browserless and not config.scraping.browserless_api_key:
            errors.append("Browserless enabled but BROWSERLESS_API_KEY not set")

        if config.scraping.scraping_timeout < 10000:
            errors.append("Scraping timeout too low (minimum 10000ms)")

        # Validate database config
        if not config.database.url:
            errors.append("Database URL not configured")

        # Validate performance config
        if config.performance.max_concurrent_scrapers < 1:
            errors.append("max_concurrent_scrapers must be >= 1")

        if config.performance.max_concurrent_scrapers > 10:
            errors.append("max_concurrent_scrapers should not exceed 10")

        is_valid = len(errors) == 0
        return is_valid, errors

    @classmethod
    def print_config(cls, config: Optional[EnvironmentConfig] = None):
        """Print current configuration"""
        if config is None:
            config = cls.get_config()

        print("\n" + "=" * 60)
        print(f"ENVIRONMENT: {config.environment.value.upper()}")
        print("=" * 60)

        print("\n[SCRAPING]")
        print(f"  Use Browserless: {config.scraping.use_browserless}")
        print(f"  Timeout: {config.scraping.scraping_timeout}ms")
        print(f"  Max Retries: {config.scraping.max_retries}")
        print(f"  Save Screenshots: {config.scraping.save_screenshots}")

        print("\n[DATABASE]")
        print(f"  URL: {config.database.url}")
        print(f"  Pool Size: {config.database.pool_size}")
        print(f"  Echo SQL: {config.database.echo}")

        print("\n[MONITORING]")
        print(f"  Log Level: {config.monitoring.log_level}")
        print(f"  Log Format: {config.monitoring.log_format}")
        print(f"  Metrics Enabled: {config.monitoring.enable_metrics}")

        print("\n[PERFORMANCE]")
        print(f"  Max Concurrent: {config.performance.max_concurrent_scrapers}")
        print(f"  Caching: {config.performance.enable_caching}")
        print(f"  Parallel Scraping: {config.performance.enable_parallel_scraping}")

        print("\n" + "=" * 60 + "\n")


# Convenience function
def get_config(environment: Optional[str] = None) -> EnvironmentConfig:
    """Get configuration for environment"""
    return ConfigurationManager.get_config(environment)


if __name__ == "__main__":
    print("Environment Configuration System")
    print("=" * 60)

    # Show all environments
    for env in [None, 'production', 'development', 'testing']:
        config = get_config(env)
        ConfigurationManager.print_config(config)

        # Validate
        is_valid, errors = ConfigurationManager.validate_config(config)
        if not is_valid:
            print("⚠️ VALIDATION ERRORS:")
            for error in errors:
                print(f"  - {error}")
            print()
