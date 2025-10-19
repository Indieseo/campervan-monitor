"""
Click on the booking search box and interact with the full form to get real prices
"""

import asyncio
import sys
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def click_and_search_apollo():
    """
    Click the search box and fill out the booking form
    """
    
    print("\n" + "="*80)
    print("APOLLO - CLICKING SEARCH BOX AND BOOKING REAL PRICES")
    print("="*80 + "\n")
    
    prices = []
    
    async with async_playwright() as p:
        print("[1/10] Launching browser (you'll see it)...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=200,  # Slower to see what's happening
            args=['--start-maximized', '--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        print("[2/10] Going to booking.apollocamper.com...")
        
        try:
            await page.goto('https://booking.apollocamper.com/', timeout=60000)
            print("       Page loaded!")
            
            await asyncio.sleep(5)
            await page.screenshot(path='data/screenshots/apollo_search_1_initial.png', full_page=True)
            
            print("\n[3/10] Looking for the search box...")
            
            # Find the search input
            search_input = await page.query_selector('input[placeholder*="travel"], input[placeholder*="where"], input[type="search"]')
            
            if search_input:
                print("       [FOUND] Search input box!")
                print("\n[4/10] CLICKING on search box...")
                
                # Click on it
                await search_input.click()
                await asyncio.sleep(3)  # Wait for dropdown/form to appear
                
                print("       [OK] Clicked! Waiting for form to appear...")
                
                await page.screenshot(path='data/screenshots/apollo_search_2_clicked.png', full_page=True)
                
                # Check what appeared
                page_text = await page.evaluate('() => document.body.innerText')
                print(f"\n       Page now has {len(page_text)} characters")
                
                print("\n[5/10] Looking for form elements that appeared...")
                
                # Look for new elements
                all_inputs = await page.query_selector_all('input, select, button')
                print(f"       Found {len(all_inputs)} interactive elements")
                
                # Try typing in the search box
                print("\n[6/10] Typing 'USA' in search box...")
                await search_input.fill('USA')
                await asyncio.sleep(2)
                
                await page.screenshot(path='data/screenshots/apollo_search_3_typed.png', full_page=True)
                
                # Look for dropdown options
                print("\n[7/10] Looking for location options...")
                
                # Try common selectors for dropdowns
                options = await page.query_selector_all('[role="option"], .option, .dropdown-item, [class*="suggestion"], [class*="result"]')
                
                if options:
                    print(f"       [FOUND] {len(options)} dropdown options!")
                    
                    # Click first option
                    if len(options) > 0:
                        print("       [ACTION] Clicking first location option...")
                        await options[0].click()
                        await asyncio.sleep(3)
                        print("       [OK] Location selected!")
                else:
                    # Try pressing Enter
                    print("       [ACTION] Pressing Enter...")
                    await search_input.press('Enter')
                    await asyncio.sleep(3)
                
                await page.screenshot(path='data/screenshots/apollo_search_4_selected.png', full_page=True)
                
                print("\n[8/10] Looking for date/vehicle selection...")
                
                # Look for date pickers or next step
                date_inputs = await page.query_selector_all('input[type="date"], input[name*="date"], input[placeholder*="date"]')
                
                if date_inputs:
                    print(f"       [FOUND] {len(date_inputs)} date inputs!")
                    
                    # Fill dates
                    pickup = (datetime.now() + timedelta(days=30)).strftime('%m/%d/%Y')
                    dropoff = (datetime.now() + timedelta(days=37)).strftime('%m/%d/%Y')
                    
                    if len(date_inputs) >= 1:
                        await date_inputs[0].fill(pickup)
                        print(f"       [OK] Pickup: {pickup}")
                    
                    if len(date_inputs) >= 2:
                        await date_inputs[1].fill(dropoff)
                        print(f"       [OK] Dropoff: {dropoff}")
                    
                    await asyncio.sleep(2)
                
                # Look for Search/Submit button
                print("\n[9/10] Looking for Search button...")
                
                search_buttons = await page.query_selector_all('button:has-text("Search"), button:has-text("SEARCH"), button:has-text("Find"), input[type="submit"]')
                
                if search_buttons:
                    print(f"       [FOUND] {len(search_buttons)} search buttons!")
                    print("       [ACTION] Clicking search button...")
                    
                    await search_buttons[0].click()
                    await asyncio.sleep(10)  # Wait for results
                    
                    print("       [OK] Search submitted!")
                    
                    await page.screenshot(path='data/screenshots/apollo_search_5_results.png', full_page=True)
                else:
                    print("       [INFO] No search button found, form might auto-submit")
                
                # Extract prices from results
                print("\n[10/10] Extracting prices from results...")
                
                results_text = await page.evaluate('() => document.body.innerText')
                current_url = page.url
                
                print(f"       Current URL: {current_url}")
                print(f"       Content length: {len(results_text)} chars")
                
                # Look for prices
                found_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', results_text)
                
                if found_prices:
                    print(f"\n       [SUCCESS] Found {len(found_prices)} price mentions!")
                    print("\n       PRICES:")
                    
                    for p in found_prices:
                        try:
                            val = float(p.replace(',', ''))
                            if 20 <= val <= 2000:  # Wider range for weekly/daily
                                prices.append(val)
                                print(f"         ${val:.2f}")
                        except:
                            pass
                else:
                    print("\n       [NO PRICES] Checking what's on the page...")
                    print(f"\n       Sample text:\n       {results_text[:800]}")
                
            else:
                print("       [ERROR] Could not find search input!")
            
            # Final results
            print("\n" + "="*80)
            print("RESULTS")
            print("="*80)
            
            if prices:
                unique = sorted(set(prices))
                print(f"\n>>> REAL APOLLO PRICES FOUND: {len(unique)} unique values\n")
                
                for price in unique:
                    print(f"    ${price:.2f}")
                
                # Separate daily vs weekly
                daily = [p for p in prices if p < 500]
                weekly = [p for p in prices if p >= 500]
                
                if daily:
                    print(f"\n>>> DAILY RATES:")
                    print(f"    Range: ${min(daily):.2f} - ${max(daily):.2f}")
                    print(f"    Average: ${sum(daily)/len(daily):.2f}/day")
                
                if weekly:
                    print(f"\n>>> WEEKLY RATES:")
                    print(f"    Range: ${min(weekly):.2f} - ${max(weekly):.2f}")
            else:
                print("\n>>> NO PRICES EXTRACTED")
                print("    Check screenshots to see what happened:")
                print("    - apollo_search_1_initial.png")
                print("    - apollo_search_2_clicked.png")
                print("    - apollo_search_3_typed.png")
                print("    - apollo_search_4_selected.png")
                print("    - apollo_search_5_results.png")
            
            print("\n" + "="*80)
            print("BROWSER STAYING OPEN FOR 90 SECONDS")
            print("You can manually continue searching")
            print("="*80 + "\n")
            
            for i in range(90, 0, -1):
                print(f"Closing in {i:02d}s...", end='\r')
                await asyncio.sleep(1)
            
            print("\n\nClosing...")
            await browser.close()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(click_and_search_apollo())





