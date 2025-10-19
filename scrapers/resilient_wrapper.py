"""
Resilient scraper wrapper with retry logic and error handling
"""

import asyncio
import time
from typing import Dict, Callable, Any
from loguru import logger
from functools import wraps


class RetryConfig:
    """Retry configuration"""
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 5.0,
        backoff_multiplier: float = 2.0,
        max_delay: float = 60.0
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay


def with_retry(retry_config: RetryConfig = None):
    """Decorator to add retry logic to async functions"""

    if retry_config is None:
        retry_config = RetryConfig()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = retry_config.initial_delay

            for attempt in range(1, retry_config.max_attempts + 1):
                try:
                    logger.info(f"Attempt {attempt}/{retry_config.max_attempts}: {func.__name__}")
                    result = await func(*args, **kwargs)

                    # Validate result
                    if _is_valid_result(result):
                        if attempt > 1:
                            logger.info(f"✅ Success on attempt {attempt}")
                        return result
                    else:
                        logger.warning(f"Invalid result on attempt {attempt}, retrying...")
                        raise ValueError("Invalid result returned")

                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt} failed: {e}")

                    if attempt < retry_config.max_attempts:
                        logger.info(f"Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        delay = min(delay * retry_config.backoff_multiplier, retry_config.max_delay)
                    else:
                        logger.error(f"All {retry_config.max_attempts} attempts failed")

            # All attempts failed
            raise last_exception

        return wrapper
    return decorator


def _is_valid_result(result: Any) -> bool:
    """Check if scraping result is valid"""

    if not result:
        return False

    if not isinstance(result, dict):
        return False

    # Check for critical fields
    if 'company_name' not in result:
        return False

    # Check data completeness
    completeness = result.get('data_completeness_pct', 0)
    if completeness < 20:  # At least 20% complete
        return False

    return True


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 300.0,
        expected_exception: Exception = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    async def call(self, func: Callable, *args, **kwargs):
        """Call function with circuit breaker protection"""

        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half-open'
                logger.info("Circuit breaker: half-open, attempting reset")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is open. Too many failures. "
                    f"Will retry after {self.recovery_timeout}s"
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True

        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = 'closed'
        logger.debug("Circuit breaker: closed")

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            logger.error(
                f"Circuit breaker: OPEN after {self.failure_count} failures"
            )


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class ResilientScraper:
    """Wrapper for scrapers with resilience patterns"""

    def __init__(self, scraper, retry_config: RetryConfig = None):
        self.scraper = scraper
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker = CircuitBreaker()

    async def scrape_with_resilience(self) -> Dict:
        """Scrape with retry logic and circuit breaker"""

        @with_retry(self.retry_config)
        async def _scrape():
            return await self.circuit_breaker.call(
                self.scraper.scrape
            )

        return await _scrape()


if __name__ == "__main__":
    print("🛡️ Resilient Scraper Wrapper")
    print("=" * 50)
    print("Provides retry logic and circuit breaker patterns for scrapers")
    print("\nFeatures:")
    print("  • Exponential backoff retry")
    print("  • Circuit breaker to prevent cascading failures")
    print("  • Configurable retry parameters")
    print("  • Automatic result validation")
