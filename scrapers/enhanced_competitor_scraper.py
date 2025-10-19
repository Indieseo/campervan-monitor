"""
Enhanced Competitor Scraper with Cookie Popup Handling
Gets real data from the remaining 4 competitors
"""

from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
from bs4 import BeautifulSoup
import re
import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
import os

# Ensure output and screenshots directories exist
os.makedirs("output", exist_ok=True)
os.makedirs("data/screenshots", exist_ok=True)

# Enhanced competitor configurations with better URLs and cookie handling
ENHANCED_COMPETITORS = [
    {
        'name': 'McRent',
        'homepage_url': 'https://www.mcrent.de/',
        'search_url': 'https://www.mcrent.de/wohnmobile/',  # Vehicle catalog page
        'currency': 'EUR',
        'country': 'Germany',
        'location_to_search': 'Munich',
        'cookie_selectors': [
            'button[class*="accept"]',
            'button[id*="accept"]',
            'button:contains("Accept")',
            'button:contains("OK")',
            'button:contains("Agree")'
        ]
    },
    {
        'name': 'Goboony',
        'homepage_url': 'https://www.goboony.com/',
        'search_url': 'https://www.goboony.com/',  # Homepage with search
        'currency': 'EUR',
        'country': 'Netherlands',
        'location_to_search': 'Munich',
        'cookie_selectors': [
            'button[class*="accept"]',
            'button[id*="accept"]',
            'button:contains("Accept")',
            'button:contains("OK")',
            'button:contains("Agree")'
        ]
    },
    {
        'name': 'Yescapa',
        'homepage_url': 'https://www.yescapa.com/',
        'search_url': 'https://www.yescapa.com/',  # Homepage
        'currency': 'EUR',
        'country': 'France',
        'location_to_search': 'Munich',
        'cookie_selectors': [
            'button:contains("OK for me")',
            'button:contains("I choose")',
            'button[class*="accept"]',
            'button[id*="accept"]'
        ]
    },
    {
        'name': 'Cruise America',
        'homepage_url': 'https://www.cruiseamerica.com/',
        'search_url': 'https://www.cruiseamerica.com/',  # Homepage
        'currency': 'USD',
        'country': 'United States',
        'location_to_search': 'Los Angeles',
        'cookie_selectors': [
            'button[class*="accept"]',
            'button[id*="accept"]',
            'button:contains("Accept")',
            'button:contains("OK")',
            'button:contains("Agree")'
        ]
    }
]


def handle_cookie_popup(driver: Driver, cookie_selectors: List[str]) -> bool:
    """Handle cookie popups using various selectors"""
    try:
        for selector in cookie_selectors:
            try:
                # Try to find and click cookie accept button
                cookie_button = driver.get_element(selector)
                if cookie_button:
                    cookie_button.click()
                    logger.info(f"✅ Clicked cookie button with selector: {selector}")
                    time.sleep(2)
                    return True
            except:
                continue
        
        # Try JavaScript approach
        try:
            driver.evaluate_script("""
                // Common cookie button selectors
                const selectors = [
                    'button[class*="accept"]',
                    'button[id*="accept"]',
                    'button:contains("Accept")',
                    'button:contains("OK")',
                    'button:contains("Agree")',
                    '[data-testid*="accept"]',
                    '.cookie-accept',
                    '#cookie-accept'
                ];
                
                for (const selector of selectors) {
                    const button = document.querySelector(selector);
                    if (button) {
                        button.click();
                        return true;
                    }
                }
                return false;
            """)
            logger.info("✅ Handled cookie popup via JavaScript")
            time.sleep(2)
            return True
        except:
            pass
        
        logger.warning("⚠️ Could not find cookie accept button")
        return False
        
    except Exception as e:
        logger.warning(f"⚠️ Cookie handling error: {e}")
        return False


