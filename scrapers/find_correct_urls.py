"""
Find the correct search URLs for the failing competitors
by navigating to their homepages and finding the search functionality
"""

from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
from bs4 import BeautifulSoup
import time
import json
import re
from datetime import datetime
from typing import Dict
from loguru import logger
import os

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

FAILING_COMPETITORS = [
    {
        'name': 'McRent',
        'homepage_url': 'https://www.mcrent.de/',
        'currency': 'EUR',
        'country': 'Germany',
    },
    {
        'name': 'Camperdays',
        'homepage_url': 'https://www.camperdays.com/',
        'currency': 'EUR',
        'country': 'Netherlands',
    },
    {
        'name': 'Goboony',
        'homepage_url': 'https://www.goboony.com/',
        'currency': 'EUR',
        'country': 'Netherlands',
    },
    {
        'name': 'Yescapa',
        'homepage_url': 'https://www.yescapa.com/',
        'currency': 'EUR',
        'country': 'France',
    },
    {
        'name': 'Cruise America',
        'homepage_url': 'https://www.cruiseamerica.com/',
        'currency': 'USD',
        'country': 'United States',
    }
]


@browser(
    reuse_driver=False,
    block_images=False,
    headless=True,
    user_agent=UserAgent.RANDOM,
    wait_for_complete_page_load=True
)
def find_search_urls(driver: Driver, data) -> Dict:
    """Find the correct search URLs by analyzing the homepage"""
    config = data
    
    logger.info(f"🔍 ANALYZING: {config['name']}")
    logger.info(f"🌐 Homepage: {config['homepage_url']}")
    
    result = {
        'company_name': config['name'],
        'homepage_url': config['homepage_url'],
        'timestamp': datetime.now().isoformat(),
        'search_urls_found': [],
        'search_forms_found': [],
        'navigation_links': [],
        'page_title': '',
        'success': False
    }
    
    try:
        # Navigate to homepage
        driver.get(config['homepage_url'])
        time.sleep(5)
        
        html = driver.page_html
        soup = BeautifulSoup(html, 'html.parser')
        result['page_title'] = driver.title
        
        # Check for Cloudflare
        if "Just a moment" in html or "Checking your browser" in html:
            logger.warning("🛡️ Cloudflare detected, waiting...")
            time.sleep(10)
            html = driver.page_html
            soup = BeautifulSoup(html, 'html.parser')
        
        logger.info(f"✅ Page loaded: {result['page_title']}")
        
        # Take screenshot
        screenshot_path = f"data/screenshots/{config['name']}_homepage_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path)
        result['screenshot'] = screenshot_path
        
        # Find all links that might lead to search/booking
        search_keywords = ['search', 'book', 'rent', 'hire', 'find', 'motorhome', 'camper', 'rv']
        
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            
            # Check if link contains search-related keywords
            if any(keyword in href.lower() or keyword in text for keyword in search_keywords):
                full_url = href if href.startswith('http') else f"{config['homepage_url'].rstrip('/')}{href}"
                result['search_urls_found'].append({
                    'url': full_url,
                    'text': link.get_text(strip=True),
                    'href': href
                })
        
        # Find search forms
        forms = soup.find_all('form')
        for form in forms:
            form_action = form.get('action', '')
            form_method = form.get('method', 'GET')
            
            # Look for input fields that might be for search
            inputs = form.find_all(['input', 'select'])
            input_types = [inp.get('type', '') for inp in inputs]
            input_names = [inp.get('name', '') for inp in inputs]
            
            if any(keyword in str(input_types + input_names).lower() for keyword in ['location', 'date', 'search', 'pickup']):
                result['search_forms_found'].append({
                    'action': form_action,
                    'method': form_method,
                    'inputs': [{'name': inp.get('name'), 'type': inp.get('type'), 'placeholder': inp.get('placeholder')} for inp in inputs]
                })
        
        # Find navigation menu items
        nav_elements = soup.find_all(['nav', 'ul', 'div'], class_=re.compile(r'nav|menu', re.I))
        for nav in nav_elements:
            nav_links = nav.find_all('a', href=True)
            for link in nav_links:
                result['navigation_links'].append({
                    'text': link.get_text(strip=True),
                    'href': link.get('href'),
                    'full_url': link.get('href') if link.get('href').startswith('http') else f"{config['homepage_url'].rstrip('/')}{link.get('href')}"
                })
        
        result['success'] = True
        logger.info(f"✅ Found {len(result['search_urls_found'])} potential search URLs")
        logger.info(f"✅ Found {len(result['search_forms_found'])} search forms")
        
    except Exception as e:
        logger.error(f"❌ Error analyzing {config['name']}: {e}")
        result['error'] = str(e)
    
    return result


def analyze_all_competitors():
    """Analyze all failing competitors to find correct URLs"""
    print("="*80)
    print("FINDING CORRECT SEARCH URLS FOR FAILING COMPETITORS")
    print("="*80 + "\n")
    
    results = []
    
    for config in FAILING_COMPETITORS:
        print(f"\n{'='*80}")
        print(f"ANALYZING: {config['name']}")
        print(f"{'='*80}\n")
        
        result = find_search_urls(data=config)
        results.append(result)
        
        if result['success']:
            print(f"\n[SUCCESS] {config['name']}:")
            print(f"  Page Title: {result['page_title']}")
            print(f"  Search URLs: {len(result['search_urls_found'])}")
            print(f"  Search Forms: {len(result['search_forms_found'])}")
            
            if result['search_urls_found']:
                print(f"  Top URLs:")
                for url_info in result['search_urls_found'][:5]:
                    print(f"    - {url_info['text']}: {url_info['url']}")
        else:
            print(f"\n[FAILED] {config['name']}: {result.get('error', 'Unknown error')}")
    
    # Save results
    output_path = f"output/url_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n[SAVED] Analysis results: {output_path}")
    
    # Summary
    print("\n" + "="*80)
    print("URL ANALYSIS SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r['success']]
    print(f"Analyzed: {len(successful)}/{len(FAILING_COMPETITORS)} competitors")
    
    for result in successful:
        print(f"\n{result['company_name']}:")
        print(f"  Search URLs: {len(result['search_urls_found'])}")
        print(f"  Search Forms: {len(result['search_forms_found'])}")
        if result['search_urls_found']:
            best_url = result['search_urls_found'][0]['url']
            print(f"  Best URL: {best_url}")
    
    return results


if __name__ == "__main__":
    analyze_all_competitors()
