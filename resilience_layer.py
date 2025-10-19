"""
Resilience Layer
Advanced error recovery, retry logic, and fallback strategies
"""

import asyncio
import sys
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
import json

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

BASE_DIR = Path(__file__).parent.resolve()
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)


class ResilientScraper:
    """Enhanced scraper with retry logic and fallbacks"""
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 30):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cache_ttl = 86400  # 24 hours
        self.failed_attempts = {}
    
    async def scrape_with_retry(
        self,
        scraper_func: Callable,
        company_name: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute scraper with automatic retry and fallback
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{self.max_retries} for {company_name}")
                
                # Execute scraper
                result = await scraper_func(*args, **kwargs)
                
                # Validate result
                if self._validate_result(result, company_name):
                    # Cache successful result
                    self._cache_result(company_name, result)
                    
                    # Reset failure counter
                    if company_name in self.failed_attempts:
                        del self.failed_attempts[company_name]
                    
                    logger.info(f"✅ {company_name}: Scraping successful")
                    return result
                else:
                    logger.warning(f"⚠️  {company_name}: Invalid result, retrying...")
                    
            except Exception as e:
                logger.error(f"❌ {company_name} attempt {attempt + 1} failed: {e}")
                
                # Track failures
                if company_name not in self.failed_attempts:
                    self.failed_attempts[company_name] = []
                self.failed_attempts[company_name].append({
                    'attempt': attempt + 1,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
                # Wait before retry (exponential backoff)
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
        
        # All retries failed - use fallback
        logger.warning(f"🔄 All retries failed for {company_name}, using fallback...")
        return await self._use_fallback(company_name)
    
    def _validate_result(self, result: Dict[str, Any], company_name: str) -> bool:
        """Validate scraping result"""
        # Check if result exists and has data
        if not result or 'results' not in result:
            return False
        
        # Check if we got actual price data
        if result.get('count', 0) == 0:
            return False
        
        # Check if prices are realistic
        results = result.get('results', [])
        for item in results:
            if 'price_text' in item:
                # Should contain currency symbol
                if '$' not in item['price_text'] and '€' not in item['price_text']:
                    return False
        
        return True
    
    def _cache_result(self, company_name: str, result: Dict[str, Any]):
        """Cache successful scraping result"""
        cache_file = CACHE_DIR / f"{company_name.lower().replace(' ', '_')}_cache.json"
        
        cache_data = {
            'company': company_name,
            'timestamp': datetime.now().isoformat(),
            'result': result
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.debug(f"💾 Cached result for {company_name}")
        except Exception as e:
            logger.error(f"Failed to cache result: {e}")
    
    def _get_cached_result(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if fresh"""
        cache_file = CACHE_DIR / f"{company_name.lower().replace(' ', '_')}_cache.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is fresh
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            age_seconds = (datetime.now() - cached_time).total_seconds()
            
            if age_seconds < self.cache_ttl:
                logger.info(f"💾 Using cached result for {company_name} ({age_seconds/3600:.1f}h old)")
                return cache_data['result']
            else:
                logger.debug(f"🕰️  Cache expired for {company_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to read cache: {e}")
            return None
    
    async def _use_fallback(self, company_name: str) -> Dict[str, Any]:
        """Use fallback strategies when scraping fails"""
        # Strategy 1: Use cached data
        cached = self._get_cached_result(company_name)
        if cached:
            logger.info(f"✅ Using cached data for {company_name}")
            cached['_from_cache'] = True
            cached['_cache_age_hours'] = self._get_cache_age(company_name)
            return cached
        
        # Strategy 2: Use last known good data from database
        logger.info(f"🔍 Attempting to use last known good data for {company_name}")
        last_good = self._get_last_known_good(company_name)
        if last_good:
            last_good['_from_database'] = True
            return last_good
        
        # Strategy 3: Return estimated/predicted price
        logger.warning(f"⚠️  No fallback data available for {company_name}, using estimate")
        return {
            'company': company_name,
            'results': [],
            'count': 0,
            '_estimated': True,
            '_error': 'All scraping attempts failed, no cache available'
        }
    
    def _get_cache_age(self, company_name: str) -> float:
        """Get age of cached data in hours"""
        cache_file = CACHE_DIR / f"{company_name.lower().replace(' ', '_')}_cache.json"
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            return (datetime.now() - cached_time).total_seconds() / 3600
        except:
            return 0
    
    def _get_last_known_good(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get last known good data from database"""
        try:
            import sqlite3
            db_path = BASE_DIR / "database" / "campervan_prices.db"
            
            if not db_path.exists():
                return None
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT base_price, discount_percentage, scrape_date
                FROM prices
                WHERE company_name = ?
                ORDER BY scrape_date DESC
                LIMIT 1
            """, (company_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'company': company_name,
                    'results': [{
                        'price_text': f"€{row[0]}/night",
                        'source': 'database_fallback',
                        'timestamp': row[2]
                    }],
                    'count': 1,
                    '_from_database': True,
                    '_last_known_date': row[2]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get last known good: {e}")
            return None
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate scraper health report"""
        cache_files = list(CACHE_DIR.glob("*_cache.json"))
        
        health = {
            'cached_companies': len(cache_files),
            'failed_companies': len(self.failed_attempts),
            'cache_status': [],
            'failures': []
        }
        
        # Cache status
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                age_hours = self._get_cache_age(cache_data['company'])
                health['cache_status'].append({
                    'company': cache_data['company'],
                    'age_hours': round(age_hours, 1),
                    'is_fresh': age_hours < 24
                })
            except:
                pass
        
        # Failure summary
        for company, attempts in self.failed_attempts.items():
            health['failures'].append({
                'company': company,
                'total_attempts': len(attempts),
                'last_error': attempts[-1]['error'] if attempts else None,
                'last_attempt': attempts[-1]['timestamp'] if attempts else None
            })
        
        return health
    
    def cleanup_cache(self, max_age_days: int = 7):
        """Clean up old cache files"""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        cleaned = 0
        
        for cache_file in CACHE_DIR.glob("*_cache.json"):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                
                if cache_time < cutoff:
                    cache_file.unlink()
                    cleaned += 1
                    logger.info(f"🗑️  Removed old cache: {cache_file.name}")
                    
            except Exception as e:
                logger.error(f"Failed to clean cache file {cache_file}: {e}")
        
        logger.info(f"✅ Cache cleanup complete: {cleaned} files removed")
        return cleaned


class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds
        self.failures = {}
        self.open_until = {}
    
    def can_execute(self, company_name: str) -> bool:
        """Check if circuit allows execution"""
        # Check if circuit is open
        if company_name in self.open_until:
            if datetime.now() < self.open_until[company_name]:
                logger.warning(f"🚫 Circuit OPEN for {company_name}, waiting...")
                return False
            else:
                # Timeout passed, try half-open
                logger.info(f"🔄 Circuit HALF-OPEN for {company_name}, attempting...")
                del self.open_until[company_name]
                self.failures[company_name] = 0
        
        return True
    
    def record_success(self, company_name: str):
        """Record successful execution"""
        if company_name in self.failures:
            self.failures[company_name] = 0
        if company_name in self.open_until:
            del self.open_until[company_name]
        logger.debug(f"✅ Circuit CLOSED for {company_name}")
    
    def record_failure(self, company_name: str):
        """Record failed execution"""
        if company_name not in self.failures:
            self.failures[company_name] = 0
        
        self.failures[company_name] += 1
        
        if self.failures[company_name] >= self.failure_threshold:
            # Open circuit
            self.open_until[company_name] = datetime.now() + timedelta(seconds=self.timeout)
            logger.error(
                f"⚡ Circuit OPENED for {company_name} "
                f"({self.failures[company_name]} failures, timeout: {self.timeout}s)"
            )


# Test/example usage
if __name__ == "__main__":
    async def test_scraper():
        """Test resilient scraper"""
        
        # Mock scraper function that sometimes fails
        async def mock_scrape(company: str):
            import random
            if random.random() < 0.3:  # 30% failure rate
                raise Exception("Scraping failed (simulated)")
            return {
                'company': company,
                'results': [{'price_text': '€95/night'}],
                'count': 1
            }
        
        resilient = ResilientScraper(max_retries=3, retry_delay=2)
        
        companies = ['Roadsurfer', 'McRent', 'Camperdays']
        
        for company in companies:
            print(f"\n🧪 Testing {company}...")
            result = await resilient.scrape_with_retry(mock_scrape, company, company)
            print(f"Result: {result.get('count', 0)} items scraped")
        
        # Health report
        print("\n📊 Health Report:")
        print(json.dumps(resilient.get_health_report(), indent=2))
    
    asyncio.run(test_scraper())
