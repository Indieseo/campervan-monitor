"""
Improved Scrapers - Interactive Booking Flow Approach
Each scraper navigates through the booking process to extract real prices
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
from loguru import logger
from .base_scraper import DeepDataScraper

# Windows async fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class ImprovedCruiseAmericaScraper(DeepDataScraper):
    """Scraper for Cruise America - Simulates booking flow"""
    
    def __init__(self, use_browserless: bool = True):
        config = {'url': 'https://www.cruiseamerica.com/rv-reservations'}
        super().__init__("Cruise America", tier=1, config=config, use_browserless=use_browserless)
        self.quote_url = "https://www.cruiseamerica.com/rv-reservations"
    
    async def scrape(self) -> Dict[str, Any]:
        """Scrape prices by simulating a booking request"""
        browser = await self.get_browser()
        results = []
        
        try:
            page = await browser.new_page()
            
            # Navigate to quote/booking page (not homepage!)
            success = await self.navigate_smart(page, self.quote_url, wait_strategy='load')
            if not success:
                raise Exception("Failed to load booking page")
            
            await self.save_screenshot(page, "booking_page_initial")
            
            # Strategy 1: Look for sample pricing on page
            price_containers = await page.query_selector_all('[class*="price"], [class*="rate"], [class*="cost"]')
            logger.info(f"Found {len(price_containers)} potential price elements")
            
            for container in price_containers[:10]:
                try:
                    text = await container.inner_text()
                    # Look for dollar amounts
                    if '$' in text and any(char.isdigit() for char in text):
                        results.append({
                            'company': self.company_name,
                            'price_text': text.strip(),
                            'source': 'sample_pricing',
                            'timestamp': datetime.now().isoformat()
                        })
                except:
                    pass
            
            # Strategy 2: Try to interact with date picker if available
            try:
                # Example: Fill in sample dates (adjust selectors based on actual site)
                pickup_date = (datetime.now() + timedelta(days=30)).strftime('%m/%d/%Y')
                return_date = (datetime.now() + timedelta(days=37)).strftime('%m/%d/%Y')
                
                # Try common date input patterns
                date_selectors = [
                    'input[name*="pickup"], input[id*="pickup"]',
                    'input[type="date"]',
                    '.date-input, .datepicker'
                ]
                
                for selector in date_selectors:
                    if await page.locator(selector).count() > 0:
                        logger.info(f"Found date input: {selector}")
                        break
                        
            except Exception as e:
                logger.debug(f"Date interaction not available: {e}")
            
            await self.save_screenshot(page, "final_state")
            await page.close()
            logger.info(f"✅ {self.company_name}: Extracted {len(results)} price indicators")
            
        except Exception as e:
            logger.error(f"❌ {self.company_name} scraping failed: {e}")
        finally:
            await browser.close()
        
        return {'company': self.company_name, 'results': results, 'count': len(results)}


class ImprovedRoadsurferScraper(DeepDataScraper):
    """Scraper for Roadsurfer - Targets pricing and vehicles page"""
    
    def __init__(self, use_browserless: bool = True):
        config = {'url': 'https://roadsurfer.com/rv-rental/prices/'}
        super().__init__("Roadsurfer", tier=1, config=config, use_browserless=use_browserless)
        self.pricing_url = "https://roadsurfer.com/rv-rental/prices/"
        self.vehicles_url = "https://roadsurfer.com/rv-rental/vehicles/"
    
    async def scrape(self) -> Dict[str, Any]:
        """Scrape Roadsurfer pricing information"""
        browser = await self.get_browser()
        results = []
        
        try:
            page = await browser.new_page()
            
            # Go to pricing page first (has sample rates)
            success = await self.navigate_smart(page, self.pricing_url, wait_strategy='load')
            if not success:
                logger.warning("Pricing page failed, trying vehicles page")
                success = await self.navigate_smart(page, self.vehicles_url, wait_strategy='load')
            
            await self.save_screenshot(page, "pricing_page")
            await asyncio.sleep(2)  # Let dynamic content load
            
            # Extract text-based pricing information
            content = await page.content()
            await self.save_html(page, "full_page")
            
            # Look for price patterns in text
            text = await page.evaluate('() => document.body.innerText')
            
            # Find price mentions (example patterns)
            import re
            price_patterns = [
                r'\$\d{1,4}(?:\.\d{2})?\s*(?:per night|/night|nightly)',
                r'starting at\s*\$\d{1,4}',
                r'from\s*\$\d{1,4}'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches[:5]:
                    results.append({
                        'company': self.company_name,
                        'price_text': match.strip(),
                        'source': 'text_extraction',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Try to find structured pricing elements
            price_elements = await page.query_selector_all('p:has-text("$"), div:has-text("$"), span:has-text("$")')
            logger.info(f"Found {len(price_elements)} elements containing $")
            
            for elem in price_elements[:10]:
                try:
                    elem_text = await elem.inner_text()
                    if any(word in elem_text.lower() for word in ['night', 'price', 'rate', 'starting', 'from']):
                        results.append({
                            'company': self.company_name,
                            'price_text': elem_text.strip(),
                            'source': 'element_extraction',
                            'timestamp': datetime.now().isoformat()
                        })
                except:
                    pass
            
            await page.close()
            logger.info(f"✅ {self.company_name}: Found {len(results)} price references")
            
        except Exception as e:
            logger.error(f"❌ {self.company_name} scraping failed: {e}")
        finally:
            await browser.close()
        
        return {'company': self.company_name, 'results': results, 'count': len(results)}


class GenericCampervanScraper(DeepDataScraper):
    """Generic scraper that works for most campervan sites"""
    
    def __init__(self, company_name: str, urls: Dict[str, str], use_browserless: bool = True):
        config = {'url': urls.get('homepage', '')}
        super().__init__(company_name, tier=2, config=config, use_browserless=use_browserless)
        self.homepage = urls.get('homepage', '')
        self.pricing_page = urls.get('pricing', '')
        self.quote_page = urls.get('quote', '')
    
    async def scrape(self) -> Dict[str, Any]:
        """Generic scraping approach - tries multiple pages"""
        browser = await self.get_browser()
        results = []
        
        try:
            page = await browser.new_page()
            
            # Try pages in priority order
            pages_to_try = [
                ('pricing', self.pricing_page),
                ('quote', self.quote_page),
                ('homepage', self.homepage)
            ]
            
            for page_type, url in pages_to_try:
                if not url:
                    continue
                    
                logger.info(f"Trying {page_type} page: {url}")
                success = await self.navigate_smart(page, url, wait_strategy='load')
                
                if success:
                    await self.save_screenshot(page, f"{page_type}_page")
                    await asyncio.sleep(2)
                    
                    # Extract all text
                    text = await page.evaluate('() => document.body.innerText')
                    
                    # Find price patterns
                    import re
                    patterns = [
                        r'\$\d{1,4}(?:\.\d{2})?\s*(?:per|/)(?:night|day)',
                        r'(?:from|starting)\s*\$\d{1,4}',
                        r'\$\d{1,4}\s*-\s*\$\d{1,4}'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        for match in matches[:3]:
                            results.append({
                                'company': self.company_name,
                                'price_text': match.strip(),
                                'page_type': page_type,
                                'timestamp': datetime.now().isoformat()
                            })
                    
                    if results:
                        break  # Found prices, no need to try more pages
            
            await page.close()
            logger.info(f"✅ {self.company_name}: Extracted {len(results)} prices")
            
        except Exception as e:
            logger.error(f"❌ {self.company_name} scraping failed: {e}")
        finally:
            await browser.close()
        
        return {'company': self.company_name, 'results': results, 'count': len(results)}


# Example usage function
async def run_improved_scrapers():
    """Run all improved scrapers and save to database"""
    from database.models import get_db_session, CompetitorPrice, ScrapeLog
    from datetime import datetime
    import re
    
    scrapers = [
        ImprovedCruiseAmericaScraper(use_browserless=True),
        ImprovedRoadsurferScraper(use_browserless=True),
        GenericCampervanScraper(
            "Apollo Motorhomes",
            {
                'homepage': 'https://www.apollocamper.com/',
                'pricing': 'https://www.apollocamper.com/our-vehicles'
            },
            use_browserless=True
        )
    ]
    
    all_results = []
    for scraper in scrapers:
        scrape_start = datetime.now()
        result = await scraper.scrape()
        scrape_duration = (datetime.now() - scrape_start).total_seconds()
        all_results.append(result)
        
        # Save to database
        session = get_db_session()
        try:
            # Save scrape log
            scrape_log = ScrapeLog(
                company_name=result['company'],
                scrape_status='success' if result['count'] > 0 else 'failed',
                scrape_duration=scrape_duration,
                items_scraped=result['count'],
                error_message=None if result['count'] > 0 else 'No prices found',
                timestamp=datetime.now()
            )
            session.add(scrape_log)
            
            # Save price records if found
            if result['count'] > 0:
                prices_saved = 0
                for price_data in result['results']:
                    # Extract numeric price from text
                    price_text = price_data.get('price_text', '')
                    price_match = re.search(r'\$(\d+(?:\.\d{2})?)', price_text)
                    
                    if price_match:
                        price_value = float(price_match.group(1))
                        
                        price_record = CompetitorPrice(
                            company_name=result['company'],
                            company_url='',  # TODO: Get from config
                            vehicle_type=price_data.get('vehicle_type', 'Unknown'),
                            price=price_value,
                            currency='USD',
                            scrape_timestamp=datetime.now()
                        )
                        session.add(price_record)
                        prices_saved += 1
                
                logger.info(f"💾 Saved {prices_saved} prices to database for {result['company']}")
            
            session.commit()
                
        except Exception as e:
            logger.error(f"❌ Database save failed for {result['company']}: {e}")
            session.rollback()
        finally:
            session.close()
    
    return all_results


if __name__ == "__main__":
    results = asyncio.run(run_improved_scrapers())
    for result in results:
        print(f"\n{result['company']}: {result['count']} prices found")
