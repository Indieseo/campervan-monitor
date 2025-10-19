"""
Circuit Breaker Pattern Implementation

Prevents repeated attempts to execute operations that are likely to fail,
allowing the system to detect failures and prevent cascading issues.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Failure threshold reached, requests fail immediately
- HALF_OPEN: Testing if service recovered, limited requests allowed
"""

import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, Optional, Any
from loguru import logger
from dataclasses import dataclass, field


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"          # Normal operation
    OPEN = "open"              # Blocking requests
    HALF_OPEN = "half_open"    # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5              # Failures before opening
    success_threshold: int = 2              # Successes in half-open to close
    timeout_seconds: int = 60               # Time before attempting recovery
    half_open_max_calls: int = 3            # Max calls in half-open state

    # Additional monitoring
    monitor_window_seconds: int = 300       # 5-minute rolling window
    min_calls_before_open: int = 3          # Minimum calls before considering circuit open


@dataclass
class CircuitBreakerMetrics:
    """Metrics tracked by circuit breaker"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changes: int = 0

    # Recent history for rolling window
    recent_calls: list = field(default_factory=list)

    def add_call(self, success: bool, timestamp: datetime):
        """Add a call to recent history"""
        self.recent_calls.append({
            'success': success,
            'timestamp': timestamp
        })
        # Keep only recent calls (last 300 seconds by default)
        cutoff = timestamp - timedelta(seconds=300)
        self.recent_calls = [
            c for c in self.recent_calls
            if c['timestamp'] > cutoff
        ]

    def get_recent_failure_rate(self) -> float:
        """Calculate failure rate in recent window"""
        if not self.recent_calls:
            return 0.0
        failures = sum(1 for c in self.recent_calls if not c['success'])
        return failures / len(self.recent_calls)


class CircuitBreaker:
    """
    Circuit Breaker for protecting against cascading failures.

    Usage:
        breaker = CircuitBreaker("MyService", config)
        result = await breaker.call(my_async_function, arg1, arg2)

    Example:
        async def scrape_website():
            # ... scraping logic ...
            return data

        breaker = CircuitBreaker("Roadsurfer")
        try:
            data = await breaker.call(scrape_website)
        except CircuitBreakerOpenError:
            logger.warning("Circuit breaker is open, skipping")
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()

        # State management
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
        self._last_state_change = datetime.now()
        self._lock = asyncio.Lock()

        logger.info(f"🔌 Circuit breaker initialized: {name}")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception from func if circuit is closed
        """
        async with self._lock:
            # Check if circuit should transition states
            await self._check_state_transition()

            # Handle based on current state
            if self.state == CircuitState.OPEN:
                self.metrics.rejected_calls += 1
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service unavailable until timeout expires."
                )

            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    self.metrics.rejected_calls += 1
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is HALF_OPEN but max test calls reached."
                    )
                self._half_open_calls += 1

        # Execute the function (outside lock to prevent blocking)
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result

        except Exception as e:
            await self._on_failure(e)
            raise

    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            now = datetime.now()
            self.metrics.total_calls += 1
            self.metrics.successful_calls += 1
            self.metrics.last_success_time = now
            self.metrics.add_call(success=True, timestamp=now)

            self._failure_count = 0

            if self.state == CircuitState.HALF_OPEN:
                self._success_count += 1
                logger.info(
                    f"✅ {self.name}: Success in HALF_OPEN "
                    f"({self._success_count}/{self.config.success_threshold})"
                )

                if self._success_count >= self.config.success_threshold:
                    await self._transition_to_closed()

            elif self.state == CircuitState.CLOSED:
                logger.debug(f"✅ {self.name}: Successful call")

    async def _on_failure(self, exception: Exception):
        """Handle failed call"""
        async with self._lock:
            now = datetime.now()
            self.metrics.total_calls += 1
            self.metrics.failed_calls += 1
            self.metrics.last_failure_time = now
            self.metrics.add_call(success=False, timestamp=now)

            self._failure_count += 1

            logger.warning(
                f"❌ {self.name}: Failure #{self._failure_count} - {exception}"
            )

            if self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open immediately opens circuit
                await self._transition_to_open()

            elif self.state == CircuitState.CLOSED:
                # Check if we should open circuit
                if (self._failure_count >= self.config.failure_threshold and
                    self.metrics.total_calls >= self.config.min_calls_before_open):
                    await self._transition_to_open()

    async def _check_state_transition(self):
        """Check if circuit should transition based on timeout"""
        if self.state == CircuitState.OPEN:
            elapsed = datetime.now() - self._last_state_change
            if elapsed.total_seconds() >= self.config.timeout_seconds:
                await self._transition_to_half_open()

    async def _transition_to_open(self):
        """Transition to OPEN state"""
        self.state = CircuitState.OPEN
        self._last_state_change = datetime.now()
        self.metrics.state_changes += 1

        failure_rate = self.metrics.get_recent_failure_rate()

        logger.error(
            f"🚨 {self.name}: Circuit OPENED! "
            f"Failures: {self._failure_count}/{self.config.failure_threshold}, "
            f"Recent failure rate: {failure_rate:.1%}, "
            f"Timeout: {self.config.timeout_seconds}s"
        )

    async def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        self.state = CircuitState.HALF_OPEN
        self._last_state_change = datetime.now()
        self._success_count = 0
        self._failure_count = 0
        self._half_open_calls = 0
        self.metrics.state_changes += 1

        logger.info(
            f"🔄 {self.name}: Circuit HALF_OPEN - Testing recovery "
            f"(max {self.config.half_open_max_calls} calls)"
        )

    async def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self.state = CircuitState.CLOSED
        self._last_state_change = datetime.now()
        self._success_count = 0
        self._failure_count = 0
        self._half_open_calls = 0
        self.metrics.state_changes += 1

        logger.info(f"✅ {self.name}: Circuit CLOSED - Service recovered!")

    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            'name': self.name,
            'state': self.state.value,
            'metrics': {
                'total_calls': self.metrics.total_calls,
                'successful_calls': self.metrics.successful_calls,
                'failed_calls': self.metrics.failed_calls,
                'rejected_calls': self.metrics.rejected_calls,
                'success_rate': (
                    self.metrics.successful_calls / self.metrics.total_calls * 100
                    if self.metrics.total_calls > 0 else 0
                ),
                'recent_failure_rate': self.metrics.get_recent_failure_rate() * 100,
                'state_changes': self.metrics.state_changes
            },
            'current_state': {
                'failure_count': self._failure_count,
                'success_count': self._success_count,
                'half_open_calls': self._half_open_calls,
                'last_state_change': self._last_state_change.isoformat()
            },
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'success_threshold': self.config.success_threshold,
                'timeout_seconds': self.config.timeout_seconds
            }
        }

    async def reset(self):
        """Manually reset circuit breaker to closed state"""
        async with self._lock:
            await self._transition_to_closed()
            logger.warning(f"🔄 {self.name}: Circuit breaker manually reset")


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and blocking requests"""
    pass


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.

    Usage:
        registry = CircuitBreakerRegistry()
        breaker = registry.get_breaker("Roadsurfer")
        result = await breaker.call(scrape_function)
    """

    def __init__(self, default_config: Optional[CircuitBreakerConfig] = None):
        self.default_config = default_config or CircuitBreakerConfig()
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

    async def get_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get or create circuit breaker for a service"""
        async with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(
                    name,
                    config or self.default_config
                )
            return self._breakers[name]

    def get_all_statuses(self) -> Dict[str, Dict]:
        """Get status of all circuit breakers"""
        return {
            name: breaker.get_status()
            for name, breaker in self._breakers.items()
        }

    async def reset_all(self):
        """Reset all circuit breakers"""
        async with self._lock:
            for breaker in self._breakers.values():
                await breaker.reset()
        logger.warning("🔄 All circuit breakers reset")


