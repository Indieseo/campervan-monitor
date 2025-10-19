"""
Roadsurfer Ultra Scraper - FIXED VERSION
Properly handles cookies and extracts real pricing data
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

class RoadsurferUltraScraper:
    def __init__(self):
        self.base_url = "https://roadsurfer.com/"
        self.locations = [
            "Munich, Germany",
            "Berlin, Germany", 
            "Hamburg, Germany",
            "Frankfurt, Germany",
            "Los Angeles",
            "San Francisco"
        ]
        self.captured_apis = []
        self.all_prices = []
        
    def handle_cookie_popup_advanced(self, driver) -> bool:
        """Advanced cookie popup handler for Roadsurfer"""
        logger.info("🍪 Handling cookie popup...")
        
        try:
            # Wait for page to load
            time.sleep(3)
            
            # Try multiple cookie selectors
            cookie_selectors = [
                'button[id*="accept"]',
                'button[class*="accept"]',
                'button[class*="cookie"]',
                'button:contains("Accept")',
                'button:contains("OK")',
                'button:contains("I agree")',
                'button:contains("Accept All")',
                'button:contains("Accept Cookies")',
                'div[class*="cookie"] button',
                'div[id*="cookie"] button',
                '.cookie-accept',
                '.accept-cookies',
                '#cookie-accept',
                '#accept-cookies',
                '[data-testid*="accept"]',
                '[data-testid*="cookie"]'
            ]
            
            for selector in cookie_selectors:
                try:
                    elements = driver.find_elements(selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            logger.info(f"✅ Cookie popup handled with selector: {selector}")
                            time.sleep(2)
                            return True
                except Exception as e:
                    continue
            
            # Try JavaScript execution
            js_scripts = [
                "document.querySelectorAll('button').forEach(btn => { if(btn.textContent.toLowerCase().includes('accept')) btn.click(); });",
                "document.querySelectorAll('[class*=\"accept\"]').forEach(el => el.click());",
                "document.querySelectorAll('[id*=\"accept\"]').forEach(el => el.click());",
                "document.querySelectorAll('[class*=\"cookie\"] button').forEach(el => el.click());",
                "document.querySelectorAll('[id*=\"cookie\"] button').forEach(el => el.click());"
            ]
            
            for script in js_scripts:
                try:
                    driver.execute_script(script)
                    time.sleep(2)
                    logger.info("✅ Cookie popup handled with JavaScript")
                    return True
                except:
                    continue
            
            # Try ESC key
            try:
                driver.press_key("Escape")
                time.sleep(2)
                logger.info("✅ Cookie popup handled with ESC key")
                return True
            except:
                pass
            
            logger.warning("⚠️ Could not handle cookie popup")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in cookie popup handling: {e}")
            return False
    
    def wait_for_search_form(self, driver) -> bool:
        """Wait for search form to be available"""
        logger.info("🔍 Waiting for search form...")
        
        try:
            # Wait for search form elements
            search_selectors = [
                'input[placeholder*="location"]',
                'input[placeholder*="Location"]',
                'input[name*="location"]',
                'input[id*="location"]',
                '.search-input',
                '.location-input',
                '[data-testid*="location"]'
            ]
            
            for selector in search_selectors:
                try:
                    element = driver.find_element(selector)
                    if element.is_displayed():
                        logger.info(f"✅ Search form found with selector: {selector}")
                        return True
                except:
                    continue
            
            # Wait a bit more and try again
            time.sleep(5)
            for selector in search_selectors:
                try:
                    element = driver.find_element(selector)
                    if element.is_displayed():
                        logger.info(f"✅ Search form found with delayed selector: {selector}")
                        return True
                except:
                    continue
            
            logger.warning("⚠️ Search form not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error waiting for search form: {e}")
            return False
    
    def fill_search_form(self, driver, location: str) -> bool:
        """Fill the search form with location"""
        logger.info(f"📍 Filling location: {location}")
        
        try:
            # Try multiple location input selectors
            location_selectors = [
                'input[placeholder*="location"]',
                'input[placeholder*="Location"]',
                'input[name*="location"]',
                'input[id*="location"]',
                '.search-input',
                '.location-input',
                '[data-testid*="location"]'
            ]
            
            location_input = None
            for selector in location_selectors:
                try:
                    element = driver.find_element(selector)
                    if element.is_displayed() and element.is_enabled():
                        location_input = element
                        break
                except:
                    continue
            
            if not location_input:
                logger.error("❌ Location input not found")
                return False
            
            # Clear and fill location
            location_input.clear()
            location_input.send_keys(location)
            time.sleep(2)
            
            # Try to select from dropdown if it appears
            try:
                dropdown_options = driver.find_elements('.dropdown-option, .autocomplete-option, .suggestion')
                for option in dropdown_options:
                    if location.lower() in option.text.lower():
                        option.click()
                        time.sleep(1)
                        break
            except:
                pass
            
            logger.info(f"✅ Location filled: {location}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error filling location: {e}")
            return False
    
    def submit_search(self, driver) -> bool:
        """Submit the search form"""
        logger.info("🔍 Submitting search...")
        
        try:
            # Try multiple search button selectors
            search_selectors = [
                'button[type="submit"]',
                'button:contains("Search")',
                'button:contains("Find")',
                'button:contains("Go")',
                '.search-button',
                '.submit-button',
                '[data-testid*="search"]',
                'input[type="submit"]'
            ]
            
            for selector in search_selectors:
                try:
                    element = driver.find_element(selector)
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        logger.info(f"✅ Search submitted with selector: {selector}")
                        time.sleep(5)  # Wait for results
                        return True
                except:
                    continue
            
            # Try pressing Enter on location input
            try:
                location_input = driver.find_element('input[placeholder*="location"], input[placeholder*="Location"]')
                location_input.send_keys("\n")
                logger.info("✅ Search submitted with Enter key")
                time.sleep(5)
                return True
            except:
                pass
            
            logger.error("❌ Could not submit search")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error submitting search: {e}")
            return False
    
    def extract_pricing_data(self, driver, location: str) -> List[Dict]:
        """Extract pricing data from search results"""
        logger.info(f"💰 Extracting pricing data for {location}")
        
        try:
            # Wait for results to load
            time.sleep(5)
            
            # Try multiple price selectors
            price_selectors = [
                '.price',
                '.cost',
                '.rate',
                '.amount',
                '[class*="price"]',
                '[class*="cost"]',
                '[class*="rate"]',
                'span:contains("€")',
                'div:contains("€")',
                'p:contains("€")',
                '.vehicle-price',
                '.rental-price',
                '.daily-price'
            ]
            
            prices = []
            for selector in price_selectors:
                try:
                    elements = driver.find_elements(selector)
                    for element in elements:
                        text = element.text.strip()
                        if '€' in text and any(char.isdigit() for char in text):
                            # Extract price using regex
                            price_match = re.search(r'€?\s*(\d+(?:\.\d{2})?)', text)
                            if price_match:
                                price = float(price_match.group(1))
                                if 10 <= price <= 1000:  # Reasonable price range
                                    prices.append({
                                        'location': location,
                                        'price': price,
                                        'currency': 'EUR',
                                        'text': text,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    logger.info(f"💰 Found price: €{price} - {text}")
                except:
                    continue
            
            # If no prices found, try to find any text with € symbol
            if not prices:
                try:
                    page_text = driver.page_source
                    price_matches = re.findall(r'€\s*(\d+(?:\.\d{2})?)', page_text)
                    for match in price_matches:
                        price = float(match)
                        if 10 <= price <= 1000:
                            prices.append({
                                'location': location,
                                'price': price,
                                'currency': 'EUR',
                                'text': f"€{price}",
                                'timestamp': datetime.now().isoformat()
                            })
                            logger.info(f"💰 Found price in page source: €{price}")
                except:
                    pass
            
            logger.info(f"✅ Extracted {len(prices)} prices for {location}")
            return prices
            
        except Exception as e:
            logger.error(f"❌ Error extracting pricing data: {e}")
            return []
    
    def scrape_location(self, driver, location: str) -> List[Dict]:
        """Scrape pricing data for specific location"""
        logger.info(f"🎯 Scraping location: {location}")
        
        try:
            # Navigate to homepage
            driver.get(self.base_url)
            time.sleep(5)
            
            # Handle cookie popup
            self.handle_cookie_popup_advanced(driver)
            
            # Wait for search form
            if not self.wait_for_search_form(driver):
                logger.error(f"❌ Search form not available for {location}")
                return []
            
            # Fill search form
            if not self.fill_search_form(driver, location):
                logger.error(f"❌ Could not fill search form for {location}")
                return []
            
            # Submit search
            if not self.submit_search(driver):
                logger.error(f"❌ Could not submit search for {location}")
                return []
            
            # Extract pricing data
            prices = self.extract_pricing_data(driver, location)
            
            # Take screenshot
            screenshot_path = f"data/screenshots/roadsurfer_{location.replace(', ', '_').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.screenshot(screenshot_path)
            logger.info(f"📸 Screenshot saved: {screenshot_path}")
            
            return prices
            
        except Exception as e:
            logger.error(f"❌ Error scraping {location}: {e}")
            return []
    
@browser(
    headless=False,
    reuse_driver=False,
    block_images=False,
    wait_for_complete_page_load=True
)
def scrape_roadsurfer_ultra_fixed(driver, data=None):
    """Scrape all Roadsurfer locations with fixed cookie handling"""
    logger.info("🚀 STARTING ROADSURFER ULTRA SCRAPER - FIXED VERSION")
    logger.info("="*80)
    
    # Initialize scraper
    scraper = RoadsurferUltraScraper()
    
    all_prices = []
    successful_searches = 0
    
    for i, location in enumerate(scraper.locations):
        logger.info(f"\n{'='*80}")
        logger.info(f"SEARCHING: {location}")
        logger.info(f"{'='*80}")
        
        try:
            prices = scraper.scrape_location(driver, location)
            if prices:
                all_prices.extend(prices)
                successful_searches += 1
                logger.info(f"✅ SUCCESS: {location} - {len(prices)} prices found")
            else:
                logger.warning(f"⚠️ NO PRICES: {location}")
            
            # Wait between searches
            if i < len(scraper.locations) - 1:
                time.sleep(3)
                
        except Exception as e:
            logger.error(f"❌ ERROR: {location} - {e}")
    
    # Summary
    logger.info(f"\n{'='*80}")
    logger.info("ROADSURFER ULTRA SCRAPING COMPLETE - FIXED VERSION")
    logger.info(f"{'='*80}")
    logger.info(f"Searches performed: {len(scraper.locations)}")
    logger.info(f"Successful searches: {successful_searches}")
    logger.info(f"Total unique prices: {len(all_prices)}")
    logger.info(f"Success: {len(all_prices) > 0}")
    
    # Save results
    results = {
        'company': 'Roadsurfer',
        'timestamp': datetime.now().isoformat(),
        'success': len(all_prices) > 0,
        'total_prices': len(all_prices),
        'successful_searches': successful_searches,
        'total_searches': len(scraper.locations),
        'prices': all_prices,
        'locations_tested': scraper.locations
    }
    
    # Create output directory
    Path("data/live_pricing").mkdir(parents=True, exist_ok=True)
    
    output_file = f"data/live_pricing/roadsurfer_ultra_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Data saved: {output_file}")
    logger.info(f"{'='*80}")
    
    return results

if __name__ == "__main__":
    scrape_roadsurfer_ultra_fixed()
