"""
Final attempt - construct direct search URL with parameters to get real vehicle prices
"""

import asyncio
import sys
import json
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def get_apollo_final_prices():
    """
    Try direct search URLs with parameters
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - FINAL REAL PRICE EXTRACTION")
    print("="*80 + "\n")
    
    # Setup dates
    pickup_date = (datetime.now() + timedelta(days=30))
    dropoff_date = (datetime.now() + timedelta(days=37))
    
    pickup_str = pickup_date.strftime('%Y-%m-%d')
    dropoff_str = dropoff_date.strftime('%Y-%m-%d')
    
    print(f"Search: {pickup_str} to {dropoff_str} (7 days)\n")
    
    real_prices = []
    all_api_data = []
    
    async with async_playwright() as p:
        print("[1/3] Launching browser...")
        
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
        
        # Monitor ALL API responses
        async def handle_response(response):
            url = response.url
            try:
                if 'api' in url.lower() and response.status == 200:
                    body = await response.text()
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(body)
                        all_api_data.append({
                            'url': url,
                            'data': data
                        })
                        
                        # Look for pricing fields
                        def extract_prices(obj, path=""):
                            prices = []
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    if isinstance(value, (int, float)) and any(keyword in key.lower() for keyword in ['price', 'rate', 'cost', 'total', 'charge', 'daily', 'fee']):
                                        if 30 <= value <= 10000:  # Reasonable price range
                                            prices.append({
                                                'field': f"{path}.{key}" if path else key,
                                                'value': value
                                            })
                                    prices.extend(extract_prices(value, f"{path}.{key}" if path else key))
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    prices.extend(extract_prices(item, f"{path}[{i}]"))
                            return prices
                        
                        prices = extract_prices(data)
                        if prices:
                            print(f"      [PRICES] {url.split('/')[-1][:40]}")
                            for p in prices[:5]:
                                print(f"         {p['field']}: ${p['value']}")
                            real_prices.extend(prices)
                    except:
                        pass
            except:
                pass
        
        page.on('response', handle_response)
        
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        print("[2/3] Trying search URLs with parameters...")
        
        # Try various search URL formats
        search_urls = [
            # Booking subdomain searches
            f"https://booking.apollocamper.com/search?pickup={pickup_str}&dropoff={dropoff_str}&location=US",
            f"https://booking.apollocamper.com/search?pickupDate={pickup_str}&returnDate={dropoff_str}&country=US",
            f"https://booking.apollocamper.com/search?from={pickup_str}&to={dropoff_str}",
            f"https://booking.apollocamper.com/en-US/search?pickup={pickup_str}&dropoff={dropoff_str}",
            
            # Main site searches
            f"https://www.apollocamper.com/search?pickup={pickup_str}&dropoff={dropoff_str}",
            f"https://www.apollocamper.com/usa/search?from={pickup_str}&to={dropoff_str}",
            f"https://www.apollocamper.com/motorhome-rental?dates={pickup_str},{dropoff_str}",
        ]
        
        for search_url in search_urls:
            try:
                print(f"\n      Trying: {search_url[:80]}...")
                response = await page.goto(search_url, wait_until='networkidle', timeout=20000)
                
                if response:
                    print(f"      Status: {response.status}")
                    
                    # Wait for API calls
                    await asyncio.sleep(5)
                    
                    # Check page content
                    text = await page.evaluate('() => document.body.innerText')
                    
                    # Look for $ amounts in visible text
                    visible_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
                    if visible_prices:
                        print(f"      Visible prices: {visible_prices[:10]}")
                        
                        # Filter to reasonable daily/weekly rates
                        for p in visible_prices:
                            try:
                                value = float(p.replace(',', ''))
                                if 30 <= value <= 1000:
                                    real_prices.append({
                                        'field': 'visible_price',
                                        'value': value,
                                        'url': search_url
                                    })
                            except:
                                pass
                    
                    # Check if we got good results
                    has_vehicles = 'vehicle' in text.lower() or 'motorhome' in text.lower()
                    has_prices = len(visible_prices) > 0
                    
                    if has_vehicles and has_prices:
                        print("      [GOOD RESULTS] Found vehicles and prices!")
                        screenshot_name = f"data/screenshots/apollo_search_results_{datetime.now().strftime('%H%M%S')}.png"
                        await page.screenshot(path=screenshot_name, full_page=True)
                        print(f"      Screenshot: {screenshot_name}")
                        break  # Found good page, stop searching
            
            except Exception as e:
                print(f"      Error: {str(e)[:50]}")
                continue
        
        print("\n[3/3] FINAL RESULTS")
        print("="*80)
        
        if real_prices:
            # Deduplicate and sort
            unique_prices = {}
            for p in real_prices:
                key = f"{p['value']}"
                if key not in unique_prices:
                    unique_prices[key] = p
            
            sorted_prices = sorted(unique_prices.values(), key=lambda x: x['value'])
            
            print(f"\n      [SUCCESS] FOUND {len(sorted_prices)} UNIQUE REAL PRICES!\n")
            
            for p in sorted_prices[:30]:
                source = p.get('field', 'unknown')
                url_info = f" ({p['url'].split('/')[-1][:30]})" if 'url' in p else ""
                print(f"      ${p['value']:.2f} - {source}{url_info}")
            
            # Calculate statistics
            daily_rates = [p['value'] for p in sorted_prices if 30 <= p['value'] <= 500]
            if daily_rates:
                print(f"\n      DAILY RATE STATISTICS:")
                print(f"         Count: {len(daily_rates)}")
                print(f"         Lowest: ${min(daily_rates):.2f}")
                print(f"         Highest: ${max(daily_rates):.2f}")
                print(f"         Average: ${sum(daily_rates)/len(daily_rates):.2f}")
                print(f"         Median: ${sorted(daily_rates)[len(daily_rates)//2]:.2f}")
        else:
            print("\n      [NO REAL PRICES FOUND]")
            print("      Apollo Motorhomes requires manual interaction with their booking widget")
            print("      or has strong anti-scraping protection on their pricing pages.")
            
            if all_api_data:
                print(f"\n      However, captured {len(all_api_data)} API responses.")
                print("      Sample endpoints:")
                for api_call in all_api_data[:10]:
                    print(f"         {api_call['url']}")
        
        print("\n" + "="*80)
        print("Keep browser open for 20 seconds for manual inspection...")
        print("="*80 + "\n")
        
        await asyncio.sleep(20)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(get_apollo_final_prices())





