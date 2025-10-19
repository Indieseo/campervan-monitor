"""
Scraper Orchestrator - Runs all booking scrapers with intelligent scheduling
"""

import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from loguru import logger

from .booking_scrapers import (
    RoadsurferBookingScraper,
    CruiseAmericaBookingScraper,
    GenericBookingScraper
)
from .scraper_config import COMPETITOR_CONFIGS, get_companies_by_strategy

# Windows async fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

BASE_DIR = Path(__file__).parent.parent.resolve()


class ScraperOrchestrator:
    """Manages and coordinates all scraping operations"""
    
    def __init__(self, use_browserless: bool = True, max_concurrent: int = 3):
        self.use_browserless = use_browserless
        self.max_concurrent = max_concurrent
        self.results = []
    
    def _create_scraper(self, company_name: str, config: Dict[str, Any]):
        """Create appropriate scraper based on company and strategy"""
        
        # Use specialized scrapers for known companies
        if company_name == "Roadsurfer":
            return RoadsurferBookingScraper(self.use_browserless)
        elif company_name == "Cruise America":
            return CruiseAmericaBookingScraper(self.use_browserless)
        else:
            # Use generic scraper for others
            return GenericBookingScraper(company_name, config, self.use_browserless)
    
    async def scrape_company(self, company_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape a single company"""
        try:
            scraper = self._create_scraper(company_name, config)
            result = await scraper.scrape()
            return result
        except Exception as e:
            logger.error(f"Failed to scrape {company_name}: {e}")
            return {
                'company': company_name,
                'results': [],
                'count': 0,
                'success': False,
                'error': str(e)
            }
    
    async def scrape_batch(self, companies: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple companies with concurrency control"""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def scrape_with_limit(company_name: str):
            async with semaphore:
                config = COMPETITOR_CONFIGS.get(company_name, {})
                logger.info(f"🚀 Starting scrape: {company_name}")
                result = await self.scrape_company(company_name, config)
                logger.info(f"✅ Completed: {company_name} - {result['count']} items")
                return result
        
        tasks = [scrape_with_limit(company) for company in companies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Exception for {companies[i]}: {result}")
                valid_results.append({
                    'company': companies[i],
                    'results': [],
                    'count': 0,
                    'success': False,
                    'error': str(result)
                })
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def scrape_by_strategy(self, strategy: str) -> List[Dict[str, Any]]:
        """Scrape all companies using a specific strategy"""
        companies = get_companies_by_strategy(strategy)
        logger.info(f"Scraping {len(companies)} companies with '{strategy}' strategy")
        return await self.scrape_batch(companies)
    
    async def scrape_all(self, limit: int = None) -> List[Dict[str, Any]]:
        """Scrape all configured companies"""
        companies = list(COMPETITOR_CONFIGS.keys())
        
        if limit:
            companies = companies[:limit]
        
        logger.info(f"Starting scrape of {len(companies)} companies")
        logger.info(f"Max concurrent: {self.max_concurrent}")
        logger.info(f"Using Browserless: {self.use_browserless}")
        
        results = await self.scrape_batch(companies)
        self.results = results
        return results
    
    async def scrape_priority_companies(self) -> List[Dict[str, Any]]:
        """Scrape high-priority companies first"""
        priority_companies = [
            "Roadsurfer",
            "Cruise America", 
            "Indie Campers",
            "Apollo Campers",
            "Escape Campervans",
            "Jucy Rentals",
            "Spaceships Rentals"
        ]
        
        logger.info(f"Scraping {len(priority_companies)} priority companies")
        return await self.scrape_batch(priority_companies)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of scraping results"""
        if not self.results:
            return {"error": "No results available"}
        
        total_companies = len(self.results)
        successful = sum(1 for r in self.results if r.get('success'))
        failed = total_companies - successful
        total_prices = sum(r.get('count', 0) for r in self.results)
        
        return {
            'total_companies': total_companies,
            'successful': successful,
            'failed': failed,
            'success_rate': f"{(successful/total_companies*100):.1f}%",
            'total_prices_extracted': total_prices,
            'avg_prices_per_company': f"{total_prices/total_companies:.1f}",
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, filepath: str = None):
        """Save results to JSON file"""
        import json
        
        if filepath is None:
            filepath = BASE_DIR / "data" / f"scrape_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            'summary': self.get_summary(),
            'results': self.results,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Results saved to: {filepath}")
        return filepath


async def test_single_company(company_name: str = "Roadsurfer"):
    """Quick test of a single company"""
    logger.info(f"Testing single company: {company_name}")
    
    orchestrator = ScraperOrchestrator(use_browserless=True, max_concurrent=1)
    config = COMPETITOR_CONFIGS.get(company_name, {})
    
    result = await orchestrator.scrape_company(company_name, config)
    
    print("\n" + "="*80)
    print(f"TEST RESULT: {company_name}")
    print("="*80)
    print(f"Success: {result['success']}")
    print(f"Items found: {result['count']}")
    
    if result['results']:
        print("\nExtracted Data:")
        for item in result['results'][:5]:
            print(f"  - {item.get('price_text', 'N/A')}")
    
    return result


async def test_priority_companies():
    """Test priority companies"""
    logger.info("Testing priority companies...")
    
    orchestrator = ScraperOrchestrator(use_browserless=True, max_concurrent=2)
    results = await orchestrator.scrape_priority_companies()
    
    summary = orchestrator.get_summary()
    
    print("\n" + "="*80)
    print("PRIORITY COMPANIES TEST RESULTS")
    print("="*80)
    print(f"Total Companies: {summary['total_companies']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Total Prices: {summary['total_prices_extracted']}")
    print(f"Avg per Company: {summary['avg_prices_per_company']}")
    
    print("\nDetailed Results:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['company']}: {result['count']} items")
    
    # Save results
    filepath = orchestrator.save_results()
    print(f"\n💾 Results saved to: {filepath}")
    
    return results


async def run_full_scrape(limit: int = None):
    """Run full scraping operation"""
    logger.info("Starting full scrape operation...")
    
    orchestrator = ScraperOrchestrator(use_browserless=True, max_concurrent=3)
    results = await orchestrator.scrape_all(limit=limit)
    
    summary = orchestrator.get_summary()
    
    print("\n" + "="*80)
    print("FULL SCRAPE RESULTS")
    print("="*80)
    print(f"Total Companies: {summary['total_companies']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Total Prices: {summary['total_prices_extracted']}")
    
    print("\nTop Performers:")
    sorted_results = sorted(results, key=lambda x: x.get('count', 0), reverse=True)
    for result in sorted_results[:10]:
        if result['success']:
            print(f"  ✅ {result['company']}: {result['count']} prices")
    
    print("\nFailed Companies:")
    for result in sorted_results:
        if not result['success']:
            error = result.get('error', 'Unknown error')
            print(f"  ❌ {result['company']}: {error[:60]}")
    
    # Save results
    filepath = orchestrator.save_results()
    print(f"\n💾 Full results saved to: {filepath}")
    
    return results


if __name__ == "__main__":
    import sys
    
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # Add file logging
    log_file = BASE_DIR / "logs" / f"scraper_{datetime.now().strftime('%Y%m%d')}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.add(log_file, rotation="10 MB")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            # Test single company
            company = sys.argv[2] if len(sys.argv) > 2 else "Roadsurfer"
            asyncio.run(test_single_company(company))
        
        elif command == "priority":
            # Test priority companies
            asyncio.run(test_priority_companies())
        
        elif command == "full":
            # Run full scrape
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            asyncio.run(run_full_scrape(limit=limit))
        
        else:
            print("Unknown command. Use: test, priority, or full")
    
    else:
        # Default: test priority companies
        print("Running priority companies test (use 'full' for all companies)")
        asyncio.run(test_priority_companies())