def extract_prices_enhanced(text: str, currency: str) -> List[float]:
    """Enhanced price extraction with multiple patterns"""
    prices = []
    
    # Different price patterns
    patterns = [
        rf'{currency}\s*(\d+(?:,\d{{3}})*(?:\.\d{{2}})?)',
        rf'(\d+(?:,\d{{3}})*(?:\.\d{{2}})?)\s*{currency}',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per|/)\s*(?:day|night)',
        r'from\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:day|night)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:€|$|USD|EUR)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                price = float(match.replace(',', ''))
                if 20 <= price <= 2000:  # Reasonable rental price range
                    prices.append(price)
            except ValueError:
                continue
    
    return sorted(list(set(prices)))  # Remove duplicates and sort


@browser(
    reuse_driver=False,
    block_images=False,
    headless=True,
    user_agent=UserAgent.RANDOM,
    wait_for_complete_page_load=True
)
def scrape_enhanced_competitor(driver: Driver, data) -> Dict:
    """Enhanced scraper with cookie handling and better URL discovery"""
    config = data
    
    logger.info(f"🚀 ENHANCED SCRAPING: {config['name']}")
    logger.info(f"🌐 URL: {config['search_url']}")
    
    result = {
        'company_name': config['name'],
        'search_location': config['location_to_search'],
        'search_start_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'search_end_date': (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat(),
        'currency': config['currency'],
        'url': config['search_url'],
        'num_results': 0,
        'min_price': None,
        'max_price': None,
        'avg_price': None,
        'prices_found': [],
        'notes': '',
        'screenshot_path': None,
        'success': False,
        'scraping_strategy': 'enhanced_with_cookie_handling'
    }
    
    try:
        # Navigate to the URL
        logger.info(f"🌐 Navigating to {config['search_url']}")
        driver.get(config['search_url'])
        
        # Wait for initial page load
        time.sleep(random.uniform(5, 8))
        
        # Handle cookie popup
        logger.info("🍪 Checking for cookie popup...")
        cookie_handled = handle_cookie_popup(driver, config.get('cookie_selectors', []))
        if cookie_handled:
            time.sleep(2)  # Wait for popup to disappear
        
        # Check for Cloudflare
        html = driver.page_html
        if "Just a moment" in html or "Checking your browser" in html:
            logger.warning("🛡️ Cloudflare detected, waiting...")
            time.sleep(random.uniform(10, 15))
            html = driver.page_html
            if "Just a moment" in html or "Checking your browser" in html:
                logger.error("❌ Cloudflare not cleared")
                result['notes'] = 'Cloudflare challenge not cleared'
                return result
        
        title = driver.title
        logger.info(f"✅ Page loaded: {title}")
        
        # Take screenshot
        screenshot_path = f"data/screenshots/{config['name']}_ENHANCED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path)
        result['screenshot_path'] = screenshot_path
        
        # Extract text content
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        logger.info(f"📄 Page text length: {len(text)} characters")
        
        # Try to find search functionality and interact with it
        logger.info("🔍 Looking for search functionality...")
        
        # Look for search forms
        search_forms = soup.find_all('form')
        for form in search_forms:
            form_inputs = form.find_all(['input', 'select'])
            input_names = [inp.get('name', '').lower() for inp in form_inputs]
            input_placeholders = [inp.get('placeholder', '').lower() for inp in form_inputs]
            
            # Check if this looks like a search form
            search_keywords = ['location', 'date', 'search', 'pickup', 'destination']
            if any(keyword in ' '.join(input_names + input_placeholders) for keyword in search_keywords):
                logger.info("🎯 Found search form, attempting to interact...")
                
                try:
                    # Try to fill location field
                    location_input = None
                    for inp in form_inputs:
                        if any(keyword in inp.get('name', '').lower() or keyword in inp.get('placeholder', '').lower() 
                               for keyword in ['location', 'pickup', 'destination']):
                            location_input = inp
                            break
                    
                    if location_input:
                        location_input.send_keys(config['location_to_search'])
                        time.sleep(2)
                    
                    # Look for search button
                    search_button = form.find('button', type='submit') or form.find('input', type='submit')
                    if search_button:
                        search_button.click()
                        time.sleep(random.uniform(5, 8))
                        
                        # Update HTML after search
                        html = driver.page_html
                        soup = BeautifulSoup(html, 'html.parser')
                        text = soup.get_text(separator=' ', strip=True)
                        logger.info("✅ Performed search, updated page content")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Search form interaction failed: {e}")
        
        # Extract prices using multiple methods
        prices = extract_prices_enhanced(text, config['currency'])
        
        # Also try extracting from specific elements
        price_elements = soup.find_all(['span', 'div', 'p', 'strong'], string=re.compile(r'[€$]\s*\d+|\d+\s*[€$]'))
        for element in price_elements:
            element_text = element.get_text()
            element_prices = extract_prices_enhanced(element_text, config['currency'])
            prices.extend(element_prices)
        
        # Look for data attributes
        elements_with_data = soup.find_all(attrs={'data-price': True})
        for element in elements_with_data:
            try:
                price = float(element.get('data-price'))
                if 20 <= price <= 2000:
                    prices.append(price)
            except:
                continue
        
        # Look for class names containing 'price'
        price_classes = soup.find_all(class_=re.compile(r'price|cost|rate', re.I))
        for element in price_classes:
            element_text = element.get_text()
            element_prices = extract_prices_enhanced(element_text, config['currency'])
            prices.extend(element_prices)
        
        # Remove duplicates and filter
        prices = sorted(list(set(prices)))
        prices = [p for p in prices if 20 <= p <= 2000]  # Final filter
        
        if prices:
            result['prices_found'] = prices
            result['num_results'] = len(prices)
            result['min_price'] = min(prices)
            result['max_price'] = max(prices)
            result['avg_price'] = round(sum(prices) / len(prices), 2)
            result['success'] = True
            logger.info(f"✅ SUCCESS: Found {len(prices)} prices: {config['currency']}{result['min_price']}-{result['max_price']}/night")
        else:
            logger.warning("⚠️ No prices found")
            result['notes'] = 'No prices found with enhanced extraction methods'
            
            # Save debug HTML
            debug_file = f"output/{config['name']}_enhanced_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"🔍 Debug HTML saved: {debug_file}")
    
    except Exception as e:
        logger.error(f"❌ Error scraping {config['name']}: {e}")
        result['notes'] = f"Error: {str(e)[:200]}"
    
    return result


