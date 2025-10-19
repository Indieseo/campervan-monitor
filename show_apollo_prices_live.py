"""
Open Apollo prices in browser and show live data
"""

import asyncio
import sys
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def show_apollo_prices():
    """
    Open browser and show Apollo prices live
    """
    
    print("\n" + "="*80)
    print("OPENING APOLLO MOTORHOMES PRICING - LIVE VIEW")
    print("="*80 + "\n")
    
    async with async_playwright() as p:
        # Launch visible browser
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        print("[1] Opening Motorhome Republic - Apollo page...")
        print("    URL: https://www.motorhomerepublic.com/apollo\n")
        
        await page.goto('https://www.motorhomerepublic.com/apollo', timeout=30000)
        await asyncio.sleep(3)
        
        print("[2] Page loaded! Taking screenshot...\n")
        
        # Take full page screenshot
        await page.screenshot(path='data/screenshots/apollo_live_prices.png', full_page=True)
        
        # Get visible text
        text = await page.evaluate('() => document.body.innerText')
        
        # Find Apollo mentions and prices
        print("="*80)
        print("APOLLO MOTORHOMES - LIVE PRICING DATA")
        print("="*80 + "\n")
        
        # Extract key info
        import re
        prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
        
        if prices:
            print(f"PRICES FOUND: {prices}\n")
        
        # Show relevant text snippets
        lines = text.split('\n')
        for line in lines:
            if 'apollo' in line.lower() and len(line.strip()) > 0:
                print(f"  {line.strip()}")
        
        print("\n" + "="*80)
        print("BROWSER WILL STAY OPEN FOR 60 SECONDS")
        print("Screenshot saved: data/screenshots/apollo_live_prices.png")
        print("="*80 + "\n")
        
        # Keep browser open so user can see
        print("Look at the browser window to see live Apollo pricing!")
        print("Countdown: ", end='')
        for i in range(60, 0, -1):
            print(f"{i}...", end='', flush=True)
            await asyncio.sleep(1)
        
        print("\n\nClosing browser...")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(show_apollo_prices())





