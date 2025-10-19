"""
Advanced McRent Testing
Multiple strategies to get McRent working
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# McRent specific URLs to test
MCRENT_URLS = [
    'https://mcrent.com/',
    'https://www.mcrent.com/en/',
    'https://mcrent.de/en/motorhome-rental/',
    'https://www.mcrent.de/de/',
    'https://mcrent.de/en/rental/',
    'https://www.mcrent.de/en/',
    'https://mcrent.de/',
    'https://www.mcrent.com/',
    'https://mcrent.de/en/motorhome-rental/germany/',
    'https://www.mcrent.de/en/motorhome-rental/munich/'
]

async def test_mcrent_advanced():
    """Advanced testing for McRent with multiple strategies"""
    logger.info("🎯 ADVANCED MCRENT TESTING")
    logger.info("="*50)

    results = []

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = await context.new_page()

        for i, url in enumerate(MCRENT_URLS):
            logger.info(f"\n📍 Test {i+1}/{len(MCRENT_URLS)}: {url}")

            try:
                # Navigate to URL
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(5000)

                # Check page content
                page_content = await page.content()
                page_title = await page.title()

                logger.info(f"📄 Page Title: {page_title}")
                logger.info(f"📊 Content Length: {len(page_content)} characters")

                # Check for error indicators
                error_indicators = ['error', '404', 'not found', 'maintenance', 'under construction']
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
                price_found = False
                price_elements = await page.query_selector_all('*')

                for element in price_elements[:100]:  # Check first 100 elements
                    try:
                        text = await element.text_content()
                        if text and '€' in text and any(char.isdigit() for char in text):
                            logger.info(f"💰 Found potential price: {text.strip()}")
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
                Path("data/screenshots").mkdir(parents=True, exist_ok=True)
                screenshot_path = f"data/screenshots/McRent_Test_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=screenshot_path)
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

        await browser.close()

    # Summary
    logger.info("\n" + "="*50)
    logger.info("MCRENT TESTING SUMMARY")
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
    Path("output").mkdir(parents=True, exist_ok=True)
    output_path = f"output/mcrent_advanced_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"\n[SAVED] Results: {output_path}")

    return results

if __name__ == "__main__":
    asyncio.run(test_mcrent_advanced())