def scrape_all_enhanced():
    """Scrape all competitors with enhanced methods"""
    print("="*80)
    print("ENHANCED COMPETITOR SCRAPING - COOKIE HANDLING")
    print("="*80 + "\n")
    
    results = []
    
    for config in ENHANCED_COMPETITORS:
        print(f"\n{'='*80}")
        print(f"ENHANCED SCRAPING: {config['name']}")
        print(f"{'='*80}\n")
        
        result = scrape_enhanced_competitor(data=config)
        results.append(result)
        
        if result['success']:
            print(f"\n[SUCCESS] {config['name']}:")
            print(f"  Results: {result['num_results']} prices found")
            print(f"  Range: {config['currency']}{result['min_price']}-{result['max_price']}/night")
            print(f"  Average: {config['currency']}{result['avg_price']}/night")
        else:
            print(f"\n[FAILED] {config['name']}: {result['notes']}")
    
    # Summary
    print("\n" + "="*80)
    print("ENHANCED SCRAPING COMPLETE - SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r['success']]
    print(f"Success: {len(successful)}/{len(ENHANCED_COMPETITORS)} competitors")
    
    if successful:
        print("\nSuccessful Scraping:")
        for r in successful:
            print(f"  ✅ {r['company_name']:15} {r['num_results']} prices | {r['currency']}{r['min_price']}-{r['max_price']}/night")
    
    failed = [r for r in results if not r['success']]
    if failed:
        print("\nStill Failing:")
        for r in failed:
            print(f"  ❌ {r['company_name']:15} {r['notes']}")
    
    # Save results
    output_path = f"output/enhanced_scraping_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[SAVED] Results: {output_path}")
    
    return results


if __name__ == "__main__":
    scrape_all_enhanced()



