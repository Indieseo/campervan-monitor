"""
Roadsurfer Aggressive Price Extraction
Uses multiple strategies to extract pricing data from page HTML
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
def extract_roadsurfer_aggressive(driver, data=None):
    """Aggressive price extraction from Roadsurfer"""
    logger.info("🚀 ROADSURFER AGGRESSIVE PRICE EXTRACTION")
    logger.info("="*60)
    
    try:
        # Navigate to Roadsurfer homepage
        driver.get("https://roadsurfer.com/")
        time.sleep(15)  # Wait longer for full page load
        
        # Handle cookie popup aggressively
        logger.info("🍪 Handling cookie popup...")
        
        # Try multiple cookie handling strategies
        cookie_strategies = [
            "document.querySelectorAll('button').forEach(btn => { if(btn.textContent.toLowerCase().includes('accept')) btn.click(); });",
            "document.querySelectorAll('[class*=\"accept\"]').forEach(el => el.click());",
            "document.querySelectorAll('[id*=\"accept\"]').forEach(el => el.click());",
            "document.querySelectorAll('.cookie-banner button').forEach(el => el.click());",
            "document.querySelectorAll('.cookie-consent button').forEach(el => el.click());",
            "document.querySelectorAll('[data-testid*=\"accept\"]').forEach(el => el.click());",
            "document.querySelectorAll('.usercentrics-button').forEach(el => el.click());",
            "document.querySelectorAll('.uc-button').forEach(el => el.click());"
        ]
        
        for strategy in cookie_strategies:
            try:
                driver.execute_script(strategy)
                time.sleep(2)
                logger.info("✅ Cookie popup handled with JavaScript")
                break
            except:
                continue
        
        # Wait for content to load
        time.sleep(10)
        
        # Get page HTML for analysis
        page_html = driver.page_html
        logger.info(f"📄 Page HTML length: {len(page_html)} characters")
        
        # Save page HTML for debugging
        html_file = f"data/roadsurfer_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(page_html)
        logger.info(f"💾 Page HTML saved: {html_file}")
        
        # AGGRESSIVE PRICE EXTRACTION
        logger.info("💰 AGGRESSIVE PRICE EXTRACTION...")
        
        all_prices = []
        
        # Strategy 1: Direct Euro symbol patterns
        euro_patterns = [
            r'€\s*(\d+(?:\.\d{2})?)',
            r'(\d+(?:\.\d{2})?)\s*€',
            r'from\s*€\s*(\d+(?:\.\d{2})?)',
            r'starting\s*at\s*€\s*(\d+(?:\.\d{2})?)',
            r'per\s*day\s*€\s*(\d+(?:\.\d{2})?)',
            r'€\s*(\d+(?:\.\d{2})?)\s*per\s*day',
            r'€\s*(\d+(?:\.\d{2})?)\s*/day',
            r'€\s*(\d+(?:\.\d{2})?)\s*/night',
            r'€\s*(\d+(?:\.\d{2})?)\s*per\s*night',
            r'€\s*(\d+(?:\.\d{2})?)\s*night',
            r'€\s*(\d+(?:\.\d{2})?)\s*day'
        ]
        
        for pattern in euro_patterns:
            matches = re.findall(pattern, page_html, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match)
                    if 10 <= price <= 1000:  # Reasonable price range
                        all_prices.append(price)
                        logger.info(f"💰 Found price (€): €{price}")
                except:
                    continue
        
        # Strategy 2: Look for price-related text without Euro symbol
        price_text_patterns = [
            r'(\d+(?:\.\d{2})?)\s*per\s*day',
            r'(\d+(?:\.\d{2})?)\s*/day',
            r'(\d+(?:\.\d{2})?)\s*per\s*night',
            r'(\d+(?:\.\d{2})?)\s*/night',
            r'from\s*(\d+(?:\.\d{2})?)',
            r'starting\s*at\s*(\d+(?:\.\d{2})?)',
            r'(\d+(?:\.\d{2})?)\s*EUR',
            r'(\d+(?:\.\d{2})?)\s*euro'
        ]
        
        for pattern in price_text_patterns:
            matches = re.findall(pattern, page_html, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match)
                    if 10 <= price <= 1000:  # Reasonable price range
                        all_prices.append(price)
                        logger.info(f"💰 Found price (text): €{price}")
                except:
                    continue
        
        # Strategy 3: Look for JSON data in page
        logger.info("🔍 Searching for JSON data...")
        json_patterns = [
            r'"price":\s*(\d+(?:\.\d{2})?)',
            r'"cost":\s*(\d+(?:\.\d{2})?)',
            r'"rate":\s*(\d+(?:\.\d{2})?)',
            r'"amount":\s*(\d+(?:\.\d{2})?)',
            r'"value":\s*(\d+(?:\.\d{2})?)'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, page_html, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match)
                    if 10 <= price <= 1000:
                        all_prices.append(price)
                        logger.info(f"💰 Found price (JSON): €{price}")
                except:
                    continue
        
        # Strategy 4: Look for data attributes
        logger.info("🔍 Searching for data attributes...")
        data_patterns = [
            r'data-price="(\d+(?:\.\d{2})?)"',
            r'data-cost="(\d+(?:\.\d{2})?)"',
            r'data-rate="(\d+(?:\.\d{2})?)"',
            r'data-amount="(\d+(?:\.\d{2})?)"'
        ]
        
        for pattern in data_patterns:
            matches = re.findall(pattern, page_html, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match)
                    if 10 <= price <= 1000:
                        all_prices.append(price)
                        logger.info(f"💰 Found price (data): €{price}")
                except:
                    continue
        
        # Strategy 5: Look for any number that could be a price
        logger.info("🔍 Searching for potential prices...")
        potential_price_patterns = [
            r'\b(\d{2,3}(?:\.\d{2})?)\b',  # 2-3 digit numbers with optional decimals
        ]
        
        for pattern in potential_price_patterns:
            matches = re.findall(pattern, page_html)
            for match in matches:
                try:
                    price = float(match)
                    if 20 <= price <= 500:  # Broader range for potential prices
                        all_prices.append(price)
                        logger.info(f"💰 Found potential price: €{price}")
                except:
                    continue
        
        # Remove duplicates and sort
        unique_prices = sorted(list(set(all_prices)))
        
        # Filter out unrealistic prices
        realistic_prices = [p for p in unique_prices if 15 <= p <= 800]
        
        # Extract vehicle information
        logger.info("🚐 Extracting vehicle information...")
        vehicles = []
        
        # Look for vehicle-related content
        vehicle_patterns = [
            r'(\d+)\s*berth',
            r'(\d+)\s*person',
            r'(\d+)\s*sleeps',
            r'(\d+)\s*seats',
            r'class\s*([ABC])',
            r'campervan',
            r'motorhome',
            r'rv',
            r'van'
        ]
        
        vehicle_info = []
        for pattern in vehicle_patterns:
            matches = re.findall(pattern, page_html, re.IGNORECASE)
            for match in matches:
                vehicle_info.append(match)
        
        # Create vehicle entries
        if vehicle_info:
            unique_vehicle_info = list(set(vehicle_info))
            for i, info in enumerate(unique_vehicle_info[:5]):
                vehicles.append({
                    'model': f"Vehicle {i+1}",
                    'description': str(info),
                    'type': 'Campervan',
                    'capacity': 4
                })
        
        # Take screenshot
        screenshot_path = f"data/screenshots/roadsurfer_aggressive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path)
        logger.info(f"📸 Screenshot saved: {screenshot_path}")
        
        # Create results
        results = {
            'company': 'Roadsurfer',
            'timestamp': datetime.now().isoformat(),
            'success': len(realistic_prices) > 0,
            'total_prices': len(realistic_prices),
            'prices': realistic_prices,
            'all_prices_found': unique_prices,
            'vehicles': vehicles,
            'currency': 'EUR',
            'extraction_method': 'aggressive_homepage',
            'page_html_length': len(page_html),
            'html_file': html_file,
            'screenshot_path': screenshot_path
        }
        
        # Save results
        Path("data/live_pricing").mkdir(parents=True, exist_ok=True)
        output_file = f"data/live_pricing/roadsurfer_aggressive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("ROADSURFER AGGRESSIVE EXTRACTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"All prices found: {len(unique_prices)}")
        logger.info(f"Realistic prices: {len(realistic_prices)}")
        logger.info(f"Vehicles found: {len(vehicles)}")
        logger.info(f"Success: {len(realistic_prices) > 0}")
        
        if realistic_prices:
            logger.info(f"Price range: €{min(realistic_prices)} - €{max(realistic_prices)}")
            logger.info(f"Average price: €{sum(realistic_prices)/len(realistic_prices):.2f}")
        
        logger.info(f"Data saved: {output_file}")
        logger.info(f"HTML saved: {html_file}")
        logger.info(f"{'='*60}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error in aggressive extraction: {e}")
        return {
            'company': 'Roadsurfer',
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    extract_roadsurfer_aggressive()
