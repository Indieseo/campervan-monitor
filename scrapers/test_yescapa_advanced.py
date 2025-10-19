"""
Advanced Yescapa Testing
Focus on cookie popup bypass strategies
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

# Yescapa URLs to test
YESCAPA_URLS = [
    'https://yescapa.fr/',
    'https://www.yescapa.com/en/',
    'https://yescapa.com/motorhome-rental/',
    'https://www.yescapa.com/rent/',
    'https://yescapa.com/',
    'https://www.yescapa.com/motorhome-hire-germany',
    'https://www.yescapa.com/motorhome-hire-germany-munich'
]

# Advanced cookie selectors
COOKIE_SELECTORS = [
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
    'div[class*="consent"] button',
    'div[id*="consent"] button',
    '.cookie-accept',
    '.accept-cookies',
    '#cookie-accept',
    '#accept-cookies',
    '[data-testid*="accept"]',
    '[data-testid*="cookie"]',
    'button[aria-label*="accept"]',
    'button[aria-label*="cookie"]'
]

def handle_cookie_popup_advanced(driver: Driver) -> bool:
    """Advanced cookie popup handler for Yescapa"""
    logger.info("🍪 Attempting advanced cookie popup handling...")
    
    try:
        # Strategy 1: Try all cookie selectors
        for selector in COOKIE_SELECTORS:
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
        
        # Strategy 2: JavaScript execution
        js_scripts = [
            "document.querySelectorAll('button').forEach(btn => { if(btn.textContent.toLowerCase().includes('accept')) btn.click(); });",
            "document.querySelectorAll('[class*=\"accept\"]').forEach(el => el.click());",
            "document.querySelectorAll('[id*=\"accept\"]').forEach(el => el.click());",
            "document.querySelectorAll('[class*=\"cookie\"] button').forEach(el => el.click());",
            "document.querySelectorAll('[id*=\"cookie\"] button').forEach(el => el.click());",
            "document.querySelectorAll('button[aria-label*=\"accept\"]').forEach(el => el.click());",
            "document.querySelectorAll('button[aria-label*=\"cookie\"]').forEach(el => el.click());"
        ]
        
        for script in js_scripts:
            try:
                driver.execute_script(script)
                time.sleep(2)
                logger.info("✅ Cookie popup handled with JavaScript")
                return True
            except:
                continue
        
        # Strategy 3: ESC key press
        try:
            driver.press_key("Escape")
            time.sleep(2)
            logger.info("✅ Cookie popup handled with ESC key")
            return True
        except:
            pass
        
        # Strategy 4: Wait and retry
        time.sleep(5)
        for selector in COOKIE_SELECTORS[:10]:  # Try top 10 selectors again
            try:
                elements = driver.find_elements(selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        logger.info(f"✅ Cookie popup handled with delayed selector: {selector}")
                        return True
            except:
                continue
        
        logger.warning("⚠️ Could not handle cookie popup with any strategy")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error in cookie popup handling: {e}")
        return False

@browser(headless=False, stealth=True, anti_detection=True)
def test_yescapa_advanced(driver: Driver):
    """Advanced testing for Yescapa with cookie bypass focus"""
    logger.info("🎯 ADVANCED YESCAPA TESTING")
    logger.info("="*50)
    
    results = []
    
    for i, url in enumerate(YESCAPA_URLS):
        logger.info(f"\n📍 Test {i+1}/{len(YESCAPA_URLS)}: {url}")
        
        try:
            # Navigate to URL
            driver.get(url)
            time.sleep(5)
            
            # Check page content before cookie handling
            page_content_before = driver.page_source
            page_title = driver.title
            
            logger.info(f"📄 Page Title: {page_title}")
            logger.info(f"📊 Content Length: {len(page_content_before)} characters")
            
            # Handle cookie popup
            cookie_handled = handle_cookie_popup_advanced(driver)
            
            # Check page content after cookie handling
            time.sleep(3)
            page_content_after = driver.page_source
            
            # Check for error indicators
            error_indicators = ['error', '404', 'not found', 'maintenance', 'under construction']
            has_error = any(indicator in page_content_after.lower() for indicator in error_indicators)
            
            if has_error:
                logger.warning(f"❌ Error page detected at {url}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': 'Error page detected',
                    'title': page_title,
                    'content_length': len(page_content_after),
                    'cookie_handled': cookie_handled
                })
                continue
            
            # Try to find price elements
            price_elements = driver.find_elements('*')
            price_found = False
            
            for element in price_elements[:100]:  # Check first 100 elements
                try:
                    text = element.text.strip()
                    if '€' in text and any(char.isdigit() for char in text):
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
                    'content_length': len(page_content_after),
                    'prices_found': True,
                    'cookie_handled': cookie_handled
                })
            else:
                logger.warning(f"⚠️ No prices found at {url}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': 'No prices found',
                    'title': page_title,
                    'content_length': len(page_content_after),
                    'cookie_handled': cookie_handled
                })
            
            # Take screenshot
            screenshot_path = f"data/screenshots/Yescapa_Test_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.screenshot(screenshot_path)
            logger.info(f"📸 Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            logger.error(f"❌ Error testing {url}: {e}")
            results.append({
                'url': url,
                'success': False,
                'error': str(e),
                'title': None,
                'content_length': 0,
                'cookie_handled': False
            })
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("YESCAPA TESTING SUMMARY")
    logger.info("="*50)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    cookie_handled = [r for r in results if r.get('cookie_handled', False)]
    
    logger.info(f"Total URLs tested: {len(results)}")
    logger.info(f"Successful: {len(successful)}")
    logger.info(f"Failed: {len(failed)}")
    logger.info(f"Cookie popups handled: {len(cookie_handled)}")
    
    if successful:
        logger.info("\n✅ Working URLs:")
        for r in successful:
            logger.info(f"  - {r['url']}")
    
    if failed:
        logger.info("\n❌ Failed URLs:")
        for r in failed:
            logger.info(f"  - {r['url']}: {r['error']}")
    
    # Save results
    output_path = f"output/yescapa_advanced_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"\n[SAVED] Results: {output_path}")
    
    return results

if __name__ == "__main__":
    test_yescapa_advanced()



