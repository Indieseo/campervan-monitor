import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import List, Dict
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus.browser import browser, Driver

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Competitor configurations
COMPETITOR_CONFIGS = {
    "McRent": {
        'base_url': 'https://www.mcrent.de/',
        'currency': 'EUR',
        'test_urls': [
            'https://mcrent.com/',
            'https://www.mcrent.com/en/',
            'https://mcrent.de/en/motorhome-rental/',
            'https://www.mcrent.de/de/',
            'https://mcrent.de/',
        ]
    },
    "Yescapa": {
        'base_url': 'https://www.yescapa.com/',
        'currency': 'EUR',
        'test_urls': [
            'https://www.yescapa.com/',
            'https://www.yescapa.com/en/',
            'https://www.yescapa.com/de/',
        ]
    },
    "Cruise America": {
        'base_url': 'https://www.cruiseamerica.com/',
        'currency': 'USD',
        'test_urls': [
            'https://www.cruiseamerica.com/',
            'https://www.cruiseamerica.com/rv-rental-locations/california/los-angeles-rv-rental',
        ]
    }
}

def handle_cookie_popup_ultimate(driver: Driver) -> bool:
    """Ultimate cookie popup handler for all competitors"""
    logger.info("🍪 Handling cookie popup with ultimate strategy...")
    
    try:
        time.sleep(3)  # Give popup time to appear
        
        cookie_selectors = [
            '#uc-btn-accept-all',  # Usercentrics
            'button.cookie-consent-button.accept-all',
            'button[data-qa="accept-all-cookies"]',
            'button:has-text("Accept all")',
            'button:has-text("Alle akzeptieren")',
            'button:has-text("Akzeptieren")',
            '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',  # Cookiebot
            '.cmp-button_button--primary',
            '.button.primary',
            '#consent-accept-all',
            '.js-cookie-consent-agree',
            '#onetrust-accept-btn-handler',  # OneTrust
            'button#didomi-notice-agree-button',  # Didomi
            'button.agree-button',
            'a.call-to-action.btn.btn-primary.btn-block.js-accept-cookies',  # Yescapa
            'button.js-accept-cookies',  # Yescapa
        ]
        
        for selector in cookie_selectors:
            try:
                element = driver.find(selector, timeout=3)
                if element:
                    element.click()
                    logger.info(f"✅ Clicked cookie accept button: {selector}")
                    time.sleep(2)
                    return True
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
        
        # Try pressing ESC key
        try:
            driver.press('Escape')
            time.sleep(2)
            logger.info("✅ Pressed ESC key.")
            return True
        except Exception as e:
            logger.warning(f"⚠️ ESC key failed: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Error in cookie popup handling: {e}")
        return False

def extract_pricing_aggressive(page_html: str, currency: str) -> List[float]:
    """Aggressively extract pricing data from HTML"""
    logger.info(f"💰 Extracting pricing data...")
    
    prices_found = []
    
    # Multiple regex patterns for different price formats
    if currency == 'EUR':
        price_patterns = [
            r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)\s*€',
            r'€\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)',
            r'(\d+)\s*€',
            r'€\s*(\d+)',
            r'from\s+€(\d+)',
            r'ab\s+€(\d+)',  # German
            r'starting\s+at\s+€(\d+)',
        ]
    else:  # USD
        price_patterns = [
            r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)\s*\$',
            r'\$\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?)',
            r'(\d+)\s*\$',
            r'\$\s*(\d+)',
            r'from\s+\$(\d+)',
            r'starting\s+at\s+\$(\d+)',
        ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, page_html, re.IGNORECASE)
        for match in matches:
            try:
                if isinstance(match, tuple):
                    price_str = match[0]
                else:
                    price_str = match
                
                # Clean and convert price
                price_str = price_str.replace('.', '').replace(',', '.')
                price = float(re.sub(r'[^\d.]', '', price_str))
                
                # Filter for realistic daily rates
                if 20 <= price <= 1000:
                    prices_found.append(price)
            except ValueError:
                continue
    
    return prices_found

