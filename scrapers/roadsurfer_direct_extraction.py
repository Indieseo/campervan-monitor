"""
Roadsurfer Direct Price Extraction
Extracts pricing data directly from homepage without search forms
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import sys
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from botasaurus.browser import browser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

@browser(
    headless=False,
    reuse_driver=False,
    block_images=False,
    wait_for_complete_page_load=True
)
def extract_roadsurfer_prices_direct(driver, data=None):
    """Extract pricing data directly from Roadsurfer homepage"""
    logger.info("🚀 ROADSURFER DIRECT PRICE EXTRACTION")
    logger.info("="*60)
    
    try:
        # Navigate to Roadsurfer homepage
        driver.get("https://roadsurfer.com/")
        time.sleep(10)  # Wait for full page load
        
        # Handle cookie popup aggressively
        logger.info("🍪 Handling cookie popup...")
        cookie_handled = False
        
        # Try multiple cookie handling strategies
        cookie_strategies = [
            # JavaScript execution
            "document.querySelectorAll('button').forEach(btn => { if(btn.textContent.toLowerCase().includes('accept')) btn.click(); });",
            "document.querySelectorAll('[class*=\"accept\"]').forEach(el => el.click());",
            "document.querySelectorAll('[id*=\"accept\"]').forEach(el => el.click());",
            "document.querySelectorAll('.cookie-banner button').forEach(el => el.click());",
            "document.querySelectorAll('.cookie-consent button').forEach(el => el.click());",
            "document.querySelectorAll('[data-testid*=\"accept\"]').forEach(el => el.click());",
            # Usercentrics specific
            "document.querySelectorAll('.usercentrics-button').forEach(el => el.click());",
            "document.querySelectorAll('.uc-button').forEach(el => el.click());"
        ]
        
        for strategy in cookie_strategies:
            try:
                driver.execute_script(strategy)
                time.sleep(2)
                cookie_handled = True
                logger.info("✅ Cookie popup handled with JavaScript")
                break
            except:
                continue
        
        # Try key presses
        if not cookie_handled:
            for key in ["Escape", "Enter", "Tab"]:
                try:
                    driver.press_key(key)
                    time.sleep(2)
                    cookie_handled = True
                    logger.info(f"✅ Cookie popup handled with {key} key")
                    break
                except:
                    continue
        
        # Wait for content to load
        time.sleep(5)
        
        # Get page source for analysis
        page_source = driver.page_html
        logger.info(f"📄 Page source length: {len(page_source)} characters")
        
        # Extract all prices using regex
        logger.info("💰 Extracting prices from page source...")
        
        # Multiple price patterns
        price_patterns = [
            r'€\s*(\d+(?:\.\d{2})?)',  # €85.50
            r'(\d+(?:\.\d{2})?)\s*€',  # 85.50€
            r'from\s*€\s*(\d+(?:\.\d{2})?)',  # from €85.50
            r'starting\s*at\s*€\s*(\d+(?:\.\d{2})?)',  # starting at €85.50
            r'per\s*day\s*€\s*(\d+(?:\.\d{2})?)',  # per day €85.50
            r'€\s*(\d+(?:\.\d{2})?)\s*per\s*day',  # €85.50 per day
            r'€\s*(\d+(?:\.\d{2})?)\s*/day',  # €85.50/day
            r'€\s*(\d+(?:\.\d{2})?)\s*/night'  # €85.50/night
        ]
        
        all_prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match)
                    if 10 <= price <= 1000:  # Reasonable price range
                        all_prices.append(price)
                        logger.info(f"💰 Found price: €{price}")
                except:
                    continue
        
        # Remove duplicates and sort
        unique_prices = sorted(list(set(all_prices)))
        
        # Also try to find prices in visible text
        logger.info("🔍 Searching for prices in visible elements...")
        try:
            # Get all text elements
            elements = driver.find_elements('*')
            for element in elements[:200]:  # Check first 200 elements
                try:
                    text = element.text.strip()
                    if '€' in text and any(char.isdigit() for char in text):
                        # Extract price from text
                        price_match = re.search(r'€\s*(\d+(?:\.\d{2})?)', text)
                        if price_match:
                            price = float(price_match.group(1))
                            if 10 <= price <= 1000 and price not in unique_prices:
                                unique_prices.append(price)
                                logger.info(f"💰 Found price in element: €{price} - {text[:50]}...")
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error searching elements: {e}")
        
        # Sort prices again
        unique_prices = sorted(unique_prices)
        
        # Extract vehicle information
        logger.info("🚐 Extracting vehicle information...")
        vehicles = []
        
        # Look for vehicle-related text
        vehicle_keywords = ['campervan', 'motorhome', 'rv', 'van', 'vehicle', 'berth', 'sleeps']
        vehicle_texts = []
        
        try:
            elements = driver.find_elements('*')
            for element in elements[:100]:
                try:
                    text = element.text.strip().lower()
                    if any(keyword in text for keyword in vehicle_keywords) and len(text) > 10:
                        vehicle_texts.append(element.text.strip())
                except:
                    continue
        except:
            pass
        
        # Create vehicle entries
        if vehicle_texts:
            for i, text in enumerate(vehicle_texts[:5]):  # Limit to 5 vehicles
                vehicles.append({
                    'model': f"Vehicle {i+1}",
                    'description': text[:100],
                    'type': 'Campervan',
                    'capacity': 4  # Default capacity
                })
        
        # Take screenshot
        screenshot_path = f"data/screenshots/roadsurfer_direct_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path)
        logger.info(f"📸 Screenshot saved: {screenshot_path}")
        
        # Create results
        results = {
            'company': 'Roadsurfer',
            'timestamp': datetime.now().isoformat(),
            'success': len(unique_prices) > 0,
            'total_prices': len(unique_prices),
            'prices': unique_prices,
            'vehicles': vehicles,
            'currency': 'EUR',
            'extraction_method': 'direct_homepage',
            'page_source_length': len(page_source),
            'screenshot_path': screenshot_path
        }
        
        # Save results
        Path("data/live_pricing").mkdir(parents=True, exist_ok=True)
        output_file = f"data/live_pricing/roadsurfer_direct_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("ROADSURFER DIRECT EXTRACTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Prices found: {len(unique_prices)}")
        logger.info(f"Vehicles found: {len(vehicles)}")
        logger.info(f"Success: {len(unique_prices) > 0}")
        
        if unique_prices:
            logger.info(f"Price range: €{min(unique_prices)} - €{max(unique_prices)}")
            logger.info(f"Average price: €{sum(unique_prices)/len(unique_prices):.2f}")
        
        logger.info(f"Data saved: {output_file}")
        logger.info(f"{'='*60}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error in direct extraction: {e}")
        return {
            'company': 'Roadsurfer',
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    extract_roadsurfer_prices_direct()
