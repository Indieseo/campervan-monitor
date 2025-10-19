"""
Try accessing Apollo booking site directly
"""

import asyncio
import sys
import json
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def access_apollo_booking_direct():
    """
    Access the booking subdomain directly
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTOR HOMES - DIRECT BOOKING SITE ACCESS")
    print("="*80 + "\n")
    
    # Setup search dates
    pickup_date = (datetime.now() + timedelta(days=30))
    dropoff_date = (datetime.now() + timedelta(days=37))
    
    print(f"Search Parameters:")
    print(f"  Pickup:  {pickup_date.strftime('%Y-%m-%d')}")
    print(f"  Dropoff: {dropoff_date.strftime('%Y-%m-%d')}")
    print(f"  Duration: 7 days\n")
    
    pricing_data = []
    
    async with async_playwright() as p:
        print("[1/5] Launching browser...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=50,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        # Monitor all responses
        async def handle_response(response):
            url = response.url
            try:
                # Look for any API calls with data
                if response.status == 200 and any(pattern in url.lower() for pattern in ['api', 'booking', 'search', 'vehicle']):
                    body = await response.text()
                    body_lower = body.lower()
                    
                    # Check for actual pricing
                    has_price = any(word in body_lower for word in ['$', 'usd', 'aud', 'price', 'rate', 'cost', 'total'])
                    has_vehicle = any(word in body_lower for word in ['vehicle', 'motorhome', 'camper', 'class'])
                    
                    if has_price or has_vehicle:
                        # Extract any dollar amounts
                        dollar_amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', body)
                        
                        print(f"      [API] {url.split('/')[-1][:50]}")
                        if dollar_amounts:
                            print(f"            Prices: {dollar_amounts[:5]}")
                            pricing_data.append({
                                'url': url,
                                'prices': dollar_amounts,
                                'body': body
                            })
            except:
                pass
        
        page.on('response', handle_response)
        
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        print("[2/5] Trying booking subdomain URLs...")
        
        # Try various booking URLs
        test_urls = [
            'https://booking.apollocamper.com/',
            'https://booking.apollocamper.com/en-US',
            'https://booking.apollocamper.com/search',
            'https://booking.apollocamper.com/vehicles',
            'https://www.apollocamper.com/usa',
            'https://www.apollocamper.com/usa/rv-rental',
            'https://www.apollocamper.com/usa/motorhome-rental',
        ]
        
        for test_url in test_urls:
            try:
                print(f"\n      Trying: {test_url}")
                response = await page.goto(test_url, wait_until='domcontentloaded', timeout=20000)
                
                if response:
                    print(f"      Status: {response.status}")
                    
                    await asyncio.sleep(3)  # Wait for JS to load
                    
                    # Get page content
                    content = await page.content()
                    text = await page.evaluate('() => document.body.innerText')
                    
                    # Check for Cloudflare
                    if 'cloudflare' in text.lower() or 'verifying' in text.lower():
                        print("      [BLOCKED] Cloudflare challenge")
                        continue
                    
                    # Check if this looks like a booking page
                    has_form = any(keyword in text.lower() for keyword in ['pick up', 'drop off', 'location', 'search'])
                    has_vehicles = 'vehicle' in text.lower() or 'motorhome' in text.lower()
                    has_prices = '$' in text or 'price' in text.lower()
                    
                    print(f"      Form: {has_form}, Vehicles: {has_vehicles}, Prices: {has_prices}")
                    
                    if has_form or has_vehicles or has_prices:
                        print("      [PROMISING] This page might have booking functionality")
                        
                        # Take screenshot
                        screenshot_name = f"data/screenshots/apollo_direct_{test_url.split('/')[-1]}.png"
                        await page.screenshot(path=screenshot_name, full_page=True)
                        print(f"      Screenshot: {screenshot_name}")
                        
                        # Look for prices in text
                        prices_found = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
                        if prices_found:
                            print(f"      Prices in text: {prices_found[:10]}")
                        
                        # Try to interact with search form
                        print("      Looking for search form...")
                        search_btn = await page.query_selector('button:has-text("Search"), button:has-text("Find"), input[type="submit"]')
                        if search_btn:
                            print("      [OK] Found search button, clicking...")
                            try:
                                await search_btn.click()
                                await asyncio.sleep(5)
                                print("      Clicked search button")
                            except Exception as e:
                                print(f"      Click failed: {e}")
                        
                        # If this page works, stay here
                        if has_prices and has_vehicles:
                            break
            
            except Exception as e:
                print(f"      Error: {str(e)[:50]}")
                continue
        
        print("\n[3/5] Analyzing current page...")
        
        current_url = page.url
        text = await page.evaluate('() => document.body.innerText')
        
        print(f"      Final URL: {current_url}")
        print(f"      Text length: {len(text)} chars")
        
        # Extract all dollar amounts from visible text
        all_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
        if all_prices:
            price_values = []
            for p in all_prices:
                try:
                    value = float(p.replace(',', ''))
                    if 30 <= value <= 1000:  # Reasonable daily/weekly rate
                        price_values.append(value)
                except:
                    continue
            
            if price_values:
                print(f"\n      [PRICES FOUND IN PAGE TEXT]")
                print(f"      Found {len(price_values)} prices in reasonable range:")
                unique_prices = sorted(set(price_values))
                print(f"      {unique_prices[:15]}")
        
        print("\n[4/5] Checking captured API pricing data...")
        
        if pricing_data:
            print(f"      [SUCCESS] Captured {len(pricing_data)} API calls with prices!\n")
            
            for i, data in enumerate(pricing_data):
                print(f"      API Call {i+1}:")
                print(f"         URL: {data['url']}")
                print(f"         Prices: {data['prices'][:10]}")
                
                # Try to parse as JSON
                try:
                    json_data = json.loads(data['body'])
                    print(f"         Sample: {str(json_data)[:200]}...")
                except:
                    pass
        else:
            print("      No pricing API calls captured")
        
        print("\n[5/5] FINAL ATTEMPT - Manual inspection required")
        print("      The browser will stay open for 30 seconds.")
        print("      Please manually try to:")
        print("      1. Find the booking form on the page")
        print("      2. Enter search details")
        print("      3. Click search")
        print("      4. Observe if prices appear")
        print("\n      Watch the console for any API calls with prices.")
        print("\n" + "="*80)
        
        # Keep browser open longer for manual inspection
        await asyncio.sleep(30)
        
        await browser.close()
        
        # Final summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Pricing API calls captured: {len(pricing_data)}")
        if pricing_data:
            all_prices_found = []
            for data in pricing_data:
                all_prices_found.extend(data['prices'])
            print(f"Total price values found: {len(all_prices_found)}")
            if all_prices_found:
                print(f"Prices: {all_prices_found[:20]}")
        print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(access_apollo_booking_direct())