def extract_vehicles_aggressive(page_html: str) -> List[Dict]:
    """Aggressively extract vehicle information"""
    logger.info("🚐 Extracting vehicle information...")
    
    vehicle_patterns = [
        r'(?:<h[1-4][^>]*>|class=["\'][^"\']*title[^"\']*["\']>[^<]*?)(campervan|motorhome|rv|van|california|grand california|columbus|surfer suite|travel bus|beach hostel|adventure camper|family fiver|city lite|dog camper|road house|holiday bus|horizon|camper van|kastenwagen|teilintegriert|alkoven)(?:\s*<|\s*<a|\s*from)',
        r'data-model=["\']([^"\']+)["\']',
        r'alt=["\']([^"\']*campervan[^"\']*)["\']',
        r'alt=["\']([^"\']*motorhome[^"\']*)["\']',
        r'class=["\'][^"\']*vehicle-name[^"\']*["\']>\s*([^<]+)\s*<',
    ]
    
    vehicle_info = []
    for pattern in vehicle_patterns:
        matches = re.findall(pattern, page_html, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                info = match[0].strip()
            else:
                info = match.strip()
            if info and len(info) > 3 and len(info) < 100:
                vehicle_info.append(info)
    
    if vehicle_info:
        unique_vehicle_info = list(set(vehicle_info))
        vehicles = []
        for info in unique_vehicle_info[:10]:  # Top 10 unique vehicles
            vehicles.append({
                'model': info,
                'description': info,
                'type': 'Campervan',
                'capacity': 4
            })
        return vehicles
    
    return []

def scrape_competitor_aggressive(driver: Driver, company: str, config: Dict) -> Dict:
    """Scrape a competitor using aggressive extraction"""
    logger.info(f"\n{'='*60}")
    logger.info(f"SCRAPING {company.upper()}")
    logger.info(f"{'='*60}")
    
    all_prices = []
    all_vehicles = []
    successful_urls = []
    failed_urls = []
    
    for url in config['test_urls']:
        logger.info(f"\n🌐 Testing URL: {url}")
        
        try:
            # Navigate to URL
            driver.get(url)
            time.sleep(5)  # Initial load time
            
            # Handle cookie popup
            handle_cookie_popup_ultimate(driver)
            time.sleep(3)  # Wait for popup to disappear
            
            # Get page HTML
            page_html = driver.page_html
            logger.info(f"📄 Page HTML length: {len(page_html)} characters")
            
            # Extract prices
            prices = extract_pricing_aggressive(page_html, config['currency'])
            logger.info(f"💰 Found {len(prices)} prices")
            
            # Extract vehicles
            vehicles = extract_vehicles_aggressive(page_html)
            logger.info(f"🚐 Found {len(vehicles)} vehicles")
            
            if prices:
                all_prices.extend(prices)
                all_vehicles.extend(vehicles)
                successful_urls.append(url)
                logger.info(f"✅ SUCCESS: {url} - {len(prices)} prices found")
                
                # Take screenshot
                screenshot_path = f"data/screenshots/{company}_aggressive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(screenshot_path)
                logger.info(f"📸 Screenshot saved: {screenshot_path}")
            else:
                failed_urls.append(url)
                logger.warning(f"⚠️ NO PRICES: {url}")
            
        except Exception as e:
            logger.error(f"❌ ERROR: {url} - {e}")
            failed_urls.append(url)
    
    # Summary
    unique_prices = sorted(list(set(all_prices)))
    logger.info(f"\n{'='*60}")
    logger.info(f"{company.upper()} SCRAPING SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"URLs tested: {len(config['test_urls'])}")
    logger.info(f"Successful URLs: {len(successful_urls)}")
    logger.info(f"Failed URLs: {len(failed_urls)}")
    logger.info(f"Total unique prices: {len(unique_prices)}")
    logger.info(f"Success: {len(unique_prices) > 0}")
    
    if unique_prices:
        logger.info(f"Price range: {config['currency']}{min(unique_prices)} - {config['currency']}{max(unique_prices)}")
        logger.info(f"Average price: {config['currency']}{sum(unique_prices)/len(unique_prices):.2f}")
    
    return {
        'company': company,
        'success': len(unique_prices) > 0,
        'total_prices': len(unique_prices),
        'successful_urls': successful_urls,
        'failed_urls': failed_urls,
        'prices': unique_prices,
        'vehicles': all_vehicles[:10],  # Top 10 unique vehicles
        'currency': config['currency'],
        'timestamp': datetime.now().isoformat()
    }

@browser(
    headless=False,
    reuse_driver=False,
    block_images=False,
    wait_for_complete_page_load=True
)
def scrape_all_competitors_ultimate(driver: Driver, data=None):
    """Scrape all failing competitors with aggressive extraction"""
    logger.info("🚀 STARTING ULTIMATE COMPETITOR FIX - V2")
    logger.info("="*80)
    logger.info("🎯 TARGET: Fix McRent, Yescapa, Cruise America")
    logger.info("="*80)
    
    all_results = []
    
    for company, config in COMPETITOR_CONFIGS.items():
        try:
            result = scrape_competitor_aggressive(driver, company, config)
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
                'timestamp': datetime.now().isoformat()
            })
    
    # Final summary
    logger.info("\n" + "="*80)
    logger.info("ULTIMATE COMPETITOR FIX COMPLETE")
    logger.info("="*80)
    
    successful = [r for r in all_results if r['success']]
    failed = [r for r in all_results if not r['success']]
    
    logger.info(f"Total competitors: {len(all_results)}")
    logger.info(f"Successful: {len(successful)}")
    logger.info(f"Failed: {len(failed)}")
    
    if successful:
        logger.info("\n✅ FIXED COMPETITORS:")
        for r in successful:
            logger.info(f"  - {r['company']}: {r['total_prices']} prices")
    
    if failed:
        logger.info("\n❌ STILL FAILING:")
        for r in failed:
            logger.info(f"  - {r['company']}")
    
    # Save results
    Path("data/live_pricing").mkdir(parents=True, exist_ok=True)
    output_file = f"data/live_pricing/ultimate_competitor_fix_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    logger.info(f"\n[SAVED] Results: {output_file}")
    logger.info("="*80)
    
    return all_results

if __name__ == "__main__":
    scrape_all_competitors_ultimate()




