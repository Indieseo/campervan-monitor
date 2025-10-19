"""
Resilient Scraper Wrapper

Wraps scrapers with circuit breaker pattern for improved resilience.
Automatically handles failures and prevents cascading issues.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Optional, List, Any
from loguru import logger

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitBreakerRegistry,
    get_global_registry
)
from scrapers.base_scraper import DeepDataScraper


class ResilientScraperConfig:
    """Configuration for resilient scraper behavior"""

    def __init__(
        self,
        # Circuit breaker settings
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: int = 60,
        half_open_max_calls: int = 3,

        # Retry settings
        max_retries: int = 3,
        retry_delay_seconds: float = 2.0,
        exponential_backoff: bool = True,

        # Fallback settings
        use_fallback_data: bool = True,
        fallback_data_age_hours: int = 24
    ):
        self.circuit_config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout_seconds=timeout_seconds,
            half_open_max_calls=half_open_max_calls
        )
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.exponential_backoff = exponential_backoff
        self.use_fallback_data = use_fallback_data
        self.fallback_data_age_hours = fallback_data_age_hours


class ResilientScraper:
    """
    Wrapper that makes any scraper resilient using circuit breaker pattern.

    Features:
    - Circuit breaker protection
    - Automatic retries with exponential backoff
    - Fallback to cached data
    - Detailed error tracking
    - Graceful degradation

    Usage:
        scraper = MyScraper("Company", 1, config)
        resilient = ResilientScraper(scraper)
        result = await resilient.scrape_with_resilience()
    """

    def __init__(
        self,
        scraper: DeepDataScraper,
        config: Optional[ResilientScraperConfig] = None,
        registry: Optional[CircuitBreakerRegistry] = None
    ):
        self.scraper = scraper
        self.config = config or ResilientScraperConfig()
        self.registry = registry or get_global_registry()
        self.company_name = scraper.company_name

        # Statistics
        self.stats = {
            'total_attempts': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'circuit_breaker_blocks': 0,
            'fallback_uses': 0,
            'retries_used': 0
        }

    async def scrape_with_resilience(self) -> Dict[str, Any]:
        """
        Execute scrape with full resilience (circuit breaker + retries).

        Returns:
            Dict containing scrape results or fallback data
        """
        self.stats['total_attempts'] += 1

        # Get circuit breaker for this scraper
        breaker = await self.registry.get_breaker(
            self.company_name,
            self.config.circuit_config
        )

        # Try with retries
        for attempt in range(self.config.max_retries + 1):
            try:
                # Execute through circuit breaker
                result = await breaker.call(self._execute_scrape)

                self.stats['successful_scrapes'] += 1

                if attempt > 0:
                    logger.info(
                        f"✅ {self.company_name}: Succeeded on attempt {attempt + 1}"
                    )

                return self._format_result(result, success=True)

            except CircuitBreakerOpenError as e:
                # Circuit breaker is blocking
                self.stats['circuit_breaker_blocks'] += 1
                logger.warning(
                    f"🚫 {self.company_name}: Circuit breaker blocked attempt"
                )

                # Try fallback immediately
                return await self._handle_fallback(str(e))

            except Exception as e:
                self.stats['failed_scrapes'] += 1

                # If we have more retries, wait and try again
                if attempt < self.config.max_retries:
                    self.stats['retries_used'] += 1
                    delay = self._calculate_retry_delay(attempt)

                    logger.warning(
                        f"⚠️ {self.company_name}: Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    await asyncio.sleep(delay)
                else:
                    # All retries exhausted
                    logger.error(
                        f"❌ {self.company_name}: All {self.config.max_retries + 1} "
                        f"attempts failed. Last error: {e}"
                    )

                    return await self._handle_fallback(str(e))

        # Should not reach here, but handle gracefully
        return await self._handle_fallback("Unknown error")

    async def _execute_scrape(self) -> Dict[str, Any]:
        """Execute the actual scrape (called through circuit breaker)"""
        return await self.scraper.scrape()

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay before retry (with optional exponential backoff)"""
        if self.config.exponential_backoff:
            return self.config.retry_delay_seconds * (2 ** attempt)
        return self.config.retry_delay_seconds

    async def _handle_fallback(self, error_msg: str) -> Dict[str, Any]:
        """Handle fallback when scraping fails"""
        if self.config.use_fallback_data:
            fallback_data = await self._get_fallback_data()
            if fallback_data:
                self.stats['fallback_uses'] += 1
                logger.info(
                    f"📦 {self.company_name}: Using fallback data "
                    f"(age: {fallback_data.get('age_hours', '?')}h)"
                )
                return self._format_result(fallback_data, success=False, is_fallback=True)

        # No fallback available, return error result
        return self._format_result(
            {
                'company_name': self.company_name,
                'error': error_msg,
                'data_completeness_pct': 0
            },
            success=False
        )

    async def _get_fallback_data(self) -> Optional[Dict[str, Any]]:
        """
        Get fallback data from database (most recent successful scrape).

        Returns:
            Latest data if available and within age threshold, None otherwise
        """
        try:
            from database.models import get_session, CompetitorPrice
            from datetime import datetime, timedelta

            session = get_session()

            # Get most recent successful scrape
            cutoff_time = datetime.now() - timedelta(
                hours=self.config.fallback_data_age_hours
            )

            latest = session.query(CompetitorPrice).filter(
                CompetitorPrice.company_name == self.company_name,
                CompetitorPrice.scrape_timestamp >= cutoff_time,
                CompetitorPrice.data_completeness_pct > 50  # Only use quality data
            ).order_by(
                CompetitorPrice.scrape_timestamp.desc()
            ).first()

            if latest:
                age_hours = (datetime.now() - latest.scrape_timestamp).total_seconds() / 3600

                # Convert to dict
                fallback = {
                    'company_name': latest.company_name,
                    'base_nightly_rate': latest.base_nightly_rate,
                    'data_completeness_pct': latest.data_completeness_pct,
                    'age_hours': round(age_hours, 1)
                }

                return fallback

            return None

        except Exception as e:
            logger.warning(f"Failed to get fallback data: {e}")
            return None

    def _format_result(
        self,
        data: Dict[str, Any],
        success: bool,
        is_fallback: bool = False
    ) -> Dict[str, Any]:
        """Format result with metadata"""
        return {
            'data': data,
            'success': success,
            'is_fallback': is_fallback,
            'company_name': self.company_name,
            'stats': self.stats.copy()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics"""
        return {
            'company_name': self.company_name,
            'stats': self.stats.copy(),
            'success_rate': (
                self.stats['successful_scrapes'] / self.stats['total_attempts'] * 100
                if self.stats['total_attempts'] > 0 else 0
            )
        }


class ResilientScraperOrchestrator:
    """
    Orchestrates multiple resilient scrapers.

    Features:
    - Manages circuit breakers for all scrapers
    - Provides aggregated statistics
    - Handles graceful shutdown

    Usage:
        orchestrator = ResilientScraperOrchestrator()
        results = await orchestrator.scrape_all(scrapers)
        report = orchestrator.generate_report()
    """

    def __init__(self, config: Optional[ResilientScraperConfig] = None):
        self.config = config or ResilientScraperConfig()
        self.registry = CircuitBreakerRegistry(
            default_config=self.config.circuit_config
        )
        self.resilient_scrapers: Dict[str, ResilientScraper] = {}

    async def scrape_single(self, scraper: DeepDataScraper) -> Dict[str, Any]:
        """Scrape single company with resilience"""
        # Get or create resilient wrapper
        if scraper.company_name not in self.resilient_scrapers:
            self.resilient_scrapers[scraper.company_name] = ResilientScraper(
                scraper,
                self.config,
                self.registry
            )

        resilient = self.resilient_scrapers[scraper.company_name]
        return await resilient.scrape_with_resilience()

    async def scrape_all(
        self,
        scrapers: List[DeepDataScraper],
        parallel: bool = False,
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple companies with resilience.

        Args:
            scrapers: List of scraper instances
            parallel: Whether to scrape in parallel
            max_concurrent: Maximum concurrent scrapers (if parallel=True)

        Returns:
            List of results
        """
        results = []

        if parallel:
            logger.info(
                f"🚀 Starting parallel scraping for {len(scrapers)} companies "
                f"(max {max_concurrent} concurrent)"
            )

            # Use semaphore to limit concurrency
            semaphore = asyncio.Semaphore(max_concurrent)

            async def scrape_with_limit(scraper):
                async with semaphore:
                    return await self.scrape_single(scraper)

            # Execute all scrapers in parallel with concurrency limit
            tasks = [scrape_with_limit(scraper) for scraper in scrapers]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle any exceptions
            results = [
                r if not isinstance(r, Exception) else {
                    'data': {'error': str(r)},
                    'success': False,
                    'company_name': 'Unknown'
                }
                for r in results
            ]
        else:
            logger.info(
                f"🔄 Starting sequential scraping for {len(scrapers)} companies"
            )
            for scraper in scrapers:
                result = await self.scrape_single(scraper)
                results.append(result)

        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report on scraping operations"""
        circuit_statuses = self.registry.get_all_statuses()

        total_stats = {
            'total_attempts': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'circuit_breaker_blocks': 0,
            'fallback_uses': 0,
            'retries_used': 0
        }

        scraper_reports = {}

        for name, resilient in self.resilient_scrapers.items():
            stats = resilient.get_stats()
            scraper_reports[name] = stats

            # Aggregate stats
            for key in total_stats:
                total_stats[key] += stats['stats'][key]

        return {
            'summary': {
                'total_companies': len(self.resilient_scrapers),
                'total_attempts': total_stats['total_attempts'],
                'success_rate': (
                    total_stats['successful_scrapes'] / total_stats['total_attempts'] * 100
                    if total_stats['total_attempts'] > 0 else 0
                ),
                **total_stats
            },
            'scrapers': scraper_reports,
            'circuit_breakers': circuit_statuses
        }

    async def reset_all_circuits(self):
        """Reset all circuit breakers"""
        await self.registry.reset_all()
        logger.info("🔄 All circuit breakers reset")


# Example usage
if __name__ == "__main__":
    async def example_usage():
        """Example of using resilient scraper"""
        from scrapers.competitor_config import get_competitor_config
        from scrapers.base_scraper import DeepDataScraper

        print("🛡️ Resilient Scraper Example")
        print("=" * 60)

        # Mock scraper for demonstration
        class MockScraper(DeepDataScraper):
            def __init__(self, company_name: str):
                config = get_competitor_config().get(company_name, {
                    'urls': {'homepage': 'https://example.com'}
                })
                super().__init__(company_name, 1, config)

            async def scrape_deep_data(self, page):
                # Simulate scraping
                self.data['base_nightly_rate'] = 100
                self.data['currency'] = 'EUR'

        # Create orchestrator
        orchestrator = ResilientScraperOrchestrator(
            ResilientScraperConfig(
                failure_threshold=3,
                max_retries=2
            )
        )

        # Create mock scrapers
        scrapers = [
            MockScraper("Roadsurfer"),
            MockScraper("Apollo"),
            MockScraper("Indie Campers")
        ]

        # Scrape all
        results = await orchestrator.scrape_all(scrapers)

        # Generate report
        report = orchestrator.generate_report()

        print("\n📊 Results:")
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['company_name']}")

        print(f"\n📈 Overall Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"   Successful: {report['summary']['successful_scrapes']}")
        print(f"   Failed: {report['summary']['failed_scrapes']}")
        print(f"   Circuit Blocks: {report['summary']['circuit_breaker_blocks']}")
        print(f"   Fallback Uses: {report['summary']['fallback_uses']}")

    asyncio.run(example_usage())
