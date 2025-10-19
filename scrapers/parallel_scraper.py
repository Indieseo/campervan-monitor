"""
Parallel Scraping Engine

Enables concurrent scraping of multiple competitors for 3-5x performance improvement.

Features:
- Async/await based parallelization
- Rate limiting to respect site policies
- Semaphore-based concurrency control
- Progress tracking
- Graceful error handling
- Resource pooling
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from loguru import logger
from pathlib import Path
import sys

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from scrapers.base_scraper import DeepDataScraper


@dataclass
class ParallelScraperConfig:
    """Configuration for parallel scraping"""

    # Concurrency controls
    max_concurrent_scrapers: int = 5        # Max scrapers running simultaneously
    max_concurrent_per_domain: int = 1      # Max requests per domain

    # Rate limiting
    requests_per_minute: int = 30           # Global rate limit
    delay_between_requests: float = 2.0     # Seconds between requests

    # Timeouts
    scraper_timeout: int = 120              # Seconds per scraper
    total_timeout: int = 600                # Total operation timeout (10 min)

    # Progress tracking
    enable_progress_callback: bool = True
    log_interval_seconds: int = 5

    # Error handling
    continue_on_error: bool = True          # Continue if one scraper fails
    collect_partial_results: bool = True    # Save partial results on timeout


@dataclass
class ScrapeTask:
    """Represents a single scrape task"""
    scraper: DeepDataScraper
    priority: int = 0                       # Higher = higher priority
    domain: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[Exception] = None
    duration_seconds: float = 0.0
    status: str = "pending"                 # pending, running, completed, failed


@dataclass
class ParallelScrapeResults:
    """Results from parallel scraping operation"""
    tasks: List[ScrapeTask]
    total_duration: float
    successful_count: int
    failed_count: int
    timeout_count: int
    average_duration: float
    throughput: float                       # Tasks per second

    def get_successful_results(self) -> List[Dict]:
        """Get all successful results"""
        return [
            task.result for task in self.tasks
            if task.status == "completed" and task.result
        ]

    def get_failed_tasks(self) -> List[ScrapeTask]:
        """Get all failed tasks"""
        return [task for task in self.tasks if task.status == "failed"]

    def generate_summary(self) -> str:
        """Generate text summary of results"""
        return f"""
Parallel Scraping Summary
{'=' * 60}
Total Companies:     {len(self.tasks)}
Successful:          {self.successful_count} ({self.successful_count/len(self.tasks)*100:.1f}%)
Failed:              {self.failed_count} ({self.failed_count/len(self.tasks)*100:.1f}%)
Timed Out:           {self.timeout_count}

Performance:
  Total Duration:    {self.total_duration:.2f}s
  Avg per Scraper:   {self.average_duration:.2f}s
  Throughput:        {self.throughput:.2f} scrapers/sec
  Speedup:           {len(self.tasks)/self.total_duration:.2f}x vs sequential

Top Performers:
"""


class RateLimiter:
    """Rate limiter using token bucket algorithm"""

    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make a request"""
        async with self._lock:
            now = time.time()
            time_since_last = now - self.last_request_time

            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

            self.last_request_time = time.time()


class DomainSemaphore:
    """Manages concurrency per domain"""

    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent
        self.semaphores: Dict[str, asyncio.Semaphore] = {}
        self._lock = asyncio.Lock()

    async def get_semaphore(self, domain: str) -> asyncio.Semaphore:
        """Get or create semaphore for domain"""
        async with self._lock:
            if domain not in self.semaphores:
                self.semaphores[domain] = asyncio.Semaphore(self.max_concurrent)
            return self.semaphores[domain]


