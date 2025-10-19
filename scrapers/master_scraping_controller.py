"""
Master Scraping Controller
Ultimate scraping system that runs until 100% completion
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus import browser, Driver
import asyncio
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/master_controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterScrapingController:
    def __init__(self):
        self.companies = [
            'Roadsurfer', 'Camperdays', 'Goboony', 'Outdoorsy', 'RVshare',
            'McRent', 'Yescapa', 'Cruise America'
        ]
        self.target_days = 365
        self.completion_threshold = 100.0
        self.max_retries = 10
        self.state_file = "output/scraping_state.json"
        self.progress_file = "output/live_progress.json"
        self.results_file = "output/ultimate_results.json"
        
        # Initialize state
        self.state = self.load_state()
        self.failure_count = {}
        
        # Create necessary directories
        Path("output").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path("data/screenshots").mkdir(parents=True, exist_ok=True)
    
    def load_state(self) -> Dict:
        """Load previous scraping state"""
        if Path(self.state_file).exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading state: {e}")
        return {}
    
    def save_state(self):
        """Save current scraping state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def get_completion_status(self) -> Dict:
        """Get current completion status"""
        total_companies = len(self.companies)
        completed_companies = 0
        total_days_scraped = 0
        total_target_days = total_companies * self.target_days
        
        for company in self.companies:
            company_data = self.state.get(company, {})
            if self.is_company_complete(company_data):
                completed_companies += 1
            
            days_scraped = len(company_data.get('daily_prices', []))
            total_days_scraped += days_scraped
        
        overall_percentage = (total_days_scraped / total_target_days) * 100
        
        return {
            'total_companies': total_companies,
            'completed_companies': completed_companies,
            'total_days_scraped': total_days_scraped,
            'total_target_days': total_target_days,
            'overall_percentage': overall_percentage,
            'companies_status': {company: self.get_company_status(company) for company in self.companies}
        }
    
    def is_company_complete(self, company_data: Dict) -> bool:
        """Check if company data is complete"""
        daily_prices = company_data.get('daily_prices', [])
        vehicles = company_data.get('vehicles', [])
        
        return (
            len(daily_prices) >= self.target_days and
            len(vehicles) > 0 and
            company_data.get('success', False)
        )
    
    def get_company_status(self, company: str) -> Dict:
        """Get status for specific company"""
        company_data = self.state.get(company, {})
        daily_prices = company_data.get('daily_prices', [])
        vehicles = company_data.get('vehicles', [])
        
        return {
            'complete': self.is_company_complete(company_data),
            'days_scraped': len(daily_prices),
            'target_days': self.target_days,
            'vehicles_found': len(vehicles),
            'success': company_data.get('success', False),
            'last_updated': company_data.get('last_updated'),
            'completion_percentage': (len(daily_prices) / self.target_days) * 100
        }
    
    def get_incomplete_companies(self) -> List[str]:
        """Get list of companies that need more work"""
        incomplete = []
        for company in self.companies:
            company_data = self.state.get(company, {})
            if not self.is_company_complete(company_data):
                incomplete.append(company)
        return incomplete
    
    def scrape_company_365_days(self, company: str) -> Dict:
        """Scrape 365 days of data for specific company"""
        logger.info(f"🎯 SCRAPING {company} - 365 DAYS")
        
        try:
            if company in ['McRent', 'Yescapa', 'Cruise America']:
                # Use advanced strategies for failing companies
                result = self.scrape_failing_company_advanced(company)
            else:
                # Use standard scraping for working companies
                result = self.scrape_working_company_standard(company)
            
            # Update state
            self.state[company] = {
                **result,
                'last_updated': datetime.now().isoformat(),
                'scraping_attempts': self.state.get(company, {}).get('scraping_attempts', 0) + 1
            }
            self.save_state()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error scraping {company}: {e}")
            self.handle_failure(company, str(e))
            return {
                'company_name': company,
                'success': False,
                'error': str(e),
                'daily_prices': [],
                'vehicles': []
            }
    
    def scrape_failing_company_advanced(self, company: str) -> Dict:
        """Advanced scraping for failing companies"""
        logger.info(f"🔧 ADVANCED SCRAPING: {company}")
        
        # Try multiple strategies
        strategies = [
            'playwright_stealth',
            'botasaurus_stealth',
            'mobile_user_agent',
            'different_browser',
            'proxy_rotation'
        ]
        
        for strategy in strategies:
            try:
                logger.info(f"🔄 Trying strategy: {strategy}")
                result = self.execute_strategy(company, strategy)
                
                if result.get('success', False):
                    logger.info(f"✅ SUCCESS with {strategy} for {company}")
                    return result
                else:
                    logger.warning(f"❌ Strategy {strategy} failed for {company}")
                    
            except Exception as e:
                logger.error(f"❌ Strategy {strategy} error for {company}: {e}")
                continue
        
        # All strategies failed
        return {
            'company_name': company,
            'success': False,
            'error': 'All advanced strategies failed',
            'daily_prices': [],
            'vehicles': []
        }
    
    def execute_strategy(self, company: str, strategy: str) -> Dict:
        """Execute specific scraping strategy"""
        if strategy == 'playwright_stealth':
            return self.scrape_with_playwright_stealth(company)
        elif strategy == 'botasaurus_stealth':
            return self.scrape_with_botasaurus_stealth(company)
        elif strategy == 'mobile_user_agent':
            return self.scrape_with_mobile_ua(company)
        else:
            return {'success': False, 'error': f'Strategy {strategy} not implemented'}
    
    async def scrape_with_playwright_stealth(self, company: str) -> Dict:
        """Scrape using Playwright with stealth"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                # Navigate to company URL
                url = self.get_company_url(company)
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Handle cookies
                await self.handle_cookies_playwright(page)
                
                # Extract data
                result = await self.extract_company_data_playwright(page, company)
                
                await browser.close()
                return result
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scrape_with_botasaurus_stealth(self, company: str) -> Dict:
        """Scrape using Botasaurus with stealth"""
        @browser(headless=False, stealth=True, anti_detection=True)
        def scrape_company(driver: Driver):
            try:
                url = self.get_company_url(company)
                driver.get(url)
                time.sleep(5)
                
                # Handle cookies
                self.handle_cookies_botasaurus(driver)
                
                # Extract data
                result = self.extract_company_data_botasaurus(driver, company)
                return result
                
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        return scrape_company()
    
    def get_company_url(self, company: str) -> str:
        """Get primary URL for company"""
        urls = {
            'Roadsurfer': 'https://roadsurfer.com/',
            'Camperdays': 'https://www.camperdays.com/',
            'Goboony': 'https://www.goboony.com/',
            'Outdoorsy': 'https://www.outdoorsy.com/',
            'RVshare': 'https://www.rvshare.com/',
            'McRent': 'https://www.mcrent.de/',
            'Yescapa': 'https://www.yescapa.com/',
            'Cruise America': 'https://www.cruiseamerica.com/'
        }
        return urls.get(company, '')
    
    async def handle_cookies_playwright(self, page):
        """Handle cookie popups with Playwright"""
        try:
            # Try common cookie selectors
            selectors = [
                'button[id*="accept"]',
                'button[class*="accept"]',
                'button:has-text("Accept")',
                'button:has-text("OK")',
                'button:has-text("I agree")'
            ]
            
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.click()
                        await page.wait_for_timeout(1000)
                        break
                except:
                    continue
        except Exception as e:
            logger.warning(f"Cookie handling failed: {e}")
    
    def handle_cookies_botasaurus(self, driver: Driver):
        """Handle cookie popups with Botasaurus"""
        try:
            selectors = [
                'button[id*="accept"]',
                'button[class*="accept"]',
                'button[class*="cookie"]'
            ]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            time.sleep(1)
                            break
                except:
                    continue
        except Exception as e:
            logger.warning(f"Cookie handling failed: {e}")
    
    async def extract_company_data_playwright(self, page, company: str) -> Dict:
        """Extract company data using Playwright"""
        try:
            # Extract vehicles
            vehicles = await self.extract_vehicles_playwright(page, company)
            
            # Extract 365 days of pricing
            daily_prices = await self.extract_365_days_playwright(page, company)
            
            return {
                'company_name': company,
                'success': True,
                'vehicles': vehicles,
                'daily_prices': daily_prices,
                'total_results': len(daily_prices),
                'currency': self.get_company_currency(company),
                'strategy_used': 'playwright_stealth'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def extract_company_data_botasaurus(self, driver: Driver, company: str) -> Dict:
        """Extract company data using Botasaurus"""
        try:
            # Extract vehicles
            vehicles = self.extract_vehicles_botasaurus(driver, company)
            
            # Extract 365 days of pricing
            daily_prices = self.extract_365_days_botasaurus(driver, company)
            
            return {
                'company_name': company,
                'success': True,
                'vehicles': vehicles,
                'daily_prices': daily_prices,
                'total_results': len(daily_prices),
                'currency': self.get_company_currency(company),
                'strategy_used': 'botasaurus_stealth'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_company_currency(self, company: str) -> str:
        """Get currency for company"""
        eur_companies = ['Roadsurfer', 'Camperdays', 'Goboony', 'McRent', 'Yescapa']
        return 'EUR' if company in eur_companies else 'USD'
    
    def handle_failure(self, company: str, error: str):
        """Handle scraping failures"""
        if company not in self.failure_count:
            self.failure_count[company] = 0
        
        self.failure_count[company] += 1
        
        logger.error(f"❌ FAILURE #{self.failure_count[company]} for {company}: {error}")
        
        if self.failure_count[company] >= self.max_retries:
            logger.error(f"🚨 MAX RETRIES REACHED for {company}")
            self.create_manual_intervention_ticket(company, error)
    
    def create_manual_intervention_ticket(self, company: str, error: str):
        """Create manual intervention ticket"""
        ticket_data = {
            'company': company,
            'error': error,
            'failure_count': self.failure_count[company],
            'timestamp': datetime.now().isoformat(),
            'required_action': 'Manual scraping required',
            'priority': 'HIGH'
        }
        
        ticket_file = f"output/manual_intervention_{company}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(ticket_file, 'w') as f:
            json.dump(ticket_data, f, indent=2)
        
        logger.error(f"🚨 MANUAL INTERVENTION TICKET CREATED: {ticket_file}")
    
    def run_until_complete(self):
        """Main execution loop - runs until 100% completion"""
        logger.info("🚀 STARTING MASTER SCRAPING CONTROLLER")
        logger.info("="*80)
        logger.info("🎯 TARGET: 100% COMPLETION - ALL 8 COMPANIES - 365 DAYS EACH")
        logger.info("="*80)
        
        cycle = 0
        while True:
            cycle += 1
            logger.info(f"\n🔄 SCRAPING CYCLE {cycle}")
            logger.info("-" * 50)
            
            # Check current status
            status = self.get_completion_status()
            logger.info(f"📊 Current completion: {status['overall_percentage']:.1f}%")
            logger.info(f"📊 Companies complete: {status['completed_companies']}/{status['total_companies']}")
            
            # Check if 100% complete
            if status['overall_percentage'] >= self.completion_threshold:
                logger.info("🎉 100% COMPLETION ACHIEVED!")
                self.final_validation()
                break
            
            # Get incomplete companies
            incomplete_companies = self.get_incomplete_companies()
            logger.info(f"📋 Incomplete companies: {incomplete_companies}")
            
            # Scrape incomplete companies
            for company in incomplete_companies:
                logger.info(f"\n🎯 Processing: {company}")
                result = self.scrape_company_365_days(company)
                
                if result.get('success', False):
                    logger.info(f"✅ SUCCESS: {company} - {result.get('total_results', 0)} days")
                else:
                    logger.error(f"❌ FAILED: {company} - {result.get('error', 'Unknown error')}")
            
            # Save progress
            self.save_progress_report()
            
            # Wait before next cycle
            logger.info(f"⏳ Waiting 60 seconds before next cycle...")
            time.sleep(60)
    
    def save_progress_report(self):
        """Save comprehensive progress report"""
        status = self.get_completion_status()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_completion': status['overall_percentage'],
            'companies_status': status['companies_status'],
            'total_days_scraped': status['total_days_scraped'],
            'total_target_days': status['total_target_days'],
            'incomplete_companies': self.get_incomplete_companies(),
            'failure_counts': self.failure_count
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    
    def final_validation(self):
        """Perform final validation of all data"""
        logger.info("🔍 PERFORMING FINAL VALIDATION")
        logger.info("="*50)
        
        validation_results = {
            'all_companies_complete': True,
            'all_365_days_present': True,
            'all_vehicles_found': True,
            'overall_validation': True
        }
        
        for company in self.companies:
            company_data = self.state.get(company, {})
            company_complete = self.is_company_complete(company_data)
            
            logger.info(f"{company}: {'✅ COMPLETE' if company_complete else '❌ INCOMPLETE'}")
            
            validation_results['all_companies_complete'] &= company_complete
        
        validation_results['overall_validation'] = validation_results['all_companies_complete']
        
        if validation_results['overall_validation']:
            logger.info("🎉 FINAL VALIDATION PASSED - 100% COMPLETION ACHIEVED!")
        else:
            logger.error("❌ FINAL VALIDATION FAILED - INCOMPLETE DATA DETECTED")
        
        # Save final results
        final_results = {
            'timestamp': datetime.now().isoformat(),
            'validation_results': validation_results,
            'all_data': self.state,
            'completion_percentage': self.get_completion_status()['overall_percentage']
        }
        
        with open(self.results_file, 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        
        logger.info(f"💾 Final results saved to: {self.results_file}")

# Placeholder methods for data extraction
async def extract_vehicles_playwright(self, page, company: str) -> List[Dict]:
    """Extract vehicle information using Playwright"""
    # Implementation needed
    return []

async def extract_365_days_playwright(self, page, company: str) -> List[Dict]:
    """Extract 365 days of pricing using Playwright"""
    # Implementation needed
    return []

def extract_vehicles_botasaurus(self, driver: Driver, company: str) -> List[Dict]:
    """Extract vehicle information using Botasaurus"""
    # Implementation needed
    return []

def extract_365_days_botasaurus(self, driver: Driver, company: str) -> List[Dict]:
    """Extract 365 days of pricing using Botasaurus"""
    # Implementation needed
    return []

if __name__ == "__main__":
    controller = MasterScrapingController()
    controller.run_until_complete()



