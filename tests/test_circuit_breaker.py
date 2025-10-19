"""
Tests for Circuit Breaker Pattern Implementation
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
    CircuitBreakerRegistry,
    get_global_registry
)


class TestCircuitBreakerConfig:
    """Test CircuitBreakerConfig class"""

    def test_default_config(self):
        """Test default configuration values"""
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.timeout_seconds == 60
        assert config.half_open_max_calls == 3

    def test_custom_config(self):
        """Test custom configuration"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=1,
            timeout_seconds=30
        )
        assert config.failure_threshold == 3
        assert config.success_threshold == 1
        assert config.timeout_seconds == 30


class TestCircuitBreakerBasics:
    """Test basic circuit breaker functionality"""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test circuit breaker initialization"""
        breaker = CircuitBreaker("TestService")
        assert breaker.name == "TestService"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.metrics.total_calls == 0

    @pytest.mark.asyncio
    async def test_successful_call(self):
        """Test successful function call"""
        async def success_func():
            return "success"

        breaker = CircuitBreaker("TestService")
        result = await breaker.call(success_func)

        assert result == "success"
        assert breaker.metrics.successful_calls == 1
        assert breaker.metrics.failed_calls == 0
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_failed_call(self):
        """Test failed function call"""
        async def fail_func():
            raise ValueError("Test error")

        breaker = CircuitBreaker("TestService")

        with pytest.raises(ValueError):
            await breaker.call(fail_func)

        assert breaker.metrics.failed_calls == 1
        assert breaker.state == CircuitState.CLOSED  # Still closed, threshold not reached


class TestCircuitBreakerStates:
    """Test circuit breaker state transitions"""

    @pytest.mark.asyncio
    async def test_transition_to_open(self):
        """Test circuit transitions to OPEN after threshold failures"""
        async def fail_func():
            raise Exception("Failure")

        config = CircuitBreakerConfig(
            failure_threshold=3,
            min_calls_before_open=2
        )
        breaker = CircuitBreaker("TestService", config)

        # Trigger failures
        for _ in range(3):
            try:
                await breaker.call(fail_func)
            except Exception:
                pass

        assert breaker.state == CircuitState.OPEN
        assert breaker.metrics.failed_calls == 3

    @pytest.mark.asyncio
    async def test_open_circuit_blocks_calls(self):
        """Test OPEN circuit blocks calls"""
        async def fail_func():
            raise Exception("Failure")

        config = CircuitBreakerConfig(
            failure_threshold=2,
            min_calls_before_open=1
        )
        breaker = CircuitBreaker("TestService", config)

        # Open the circuit
        for _ in range(2):
            try:
                await breaker.call(fail_func)
            except Exception:
                pass

        assert breaker.state == CircuitState.OPEN

        # Try to make another call
        with pytest.raises(CircuitBreakerOpenError):
            await breaker.call(fail_func)

        assert breaker.metrics.rejected_calls == 1

    @pytest.mark.asyncio
    async def test_transition_to_half_open(self):
        """Test circuit transitions to HALF_OPEN after timeout"""
        async def fail_func():
            raise Exception("Failure")

        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=1,  # Short timeout for testing
            min_calls_before_open=1
        )
        breaker = CircuitBreaker("TestService", config)

        # Open the circuit
        for _ in range(2):
            try:
                await breaker.call(fail_func)
            except Exception:
                pass

        assert breaker.state == CircuitState.OPEN

        # Wait for timeout
        await asyncio.sleep(1.5)

        # Next call attempt should transition to HALF_OPEN
        try:
            await breaker.call(fail_func)
        except Exception:
            pass

        assert breaker.state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_half_open_to_closed_recovery(self):
        """Test successful recovery from HALF_OPEN to CLOSED"""
        call_count = [0]

        async def flaky_func():
            call_count[0] += 1
            # Fail first 3 calls, then succeed
            if call_count[0] <= 3:
                raise Exception("Failure")
            return "success"

        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=1,
            min_calls_before_open=1
        )
        breaker = CircuitBreaker("TestService", config)

        # Open the circuit
        for _ in range(2):
            try:
                await breaker.call(flaky_func)
            except Exception:
                pass

        assert breaker.state == CircuitState.OPEN

        # Wait for timeout
        await asyncio.sleep(1.5)

        # First call in HALF_OPEN fails, goes back to OPEN
        try:
            await breaker.call(flaky_func)
        except Exception:
            pass

        assert breaker.state == CircuitState.OPEN

        # Wait again
        await asyncio.sleep(1.5)

        # Now succeed twice to close circuit
        for _ in range(2):
            try:
                result = await breaker.call(flaky_func)
                assert result == "success"
            except Exception:
                pass

        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_half_open_failure_reopens(self):
        """Test failure in HALF_OPEN immediately reopens circuit"""
        async def fail_func():
            raise Exception("Failure")

        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=1,
            min_calls_before_open=1
        )
        breaker = CircuitBreaker("TestService", config)

        # Open the circuit
        for _ in range(2):
            try:
                await breaker.call(fail_func)
            except Exception:
                pass

        await asyncio.sleep(1.5)

        # Fail in HALF_OPEN
        try:
            await breaker.call(fail_func)
        except Exception:
            pass

        assert breaker.state == CircuitState.OPEN


class TestCircuitBreakerMetrics:
    """Test circuit breaker metrics tracking"""

    @pytest.mark.asyncio
    async def test_metrics_tracking(self):
        """Test metrics are correctly tracked"""
        call_count = [0]

        async def flaky_func():
            call_count[0] += 1
            if call_count[0] % 2 == 0:
                raise Exception("Failure")
            return "success"

        config = CircuitBreakerConfig(
            failure_threshold=10,  # High threshold to keep circuit closed
            min_calls_before_open=20
        )
        breaker = CircuitBreaker("TestService", config)

        # Make mixed calls
        for _ in range(6):
            try:
                await breaker.call(flaky_func)
            except Exception:
                pass

        assert breaker.metrics.total_calls == 6
        assert breaker.metrics.successful_calls == 3
        assert breaker.metrics.failed_calls == 3
        assert breaker.metrics.last_success_time is not None
        assert breaker.metrics.last_failure_time is not None

    @pytest.mark.asyncio
    async def test_recent_failure_rate(self):
        """Test recent failure rate calculation"""
        async def fail_func():
            raise Exception("Failure")

        breaker = CircuitBreaker("TestService")

        # All failures
        for _ in range(5):
            try:
                await breaker.call(fail_func)
            except Exception:
                pass

        failure_rate = breaker.metrics.get_recent_failure_rate()
        assert failure_rate == 1.0  # 100% failure


class TestCircuitBreakerStatus:
    """Test circuit breaker status reporting"""

    @pytest.mark.asyncio
    async def test_get_status(self):
        """Test status reporting"""
        async def success_func():
            return "success"

        breaker = CircuitBreaker("TestService")
        await breaker.call(success_func)

        status = breaker.get_status()

        assert status['name'] == "TestService"
        assert status['state'] == CircuitState.CLOSED.value
        assert 'metrics' in status
        assert 'current_state' in status
        assert 'config' in status
        assert status['metrics']['total_calls'] == 1
        assert status['metrics']['success_rate'] == 100.0

    @pytest.mark.asyncio
    async def test_manual_reset(self):
        """Test manual circuit reset"""
        async def fail_func():
            raise Exception("Failure")

        config = CircuitBreakerConfig(
            failure_threshold=2,
            min_calls_before_open=1
        )
        breaker = CircuitBreaker("TestService", config)

        # Open the circuit
        for _ in range(2):
            try:
                await breaker.call(fail_func)
            except Exception:
                pass

        assert breaker.state == CircuitState.OPEN

        # Reset
        await breaker.reset()

        assert breaker.state == CircuitState.CLOSED
        assert breaker._failure_count == 0


class TestCircuitBreakerRegistry:
    """Test circuit breaker registry"""

    @pytest.mark.asyncio
    async def test_registry_creation(self):
        """Test registry creates breakers on demand"""
        registry = CircuitBreakerRegistry()

        breaker1 = await registry.get_breaker("Service1")
        breaker2 = await registry.get_breaker("Service2")
        breaker1_again = await registry.get_breaker("Service1")

        assert breaker1.name == "Service1"
        assert breaker2.name == "Service2"
        assert breaker1 is breaker1_again  # Same instance

    @pytest.mark.asyncio
    async def test_registry_custom_config(self):
        """Test registry with custom config"""
        custom_config = CircuitBreakerConfig(failure_threshold=10)
        registry = CircuitBreakerRegistry(default_config=custom_config)

        breaker = await registry.get_breaker("TestService")

        assert breaker.config.failure_threshold == 10

    @pytest.mark.asyncio
    async def test_get_all_statuses(self):
        """Test getting all statuses from registry"""
        registry = CircuitBreakerRegistry()

        await registry.get_breaker("Service1")
        await registry.get_breaker("Service2")

        statuses = registry.get_all_statuses()

        assert len(statuses) == 2
        assert "Service1" in statuses
        assert "Service2" in statuses

    @pytest.mark.asyncio
    async def test_reset_all(self):
        """Test resetting all breakers"""
        async def fail_func():
            raise Exception("Failure")

        config = CircuitBreakerConfig(
            failure_threshold=1,
            min_calls_before_open=1
        )
        registry = CircuitBreakerRegistry(default_config=config)

        breaker1 = await registry.get_breaker("Service1")
        breaker2 = await registry.get_breaker("Service2")

        # Open both circuits
        for breaker in [breaker1, breaker2]:
            try:
                await breaker.call(fail_func)
            except Exception:
                pass

        assert breaker1.state == CircuitState.OPEN
        assert breaker2.state == CircuitState.OPEN

        # Reset all
        await registry.reset_all()

        assert breaker1.state == CircuitState.CLOSED
        assert breaker2.state == CircuitState.CLOSED


class TestGlobalRegistry:
    """Test global registry singleton"""

    def test_global_registry_singleton(self):
        """Test global registry is singleton"""
        registry1 = get_global_registry()
        registry2 = get_global_registry()

        assert registry1 is registry2


# Integration test with realistic scenario
class TestCircuitBreakerIntegration:
    """Integration tests with realistic scenarios"""

    @pytest.mark.asyncio
    async def test_scraper_simulation(self):
        """Simulate scraper with circuit breaker"""
        scrape_count = [0]

        async def scrape_website():
            """Simulated scraper that fails intermittently"""
            scrape_count[0] += 1
            await asyncio.sleep(0.1)  # Simulate network delay

            # Fail 70% of the time initially
            if scrape_count[0] < 10:
                if scrape_count[0] % 3 != 0:
                    raise Exception("Scraping failed")

            return {"company": "TestCompany", "price": 100}

        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=1,
            min_calls_before_open=2
        )

        breaker = CircuitBreaker("TestCompanyScraper", config)

        results = []
        errors = []

        # Simulate multiple scraping attempts
        for i in range(15):
            try:
                result = await breaker.call(scrape_website)
                results.append(result)
            except CircuitBreakerOpenError as e:
                errors.append(('blocked', str(e)))
            except Exception as e:
                errors.append(('failed', str(e)))

            await asyncio.sleep(0.2)

        # Verify circuit breaker prevented some attempts
        assert len(errors) > 0
        assert any(err_type == 'blocked' for err_type, _ in errors)
        assert breaker.metrics.rejected_calls > 0

        # Eventually some should succeed
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
