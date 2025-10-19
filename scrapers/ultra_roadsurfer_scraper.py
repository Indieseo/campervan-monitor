"""
ULTRA ROADSURFER SCRAPER
Maximum aggression - API interception + multiple search locations + date ranges
Gets ALL available pricing data
"""

import asyncio
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Path("output").mkdir(exist_ok=True)
Path("data/screenshots").mkdir(parents=True, exist_ok=True)
Path("data/live_pricing").mkdir(parents=True, exist_ok=True)

# Search configurations
SEARCH_CONFIGS = [
    {'location': 'Munich, Germany', 'url': 'https://roadsurfer.com/'},
    {'location': 'Berlin, Germany', 'url': 'https://roadsurfer.com/'},
    {'location': 'Hamburg, Germany', 'url': 'https://roadsurfer.com/'},
    {'location': 'Frankfurt, Germany', 'url': 'https://roadsurfer.com/'},
    {'location': 'Los Angeles', 'url': 'https://roadsurfer.com/'},
    {'location': 'San Francisco', 'url': 'https://roadsurfer.com/'},
]

# Date ranges to try
DATE_RANGES = [
    (30, 37),   # 30 days from now, 7 day rental
    (60, 67),   # 60 days from now
    (90, 97),   # 90 days from now
    (120, 127), # 120 days from now
]

async def ultra_scrape_roadsurfer():
    """Ultra aggressive Roadsurfer scraping with API interception"""
    logger.info("="*80)
    logger.info("ULTRA ROADSURFER SCRAPER - ALL PRICING DATA")
    logger.info("="*80)

    all_results = {
        'searches_performed': 0,
        'api_calls_captured': [],
        'prices_by_location': {},
        'all_prices': [],
        'success': False
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # API interception
        async def handle_response(response):
            url = response.url
            if any(kw in url.lower() for kw in ['api', 'search', 'booking', 'price', 'vehicle', 'availability']):
                try:
                    if response.status == 200 and 'json' in response.headers.get('content-type', ''):
                        data = await response.json()
                        logger.info(f"[API CAPTURED] {url[:100]}")

                        all_results['api_calls_captured'].append({
                            'url': url,
                            'data': data,
                            'timestamp': datetime.now().isoformat()
                        })

                        # Extract prices
                        extract_prices_recursive(data, all_results['all_prices'])
                except:
                    pass

        page.on("response", handle_response)

        # Try each search configuration
        for config in SEARCH_CONFIGS:
            location = config['location']
            logger.info(f"\n{'='*80}")
            logger.info(f"SEARCHING: {location}")
            logger.info(f"{'='*80}")

            try:
                await page.goto(config['url'], wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(5)

                # Handle cookies
                try:
                    await page.evaluate("""
                        () => {
                            const btns = document.querySelectorAll('button');
                            for (const btn of btns) {
                                if (btn.textContent.toLowerCase().includes('accept')) {
                                    btn.click();
                                    break;
                                }
                            }
                        }
                    """)
                    await asyncio.sleep(2)
                except:
                    pass

                # Close any modals
                await page.keyboard.press('Escape')
                await asyncio.sleep(1)

                # Find and fill location
                logger.info(f"Filling location: {location}")
                try:
                    # Try multiple location input strategies
                    location_filled = False

                    # Strategy 1: Direct input field
                    for selector in ['input[placeholder*="location" i]', 'input[type="text"]', 'input[name*="location" i]']:
                        try:
                            input_elem = page.locator(selector).first
                            if await input_elem.is_visible(timeout=2000):
                                await input_elem.click()
                                await asyncio.sleep(1)
                                await input_elem.fill(location)
                                await asyncio.sleep(2)

                                # Try to select from dropdown
                                try:
                                    await page.locator(f'text=/{location.split(",")[0]}/i').first.click(timeout=3000)
                                except:
                                    await input_elem.press('Enter')

                                location_filled = True
                                logger.info(f"Location filled: {selector}")
                                break
                        except:
                            continue

                    if location_filled:
                        await asyncio.sleep(3)

                        # Wait for results to load
                        await asyncio.sleep(5)

                        # Extract prices from page
                        content = await page.content()
                        prices = extract_prices_from_html(content)

                        if prices:
                            if location not in all_results['prices_by_location']:
                                all_results['prices_by_location'][location] = []
                            all_results['prices_by_location'][location].extend(prices)
                            all_results['all_prices'].extend(prices)
                            logger.info(f"Found {len(prices)} prices for {location}: {prices[:10]}")

                        all_results['searches_performed'] += 1

                        # Screenshot
                        screenshot = f"data/screenshots/Roadsurfer_ULTRA_{location.replace(' ', '_').replace(',', '')}_{datetime.now().strftime('%H%M%S')}.png"
                        await page.screenshot(path=screenshot, full_page=True)
                        logger.info(f"Screenshot: {screenshot}")

                except Exception as e:
                    logger.warning(f"Location {location} error: {e}")

                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Search {location} failed: {e}")

        await browser.close()

    # Process results
    all_results['all_prices'] = list(set(all_results['all_prices']))

    if all_results['all_prices']:
        all_results['success'] = True
        all_results['summary'] = {
            'total_unique_prices': len(all_results['all_prices']),
            'min_price': min(all_results['all_prices']),
            'max_price': max(all_results['all_prices']),
            'avg_price': sum(all_results['all_prices']) / len(all_results['all_prices']),
            'currency': 'EUR',
            'locations_searched': len(all_results['prices_by_location'])
        }

    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"data/live_pricing/roadsurfer_ultra_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    logger.info("\n" + "="*80)
    logger.info("ULTRA ROADSURFER SCRAPING COMPLETE")
    logger.info(f"Searches performed: {all_results['searches_performed']}")
    logger.info(f"API calls captured: {len(all_results['api_calls_captured'])}")
    logger.info(f"Total unique prices: {len(all_results['all_prices'])}")
    if all_results['all_prices']:
        logger.info(f"Price range: €{min(all_results['all_prices'])}-€{max(all_results['all_prices'])}")
    logger.info(f"Success: {all_results['success']}")
    logger.info(f"Data saved: {output_file}")
    logger.info("="*80)

    return all_results


def extract_prices_recursive(data, prices_list):
    """Recursively extract prices from JSON"""
    if isinstance(data, dict):
        for key, value in data.items():
            if any(word in str(key).lower() for word in ['price', 'cost', 'rate', 'amount', 'total']):
                if isinstance(value, (int, float)) and 20 <= value <= 1000:
                    prices_list.append(float(value))
                    logger.info(f"[JSON PRICE] {key}: €{value}")
            extract_prices_recursive(value, prices_list)
    elif isinstance(data, list):
        for item in data:
            extract_prices_recursive(item, prices_list)


def extract_prices_from_html(html):
    """Extract EUR prices from HTML"""
    patterns = [
        r'€\s*(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)',
        r'(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*€',
        r'EUR\s*(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)',
    ]

    prices = []
    for pattern in patterns:
        matches = re.findall(pattern, html)
        for match in matches:
            try:
                clean = match.replace(',', '').replace(' ', '')
                price = float(clean)
                if 20 <= price <= 1000:
                    prices.append(price)
            except:
                continue

    return list(set(prices))


if __name__ == "__main__":
    asyncio.run(ultra_scrape_roadsurfer())