# Global registry instance
_global_registry: Optional[CircuitBreakerRegistry] = None


def get_global_registry() -> CircuitBreakerRegistry:
    """Get global circuit breaker registry (singleton)"""
    global _global_registry
    if _global_registry is None:
        _global_registry = CircuitBreakerRegistry()
    return _global_registry


# Example usage and testing
if __name__ == "__main__":
    async def test_circuit_breaker():
        """Test circuit breaker functionality"""
        print("🔌 Circuit Breaker Test Suite")
        print("=" * 60)

        # Test function that fails sometimes
        call_count = 0

        async def flaky_service():
            nonlocal call_count
            call_count += 1

            # Fail first 5 calls, then succeed
            if call_count <= 5:
                raise Exception(f"Service failure #{call_count}")

            return {"status": "success", "call": call_count}

        # Create circuit breaker with low thresholds for testing
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=2,
            half_open_max_calls=2
        )

        breaker = CircuitBreaker("TestService", config)

        # Test 1: Cause failures to open circuit
        print("\n📍 Test 1: Triggering circuit opening...")
        for i in range(5):
            try:
                await breaker.call(flaky_service)
            except CircuitBreakerOpenError as e:
                print(f"  ⚠️  Call {i+1}: Circuit breaker open - {e}")
            except Exception as e:
                print(f"  ❌ Call {i+1}: Service failed - {e}")
            await asyncio.sleep(0.1)

        # Test 2: Show circuit is blocking
        print("\n📍 Test 2: Verify circuit is blocking...")
        try:
            await breaker.call(flaky_service)
        except CircuitBreakerOpenError:
            print("  ✅ Circuit correctly blocking calls")

        # Test 3: Wait for timeout and test recovery
        print(f"\n📍 Test 3: Waiting {config.timeout_seconds}s for timeout...")
        await asyncio.sleep(config.timeout_seconds + 0.5)

        print("  Testing recovery in HALF_OPEN state...")
        for i in range(3):
            try:
                result = await breaker.call(flaky_service)
                print(f"  ✅ Call {i+1}: Success - {result}")
            except Exception as e:
                print(f"  ❌ Call {i+1}: Failed - {e}")
            await asyncio.sleep(0.1)

        # Print final status
        print("\n📊 Final Status:")
        status = breaker.get_status()
        print(f"  State: {status['state'].upper()}")
        print(f"  Total Calls: {status['metrics']['total_calls']}")
        print(f"  Success Rate: {status['metrics']['success_rate']:.1f}%")
        print(f"  State Changes: {status['metrics']['state_changes']}")
        print(f"  Rejected Calls: {status['metrics']['rejected_calls']}")

        print("\n✅ Test complete!")

    # Run test
    asyncio.run(test_circuit_breaker())