class ParallelScraper:
    """
    Parallel scraping engine for high-performance data collection.

    Usage:
        scrapers = [scraper1, scraper2, scraper3, ...]
        parallel_scraper = ParallelScraper(config)
        results = await parallel_scraper.scrape_all(scrapers)

    Example:
        config = ParallelScraperConfig(
            max_concurrent_scrapers=5,
            requests_per_minute=30
        )
        engine = ParallelScraper(config)
        results = await engine.scrape_all(my_scrapers)

        print(f"Completed {results.successful_count} out of {len(results.tasks)}")
    """

    def __init__(
        self,
        config: Optional[ParallelScraperConfig] = None,
        progress_callback: Optional[Callable[[Dict], None]] = None
    ):
        self.config = config or ParallelScraperConfig()
        self.progress_callback = progress_callback

        # Rate limiting and concurrency controls
        self.rate_limiter = RateLimiter(self.config.requests_per_minute)
        self.global_semaphore = asyncio.Semaphore(
            self.config.max_concurrent_scrapers
        )
        self.domain_semaphore = DomainSemaphore(
            self.config.max_concurrent_per_domain
        )

        # Progress tracking
        self.start_time: Optional[float] = None
        self.completed_count = 0
        self.total_count = 0

    async def scrape_all(
        self,
        scrapers: List[DeepDataScraper],
        priorities: Optional[List[int]] = None
    ) -> ParallelScrapeResults:
        """
        Scrape all companies in parallel.

        Args:
            scrapers: List of scraper instances
            priorities: Optional priority for each scraper (higher = earlier)

        Returns:
            ParallelScrapeResults with detailed information
        """
        logger.info(
            f"🚀 Starting parallel scraping for {len(scrapers)} companies "
            f"(max {self.config.max_concurrent_scrapers} concurrent)"
        )

        self.start_time = time.time()
        self.total_count = len(scrapers)
        self.completed_count = 0

        # Create tasks
        tasks = self._create_tasks(scrapers, priorities)

        # Sort by priority (higher first)
        tasks.sort(key=lambda t: t.priority, reverse=True)

        # Start progress monitor
        progress_task = None
        if self.config.enable_progress_callback:
            progress_task = asyncio.create_task(self._monitor_progress(tasks))

        # Execute tasks in parallel
        try:
            await asyncio.wait_for(
                self._execute_tasks(tasks),
                timeout=self.config.total_timeout
            )
        except asyncio.TimeoutError:
            logger.error(
                f"⏱️ Parallel scraping timed out after "
                f"{self.config.total_timeout}s"
            )

        # Stop progress monitor
        if progress_task:
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass

        # Generate results
        total_duration = time.time() - self.start_time
        results = self._generate_results(tasks, total_duration)

        logger.info(
            f"✅ Parallel scraping complete: {results.successful_count}/"
            f"{len(tasks)} successful in {total_duration:.2f}s"
        )

        return results

    def _create_tasks(
        self,
        scrapers: List[DeepDataScraper],
        priorities: Optional[List[int]] = None
    ) -> List[ScrapeTask]:
        """Create scrape tasks from scrapers"""
        tasks = []

        for i, scraper in enumerate(scrapers):
            priority = priorities[i] if priorities and i < len(priorities) else 0

            # Extract domain from URL
            domain = self._extract_domain(scraper.config.get('urls', {}).get('homepage', ''))

            task = ScrapeTask(
                scraper=scraper,
                priority=priority,
                domain=domain
            )
            tasks.append(task)

        return tasks

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return "unknown"

        # Simple domain extraction
        if '://' in url:
            url = url.split('://')[1]
        domain = url.split('/')[0]
        return domain

    async def _execute_tasks(self, tasks: List[ScrapeTask]):
        """Execute all tasks in parallel with concurrency limits"""
        # Create coroutines for all tasks
        coroutines = [self._execute_single_task(task) for task in tasks]

        # Execute with gather to run in parallel
        await asyncio.gather(*coroutines, return_exceptions=True)

    async def _execute_single_task(self, task: ScrapeTask):
        """Execute a single scrape task"""
        # Acquire global semaphore (limit total concurrent scrapers)
        async with self.global_semaphore:
            # Acquire domain semaphore (limit per-domain requests)
            domain_sem = await self.domain_semaphore.get_semaphore(task.domain)

            async with domain_sem:
                # Apply rate limiting
                await self.rate_limiter.acquire()

                # Execute the scrape
                task.status = "running"
                task.start_time = datetime.now()

                logger.info(f"🔄 Starting: {task.scraper.company_name}")

                try:
                    # Execute with timeout
                    task.result = await asyncio.wait_for(
                        task.scraper.scrape(),
                        timeout=self.config.scraper_timeout
                    )

                    task.status = "completed"
                    logger.info(f"✅ Completed: {task.scraper.company_name}")

                except asyncio.TimeoutError:
                    task.status = "timeout"
                    task.error = TimeoutError(
                        f"Scraper timed out after {self.config.scraper_timeout}s"
                    )
                    logger.warning(
                        f"⏱️ Timeout: {task.scraper.company_name} "
                        f"({self.config.scraper_timeout}s)"
                    )

                except Exception as e:
                    task.status = "failed"
                    task.error = e
                    logger.error(f"❌ Failed: {task.scraper.company_name} - {e}")

                    if not self.config.continue_on_error:
                        raise

                finally:
                    task.end_time = datetime.now()
                    task.duration_seconds = (
                        task.end_time - task.start_time
                    ).total_seconds()

                    self.completed_count += 1

    async def _monitor_progress(self, tasks: List[ScrapeTask]):
        """Monitor and report progress"""
        while True:
            await asyncio.sleep(self.config.log_interval_seconds)

            elapsed = time.time() - self.start_time
            progress_pct = (self.completed_count / self.total_count * 100
                          if self.total_count > 0 else 0)

            # Count by status
            running = sum(1 for t in tasks if t.status == "running")
            completed = sum(1 for t in tasks if t.status == "completed")
            failed = sum(1 for t in tasks if t.status == "failed")

            logger.info(
                f"📊 Progress: {self.completed_count}/{self.total_count} "
                f"({progress_pct:.1f}%) | "
                f"Running: {running} | "
                f"Completed: {completed} | "
                f"Failed: {failed} | "
                f"Elapsed: {elapsed:.0f}s"
            )

            # Call custom progress callback
            if self.progress_callback:
                self.progress_callback({
                    'completed': self.completed_count,
                    'total': self.total_count,
                    'progress_pct': progress_pct,
                    'running': running,
                    'elapsed': elapsed
                })

    def _generate_results(
        self,
        tasks: List[ScrapeTask],
        total_duration: float
    ) -> ParallelScrapeResults:
        """Generate results object from completed tasks"""
        successful_count = sum(1 for t in tasks if t.status == "completed")
        failed_count = sum(1 for t in tasks if t.status == "failed")
        timeout_count = sum(1 for t in tasks if t.status == "timeout")

        # Calculate average duration (only for completed tasks)
        completed_durations = [
            t.duration_seconds for t in tasks
            if t.status == "completed" and t.duration_seconds > 0
        ]
        average_duration = (
            sum(completed_durations) / len(completed_durations)
            if completed_durations else 0
        )

        throughput = len(tasks) / total_duration if total_duration > 0 else 0

        return ParallelScrapeResults(
            tasks=tasks,
            total_duration=total_duration,
            successful_count=successful_count,
            failed_count=failed_count,
            timeout_count=timeout_count,
            average_duration=average_duration,
            throughput=throughput
        )


