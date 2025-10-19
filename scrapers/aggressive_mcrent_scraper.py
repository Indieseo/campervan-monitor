"""
AGGRESSIVE MCRENT SCRAPER
Uses Playwright network interception to capture live booking API data
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

# All possible McRent URLs
MCRENT_URLS = [
    'https://www.mcrent.com/en/',
    'https://www.mcrent.de/',
    'https://www.mcrent.de/en/',
    'https://mcrent.com/',
    'https://www.mcrent.de/en/motorhome-rental/',
    'https://www.mcrent.de/en/motorhome-rental/germany/',
    'https://mcrent.de/',
]

async def intercept_and_scrape_mcrent():
    """Use network interception to capture McRent's live pricing API"""
    logger.info("="*80)
    logger.info("AGGRESSIVE MCRENT SCRAPER - API INTERCEPTION")
    logger.info("="*80)

    captured_data = {
        'api_calls': [],
        'prices_found': [],
        'success': False
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # Capture all network requests
        async def handle_request(request):
            url = request.url
            if any(keyword in url.lower() for keyword in ['price', 'search', 'booking', 'availability', 'api', 'vehicle', 'rent']):
                logger.info(f"[REQUEST] {request.method} {url}")
                captured_data['api_calls'].append({
                    'type': 'request',
                    'method': request.method,
                    'url': url,
                    'timestamp': datetime.now().isoformat()
                })

        async def handle_response(response):
            url = response.url
            if any(keyword in url.lower() for keyword in ['price', 'search', 'booking', 'availability', 'api', 'vehicle', 'rent']):
                try:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'json' in content_type:
                            try:
                                json_data = await response.json()
                                logger.info(f"[API DATA] {url}")
                                logger.info(f"[JSON] {json.dumps(json_data, indent=2)[:500]}")

                                captured_data['api_calls'].append({
                                    'type': 'response',
                                    'url': url,
                                    'status': response.status,
                                    'data': json_data,
                                    'timestamp': datetime.now().isoformat()
                                })

                                # Extract prices from JSON
                                extract_prices_from_json(json_data, captured_data)
                            except:
                                pass
                except Exception as e:
                    logger.debug(f"Response handling error: {e}")

        page.on("request", handle_request)
        page.on("response", handle_response)

        # Try each URL
        for url in MCRENT_URLS:
            logger.info(f"\nTrying: {url}")

            try:
                await page.goto(url, wait_until='networkidle', timeout=60000)
                await asyncio.sleep(5)

                # Handle cookies
                try:
                    accept_btn = page.locator('button:has-text("Accept"), button:has-text("OK")').first
                    if await accept_btn.is_visible(timeout=2000):
                        await accept_btn.click()
                        await asyncio.sleep(2)
                except:
                    pass

                # Take screenshot
                screenshot = f"data/screenshots/McRent_AGGRESSIVE_{datetime.now().strftime('%H%M%S')}.png"
                await page.screenshot(path=screenshot, full_page=True)
                logger.info(f"Screenshot: {screenshot}")

                # Look for search form and interact
                try:
                    # Try to find any input field
                    inputs = await page.locator('input[type="text"]').all()
                    if len(inputs) > 0:
                        logger.info(f"Found {len(inputs)} input fields")
                        # Fill first field with "Munich"
                        await inputs[0].click()
                        await inputs[0].fill('Munich')
                        await asyncio.sleep(2)

                    # Look for any button
                    buttons = await page.locator('button').all()
                    for i, btn in enumerate(buttons[:5]):
                        try:
                            text = await btn.inner_text()
                            if any(word in text.lower() for word in ['search', 'find', 'show', 'rent', 'book']):
                                logger.info(f"Clicking button: {text}")
                                await btn.click()
                                await asyncio.sleep(8)
                                break
                        except:
                            continue
                except Exception as e:
                    logger.warning(f"Form interaction: {e}")

                # Extract prices from visible page
                content = await page.content()
                prices = extract_prices_from_html(content)
                if prices:
                    captured_data['prices_found'].extend(prices)
                    logger.info(f"Found {len(prices)} prices: {prices}")

                # If we found data, stop
                if captured_data['prices_found'] or len(captured_data['api_calls']) > 5:
                    logger.info("Found data, stopping...")
                    break

                await asyncio.sleep(3)

            except Exception as e:
                logger.error(f"Error with {url}: {e}")
                continue

        await browser.close()

    # Process results
    if captured_data['prices_found']:
        captured_data['success'] = True
        prices = list(set(captured_data['prices_found']))
        captured_data['summary'] = {
            'total_prices': len(prices),
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices)
        }

    # Save all captured data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"data/live_pricing/mcrent_aggressive_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(captured_data, f, indent=2)

    logger.info("\n" + "="*80)
    logger.info("MCRENT AGGRESSIVE SCRAPING COMPLETE")
    logger.info(f"API calls captured: {len(captured_data['api_calls'])}")
    logger.info(f"Prices found: {len(captured_data['prices_found'])}")
    logger.info(f"Success: {captured_data['success']}")
    logger.info(f"Data saved: {output_file}")
    logger.info("="*80)

    return captured_data


def extract_prices_from_json(data, captured_data):
    """Recursively extract prices from JSON data"""
    if isinstance(data, dict):
        for key, value in data.items():
            if any(word in key.lower() for word in ['price', 'cost', 'rate', 'amount', 'total']):
                if isinstance(value, (int, float)):
                    if 10 <= value <= 1000:
                        captured_data['prices_found'].append(float(value))
                        logger.info(f"[PRICE FROM JSON] {key}: €{value}")
            extract_prices_from_json(value, captured_data)
    elif isinstance(data, list):
        for item in data:
            extract_prices_from_json(item, captured_data)


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
                price = float(match.replace(',', '').replace('.', '', match.count('.')-1 if match.count('.') > 1 else 0))
                if 10 <= price <= 1000:
                    prices.append(price)
            except:
                continue

    return list(set(prices))


if __name__ == "__main__":
    asyncio.run(intercept_and_scrape_mcrent())
