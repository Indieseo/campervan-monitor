"""
Fill out Apollo booking form to trigger pricing API calls
"""

import asyncio
import sys
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def fill_apollo_booking_form():
    """
    Fill out the booking form to trigger pricing API
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - FILL BOOKING FORM FOR REAL PRICES")
    print("="*80 + "\n")
    
    # Setup search dates
    pickup_date = (datetime.now() + timedelta(days=30)).strftime('%m/%d/%Y')
    dropoff_date = (datetime.now() + timedelta(days=37)).strftime('%m/%d/%Y')
    
    print(f"Search Parameters:")
    print(f"  Pickup:  {pickup_date}")
    print(f"  Dropoff: {dropoff_date}")
    print(f"  Duration: 7 days\n")
    
    # Track API calls with pricing
    pricing_apis = []
    vehicle_data = []
    
    async with async_playwright() as p:
        print("[1/6] Launching browser...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=100,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--window-size=1920,1080',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='en-US',
        )
        
        page = await context.new_page()
        
        # Capture responses
        async def handle_response(response):
            url = response.url
            if 'booking.apollocamper.com/api' in url:
                try:
                    if response.status == 200:
                        body = await response.text()
                        print(f"      [API] {url.split('/')[-1].split('?')[0]}: {len(body)} chars")
                        
                        # Check if this contains pricing data
                        body_lower = body.lower()
                        if any(keyword in body_lower for keyword in ['price', 'rate', 'cost', 'total', 'daily']):
                            pricing_apis.append({
                                'url': url,
                                'body': body,
                                'timestamp': datetime.now().isoformat()
                            })
                            print(f"            [PRICE DATA FOUND!]")
                            
                        # Check if this contains vehicle data
                        if any(keyword in body_lower for keyword in ['vehicle', 'motorhome', 'camper', 'class']):
                            try:
                                data = json.loads(body)
                                if isinstance(data, list) and data:
                                    vehicle_data.append({
                                        'url': url,
                                        'data': data,
                                        'count': len(data)
                                    })
                                    print(f"            [VEHICLE DATA: {len(data)} items]")
                            except:
                                pass
                except Exception as e:
                    pass
        
        page.on('response', handle_response)
        
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        print("[2/6] Loading Apollo homepage...")
        
        try:
            await page.goto('https://www.apollocamper.com/', timeout=60000)
            print("      Page loaded")
            
            # Wait for page to fully load
            await asyncio.sleep(5)
            
            print("\n[3/6] Looking for booking form...")
            
            # Take screenshot to see current state
            await page.screenshot(path='data/screenshots/apollo_before_form.png', full_page=True)
            
            # Get page content to analyze
            page_text = await page.evaluate('() => document.body.innerText')
            
            # Look for form elements
            all_inputs = await page.query_selector_all('input')
            print(f"      Found {len(all_inputs)} input elements")
            
            # Check for specific booking widget elements
            pickup_inputs = await page.query_selector_all('input[name*="pickup"], input[id*="pickup"], input[placeholder*="pick"]')
            date_inputs = await page.query_selector_all('input[type="date"], input[name*="date"]')
            location_selects = await page.query_selector_all('select[name*="location"], select[id*="location"]')
            
            print(f"      Pickup inputs: {len(pickup_inputs)}")
            print(f"      Date inputs: {len(date_inputs)}")
            print(f"      Location selects: {len(location_selects)}")
            
            # Try to find and interact with booking widget
            print("\n[4/6] Attempting to interact with booking widget...")
            
            # Method 1: Look for visible search/book buttons
            search_buttons = await page.query_selector_all('button, input[type="submit"], a.button, .search-button')
            print(f"      Found {len(search_buttons)} potential buttons")
            
            for i, button in enumerate(search_buttons[:20]):
                try:
                    text = await button.inner_text()
                    is_visible = await button.is_visible()
                    if text and any(keyword in text.lower() for keyword in ['search', 'book', 'find', 'check', 'availability']):
                        print(f"      Button {i}: '{text}' (visible: {is_visible})")
                        
                        if is_visible and 'search' in text.lower():
                            print(f"         Attempting to click '{text}'...")
                            try:
                                await button.click(timeout=5000)
                                await asyncio.sleep(3)
                                print("         [OK] Clicked!")
                                break
                            except Exception as e:
                                print(f"         [ERROR] {str(e)[:50]}")
                except:
                    continue
            
            # Wait a bit to see if form appeared
            await asyncio.sleep(2)
            
            # Try to find date/location inputs again after potential form reveal
            print("\n      Looking for form fields after interaction...")
            
            # Check if there's a booking iframe
            iframes = await page.query_selector_all('iframe')
            booking_iframe = None
            for iframe in iframes:
                src = await iframe.get_attribute('src')
                if src and 'booking' in src:
                    print(f"      [OK] Found booking iframe: {src}")
                    booking_iframe = iframe
                    break
            
            if booking_iframe:
                print("      Switching to booking iframe...")
                frame = await booking_iframe.content_frame()
                if frame:
                    # Look for form elements in iframe
                    iframe_inputs = await frame.query_selector_all('input')
                    print(f"      Found {len(iframe_inputs)} inputs in iframe")
                    
                    # Try to fill form in iframe
                    try:
                        # Fill pickup date
                        pickup_input = await frame.query_selector('input[name*="pickup"], input[id*="pickup"]')
                        if pickup_input:
                            await pickup_input.fill(pickup_date)
                            print(f"      [OK] Filled pickup date: {pickup_date}")
                        
                        # Fill dropoff date
                        dropoff_input = await frame.query_selector('input[name*="dropoff"], input[name*="return"]')
                        if dropoff_input:
                            await dropoff_input.fill(dropoff_date)
                            print(f"      [OK] Filled dropoff date: {dropoff_date}")
                        
                        # Click search
                        search_btn = await frame.query_selector('button:has-text("Search"), input[type="submit"]')
                        if search_btn:
                            await search_btn.click()
                            print("      [OK] Clicked search button")
                            await asyncio.sleep(5)  # Wait for results
                    except Exception as e:
                        print(f"      [ERROR] Form fill failed: {e}")
            
            print("\n[5/6] Analyzing captured data...")
            
            await asyncio.sleep(3)  # Wait for any pending API calls
            
            if pricing_apis:
                print(f"\n      [SUCCESS] Captured {len(pricing_apis)} API calls with pricing data!\n")
                
                for i, api_call in enumerate(pricing_apis):
                    print(f"      API Call {i+1}:")
                    print(f"         URL: {api_call['url']}")
                    
                    try:
                        data = json.loads(api_call['body'])
                        
                        # Try to extract prices
                        def find_prices(obj, prices=None):
                            if prices is None:
                                prices = []
                            
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    if any(k in key.lower() for k in ['price', 'rate', 'cost', 'total', 'daily']):
                                        if isinstance(value, (int, float)):
                                            prices.append((key, value))
                                    find_prices(value, prices)
                            elif isinstance(obj, list):
                                for item in obj:
                                    find_prices(item, prices)
                            
                            return prices
                        
                        prices = find_prices(data)
                        
                        if prices:
                            print(f"         [PRICES FOUND]")
                            for key, value in prices[:10]:
                                print(f"            {key}: ${value}")
                        else:
                            # Show sample of data
                            print(f"         Data sample: {str(data)[:300]}...")
                    
                    except:
                        print(f"         Body: {api_call['body'][:300]}...")
            
            if vehicle_data:
                print(f"\n      [SUCCESS] Captured {len(vehicle_data)} API calls with vehicle data!\n")
                
                for i, veh_call in enumerate(vehicle_data):
                    print(f"      Vehicle API Call {i+1}:")
                    print(f"         URL: {veh_call['url']}")
                    print(f"         Vehicles: {veh_call['count']}")
                    
                    # Show sample
                    if veh_call['data']:
                        print(f"         Sample: {json.dumps(veh_call['data'][0], indent=12)[:400]}...")
            
            if not pricing_apis and not vehicle_data:
                print("\n      [NO PRICING DATA YET]")
                print("      The booking form might need more specific interaction")
                print("      or pricing data might load via different mechanism")
            
            # Take final screenshot
            await page.screenshot(path='data/screenshots/apollo_after_form.png', full_page=True)
            print("\n      Screenshot: apollo_after_form.png")
            
            print("\n[6/6] Summary")
            print("="*80)
            print(f"      API calls captured: {len(pricing_apis) + len(vehicle_data)}")
            print(f"      Pricing APIs: {len(pricing_apis)}")
            print(f"      Vehicle APIs: {len(vehicle_data)}")
            print("="*80 + "\n")
            
            print("Keeping browser open for 15 seconds...")
            await asyncio.sleep(15)
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(fill_apollo_booking_form())