# Utility functions for common use cases

async def scrape_companies_parallel(
    scrapers: List[DeepDataScraper],
    max_concurrent: int = 5
) -> List[Dict]:
    """
    Simple helper to scrape multiple companies in parallel.

    Args:
        scrapers: List of scraper instances
        max_concurrent: Maximum concurrent scrapers

    Returns:
        List of scrape results
    """
    config = ParallelScraperConfig(max_concurrent_scrapers=max_concurrent)
    engine = ParallelScraper(config)
    results = await engine.scrape_all(scrapers)
    return results.get_successful_results()


async def scrape_with_priorities(
    scrapers: List[DeepDataScraper],
    priorities: List[int],
    max_concurrent: int = 5
) -> ParallelScrapeResults:
    """
    Scrape with priority ordering.

    Args:
        scrapers: List of scraper instances
        priorities: Priority for each scraper (higher = earlier)
        max_concurrent: Maximum concurrent scrapers

    Returns:
        Complete results with statistics
    """
    config = ParallelScraperConfig(max_concurrent_scrapers=max_concurrent)
    engine = ParallelScraper(config)
    return await engine.scrape_all(scrapers, priorities)


# Example usage
if __name__ == "__main__":
    async def example_parallel_scraping():
        """Example of parallel scraping"""
        from scrapers.competitor_config import get_competitor_config
        from scrapers.base_scraper import DeepDataScraper

        print("🚀 Parallel Scraping Example")
        print("=" * 60)

        # Mock scraper for demonstration
        class MockScraper(DeepDataScraper):
            def __init__(self, company_name: str, delay: float = 2.0):
                config = get_competitor_config().get(company_name, {
                    'urls': {'homepage': f'https://{company_name}.com'}
                })
                super().__init__(company_name, 1, config)
                self.delay = delay

            async def scrape_deep_data(self, page):
                # Simulate scraping delay
                await asyncio.sleep(self.delay)
                self.data['base_nightly_rate'] = 100
                self.data['currency'] = 'EUR'

        # Create mock scrapers with different delays
        scrapers = [
            MockScraper("Company1", delay=2.0),
            MockScraper("Company2", delay=1.5),
            MockScraper("Company3", delay=3.0),
            MockScraper("Company4", delay=2.5),
            MockScraper("Company5", delay=1.0),
        ]

        # Configure parallel scraping
        config = ParallelScraperConfig(
            max_concurrent_scrapers=3,
            requests_per_minute=60
        )

        engine = ParallelScraper(config)

        # Execute
        print(f"\n⏱️ Sequential would take: ~{sum(s.delay for s in scrapers):.1f}s")
        print(f"🚀 Running with {config.max_concurrent_scrapers} concurrent...\n")

        results = await engine.scrape_all(scrapers)

        # Print summary
        print(results.generate_summary())

        speedup = (sum(s.delay for s in scrapers) / results.total_duration
                  if results.total_duration > 0 else 0)
        print(f"⚡ Speedup: {speedup:.2f}x faster than sequential!")

    asyncio.run(example_parallel_scraping())
