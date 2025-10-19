"""
Click the actual visible button dropdowns to fill Apollo booking form
"""

import asyncio
import sys
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def click_button_dropdowns():
    """
    Click the button dropdowns that make up the booking widget
    """
    
    print("\n" + "="*80)
    print("APOLLO - CLICKING BUTTON DROPDOWNS")
    print("="*80 + "\n")
    
    prices = []
    
    async with async_playwright() as p:
        print("[1/8] Launching...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=300,  # Slower to see actions
            args=['--start-maximized']
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        # Monitor API responses
        async def handle_response(response):
            if 'api' in response.url and response.status == 200:
                try:
                    body = await response.text()
                    price_matches = re.findall(r'"(?:price|rate|cost|daily|total)":\s*(\d+(?:\.\d{2})?)', body)
                    if price_matches:
                        print(f"\n>>> [PRICE API] {response.url[:60]}")
                        print(f"    Prices: {price_matches[:10]}")
                        for p in price_matches:
                            prices.append(float(p))
                except:
                    pass
        
        page.on('response', handle_response)
        
        print("[2/8] Loading apollocamper.com...")
        
        try:
            await page.goto('https://www.apollocamper.com/', timeout=90000)
            await asyncio.sleep(8)  # Wait for widgets to load
            
            print("\n[3/8] Clicking 'Pick up from' button...")
            
            # Find and click pickup button
            pickup_btn = await page.query_selector('button:has-text("Pick up from")')
            if pickup_btn:
                await pickup_btn.click()
                print("    Clicked! Waiting for dropdown...")
                await asyncio.sleep(3)
                
                await page.screenshot(path='data/screenshots/apollo_btn_1_pickup_opened.png', full_page=True)
                
                # Look for location options
                options = await page.query_selector_all('[role="option"], li[data-value], .location-option, .dropdown-item')
                print(f"    Found {len(options)} options")
                
                # Click first USA option
                for opt in options:
                    try:
                        text = await opt.inner_text()
                        if any(keyword in text.lower() for keyword in ['los angeles', 'usa', 'california', 'united states', 'lax']):
                            print(f"    Selecting: {text[:50]}")
                            await opt.click()
                            await asyncio.sleep(2)
                            break
                    except:
                        continue
                
                if not options:
                    # Try typing
                    print("    No dropdown options, trying to type...")
                    await page.keyboard.type('Los Angeles')
                    await asyncio.sleep(2)
                    await page.keyboard.press('Enter')
                    await asyncio.sleep(2)
            
            print("\n[4/8] Clicking 'Travel Dates' button...")
            
            dates_btn = await page.query_selector('button:has-text("Travel Dates")')
            if dates_btn:
                await dates_btn.click()
                print("    Clicked! Waiting for date picker...")
                await asyncio.sleep(3)
                
                await page.screenshot(path='data/screenshots/apollo_btn_2_dates_opened.png', full_page=True)
                
                # Look for date inputs or calendar
                date_inputs = await page.query_selector_all('input[type="date"], input[placeholder*="date"]')
                if date_inputs:
                    print(f"    Found {len(date_inputs)} date inputs")
                    
                    pickup_date = (datetime.now() + timedelta(days=30)).strftime('%m/%d/%Y')
                    dropoff_date = (datetime.now() + timedelta(days=37)).strftime('%m/%d/%Y')
                    
                    if len(date_inputs) >= 1:
                        await date_inputs[0].fill(pickup_date)
                        print(f"    Pickup: {pickup_date}")
                    if len(date_inputs) >= 2:
                        await date_inputs[1].fill(dropoff_date)
                        print(f"    Dropoff: {dropoff_date}")
                    
                    await asyncio.sleep(2)
                else:
                    # Try clicking calendar dates
                    print("    Looking for calendar...")
                    calendar = await page.query_selector('.calendar, [class*="datepicker"]')
                    if calendar:
                        print("    Found calendar - clicking dates...")
                        # Click some future dates
                        dates = await calendar.query_selector_all('[role="gridcell"], .day')
                        if len(dates) > 30:
                            await dates[30].click()  # ~30 days from now
                            await asyncio.sleep(1)
                            await dates[37].click()  # 7 days later
                            await asyncio.sleep(2)
            
            print("\n[5/8] Clicking 'Passengers' button...")
            
            passengers_btn = await page.query_selector('button:has-text("Passengers")')
            if passengers_btn:
                await passengers_btn.click()
                await asyncio.sleep(2)
                
                # Select 2 passengers
                options = await page.query_selector_all('[role="option"], li')
                for opt in options:
                    try:
                        text = await opt.inner_text()
                        if '2' in text:
                            await opt.click()
                            print("    Selected: 2 passengers")
                            await asyncio.sleep(1)
                            break
                    except:
                        continue
            
            print("\n[6/8] Clicking 'Search' button...")
            
            search_btn = await page.query_selector('button:has-text("Search")')
            if search_btn:
                print("    Found search button!")
                
                # Try clicking with force
                try:
                    await search_btn.click(force=True)
                    print("    Clicked search!")
                    
                    print("    Waiting 15 seconds for results...")
                    await asyncio.sleep(15)
                    
                    await page.screenshot(path='data/screenshots/apollo_btn_3_results.png', full_page=True)
                    
                except Exception as e:
                    print(f"    Click error: {e}")
                    # Try JS click
                    print("    Trying JavaScript click...")
                    await page.evaluate('document.querySelector(\'button:has-text("Search")\').click()')
                    await asyncio.sleep(15)
            
            print("\n[7/8] Extracting results...")
            
            final_url = page.url
            final_text = await page.inner_text('body')
            
            print(f"\n    Final URL: {final_url}")
            print(f"    Text length: {len(final_text)} chars")
            
            # Extract prices
            found_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', final_text)
            
            if found_prices:
                print(f"\n    [PRICES] Found {len(found_prices)} mentions:")
                for p in found_prices[:30]:
                    try:
                        val = float(p.replace(',', ''))
                        if 20 <= val <= 2000:
                            prices.append(val)
                            print(f"       ${val}")
                    except:
                        pass
            
            print("\n[8/8] RESULTS")
            print("="*80)
            
            if prices:
                unique = sorted(set(prices))
                print(f"\n>>> SUCCESS! {len(unique)} REAL APOLLO PRICES!\n")
                
                for price in unique:
                    print(f"    ${price:.2f}")
                
                print(f"\n>>> STATISTICS:")
                print(f"    Lowest:  ${min(prices):.2f}")
                print(f"    Highest: ${max(prices):.2f}")
                print(f"    Average: ${sum(prices)/len(prices):.2f}")
                print(f"\n>>> SOURCE: apollocamper.com automated search")
            else:
                print("\n>>> NO PRICES FOUND")
                print("    Check screenshots:")
                print("      - apollo_btn_1_pickup_opened.png")
                print("      - apollo_btn_2_dates_opened.png")  
                print("      - apollo_btn_3_results.png")
            
            print("\n" + "="*80)
            print("BROWSER OPEN 90 SECONDS - CHECK MANUALLY")
            print("="*80 + "\n")
            
            for i in range(90, 0, -1):
                print(f"{i:02d}s...", end='\r')
                await asyncio.sleep(1)
            
            await browser.close()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(click_button_dropdowns())





