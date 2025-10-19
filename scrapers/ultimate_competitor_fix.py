"""
Ultimate Competitor Fix
Fixes all failing competitors with advanced cookie handling and real data extraction
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus.browser import browser
import asyncio
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class UltimateCompetitorFix:
    def __init__(self):
        self.competitors = {
            'McRent': {
                'urls': [
                    'https://www.mcrent.de/',
                    'https://mcrent.de/en/',
                    'https://www.mcrent.com/',
                    'https://mcrent.de/en/motorhome-rental/'
                ],
                'currency': 'EUR',
                'locations': ['Munich', 'Berlin', 'Hamburg']
            },
            'Yescapa': {
                'urls': [
                    'https://www.yescapa.com/',
                    'https://www.yescapa.com/en/',
                    'https://www.yescapa.com/fr/'
                ],
                'currency': 'EUR',
                'locations': ['Paris', 'Lyon', 'Marseille']
            },
            'Cruise America': {
                'urls': [
                    'https://www.cruiseamerica.com/',
                    'https://www.cruiseamerica.com/rent/',
                    'https://www.cruiseamerica.com/locations/'
                ],
                'currency': 'USD',
                'locations': ['Los Angeles', 'San Francisco', 'Denver']
            }
        }
        
    def handle_cookie_popup_ultimate(self, driver) -> bool:
        """Ultimate cookie popup handler for all competitors"""
        logger.info("🍪 Handling cookie popup with ultimate strategy...")
        
        try:
            # Wait for page to load
            time.sleep(5)
            
            # Try multiple cookie selectors (comprehensive list)
            cookie_selectors = [
                # Generic accept buttons
                'button[id*="accept"]',
                'button[class*="accept"]',
                'button:contains("Accept")',
                'button:contains("OK")',
                'button:contains("I agree")',
                'button:contains("Accept All")',
                'button:contains("Accept Cookies")',
                'button:contains("Allow")',
                'button:contains("Continue")',
                'button:contains("Got it")',
                'button:contains("Understood")',
                'button:contains("Agree")',
                
                # Cookie-specific selectors
                'div[class*="cookie"] button',
                'div[id*="cookie"] button',
                '.cookie-accept',
                '.accept-cookies',
                '.cookie-consent button',
                '.cookie-banner button',
                '#cookie-accept',
                '#accept-cookies',
                '#cookie-consent button',
                '#cookie-banner button',
                
                # Data attributes
                '[data-testid*="accept"]',
                '[data-testid*="cookie"]',
                '[data-cy*="accept"]',
                '[data-cy*="cookie"]',
                
                # Specific company selectors
                '.usercentrics-button',
                '.uc-button',
                '.consent-button',
                '.gdpr-accept',
                '.privacy-accept'
            ]
            
            for selector in cookie_selectors:
                try:
                    elements = driver.find_elements(selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            logger.info(f"✅ Cookie popup handled with selector: {selector}")
                            time.sleep(3)
                            return True
                except Exception as e:
                    continue
            
            # Try JavaScript execution (comprehensive)
            js_scripts = [
                # Generic accept buttons
                "document.querySelectorAll('button').forEach(btn => { if(btn.textContent.toLowerCase().includes('accept')) btn.click(); });",
                "document.querySelectorAll('button').forEach(btn => { if(btn.textContent.toLowerCase().includes('ok')) btn.click(); });",
                "document.querySelectorAll('button').forEach(btn => { if(btn.textContent.toLowerCase().includes('agree')) btn.click(); });",
                "document.querySelectorAll('button').forEach(btn => { if(btn.textContent.toLowerCase().includes('allow')) btn.click(); });",
                "document.querySelectorAll('button').forEach(btn => { if(btn.textContent.toLowerCase().includes('continue')) btn.click(); });",
                
                # Class-based selectors
                "document.querySelectorAll('[class*=\"accept\"]').forEach(el => el.click());",
                "document.querySelectorAll('[class*=\"cookie\"]').forEach(el => el.click());",
                "document.querySelectorAll('[class*=\"consent\"]').forEach(el => el.click());",
                "document.querySelectorAll('[class*=\"gdpr\"]').forEach(el => el.click());",
                "document.querySelectorAll('[class*=\"privacy\"]').forEach(el => el.click());",
                
                # ID-based selectors
                "document.querySelectorAll('[id*=\"accept\"]').forEach(el => el.click());",
                "document.querySelectorAll('[id*=\"cookie\"]').forEach(el => el.click());",
                "document.querySelectorAll('[id*=\"consent\"]').forEach(el => el.click());",
                
                # Specific button types
                "document.querySelectorAll('[class*=\"cookie\"] button').forEach(el => el.click());",
                "document.querySelectorAll('[id*=\"cookie\"] button').forEach(el => el.click());",
                "document.querySelectorAll('.cookie-banner button').forEach(el => el.click());",
                "document.querySelectorAll('.cookie-consent button').forEach(el => el.click());",
                
                # Usercentrics specific
                "document.querySelectorAll('.usercentrics-button').forEach(el => el.click());",
                "document.querySelectorAll('.uc-button').forEach(el => el.click());",
                "document.querySelectorAll('[data-testid*=\"accept\"]').forEach(el => el.click());"
            ]
            
            for script in js_scripts:
                try:
                    driver.execute_script(script)
                    time.sleep(2)
                    logger.info("✅ Cookie popup handled with JavaScript")
                    return True
                except:
                    continue
            
            # Try multiple key presses
            keys_to_try = ["Escape", "Enter", "Tab", "Space"]
            for key in keys_to_try:
                try:
                    driver.press_key(key)
                    time.sleep(2)
                    logger.info(f"✅ Cookie popup handled with {key} key")
                    return True
                except:
                    continue
            
            # Try clicking on overlay/background to dismiss
            try:
                driver.execute_script("document.querySelector('.cookie-overlay, .cookie-backdrop, .modal-backdrop').click();")
                time.sleep(2)
                logger.info("✅ Cookie popup handled by clicking overlay")
                return True
            except:
                pass
            
            logger.warning("⚠️ Could not handle cookie popup with any method")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in cookie popup handling: {e}")
            return False
    
    def wait_for_content(self, driver, timeout: int = 30) -> bool:
        """Wait for actual content to load (not just cookie popups)"""
        logger.info("⏳ Waiting for actual content to load...")
        
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Check if we have actual content (not just cookie popups)
                page_source = driver.page_source.lower()
                
                # Look for content indicators
                content_indicators = [
                    'search', 'location', 'date', 'price', 'vehicle', 'rental',
                    'book', 'reserve', 'motorhome', 'camper', 'rv'
                ]
                
                content_found = any(indicator in page_source for indicator in content_indicators)
                
                if content_found:
                    logger.info("✅ Actual content detected")
                    return True
                
                time.sleep(2)
            
            logger.warning("⚠️ Timeout waiting for content")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error waiting for content: {e}")
            return False
    
    def extract_pricing_data_ultimate(self, driver, company: str, currency: str) -> List[Dict]:
        """Ultimate pricing data extraction for all competitors"""
        logger.info(f"💰 Extracting pricing data for {company}")
        
        try:
            # Wait for content
            if not self.wait_for_content(driver):
                logger.warning("⚠️ Content not loaded, proceeding anyway")
            
            # Get page source for analysis
            page_source = driver.page_source
            
            # Try multiple price selectors
            price_selectors = [
                # Generic price selectors
                '.price', '.cost', '.rate', '.amount', '.fee',
                '[class*="price"]', '[class*="cost"]', '[class*="rate"]',
                '[class*="amount"]', '[class*="fee"]',
                
                # Currency-specific selectors
                f'span:contains("{currency}")', f'div:contains("{currency}")',
                f'p:contains("{currency}")', f'strong:contains("{currency}")',
                
                # Vehicle-specific selectors
                '.vehicle-price', '.rental-price', '.daily-price',
                '.motorhome-price', '.camper-price', '.rv-price',
                
                # Table and list selectors
                'td:contains("' + currency + '")', 'li:contains("' + currency + '")',
                'tr:contains("' + currency + '")', 'div:contains("' + currency + '")',
                
                # Data attributes
                '[data-price]', '[data-cost]', '[data-rate]',
                '[data-testid*="price"]', '[data-testid*="cost"]'
            ]
            
            prices = []
            for selector in price_selectors:
                try:
                    elements = driver.find_elements(selector)
                    for element in elements:
                        text = element.text.strip()
                        if currency in text and any(char.isdigit() for char in text):
                            # Extract price using regex
                            price_match = re.search(rf'{currency}?\s*(\d+(?:\.\d{{2}})?)', text)
                            if price_match:
                                price = float(price_match.group(1))
                                # Reasonable price ranges
                                if currency == 'EUR' and 10 <= price <= 1000:
                                    prices.append({
                                        'company': company,
                                        'price': price,
                                        'currency': currency,
                                        'text': text,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    logger.info(f"💰 Found price: {currency}{price} - {text}")
                                elif currency == 'USD' and 20 <= price <= 2000:
                                    prices.append({
                                        'company': company,
                                        'price': price,
                                        'currency': currency,
                                        'text': text,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    logger.info(f"💰 Found price: {currency}{price} - {text}")
                except:
                    continue
            
            # If no prices found with selectors, try page source analysis
            if not prices:
                try:
                    # Extract all prices from page source
                    if currency == 'EUR':
                        price_matches = re.findall(rf'€\s*(\d+(?:\.\d{{2}})?)', page_source)
                    else:
                        price_matches = re.findall(rf'\$\s*(\d+(?:\.\d{{2}})?)', page_source)
                    
                    for match in price_matches:
                        price = float(match)
                        if currency == 'EUR' and 10 <= price <= 1000:
                            prices.append({
                                'company': company,
                                'price': price,
                                'currency': currency,
                                'text': f"{currency}{price}",
                                'timestamp': datetime.now().isoformat()
                            })
                            logger.info(f"💰 Found price in page source: {currency}{price}")
                        elif currency == 'USD' and 20 <= price <= 2000:
                            prices.append({
                                'company': company,
                                'price': price,
                                'currency': currency,
                                'text': f"{currency}{price}",
                                'timestamp': datetime.now().isoformat()
                            })
                            logger.info(f"💰 Found price in page source: {currency}{price}")
                except:
                    pass
            
            # Remove duplicates
            unique_prices = []
            seen_prices = set()
            for price in prices:
                price_key = (price['company'], price['price'], price['currency'])
                if price_key not in seen_prices:
                    unique_prices.append(price)
                    seen_prices.add(price_key)
            
            logger.info(f"✅ Extracted {len(unique_prices)} unique prices for {company}")
            return unique_prices
            
        except Exception as e:
            logger.error(f"❌ Error extracting pricing data: {e}")
            return []
    
    def scrape_competitor(self, driver, company: str, config: Dict) -> Dict:
        """Scrape individual competitor with all URLs"""
        logger.info(f"🎯 SCRAPING {company.upper()}")
        logger.info("="*60)
        
        all_prices = []
        successful_urls = []
        failed_urls = []
        
        for i, url in enumerate(config['urls']):
            logger.info(f"\n📍 Testing URL {i+1}/{len(config['urls'])}: {url}")
            
            try:
                # Navigate to URL
                driver.get(url)
                time.sleep(5)
                
                # Handle cookie popup
                self.handle_cookie_popup_ultimate(driver)
                
                # Wait for content
                self.wait_for_content(driver)
                
                # Extract pricing data
                prices = self.extract_pricing_data_ultimate(driver, company, config['currency'])
                
                if prices:
                    all_prices.extend(prices)
                    successful_urls.append(url)
                    logger.info(f"✅ SUCCESS: {url} - {len(prices)} prices found")
                else:
                    failed_urls.append(url)
                    logger.warning(f"⚠️ NO PRICES: {url}")
                
                # Take screenshot
                screenshot_path = f"data/screenshots/{company}_URL_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.screenshot(screenshot_path)
                logger.info(f"📸 Screenshot saved: {screenshot_path}")
                
                # Wait between URLs
                if i < len(config['urls']) - 1:
                    time.sleep(3)
                    
            except Exception as e:
                logger.error(f"❌ ERROR: {url} - {e}")
                failed_urls.append(url)
        
        # Summary for this company
        logger.info(f"\n{'='*60}")
        logger.info(f"{company.upper()} SCRAPING SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"URLs tested: {len(config['urls'])}")
        logger.info(f"Successful URLs: {len(successful_urls)}")
        logger.info(f"Failed URLs: {len(failed_urls)}")
        logger.info(f"Total prices found: {len(all_prices)}")
        logger.info(f"Success: {len(all_prices) > 0}")
        
        return {
            'company': company,
            'success': len(all_prices) > 0,
            'total_prices': len(all_prices),
            'successful_urls': successful_urls,
            'failed_urls': failed_urls,
            'prices': all_prices,
            'currency': config['currency'],
            'timestamp': datetime.now().isoformat()
        }
    
    @browser(
        headless=False,
        reuse_driver=False,
        block_images=False,
        wait_for_complete_page_load=True
    )
    def scrape_all_competitors(self, driver):
        """Scrape all failing competitors"""
        logger.info("🚀 STARTING ULTIMATE COMPETITOR FIX")
        logger.info("="*80)
        logger.info("🎯 TARGET: Fix McRent, Yescapa, Cruise America")
        logger.info("="*80)
        
        all_results = []
        
        for company, config in self.competitors.items():
            try:
                result = self.scrape_competitor(driver, company, config)
                all_results.append(result)
                
                if result['success']:
                    logger.info(f"🎉 {company.upper()} FIXED! - {result['total_prices']} prices found")
                else:
                    logger.error(f"❌ {company.upper()} STILL FAILING - No prices found")
                
                # Wait between companies
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ CRITICAL ERROR with {company}: {e}")
                all_results.append({
                    'company': company,
                    'success': False,
                    'error': str(e),
                    'total_prices': 0,
                    'prices': []
                })
        
        # Final summary
        logger.info(f"\n{'='*80}")
        logger.info("ULTIMATE COMPETITOR FIX COMPLETE")
        logger.info(f"{'='*80}")
        
        successful_companies = [r for r in all_results if r['success']]
        failed_companies = [r for r in all_results if not r['success']]
        
        logger.info(f"Companies tested: {len(all_results)}")
        logger.info(f"Successful: {len(successful_companies)}")
        logger.info(f"Failed: {len(failed_companies)}")
        
        if successful_companies:
            logger.info("\n✅ FIXED COMPANIES:")
            for result in successful_companies:
                logger.info(f"  - {result['company']}: {result['total_prices']} prices")
        
        if failed_companies:
            logger.info("\n❌ STILL FAILING:")
            for result in failed_companies:
                logger.info(f"  - {result['company']}: {result.get('error', 'No prices found')}")
        
        # Save results
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_companies': len(all_results),
            'successful_companies': len(successful_companies),
            'failed_companies': len(failed_companies),
            'results': all_results
        }
        
        # Create output directory
        Path("data/live_pricing").mkdir(parents=True, exist_ok=True)
        
        output_file = f"data/live_pricing/ultimate_competitor_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n💾 Results saved: {output_file}")
        logger.info(f"{'='*80}")
        
        return results

if __name__ == "__main__":
    fixer = UltimateCompetitorFix()
    fixer.scrape_all_competitors()
