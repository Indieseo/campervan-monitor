"""
Advanced Cruise America Testing
Multiple strategies to get Cruise America working
"""

import json
import time
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus import browser, Driver
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Cruise America URLs to test
CRUISE_AMERICA_URLS = [
    'https://cruiseamerica.com/',
    'https://www.cruiseamerica.com/rent/',
    'https://cruiseamerica.com/locations/',
    'https://www.cruiseamerica.com/rv-rental/',
    'https://cruiseamerica.com/find-rv',
    'https://www.cruiseamerica.com/locations/los-angeles-ca',
    'https://cruiseamerica.com/locations/denver-co',
    'https://www.cruiseamerica.com/',
    'https://cruiseamerica.com/rental/',
    'https://www.cruiseamerica.com/locations/'
]

@browser(headless=False, stealth=True, anti_detection=True)
def test_cruise_america_advanced(driver: Driver):
    """Advanced testing for Cruise America with multiple strategies"""
    logger.info("🎯 ADVANCED CRUISE AMERICA TESTING")
    logger.info("="*50)
    
    results = []
    
    for i, url in enumerate(CRUISE_AMERICA_URLS):
        logger.info(f"\n📍 Test {i+1}/{len(CRUISE_AMERICA_URLS)}: {url}")
        
        try:
            # Navigate to URL
            driver.get(url)
            time.sleep(5)
            
            # Check page content
            page_content = driver.page_source
            page_title = driver.title
            
            logger.info(f"📄 Page Title: {page_title}")
            logger.info(f"📊 Content Length: {len(page_content)} characters")
            
            # Check for error indicators
            error_indicators = ['error', '404', 'not found', 'maintenance', 'under construction', 'temporarily unavailable']
            has_error = any(indicator in page_content.lower() for indicator in error_indicators)
            
            if has_error:
                logger.warning(f"❌ Error page detected at {url}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': 'Error page detected',
                    'title': page_title,
                    'content_length': len(page_content)
                })
                continue
            
            # Try to find price elements
            price_elements = driver.find_elements('*')
            price_found = False
            
            for element in price_elements[:100]:  # Check first 100 elements
                try:
                    text = element.text.strip()
                    if '$' in text and any(char.isdigit() for char in text):
                        logger.info(f"💰 Found potential price: {text}")
                        price_found = True
                        break
                except:
                    continue
            
            if price_found:
                logger.info(f"✅ Potential prices found at {url}")
                results.append({
                    'url': url,
                    'success': True,
                    'error': None,
                    'title': page_title,
                    'content_length': len(page_content),
                    'prices_found': True
                })
            else:
                logger.warning(f"⚠️ No prices found at {url}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': 'No prices found',
                    'title': page_title,
                    'content_length': len(page_content)
                })
            
            # Take screenshot
            screenshot_path = f"data/screenshots/CruiseAmerica_Test_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.screenshot(screenshot_path)
            logger.info(f"📸 Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            logger.error(f"❌ Error testing {url}: {e}")
            results.append({
                'url': url,
                'success': False,
                'error': str(e),
                'title': None,
                'content_length': 0
            })
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("CRUISE AMERICA TESTING SUMMARY")
    logger.info("="*50)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    logger.info(f"Total URLs tested: {len(results)}")
    logger.info(f"Successful: {len(successful)}")
    logger.info(f"Failed: {len(failed)}")
    
    if successful:
        logger.info("\n✅ Working URLs:")
        for r in successful:
            logger.info(f"  - {r['url']}")
    
    if failed:
        logger.info("\n❌ Failed URLs:")
        for r in failed:
            logger.info(f"  - {r['url']}: {r['error']}")
    
    # Save results
    output_path = f"output/cruise_america_advanced_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"\n[SAVED] Results: {output_path}")
    
    return results

if __name__ == "__main__":
    test_cruise_america_advanced()



