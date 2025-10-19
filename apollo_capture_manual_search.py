"""
Open browser and monitor network while YOU manually search
This will capture the REAL pricing API when you submit the form
"""

import asyncio
import sys
import json
import re
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def capture_manual_search():
    """
    Monitor network while user manually searches
    """
    
    print("\n" + "="*80)
    print("APOLLO - MANUAL SEARCH WITH NETWORK CAPTURE")
    print("="*80 + "\n")
    print("I'll open the browser and monitor ALL network traffic.")
    print("YOU manually:")
    print("  1. Click 'Where would you like to travel?'")
    print("  2. Select a location (e.g., USA)")
    print("  3. Choose dates")
    print("  4. Click Search")
    print("\nI'll capture the pricing API call automatically!")
    print("="*80 + "\n")
    
    captured_requests = []
    prices_found = []
    
    async with async_playwright() as p:
        print("[SETUP] Launching browser...")
        
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        print("[SETUP] Installing network monitors...\n")
        
        # Monitor ALL requests
        async def log_request(request):
            url = request.url
            method = request.method
            
            # Log everything from apollo/booking domains
            if 'apollo' in url or 'booking' in url:
                captured_requests.append({
                    'method': method,
                    'url': url,
                    'type': request.resource_type,
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"[REQUEST] {method} {url}")
        
        # Monitor ALL responses
        async def log_response(response):
            url = response.url
            status = response.status
            
            if 'apollo' in url or 'booking' in url:
                print(f"[RESPONSE] {status} {url[:80]}")
                
                # Try to get response body for API calls
                if 'api' in url and status == 200:
                    try:
                        content_type = response.headers.get('content-type', '')
                        if 'json' in content_type:
                            body = await response.text()
                            print(f"[JSON] {len(body)} chars")
                            
                            # Look for prices
                            price_patterns = [
                                r'"price":\s*(\d+(?:\.\d{2})?)',
                                r'"rate":\s*(\d+(?:\.\d{2})?)',
                                r'"cost":\s*(\d+(?:\.\d{2})?)',
                                r'"total":\s*(\d+(?:\.\d{2})?)',
                                r'"daily":\s*(\d+(?:\.\d{2})?)',
                            ]
                            
                            for pattern in price_patterns:
                                matches = re.findall(pattern, body)
                                if matches:
                                    print(f"[PRICES FOUND] {pattern}: {matches[:10]}")
                                    for m in matches:
                                        try:
                                            val = float(m)
                                            if 20 <= val <= 2000:
                                                prices_found.append(val)
                                        except:
                                            pass
                            
                            # Save full response
                            if len(body) < 10000:
                                print(f"[API RESPONSE]\n{json.dumps(json.loads(body), indent=2)[:1000]}")
                    except Exception as e:
                        print(f"[ERROR reading response] {str(e)[:50]}")
        
        page.on('request', log_request)
        page.on('response', log_response)
        
        print("[READY] Going to booking.apollocamper.com...")
        print("="*80 + "\n")
        
        try:
            await page.goto('https://booking.apollocamper.com/', timeout=60000)
            
            print("\n" + "="*80)
            print("BROWSER IS READY - YOUR TURN!")
            print("="*80)
            print("\nNOW YOU:")
            print("  1. Click the search box")
            print("  2. Choose location")
            print("  3. Pick dates")
            print("  4. Click SEARCH")
            print("\nI'm watching all network traffic...")
            print("="*80 + "\n")
            
            # Keep browser open for a long time
            for i in range(300, 0, -1):
                if i % 30 == 0:
                    print(f"\n[{i}s remaining] Still monitoring... ({len(captured_requests)} requests captured)")
                await asyncio.sleep(1)
            
            print("\n\n" + "="*80)
            print("RESULTS")
            print("="*80)
            
            print(f"\nCaptured {len(captured_requests)} network requests")
            
            # Show API calls
            api_calls = [r for r in captured_requests if 'api' in r['url'].lower()]
            if api_calls:
                print(f"\nAPI Calls ({len(api_calls)}):")
                for call in api_calls:
                    print(f"  {call['method']} {call['url']}")
            
            if prices_found:
                unique = sorted(set(prices_found))
                print(f"\n>>> PRICES CAPTURED: {len(unique)} unique values\n")
                for p in unique:
                    print(f"    ${p:.2f}")
                
                print(f"\n>>> STATISTICS:")
                print(f"    Lowest:  ${min(prices_found):.2f}")
                print(f"    Highest: ${max(prices_found):.2f}")
                print(f"    Average: ${sum(prices_found)/len(prices_found):.2f}")
            else:
                print("\n>>> NO PRICES CAPTURED")
                print("    Did you complete the search?")
                print("    Check the requests above for the API endpoint used")
            
            print("\n" + "="*80)
            
            await browser.close()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await browser.close()


if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(capture_manual_search())





