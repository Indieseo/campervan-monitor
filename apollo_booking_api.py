"""
Query Apollo Motorhomes booking API directly for real prices
"""

import asyncio
import sys
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import requests

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def query_apollo_api_direct():
    """
    Query Apollo booking API directly using requests
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - DIRECT BOOKING API QUERY")
    print("="*80 + "\n")
    
    base_api = "https://booking.apollocamper.com/api"
    
    # Setup search dates
    pickup_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    dropoff_date = (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d')
    
    print(f"Search Parameters:")
    print(f"  Pickup:  {pickup_date}")
    print(f"  Dropoff: {dropoff_date}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.apollocamper.com/',
    }
    
    print("[1/5] Querying countries...")
    try:
        response = requests.get(f"{base_api}/countries", headers=headers, params={'country': 'AU'}, timeout=10)
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"      Response: {json.dumps(data, indent=2)[:200]}...")
    except Exception as e:
        print(f"      Error: {e}")
    
    print("\n[2/5] Querying locations...")
    try:
        params = {
            'brandsObj': 'B,Y,M,A,C,H',
            'addressFormat': 'line1,line2,city,stateCode,postCode',
            'country': 'AU',
            'groupField': 'addressState',
            'allowSameDayPickUp': 'true'
        }
        response = requests.get(f"{base_api}/locations", headers=headers, params=params, timeout=10)
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"      Found {len(data) if isinstance(data, list) else 'N/A'} locations")
            if isinstance(data, list) and data:
                print(f"      Sample: {json.dumps(data[0], indent=2)[:300]}...")
    except Exception as e:
        print(f"      Error: {e}")
    
    print("\n[3/5] Trying to query vehicles/search endpoints...")
    
    # Try common booking API endpoints
    test_endpoints = [
        '/vehicles',
        '/search',
        '/availability',
        '/rates',
        '/pricing',
        '/fleet',
        '/motorhomes',
    ]
    
    for endpoint in test_endpoints:
        try:
            print(f"      Trying: {base_api}{endpoint}")
            response = requests.get(f"{base_api}{endpoint}", headers=headers, timeout=5)
            print(f"         Status: {response.status_code}", end="")
            if response.status_code == 200:
                print(" [SUCCESS]")
                try:
                    data = response.json()
                    print(f"         Response: {json.dumps(data, indent=2)[:500]}...")
                except:
                    print(f"         Response (text): {response.text[:200]}...")
            else:
                print()
        except Exception as e:
            print(f"         Error: {str(e)[:50]}")
    
    print("\n[4/5] Trying search with parameters...")
    
    # Try search with actual dates and location
    search_params = [
        {
            'pickupDate': pickup_date,
            'dropoffDate': dropoff_date,
            'pickupLocation': 'LAX',  # Los Angeles
            'dropoffLocation': 'LAX',
        },
        {
            'startDate': pickup_date,
            'endDate': dropoff_date,
            'location': 'US',
        },
        {
            'from': pickup_date,
            'to': dropoff_date,
            'country': 'US',
        },
    ]
    
    for params in search_params:
        try:
            print(f"      Params: {params}")
            response = requests.get(f"{base_api}/search", headers=headers, params=params, timeout=10)
            print(f"      Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      [SUCCESS] Got data: {json.dumps(data, indent=2)[:500]}...")
                    break
                except:
                    print(f"      Response: {response.text[:200]}...")
        except Exception as e:
            print(f"      Error: {str(e)[:50]}")
    
    print("\n[5/5] Complete - No direct API access found")
    print("      The booking API likely requires authentication or session tokens")
    print("      from the main website. Need to use browser automation instead.")
    print("\n" + "="*80 + "\n")


async def query_apollo_api_browser():
    """
    Query Apollo booking API through browser with proper context
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - BOOKING API VIA BROWSER")
    print("="*80 + "\n")
    
    # Setup search dates
    pickup_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    dropoff_date = (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d')
    
    print(f"Search Parameters:")
    print(f"  Pickup:  {pickup_date}")
    print(f"  Dropoff: {dropoff_date}\n")
    
    async with async_playwright() as p:
        print("[1/4] Launching browser...")
        
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        # Track API responses
        api_responses = []
        
        async def handle_response(response):
            url = response.url
            if 'booking.apollocamper.com/api' in url:
                try:
                    if response.status == 200:
                        body = await response.text()
                        api_responses.append({
                            'url': url,
                            'status': response.status,
                            'body': body
                        })
                        print(f"      [API] {response.status} {url}")
                        if len(body) < 1000:
                            print(f"            {body}")
                        else:
                            print(f"            {body[:200]}... ({len(body)} chars)")
                except Exception as e:
                    print(f"      [API ERROR] {url}: {e}")
        
        page.on('response', handle_response)
        
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        print("[2/4] Loading Apollo homepage to initialize session...")
        
        try:
            await page.goto('https://www.apollocamper.com/', timeout=60000)
            await asyncio.sleep(5)  # Wait for booking widget to load
            
            print("\n[3/4] Looking for booking form...")
            
            # Look for booking form elements
            form_found = False
            
            # Try to find pickup date input
            date_inputs = await page.query_selector_all('input[type="date"], input[name*="date"], input[id*="date"], input[placeholder*="date"]')
            print(f"      Found {len(date_inputs)} date inputs")
            
            # Try to find the booking widget
            booking_widget = await page.query_selector('[class*="booking"], [id*="booking"], [class*="search"], [id*="search"]')
            if booking_widget:
                print("      [OK] Found booking widget")
                
                # Try to interact with it
                try:
                    # Look for "Search" or "Book Now" buttons
                    buttons = await booking_widget.query_selector_all('button')
                    print(f"      Found {len(buttons)} buttons in widget")
                    
                    for button in buttons:
                        text = await button.inner_text()
                        if any(keyword in text.lower() for keyword in ['search', 'book', 'find', 'check']):
                            print(f"      Found button: {text}")
                except Exception as e:
                    print(f"      Error inspecting widget: {e}")
            
            # Take screenshot
            await page.screenshot(path='data/screenshots/apollo_booking_form.png', full_page=True)
            print("      Screenshot: apollo_booking_form.png")
            
            print("\n[4/4] Checking captured API responses...")
            
            if api_responses:
                print(f"      Captured {len(api_responses)} API responses")
                for i, resp in enumerate(api_responses):
                    print(f"\n      Response {i+1}:")
                    print(f"         URL: {resp['url']}")
                    print(f"         Status: {resp['status']}")
                    try:
                        data = json.loads(resp['body'])
                        print(f"         Data: {json.dumps(data, indent=10)[:500]}...")
                        
                        # Look for price data
                        body_str = str(resp['body']).lower()
                        if any(keyword in body_str for keyword in ['price', 'rate', 'cost', 'total']):
                            print("         [!!] Contains pricing data!")
                    except:
                        print(f"         Body: {resp['body'][:200]}...")
            else:
                print("      No booking API calls captured yet")
                print("      Need to interact with booking form to trigger API calls")
            
            print("\n" + "="*80)
            print("BOOKING API EXPLORATION COMPLETE")
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
    # First try direct API
    print("PART 1: Direct API Queries")
    query_apollo_api_direct()
    
    print("\n\nPART 2: Browser-based API Capture")
    asyncio.run(query_apollo_api_browser())





