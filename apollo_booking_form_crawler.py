"""
Crawl booking.apollocamper.com and fill out search form for real prices
"""

import asyncio
import sys
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def crawl_apollo_booking():
    """
    Crawl the booking subdomain and interact with search form
    """
    
    print("\n" + "="*80)
    print("APOLLO BOOKING ENGINE - REAL PRICE EXTRACTION")
    print("="*80 + "\n")
    
    prices_found = []
    
    # Search dates (30 days from now, 7-day rental)
    pickup_date = datetime.now() + timedelta(days=30)
    dropoff_date = pickup_date + timedelta(days=7)
    
    print(f"Search Parameters:")
    print(f"  Pickup:  {pickup_date.strftime('%Y-%m-%d')}")
    print(f"  Dropoff: {dropoff_date.strftime('%Y-%m-%d')}")
    print(f"  Duration: 7 days\n")
    
    async with async_playwright() as p:
        print("[1/8] Launching browser...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=100,
            args=['--start-maximized', '--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        print("[2/8] Navigating to booking subdomain...")
        print("       URL: https://booking.apollocamper.com/\n")
        
        try:
            await page.goto('https://booking.apollocamper.com/', timeout=60000)
            await asyncio.sleep(5)  # Wait for full page load
            
            await page.screenshot(path='data/screenshots/apollo_booking_1.png', full_page=True)
            
            print("[3/8] Analyzing page structure...")
            
            # Get all text
            text = await page.evaluate('() => document.body.innerText')
            print(f"       Page loaded: {len(text)} characters")
            
            # Look for form elements
            print("\n[4/8] Looking for search form elements...")
            
            # Find all inputs
            inputs = await page.query_selector_all('input, select')
            print(f"       Found {len(inputs)} input/select elements")
            
            # Look for date pickers, location selects, etc
            for i, input_elem in enumerate(inputs[:30]):
                try:
                    input_type = await input_elem.get_attribute('type')
                    input_name = await input_elem.get_attribute('name')
                    input_id = await input_elem.get_attribute('id')
                    input_placeholder = await input_elem.get_attribute('placeholder')
                    
                    if any([input_name, input_id, input_placeholder]):
                        print(f"       Input {i}: type={input_type}, name={input_name}, id={input_id}, placeholder={input_placeholder}")
                except:
                    continue
            
            # Look for buttons
            buttons = await page.query_selector_all('button')
            print(f"\n       Found {len(buttons)} buttons:")
            for i, btn in enumerate(buttons[:15]):
                try:
                    text = await btn.inner_text()
                    if text and len(text.strip()) > 0:
                        print(f"       Button {i}: '{text.strip()}'")
                except:
                    continue
            
            print("\n[5/8] Attempting to interact with booking form...")
            
            # Try to find and fill location
            try:
                # Look for location/pickup field
                location_input = await page.query_selector('input[name*="location"], input[id*="location"], input[placeholder*="location"], select[name*="location"]')
                if location_input:
                    print("       [FOUND] Location input")
                    await location_input.click()
                    await asyncio.sleep(1)
                    await location_input.fill('Los Angeles')
                    await asyncio.sleep(2)
                    print("       [OK] Filled location: Los Angeles")
            except Exception as e:
                print(f"       [ERROR] Location: {str(e)[:50]}")
            
            # Try to find date pickers
            try:
                date_inputs = await page.query_selector_all('input[type="date"], input[name*="date"], input[placeholder*="date"]')
                if date_inputs and len(date_inputs) >= 2:
                    print(f"       [FOUND] {len(date_inputs)} date inputs")
                    
                    # Fill pickup date
                    await date_inputs[0].fill(pickup_date.strftime('%m/%d/%Y'))
                    print(f"       [OK] Pickup: {pickup_date.strftime('%m/%d/%Y')}")
                    
                    # Fill dropoff date
                    await date_inputs[1].fill(dropoff_date.strftime('%m/%d/%Y'))
                    print(f"       [OK] Dropoff: {dropoff_date.strftime('%m/%d/%Y')}")
                    
                    await asyncio.sleep(2)
            except Exception as e:
                print(f"       [ERROR] Dates: {str(e)[:50]}")
            
            # Look for Search button
            try:
                search_btn = await page.query_selector('button:has-text("Search"), button:has-text("SEARCH"), input[type="submit"]')
                if search_btn:
                    print("       [FOUND] Search button")
                    print("       [ACTION] Clicking search...")
                    await search_btn.click()
                    await asyncio.sleep(10)  # Wait for results
                    print("       [OK] Search submitted!")
            except Exception as e:
                print(f"       [ERROR] Search: {str(e)[:50]}")
            
            print("\n[6/8] Checking for results/prices...")
            
            # Get updated page content
            await asyncio.sleep(5)
            results_text = await page.evaluate('() => document.body.innerText')
            results_url = page.url
            
            print(f"       Current URL: {results_url}")
            
            await page.screenshot(path='data/screenshots/apollo_booking_results.png', full_page=True)
            
            # Extract prices
            found_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', results_text)
            if found_prices:
                print(f"\n       [PRICES FOUND] {len(found_prices)} price mentions:")
                for p in found_prices:
                    try:
                        val = float(p.replace(',', ''))
                        if 30 <= val <= 1000:
                            prices_found.append(val)
                            print(f"          ${val:.2f}")
                    except:
                        pass
            
            # Look for vehicle cards/results
            print("\n[7/8] Looking for vehicle listings...")
            
            vehicle_cards = await page.query_selector_all('[class*="vehicle"], [class*="result"], [class*="card"], [class*="product"]')
            print(f"       Found {len(vehicle_cards)} potential vehicle elements")
            
            # Check each card for prices
            for i, card in enumerate(vehicle_cards[:10]):
                try:
                    card_text = await card.inner_text()
                    card_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', card_text)
                    if card_prices:
                        print(f"       Card {i}: {card_prices}")
                        for p in card_prices:
                            try:
                                val = float(p.replace(',', ''))
                                if 30 <= val <= 1000:
                                    prices_found.append(val)
                            except:
                                pass
                except:
                    continue
            
            print("\n[8/8] FINAL RESULTS")
            print("="*80)
            
            if prices_found:
                unique_prices = sorted(set(prices_found))
                print(f"\n>>> SUCCESS! FOUND {len(unique_prices)} REAL APOLLO PRICES!\n")
                
                for price in unique_prices:
                    print(f"    ${price:.2f}/day")
                
                print(f"\n>>> STATISTICS:")
                print(f"    Lowest:  ${min(prices_found):.2f}")
                print(f"    Highest: ${max(prices_found):.2f}")
                print(f"    Average: ${sum(prices_found)/len(prices_found):.2f}")
                print(f"\n    Source: booking.apollocamper.com")
                print(f"    Method: Interactive form submission")
            else:
                print("\n>>> NO PRICES YET")
                print("    The booking form might need specific:")
                print("    - Valid location codes")
                print("    - Specific date formats")
                print("    - Additional required fields")
                print("\n    Current page text sample:")
                print(f"    {results_text[:500]}")
            
            print("\n" + "="*80)
            print("BROWSER OPEN FOR 60 SECONDS - EXPLORE MANUALLY")
            print("="*80 + "\n")
            
            for i in range(60, 0, -1):
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
    asyncio.run(crawl_apollo_booking())





