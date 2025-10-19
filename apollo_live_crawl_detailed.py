"""
Live crawl of apollocamper.com with detailed real-time progress
"""

import asyncio
import sys
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def live_crawl_apollo():
    """
    Live crawl with real-time updates
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - LIVE CRAWL WITH REAL-TIME RESULTS")
    print("="*80 + "\n")
    
    all_prices = []
    
    async with async_playwright() as p:
        print(">>> Launching browser (non-headless so you can see)...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=100,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        # Anti-detection
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        print(">>> Navigating to apollocamper.com...")
        print("    URL: https://www.apollocamper.com/\n")
        
        try:
            await page.goto('https://www.apollocamper.com/', timeout=60000)
            
            print(">>> Waiting for Cloudflare clearance...")
            
            # Wait for Cloudflare with progress
            for i in range(30):
                await asyncio.sleep(1)
                
                text = await page.evaluate('() => document.body.innerText')
                content = await page.content()
                
                is_cf = 'cloudflare' in text.lower() or 'verifying' in text.lower()
                
                if not is_cf and len(content) > 50000:
                    print(f"    [OK] Cloudflare cleared after {i+1} seconds!")
                    break
                
                if i % 3 == 0:
                    print(f"    [{i+1}s] Still waiting for clearance...", end='\r')
            
            print("\n\n>>> Extracting homepage content...")
            
            text = await page.evaluate('() => document.body.innerText')
            
            # Look for prices
            prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
            if prices:
                print(f"    Found {len(prices)} price mentions on homepage")
                for p in prices[:10]:
                    try:
                        val = float(p.replace(',', ''))
                        if 30 <= val <= 1000:
                            all_prices.append(val)
                            print(f"       ${val}")
                    except:
                        pass
            else:
                print("    No prices found on homepage")
            
            # Take screenshot
            await page.screenshot(path='data/screenshots/apollo_crawl_homepage.png', full_page=True)
            print("    Screenshot: apollo_crawl_homepage.png")
            
            # Try USA page
            print("\n>>> Navigating to USA RV rental page...")
            print("    URL: https://www.apollocamper.com/usa/rv-rental\n")
            
            try:
                response = await page.goto('https://www.apollocamper.com/usa/rv-rental', timeout=30000)
                print(f"    Response: {response.status}")
                
                await asyncio.sleep(3)
                
                text = await page.evaluate('() => document.body.innerText')
                
                # Check if blocked
                if 'cloudflare' in text.lower() or response.status == 403:
                    print("    [BLOCKED] Cloudflare blocking this page")
                else:
                    print("    [OK] Page loaded successfully!")
                    
                    # Extract prices
                    usa_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
                    if usa_prices:
                        print(f"    Found {len(usa_prices)} price mentions:")
                        for p in usa_prices[:15]:
                            try:
                                val = float(p.replace(',', ''))
                                if 30 <= val <= 1000:
                                    all_prices.append(val)
                                    print(f"       ${val}")
                            except:
                                pass
                    
                    await page.screenshot(path='data/screenshots/apollo_crawl_usa.png', full_page=True)
                    print("    Screenshot: apollo_crawl_usa.png")
            
            except Exception as e:
                print(f"    [ERROR] {str(e)[:60]}")
            
            # Try vehicles page
            print("\n>>> Navigating to vehicles page...")
            print("    URL: https://www.apollocamper.com/vehicles\n")
            
            try:
                response = await page.goto('https://www.apollocamper.com/vehicles', timeout=30000)
                await asyncio.sleep(3)
                
                text = await page.evaluate('() => document.body.innerText')
                
                if 'cloudflare' not in text.lower() and response.status == 200:
                    print("    [OK] Vehicles page loaded!")
                    
                    vehicle_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
                    if vehicle_prices:
                        print(f"    Found {len(vehicle_prices)} prices:")
                        for p in vehicle_prices[:15]:
                            try:
                                val = float(p.replace(',', ''))
                                if 30 <= val <= 1000:
                                    all_prices.append(val)
                                    print(f"       ${val}")
                            except:
                                pass
                    
                    await page.screenshot(path='data/screenshots/apollo_crawl_vehicles.png', full_page=True)
                else:
                    print(f"    [BLOCKED] Status {response.status}")
            
            except Exception as e:
                print(f"    [ERROR] {str(e)[:60]}")
            
            # Summary
            print("\n" + "="*80)
            print("CRAWL RESULTS SUMMARY")
            print("="*80)
            
            if all_prices:
                unique_prices = sorted(set(all_prices))
                print(f"\n>>> REAL PRICES FOUND: {len(unique_prices)} unique values\n")
                
                for price in unique_prices:
                    print(f"    ${price:.2f}")
                
                print(f"\n>>> PRICE STATISTICS:")
                print(f"    Lowest:  ${min(all_prices):.2f}")
                print(f"    Highest: ${max(all_prices):.2f}")
                print(f"    Average: ${sum(all_prices)/len(all_prices):.2f}")
            else:
                print("\n>>> NO PRICES EXTRACTED")
                print("    Apollo uses heavy Cloudflare protection")
                print("    Prices may require JavaScript rendering or form interaction")
            
            print("\n" + "="*80)
            print("BROWSER STAYING OPEN FOR 45 SECONDS")
            print("Feel free to manually navigate and explore")
            print("="*80 + "\n")
            
            # Keep open longer
            for i in range(45, 0, -1):
                print(f"Closing in {i} seconds...", end='\r')
                await asyncio.sleep(1)
            
            print("\n\nClosing browser...")
            await browser.close()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(live_crawl_apollo())





